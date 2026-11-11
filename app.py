mport os, re, secrets, uuid
from datetime import datetime, timezone
from functools import wraps
from flask import Flask, render_template, request, session, redirect, url_for, abort, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

app.config.update(
    SECRET_KEY=os.environ.get("SECRET_KEY", "dev-only-change-me"),
    SQLALCHEMY_DATABASE_URI=os.environ.get("DATABASE_URL", "sqlite:///souk.db").replace("postgres://", "postgresql://"),
    SQLALCHEMY_TRACK_MODIFICATIONS=False,
    MAX_CONTENT_LENGTH=5 * 1024 * 1024,
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE="Lax",
    SESSION_COOKIE_SECURE=os.environ.get("SECURE_COOKIES", "0") == "1",
    PERMANENT_SESSION_LIFETIME=3600,
)

db = SQLAlchemy(app)

ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD")
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

# ---------- Init DB ----------

def init_db():
    db.create_all()
    if not Product.query.first():
        db.session.add_all([
            Product(name="سماعة بلوتوث Pro Max", price=199, old_price=349, category="إلكترونيات",
                    image="https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=600"),
            Product(name="ساعة ذكية Ultra", price=299, old_price=499, category="إلكترونيات",
                    image="https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=600"),
        ])
        db.session.commit()

with app.app_context():
    init_db()

# ---------- Helpers / Security ----------

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
    try:
        cart_count = sum(int(v) for v in session.get("cart", {}).values())
    except (ValueError, TypeError):
        cart_count = 0
    return dict(csrf=session["_t"], cart_count=cart_count,
                WHATSAPP=WHATSAPP, admin=session.get("admin"), statuses=STATUSES)

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
        try:
            pid_int, qty = int(pid), int(q)
        except (ValueError, TypeError):
            continue
        p = Product.query.get(pid_int)
        if p and p.active and qty > 0:
            qty = min(qty, 50)
            items.append((p, qty))
            total += p.price * qty
    return items, total

