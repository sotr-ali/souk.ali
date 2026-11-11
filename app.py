import os, secrets
from flask import Flask, request, session, redirect, url_for, render_template_string

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "souk-test-123")

# داتا مؤقتة للتجريب فقط - كتمسح إلا طفيتي السيرفر
PRODUCTS = [
    {"id": 1, "name": "سماعة بلوتوث Pro Max", "price": 199, "old": 349, "img": "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=600"},
    {"id": 2, "name": "ساعة ذكية Ultra", "price": 299, "old": 499, "img": "https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=600"},
]
ORDERS = []
ADMIN_PASS = os.environ.get("ADMIN_PASSWORD", "1234")  # للتجريب فقط

BASE = """
<!DOCTYPE html><html dir="rtl" lang="ar"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><title>SOUK ALI</title>
<style>
body{font-family:Arial;margin:0;background:#f8f9fa;text-align:center}
header{background:#111;color:#fff;padding:15px;display:flex;justify-content:space-between}
.logo{font-weight:900;font-size:22px}.logo span{color:#ff3b30}
.hero{background:linear-gradient(135deg,#111,#ff3b30);color:#fff;padding:30px 15px}
.hero button{background:#ffc107;border:none;padding:13px 30px;border-radius:30px;font-weight:900}
.grid{display:grid;grid-template-columns:1fr 1fr;gap:12px;padding:12px}
.card{background:#fff;border-radius:18px;overflow:hidden;padding-bottom:12px}
.card img{width:100%;height:170px;object-fit:cover}
.btn{background:#25D366;color:#fff;border:none;padding:12px;border-radius:12px;font-weight:900;width:90%;margin:10px 0}
input{width:90%;padding:13px;margin:8px;border:1px solid #ddd;border-radius:12px}
.box{background:#fff;max-width:420px;margin:20px auto;padding:20px;border-radius:18px}
</style></head><body>
<header><div class="logo">SOUK<span>ALI</span></div><div><a href="/cart" style="color:#fff;text-decoration:none">🛒 {{cart}} | <a href="/admin" style="color:#ffc107">أدمن</a></div></header>
{{content}}
</body></html>
"""

def render(content, cart=0):
    return render_template_string(BASE.replace("{{content}}", content), cart=cart)

def cart_count():
    return sum(session.get("cart", {}).values())

@app.route("/")
def index():
    q = request.args.get("q", "")
    prods = [p for p in PRODUCTS if q in p["name"]] if q else PRODUCTS
    cards = ""
    for p in prods:
        cards += f"""<div class="card"><img src="{p['img']}"><h3>{p['name']}</h3>
        <p><b style="color:#ff3b30">{p['price']} درهم</b> <s>{p['old']}</s></p>
        <form method="post" action="/add/{p['id']}"><button class="btn">زيد للسلة 🛒</button></form></div>"""
    if not cards: cards = "<p>ما لقيناش هاد المنتج 😢</p>"
    html = f"""
    <div class="hero"><h1>سوق علي - تسوق بثقة 🚀</h1><p>الدفع عند الاستلام</p></div>
    <form><input name="q" value="{q}" placeholder="🔍 قلب على منتج..."><button>قلب</button></form>
    <h2>🔥 العروض</h2><div class="grid">{cards}</div>
    """
    return render(html, cart_count())

@app.post("/add/<int:pid>")
def add(pid):
    cart = session.get("cart", {})
    cart[str(pid)] = cart.get(str(pid), 0) + 1
    session["cart"] = cart
    return redirect(url_for("cart_page"))

@app.route("/cart")
def cart_page():
    cart = session.get("cart", {})
    items = ""
    total = 0
    for pid, qty in cart.items():
        p = next((x for x in PRODUCTS if x["id"] == int(pid)), None)
        if p:
            total += p["price"] * qty
            items += f"<p>{p['name']} × {qty} = {p['price']*qty} درهم</p>"
    if not items: items = "<p>السلة خاوية</p>"
    html = f"""
    <div class="box"><h2>🛒 السلة ديالك</h2>{items}<h3>المجموع: {total} درهم</h3>
    <form method="post" action="/checkout">
    <input name="name" placeholder="الاسم الكامل" required>
    <input name="phone" placeholder="النمرة 06..." required>
    <input name="city" placeholder="المدينة" required>
    <input name="address" placeholder="العنوان" required>
    <button class="btn">أكد الطلب ✅</button></form></div>
    """
    return render(html, cart_count())

@app.post("/checkout")
def checkout():
    cart = session.get("cart", {})
    total = sum(next((p["price"] for p in PRODUCTS if p["id"]==int(pid)),0)*qty for pid,qty in cart.items())
    ORDERS.append({"name": request.form.get("name"), "phone": request.form.get("phone"), "city": request.form.get("city"), "total": total})
    session.pop("cart", None)
    return render(f"<div class='box'><h1>✅ شكرا!</h1><p>وصلنا الطلب ديالك ديال {total} درهم</p><p>غادي نعيطو ليك باش نأكدو</p><a href='/'>رجع للمتجر</a></div>")

@app.route("/admin", methods=["GET","POST"])
def admin():
    if request.method == "POST":
        if request.form.get("password") == ADMIN_PASS:
            session["admin"] = True
        return redirect("/admin")
    if not session.get("admin"):
        return render("""<div class="box"><h2>🔒 دخول المدير</h2>
        <form method="post"><input name="password" type="password" placeholder="المودباس: 1234">
        <button class="btn" style="background:#111">دخول</button></form></div>""")
    orders_html = "".join([f"<p>👤 {o['name']} - {o['phone']} - {o['city']} - <b>{o['total']} درهم</b></p>" for o in ORDERS]) or "<p>باقي ما كاين حتى طلب</p>"
    prods_html = "".join([f"<p>{p['name']} - {p['price']} درهم</p>" for p in PRODUCTS])
    return render(f"""<div class="box"><h2>لوحة الأدمن</h2><h3>الطلبات:</h3>{orders_html}<h3>المنتجات:</h3>{prods_html}
    <form method="post" action="/admin/add"><input name="name" placeholder="سمية المنتج" required>
    <input name="price" type="number" placeholder="الثمن" required>
    <input name="img" placeholder="رابط التصويرة" required>
    <button class="btn">زيد منتج ✅</button></form>
    <a href="/">رجع للموقع</a></div>""")

@app.post("/admin/add")
def admin_add():
    if not session.get("admin"): return redirect("/admin")
    PRODUCTS.append({"id": max([p["id"] for p in PRODUCTS])+1 if PRODUCTS else 1,
                     "name": request.form.get("name"), "price": int(request.form.get("price") or 0), "old": 0,
                     "img": request.form.get("img")})
    return redirect("/admin")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
