import os
import json
from flask import Flask, render_template_string, jsonify, Response, request, session, redirect, url_for

app = Flask(__name__)

# ===== 1. الحماية - هادو كيبقاو غير فالسيرفر، الزبون ما كيشوفهمش =====
# المودباس دابا هنايا، ماشي ف JavaScript
# بدل "ob10m" باللي بغيتي، ولا ديرو فـ Render فـ Environment Variables
ADMIN_PASS = os.environ.get("ADMIN_PASS", "ob10m")
app.secret_key = os.environ.get("SECRET_KEY", "souk-ali-secret-12345")

WHATSAPP_NUMBER = "212770384739"  # نمرتك ديال واتساب

# ===== 2. تخزين المنتجات فالسيرفر =====
PRODUCTS_FILE = "products.json"

def load_products():
    if not os.path.exists(PRODUCTS_FILE):
        default = [
            {"id": 1, "name": "سماعة بلوتوث Pro Max", "price": 199, "old": 349, "img": "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=600"},
            {"id": 2, "name": "ساعة ذكية Ultra", "price": 299, "old": 499, "img": "https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=600"},
        ]
        save_products(default)
        return default
    try:
        with open(PRODUCTS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return []

def save_products(products):
    with open(PRODUCTS_FILE, "w", encoding="utf-8") as f:
        json.dump(products, f, ensure_ascii=False, indent=2)

# ===== PWA =====
MANIFEST = {
  "name": "SOUK ALI",
  "short_name": "SOUK ALI",
  "start_url": "/",
  "display": "standalone",
  "background_color": "#111111",
  "theme_color": "#111111",
  "icons": [
    {"src": "https://cdn-icons-png.flaticon.com/512/3081/3081559.png","sizes": "192x192","type": "image/png"},
    {"src": "https://cdn-icons-png.flaticon.com/512/3081/3081559.png","sizes": "512x512","type": "image/png"}
  ]
}

SW = """
self.addEventListener('install', e => { self.skipWaiting(); });
self.addEventListener('activate', e => { self.clients.claim(); });
"""

HTML = """
<!DOCTYPE html>
<html dir="rtl" lang="ar"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>SOUK ALI</title>
<link rel="manifest" href="/manifest.json"><meta name="theme-color" content="#111111">
<style>
body{font-family:Arial;margin:0;background:#f8f9fa;text-align:center}
.topbar{background:#111;color:#fff;padding:8px;font-size:13px} .topbar b{color:#ffc107}
header{position:sticky;top:0;background:#fff;display:flex;justify-content:space-between;align-items:center;padding:12px 15px;box-shadow:0 2px 10px rgba(0,0,0,.08);z-index:100}
.logo{font-size:24px;font-weight:900} .logo span{color:#ff3b30}
.hero{background:linear-gradient(135deg,#111,#ff3b30);color:#fff;padding:30px 15px;border-radius:0 0 25px 25px}
.hero h1{margin:0;font-size:28px} .hero button{background:#ffc107;border:none;padding:13px 30px;border-radius:30px;font-weight:900;font-size:16px;margin-top:10px;cursor:pointer}
.appBtn{background:#fff!important;color:#111!important;border:none;padding:12px 22px;border-radius:30px;font-weight:900;margin-top:12px;font-size:15px;cursor:pointer}
.searchBox{background:#fff;padding:12px;position:sticky;top:58px;z-index:99;box-shadow:0 2px 10px rgba(0,0,0,.06)}
.searchBox input{width:90%;padding:13px;border:2px solid #eee;border-radius:30px;font-size:15px;text-align:center;outline:none}
.grid{display:grid;grid-template-columns:1fr 1fr;gap:12px;padding:12px} .card{background:#fff;border-radius:18px;overflow:hidden;padding-bottom:12px;box-shadow:0 4px 15px rgba(0,0,0,.06)} .card img{width:100%;height:180px;object-fit:cover} .btn{width:calc(100% - 20px);margin:10px;background:#25D366;color:#fff;border:none;padding:12px;border-radius:12px;font-weight:900;cursor:pointer}
input,select{width:90%;padding:13px;margin:8px;border:1px solid #ddd;border-radius:12px} .box{background:#fff;max-width:420px;margin:20px auto;padding:20px;border-radius:18px} #preview{width:100%;border-radius:12px;display:none}
.lock{font-size:50px} .loginBtn{background:#111;color:#fff;border:none;padding:13px 30px;border-radius:12px;font-weight:900;width:90%;font-size:16px;cursor:pointer}
.modal{display:none;position:fixed;top:0;left:0;width:100%;height:100%;background:rgba(0,0,0,.6);z-index:200;align-items:center;justify-content:center}
.modal-content{background:#fff;margin:20px;padding:20px;border-radius:20px;max-width:400px;width:90%;text-align:center}
.close{float:left;font-size:22px;cursor:pointer}
.badge{background:#ff3b30;color:#fff;padding:3px 8px;border-radius:10px;font-size:12px}
</style></head><body>
<div class="topbar">🔥 <b>تخفيض حتى 50%</b> - التوصيل مجاني فوق 300 درهم</div>
<div id="app"></div>
<div id="orderModal" class="modal"><div class="modal-content"><span class="close" onclick="closeModal()">✖</span><h2 id="modalTitle">اطلب دابا</h2><p id="modalProduct" style="color:#666"></p><input id="cName" placeholder="سميتك الكاملة *"><input id="cPhone" placeholder="نمرتك * - مثال 0612345678"><input id="cCity" placeholder="مدينتك * - مثال كازا"><select id="cQty"><option value="1">1 قطعة</option><option value="2">2 قطع</option><option value="3">3 قطع</option></select><button class="btn" onclick="sendOrder()">تأكيد الطلب عبر واتساب ✅</button><p style="font-size:12px;color:#888">الدفع عند التوصيل - غادي نعيطو ليك للتأكيد</p></div></div>
<script>
let products = [];
let selectedProduct = null;
async function load(){ let r = await fetch('/api/products'); products = await r.json(); render(); }
function render(){
 let q = document.getElementById('searchInput') ? document.getElementById('searchInput').value : '';
 let filtered = products.filter(p => p.name.includes(q));
 let cards='';
 if(filtered.length==0){ cards = `<p style="grid-column:1/3">😢 ما لقيناش "${q}"</p>`; }
 filtered.forEach(p=>{ cards+=`<div class="card"><img src="${p.img}"><h3>${p.name}</h3><p><b style="color:#ff3b30">${p.price} درهم</b> <s>${p.old||''}</s></p><button class="btn" onclick="openOrder(${p.id})">اطلب دابا 🚀</button></div>`; });
 document.getElementById('app').innerHTML=`<header><div class="logo">SOUK<span>ALI</span></div><div>🛒 SOUK ALI</div></header><div class="hero"><h1>سوق علي - تسوق بثقة 🚀</h1><p>أكثر من 1000 زبون راضي - الدفع عند الاستلام</p><br><button onclick="document.getElementById('prods').scrollIntoView({behavior:'smooth'})">تسوق الآن 🔥</button></div><div class="searchBox"><input id="searchInput" placeholder="🔍 قلب على أي منتج... سماعة، ساعة..." value="${q}" oninput="render()"></div><h2 id="prods">🔥 العروض الأكثر مبيعا</h2><div class="grid">${cards}</div><p>واتساب: 0770384739 | <a href="/admin">دخول المدير</a></p>`;
}
function openOrder(id){
 selectedProduct = products.find(p=>p.id==id);
 document.getElementById('modalProduct').innerText = selectedProduct.name + ' - ' + selectedProduct.price + ' درهم';
 document.getElementById('orderModal').style.display='flex';
}
function closeModal(){ document.getElementById('orderModal').style.display='none'; }
async function sendOrder(){
 let name=document.getElementById('cName').value.trim();
 let phone=document.getElementById('cPhone').value.trim();
 let city=document.getElementById('cCity').value.trim();
 let qty=document.getElementById('cQty').value;
 if(!name||!phone||!city){ alert('عمر سميتك ونمرتك ومدينتك!'); return; }
 let msg = `سلام سوق علي، بغيت نشري:%0A✅ المنتج: ${selectedProduct.name}%0A💰 الثمن: ${selectedProduct.price} درهم%0A📦 العدد: ${qty}%0A👤 السمية: ${name}%0A📞 النمرة: ${phone}%0A📍 المدينة: ${city}`;
 window.open(`https://wa.me/212770384739?text=${msg}`, '_blank');
 closeModal();
 alert('شكرا '+name+'! طلبك تسجل، غادي نعيطو ليك للتأكيد ✅');
}
if('serviceWorker' in navigator){ navigator.serviceWorker.register('/sw.js'); }
load();
</script></body></html>
"""

ADMIN_HTML = """
<!DOCTYPE html><html dir="rtl" lang="ar"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>مدير - SOUK ALI</title>
<style>body{font-family:Arial;background:#f8f9fa;text-align:center} .box{background:#fff;max-width:480px;margin:20px auto;padding:20px;border-radius:18px} input{width:90%;padding:13px;margin:8px;border:1px solid #ddd;border-radius:12px} button{background:#111;color:#fff;border:none;padding:13px 20px;border-radius:12px;font-weight:900;cursor:pointer;width:90%} .del{background:#ff3b30} img{width:100%;border-radius:12px;display:none} .pItem{display:flex;justify-content:space-between;align-items:center;border-bottom:1px solid #eee;padding:8px} .pItem img{width:50px;height:50px;object-fit:cover;display:block;border-radius:8px}</style></head><body>
<div class="box"><h2>➕ لوحة المدير - SOUK ALI</h2>
{% if not logged %}
<form method="POST" action="/admin/login"><input name="password" type="password" placeholder="المودباس" required><button>دخول ✅</button>{% if error %}<p style="color:red">{{error}}</p>{% endif %}</form>
{% else %}
<form method="POST" action="/admin/add"><input name="name" placeholder="سمية المنتج *" required><input name="price" type="number" placeholder="الثمن *" required><input name="old" type="number" placeholder="الثمن القديم"><input name="img" placeholder="رابط التصويرة - ولا خليه خاوي"><button>زيد المنتج ✅</button></form>
<hr><h3>المنتجات ({{products|length}})</h3>
{% for p in products %}
<div class="pItem"><div style="display:flex;gap:10px;align-items:center"><img src="{{p.img}}"><span>{{p.name}} - {{p.price}} درهم</span></div><form method="POST" action="/admin/delete/{{p.id}}" style="width:auto"><button class="del" style="width:auto;padding:8px 12px">مسح</button></form></div>
{% endfor %}
<br><a href="/admin/logout">خروج 🔒</a> | <a href="/">رجع للموقع</a>
{% endif %}
</div></body></html>
"""

# ===== Routes =====
@app.route("/manifest.json")
def manifest():
    return jsonify(MANIFEST)

@app.route("/sw.js")
def sw():
    return Response(SW, mimetype="application/javascript")

@app.route("/api/products")
def api_products():
    return jsonify(load_products())

@app.route("/")
def home():
    return render_template_string(HTML)

@app.route("/admin")
def admin():
    logged = session.get("admin") == True
    return render_template_string(ADMIN_HTML, logged=logged, products=load_products(), error=request.args.get("error"))

@app.route("/admin/login", methods=["POST"])
def admin_login():
    # المقارنة كتدار هنايا فالسيرفر فقط
    if request.form.get("password") == ADMIN_PASS:
        session["admin"] = True
        return redirect("/admin")
    return redirect("/admin?error=المودباس غالط!")

@app.route("/admin/logout")
def admin_logout():
    session.pop("admin", None)
    return redirect("/")

@app.route("/admin/add", methods=["POST"])
def admin_add():
    if session.get("admin") != True:
        return redirect("/admin")
    products = load_products()
    new_id = max([p.get("id", 0) for p in products], default=0) + 1
    img = request.form.get("img") or "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=600"
    products.append({
        "id": new_id,
        "name": request.form.get("name"),
        "price": int(request.form.get("price") or 0),
        "old": int(request.form.get("old") or 0) if request.form.get("old") else "",
        "img": img
    })
    save_products(products)
    return redirect("/admin")

@app.route("/admin/delete/<int:pid>", methods=["POST"])
def admin_delete(pid):
    if session.get("admin") != True:
        return redirect("/admin")
    products = [p for p in load_products() if p.get("id") != pid]
    save_products(products)
    return redirect("/admin")

if __name__ == "__main__":
    # فـ Render غادي يخدم بـ PORT
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