def parse_int(value, default=0from flask import Flask, render_template_string, jsonify, Response
app = Flask(__name__)

MANIFEST = {
  "name": "SOUK ALI",
  "short_name": "SOUK ALI",
  "start_url": "/",
  "display": "standalone",
  "background_color": "#111111",
  "theme_color": "#111111",
  "icons": [
    {"src": "https://cdn-icons-png.flaticon.com/512/3081/3081559.png","sizes": "192x192","type": "image/png"},
    {"src": "https://cdn-icons-png.flaticon.com/512/3081/3081559.png","sizes": "512x512","type": "image/png", "purpose": "any maskable"}
  ]
}

SW = """
self.addEventListener('install', e => { self.skipWaiting(); });
self.addEventListener('activate', e => { self.clients.claim(); });
self.addEventListener('fetch', e => { });
"""

HTML = """
<!DOCTYPE html>
<html dir="rtl" lang="ar"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>SOUK ALI</title>
<link rel="manifest" href="/manifest.json"><meta name="theme-color" content="#111111">
<style>
body{font-family:Arial;margin:0;background:#f8f9fa;text-align:center}
.topbar{background:#111;color:#fff;padding:8px;font-size:13px} .topbar b{color:#ffc107}
header{position:sticky;top:0;background:#fff;display:flex;justify-content:space-between;align-items:center;padding:12px 15px;box-shadow:0 2px 10px rgba(0,0,0,.08)}
.logo{font-size:24px;font-weight:900} .logo span{color:#ff3b30}
.hero{background:linear-gradient(135deg,#111,#ff3b30);color:#fff;padding:30px 15px;border-radius:0 0 25px 25px}
.hero h1{margin:0;font-size:28px} .hero button{background:#ffc107;border:none;padding:13px 30px;border-radius:30px;font-weight:900;font-size:16px;margin-top:10px}
.appBtn{background:#fff!important;color:#111!important;border:none;padding:12px 22px;border-radius:30px;font-weight:900;margin-top:12px;font-size:15px}
.searchBox{background:#fff;padding:12px;position:sticky;top:58px;z-index:99;box-shadow:0 2px 10px rgba(0,0,0,.06)}
.searchBox input{width:90%;padding:13px;border:2px solid #eee;border-radius:30px;font-size:15px;text-align:center;outline:none}
.grid{display:grid;grid-template-columns:1fr 1fr;gap:12px;padding:12px} .card{background:#fff;border-radius:18px;overflow:hidden;padding-bottom:12px;box-shadow:0 4px 15px rgba(0,0,0,.06)} .card img{width:100%;height:180px;object-fit:cover} .btn{width:calc(100% - 20px);margin:10px;background:#25D366;color:#fff;border:none;padding:12px;border-radius:12px;font-weight:900}
input{width:90%;padding:13px;margin:8px;border:1px solid #ddd;border-radius:12px} .box{background:#fff;max-width:420px;margin:20px auto;padding:20px;border-radius:18px} #preview{width:100%;border-radius:12px;display:none}
.lock{font-size:50px} .loginBtn{background:#111;color:#fff;border:none;padding:13px 30px;border-radius:12px;font-weight:900;width:90%;font-size:16px}
</style></head><body>
<div class="topbar">🔥 <b>تخفيض حتى 50%</b> - التوصيل مجاني فوق 300 درهم</div>
<div id="app"></div>
<script>
if('serviceWorker' in navigator){ navigator.serviceWorker.register('/sw.js'); }
let deferredPrompt = null;
window.addEventListener('beforeinstallprompt', (e)=>{ e.preventDefault(); deferredPrompt = e; });
window.addEventListener('appinstalled', ()=>{ deferredPrompt = null; });

let products = JSON.parse(localStorage.getItem('souk_products') || '[]');
if(products.length==0){
 products=[
  {name:'سماعة بلوتوث Pro Max',price:199,old:349,img:'https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=600'},
  {name:'ساعة ذكية Ultra',price:299,old:499,img:'https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=600'}
 ];
 localStorage.setItem('souk_products',JSON.stringify(products));
}
let selectedImg='';
const ADMIN_PASS = 'ob10m';
let searchText = '';
function render(){
 let filtered = products.filter(p => p.name.includes(searchText));
 let cards='';
 if(filtered.length==0){ cards = `<p style="grid-column:1/3">😢 ما لقيناش "${searchText}"</p>`; }
 filtered.forEach(p=>{ cards+=`<div class="card"><img src="${p.img}"><h3>${p.name}</h3><p><b style="color:#ff3b30">${p.price} درهم</b> <s>${p.old||''}</s></p><a href="https://wa.me/212770384739?text=بغيت نشري ${encodeURIComponent(p.name)}"><button class="btn">اطلب عبر واتساب ✅</button></a></div>`; });
 document.getElementById('app').innerHTML=`<header><div class="logo">SOUK<span>ALI</span></div><div>🛒</div></header><div class="hero"><h1>سوق علي - تسوق بثقة 🚀</h1><p>أكثر من 1000 زبون راضي - الدفع عند الاستلام</p><br><button onclick="document.getElementById('prods').scrollIntoView({behavior:'smooth'})">تسوق الآن 🔥</button><br><button id="installBtn" class="appBtn" onclick="installApp()">📲 ثبت التطبيق في هاتفك</button></div><div class="searchBox"><input id="searchInput" placeholder="🔍 قلب على أي منتج... سماعة، ساعة..." value="${searchText}" oninput="doSearch(this.value)"></div><h2 id="prods">🔥 العروض الأكثر مبيعا</h2><div class="grid">${cards}</div><p>واتساب: 0770384739</p>`;
 window.doSearch = (v)=>{ searchText=v; render(); let inp=document.getElementById('searchInput'); inp.focus(); inp.setSelectionRange(inp.value.length, inp.value.length); };
}
async function installApp(){
  if(deferredPrompt){
    deferredPrompt.prompt();
    const choice = await deferredPrompt.userChoice;
    if(choice.outcome === 'accepted'){ console.log('تم التثبيت'); }
    deferredPrompt = null;
  } else {
    // إلا كان التطبيق أصلا مثبّت ولا المتصفح ما عطاش الإذن، نعاود نطلب من Chrome يبين النافذة
    alert('ساين 2 ثواني و عاود كليكي - Chrome كيوجد التثبيت');
  }
}
function showAdmin(){
 document.getElementById('app').innerHTML=`<div class="box"><h2>➕ زيد منتج</h2><input id="n" placeholder="سميت المنتج"><input id="pr" type="number" placeholder="الثمن"><input id="old" type="number" placeholder="الثمن القديم"><input id="file" type="file" accept="image/*"><img id="preview"><button class="btn" onclick="add()">زيد المنتج ✅</button><div id="list"></div><button onclick="logout()" style="background:red;color:#fff;border:none;padding:10px 20px;border-radius:10px;margin-top:10px">خروج 🔒</button><br><a href="/">رجع للموقع</a></div>`;
 document.getElementById('file').addEventListener('change', function(e){ let f=e.target.files[0]; let r=new FileReader(); r.onload=function(ev){selectedImg=ev.target.result; document.getElementById('preview').src=selectedImg; document.getElementById('preview').style.display='block';}; r.readAsDataURL(f); });
 window.add=()=>{ let n=document.getElementById('n').value, pr=document.getElementById('pr').value, old=document.getElementById('old').value; if(!n||!pr||!selectedImg){alert('عمر كلشي!');return} products.push({name:n,price:pr,old:old,img:selectedImg}); localStorage.setItem('souk_products',JSON.stringify(products)); alert('تزاد!'); location.reload(); };
 let l=''; products.forEach((p,i)=>{l+=`<p>${p.name} <button onclick="del(${i})">مسح</button></p>`}); document.getElementById('list').innerHTML=l;
 window.del=(i)=>{products.splice(i,1); localStorage.setItem('souk_products',JSON.stringify(products)); location.reload()};
}
function logout(){ localStorage.removeItem('souk_admin'); location.reload(); }
if(location.pathname.includes('admin')){
 if(localStorage.getItem('souk_admin')==='ok'){ showAdmin(); }
 else {
  document.getElementById('app').innerHTML=`<div class="box"><div class="lock">🔒</div><h2>دخول المدير فقط</h2><input id="pass" type="password" placeholder="كتب المودباس"><button class="loginBtn" onclick="checkPass()">دخول ✅</button><p id="err" style="color:red"></p><a href="/">رجع للموقع</a></div>`;
  window.checkPass=()=>{ let p=document.getElementById('pass').value; if(p===ADMIN_PASS){ localStorage.setItem('souk_admin','ok'); showAdmin(); } else { document.getElementById('err').innerText='❌ المودباس غالط!'; } };
 }
} else { render(); }
</script></body></html>
"""
@app.route("/manifest.json")
def manifest():
    return jsonify(MANIFEST)
@app.route("/sw.js")
def sw():
    return Response(SW, mimetype="application/javascript")
@app.route("/")
@app.route("/admin")
@app.route("/api/index")
@app.route("/<path:path>")
def home(path=None):
    return render_template_string(HTML)
if __name__ == "__main__":
    app.run()import os, re, secrets, uuid
from datetime import datetime, timezone
from functools import wraps
from flask import Flask, render_template, request, session, redirect, url_for, abort, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
SECRET_KEY = os.environ.get("SECRET_KEY")
if not SECRET_KEY and os.environ.get("FLASK_DEBUG") != "1":
    raise RuntimeError("حدد SECRET_KEY ف environment (ولا FLASK_DEBUG=1 للتجريب المحلي)")

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

ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD")
WHATSAPP = os.environ.get("WHATSAPP", "212770384739")
UPLOADS = os.path.join(app.static_folder, "uploads")
STATUSES = ["جديد", "تأكد", "تم الشحن", "تسلّم", "ملغي"]
ALLOWED_EXTS = {"jpg", "jpeg", "png", "webp"}
PHONE_RE = re.compile(r"(\+212|0)[5-7]\d{8}")

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

def parse_int(value, default=0, lo=None, hi=None):
    try:
        n = int(str(value).strip())
    except (ValueError, TypeError):
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

@app.route("/")
def index():
    q, cat = request.args.get("q", "").strip()[:100], request.args.get("cat", "")
    qs = Product.query.filter_by(active=True)
    if q: qs = qs.filter(Product.name.ilike(f"%{q}%"))
    if cat: qs = qs.filter_by(category=cat)
    cats = [c for (c,) in db.session.query(Product.category).filter(Product.active, Product.category != "").distinct()]
    return render_template("index.html", products=qs.order_by(Product.id.desc()).all(), cats=cats, q=q)

@app.route("/product/<int:pid>")
def product(pid):
    p = db.get_or_404(Product, pid)
    if not p.active: abort(404)
    return render_template("product.html", p=p)

@app.post("/cart/add/<int:pid>")
def cart_add(pid):
    p = db.get_or_404(Product, pid)
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
    if isinstance(cart, dict): cart.pop(str(pid), None); session["cart"] = cart
    return redirect(url_for("cart"))

@app.route("/cart")
def cart():
    items, total = get_cart()
    return render_template("cart.html", items=items, total=total)

@app.post("/checkout")
def checkout():
    items, total = get_cart()
    f = request.form
    name, phone, city, address = [f.get(k, "").strip()[:200] for k in ("name", "phone", "city", "address")]
    if not items or not all((name, city, address)) or not PHONE_RE.fullmatch(phone.replace(" ", "")):
        flash("عمر كل الخانات. رقم الهاتف مثال: 0612345678")
        return redirect(url_for("cart"))
    o = Order(name=name, phone=phone, city=city, address=address, total=total,
              items="\n".join(f"{p.name} × {q} = {p.price * q} درهم" for p, q in items))
    db.session.add(o); db.session.commit()
    session.pop("cart", None)
    return redirect(url_for("thanks", oid=o.id))

@app.route("/thanks/<int:oid>")
def thanks(oid):
    return render_template("thanks.html", oid=oid)

@app.route("/admin", methods=["GET", "POST"])
def admin():
    if request.method == "POST" and not session.get("admin"):
        pw = request.form.get("password", "")
        if ADMIN_PASSWORD and secrets.compare_digest(pw.encode(), ADMIN_PASSWORD.encode()):
            session.clear(); session["_t"] = secrets.token_hex(16)
            session["admin"] = True; session.permanent = True
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
    price = parse_int(f.get("price"), -1, -1)
    if not name or price < 0: abort(400)
    img = f.get("image_url", "").strip()
    if not img.startswith("https://"): img = ""
    file = request.files.get("file")
    if file and file.filename:
        ext = file.filename.rsplit(".", 1)[-1].lower()
        if ext not in ALLOWED_EXTS: abort(400)
        os.makedirs(UPLOADS, exist_ok=True)
        fn = f"{uuid.uuid4().hex}.{ext}"
        file.save(os.path.join(UPLOADS, fn)); img = "/static/uploads/" + fn
    db.session.add(Product(name=name, price=price, old_price=parse_int(f.get("old_price")) or None, image=img,
                
