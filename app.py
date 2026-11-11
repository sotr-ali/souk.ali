import os, re, secrets, uuid
from datetime import datetime, timezone
from functools import wraps
from flask import Flask, render_template, request, session, redirect, url_for, abort, flash, jsonify, Response
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

SECRET_KEY = os.environ.get("SECRET_KEY")
if not SECRET_KEY and os.environ.get("FLASK_DEBUG") != "1":
    raise RuntimeError("حدد SECRET_KEY ف environment")

app.config.update(
    SECRET_KEY=SECRET_KEY or "dev-only-change-me",
    SQLALCHEMY_DATABASE_URI=os.environ.get("DATABASE_URL", "sqlite:///souk.db").replace("postgres://", "postgresql://"),
    SQLALCHEMY_TRACK_MODIFICATIONS=False,
    MAX_CONTENT_LENGTH=5 * 1024 * 1024,
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE="Lax",
    SESSION_COOKIE_SECURE=os.environ.get("SECURE_COOKIES", "0") == "1",
    PERMANENT_SESSION_LIFETIME=3600,
)
db = SQLAlchemy(app)

ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD") #  عمرك تحطو هنا فالكود
WHATSAPP = os.environ.get("WHATSAPP", "212770384739")
UPLOADS = os.path.join(app.static_folder, "uploads")
STATUSES = ["جديد", "تأكد", "تم الشحن", "تسلّم", "ملغي"]
ALLOWED_EXTS = {"jpg", "jpeg", "png", "webp"}
PHONE_RE = re.compile(r"(\+212|0)[5-7]\d{8}")

# ---------- Models ----------
class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    price = db.Column(db.Integer, nullable=False)
    old_price = db.Column(db.Integer)
    image = db.Column(db.String(500), default="")
    category = db.Column(db.String(80), default="")
    description = db.Column(db.Text, default="")
    active = db.Column(db.Boolean, default=True)

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    phone = db.Column(db.String(30), nullable=False)
    city = db.Column(db.String(100), nullable=False)
    address = db.Column(db.String(300), nullable=False)
    items = db.Column(db.Text, default="")
    total = db.Column(db.Integer, nullable=False, default=0)
    status = db.Column(db.String(30), default=STATUSES[0])
    created = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

def init_db():
    db.create_all()
    if not Product.query.first():
        db.session.add_all([
            Product(name="سماعة بلوتوث Pro Max", price=199, old_price=349, category="إلكترونيات",
                    image="https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=600"),
            Product(name="ساعة ذكية Ultra", price=299, old_price=499, category="إلكترونيات",
                    image="https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=600")])
        db.session.commit()

with app.app_context():
    init_db()

# ---------- Helpers ----------
def parse_int(value, default=0, lo=None, hi=None):
    try:
        n = int(str(value).strip())
    except (ValueError, TypeError, AttributeError):
        return default
    if lo is not None: n = max(lo, n)
    if hi is not None: n = min(hi, n)
    return n

@app.before_request
def csrf_check():
    if request.method == "POST":
        token = request.form.get("_t", "")
        if not token or not secrets.compare_digest(token, session.get("_t", "x")):
            abort(400)

@app.context_processor
def inject():
    if "_t" not in session:
        session["_t"] = secrets.token_hex(16)
    cart = session.get("cart", {})
    count = sum(parse_int(v) for v in cart.values()) if isinstance(cart, dict) else 0
    return dict(csrf=session["_t"], cart_count=count, WHATSAPP=WHATSAPP,
                admin=session.get("admin"), statuses=STATUSES)

def admin_required(f):
    @wraps(f)
    def w(*a, **k):
        if not session.get("admin"):
            return redirect(url_for("admin"))
        return f(*a, **k)
    return w

def get_cart():
    items, total = [], 0
    cart = session.get("cart", {})
    if not isinstance(cart, dict):
        return items, total
    for pid, q in cart.items():
        qty = parse_int(q, 0, 0, 50)
        p = db.session.get(Product, parse_int(pid))
        if p and p.active and qty > 0:
            items.append((p, qty)); total += p.price * qty
    return items, total

# ---------- PWA ----------
@app.route("/manifest.json")
def manifest():
    return jsonify({
        "name": "SOUK ALI",
        "short_name": "SOUK ALI",
        "start_url": "/",
        "display": "standalone",
        "background_color": "#111111",
        "theme_color": "#111111",
        "icons": [
            {"src": "https://cdn-icons-png.flaticon.com/512/3081/3081559.png", "sizes": "192x192", "type": "image/png"},
            {"src": "https://cdn-icons-png.flaticon.com/512/3081/3081559.png", "sizes": "512x512", "type": "image/png", "purpose": "any maskable"}
        ]
    })

@app.route("/sw.js")
def sw():
    js = "self.addEventListener('install', e => { self.skipWaiting(); });\nself.addEventListener('activate', e => { self.clients.claim(); });"
    return Response(js, mimetype="application/javascript")

# ---------- Public ----------
@app.route("/")
def index():
    q = request.args.get("q", "").strip()[:100]
    cat = request.args.get("cat", "").strip()[:80]
    qs = Product.query.filter_by(active=True)
    if q:
        safe_q = q.replace("%", "").replace("_", "")
        qs = qs.filter(Product.name.ilike(f"%{safe_q}%"))
    if cat:
        qs = qs.filter_by(category=cat)
    cats = [c for (c,) in db.session.query(Product.category).filter(Product.active, Product.category != "").distinct()]
    return render_template("index.html", products=qs.order_by(Product.id.desc()).all(), cats=cats, q=q)

@app.route("/product/<int:pid>")
def product(pid):
    p = Product.query.get_or_404(pid)
    if not p.active: abort(404)
    return render_template("product.html", p=p)

@app.post("/cart/add/<int:pid>")
def cart_add(pid):
    p = Product.query.get_or_404(pid)
    if not p.active: abort(404)
    cart = session.get("cart", {})
    if not isinstance(cart, dict): cart = {}
    qty = parse_int(request.form.get("qty"), 1, 1, 20)
    cart[str(pid)] = min(parse_int(cart.get(str(pid)), 0) + qty, 50)
    session["cart"] = cart
    return redirect(url_for("cart"))

@app.post("/cart/remove/<int:pid>")
def cart_remove(pid):
    cart = session.get("cart", {})
    if isinstance(cart, dict):
        cart.pop(str(pid), None); session["cart"] = cart
    return redirect(url_for("cart"))

@app.route("/cart")
def cart():
    items, total = get_cart()
    return render_template("cart.html", items=items, total=total)

@app.post("/checkout")
def checkout():
    items, total = get_cart()
    f = request.form
    name = f.get("name", "").strip()[:200]
    phone = f.get("phone", "").strip().replace(" ", "")[:30]
    city = f.get("city", "").strip()[:100]
    address = f.get("address", "").strip()[:300]
    if not items or not all((name, city, address)) or not PHONE_RE.fullmatch(phone):
        flash("عمر كل الخانات. رقم الهاتف مثال: 0612345678")
        return redirect(url_for("cart"))
    o = Order(name=name, phone=phone, city=city, address=address, total=total,
              items="\n".join(f"{p.name} × {q} = {p.price * q} درهم" for p, q in items))
    db.session.add(o); db.session.commit()
    session.pop("cart", None)
    return redirect(url_for("thanks", oid=o.id))

@app.route("/thanks/<int:oid>")
def thanks(oid):
    o = Order.query.get_or_404(oid)
    return render_template("thanks.html", oid=o.id, order=o)

# ---------- Admin ----------
@app.route("/admin", methods=["GET", "POST"])
def admin():
    if request.method == "POST" and not session.get("admin"):
        pw = request.form.get("password", "")
        if ADMIN_PASSWORD and pw and secrets.compare_digest(pw, ADMIN_PASSWORD):
            session.clear()
            session["_t"] = secrets.token_hex(16)
            session["admin"] = True
            session.permanent = True
        else:
            flash("المودباس غالط")
        return redirect(url_for("admin"))
    if not session.get("admin"):
        return render_template("admin.html", products=[], orders=[])
    return render_template("admin.html", products=Product.query.order_by(Product.id.desc()).all(),
                           orders=Order.query.order_by(Order.id.desc()).limit(100).all())

@app.post("/admin/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))

@app.post("/admin/product")
@admin_required
def add_product():
    f = request.form
    name = f.get("name", "").strip()[:200]
    price = parse_int(f.get("price"), -1)
    if not name or price <= 0 or price > 1000000:
        flash("الثمن أو الاسم غالط"); return redirect(url_for("admin"))
    img = f.get("image_url", "").strip()[:500]
    if not img.startswith("https://"): img = ""
    file = request.files.get("file")
    if file and file.filename:
        ext = file.filename.rsplit(".", 1)[-1].lower() if "." in file.filename else ""
        if ext not in ALLOWED_EXTS: abort(400)
        os.makedirs(UPLOADS, exist_ok=True)
        fn = f"{uuid.uuid4().hex}.{ext}"
        file.save(os.path.join(UPLOADS, fn)); img = "/static/uploads/" + fn
    old = parse_int(f.get("old_price"), 0) or None
    if old is not None and old < price: old = None
    db.session.add(Product(name=name, price=price, old_price=old, image=img,
                           category=f.get("category", "").strip()[:80],
                           description=f.get("description", "").strip()[:2000]))
    db.session.commit()
    return redirect(url_for("admin"))

@app.post("/admin/product/<int:pid>/delete")
@admin_required
def del_product(pid):
    db.session.delete(Product.query.get_or_404(pid)); db.session.commit()
    return redirect(url_for("admin"))

@app.post("/admin/order/<int:oid>")
@admin_required
def set_status(oid):
    s = request.form.get("status")
    if s in STATUSES:
        o = Order.query.get_or_404(oid); o.status = s; db.session.commit()
    return redirect(url_for("admin"))

@app.errorhandler(404)
def not_found(e):
    return render_template("404.html"), 404

@app.errorhandler(400)
def bad(e):
    return render_template("400.html"), 400

if __name__ == "__main__":
    app.run(debug=os.environ.get("FLASK_DEBUG") == "1")
