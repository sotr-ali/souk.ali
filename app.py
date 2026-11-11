import os, json
from flask import Flask, render_template_string, jsonify, Response, request, session, redirect

app = Flask(__name__)
ADMIN_PASS = os.environ.get("ADMIN_PASS", "ob10m")
app.secret_key = os.environ.get("SECRET_KEY", "souk-ali-secret-12345")
WHATSAPP = "212770384739"
PRODUCTS_FILE = "products.json"

def load_products():
    if not os.path.exists(PRODUCTS_FILE):
        default = [
            {"id":1,"name":"سماعة بلوتوث Pro Max","price":199,"old":349,"img":"https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=600","desc":"صوت نقي، بطارية 24 ساعة، بلوتوث 5.3، كتخدم مع آيفون وأندرويد","cat":"إلكترونيات"},
            {"id":2,"name":"ساعة ذكية Ultra","price":299,"old":499,"img":"https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=600","desc":"شاشة AMOLED، قياس نبضات القلب، مقاومة للماء، بطارية 7 أيام","cat":"إلكترونيات"},
        ]
        save_products(default); return default
    try:
        with open(PRODUCTS_FILE,"r",encoding="utf-8") as f: return json.load(f)
    except: return []

def save_products(p):
    with open(PRODUCTS_FILE,"w",encoding="utf-8") as f: json.dump(p,f,ensure_ascii=False,indent=2)

MANIFEST = {"name":"SOUK ALI","short_name":"SOUK ALI","start_url":"/","display":"standalone","background_color":"#111111","theme_color":"#111111","icons":[{"src":"https://cdn-icons-png.flaticon.com/512/3081/3081559.png","sizes":"192x192","type":"image/png"}]}
SW = "self.addEventListener('install',e=>{self.skipWaiting()});self.addEventListener('activate',e=>{self.clients.claim()});"

# ===== الموقع - ناضي، سريع، SEO =====
HTML = """
<!DOCTYPE html><html dir="rtl" lang="ar"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>SOUK ALI | تسوق بثقة - الدفع عند الاستلام في المغرب</title>
<meta name="description" content="سوق علي - أفضل متجر إلكتروني في المغرب. سماعات، ساعات ذكية، الدفع عند الاستلام، التوصيل لجميع المدن. كازا، الرباط، فاس، مراكش.">
<meta property="og:title" content="SOUK ALI - تسوق بثقة"><meta property="og:description" content="الدفع عند الاستلام - التوصيل لجميع المدن">
<link rel="manifest" href="/manifest.json"><meta name="theme-color" content="#111111">
<style>
*{box-sizing:border-box}body{font-family:Arial;margin:0;background:#f8f9fa;text-align:center}
.topbar{background:#111;color:#fff;padding:8px;font-size:13px}.topbar b{color:#ffc107}
header{position:sticky;top:0;background:#fff;display:flex;justify-content:space-between;align-items:center;padding:12px 15px;box-shadow:0 2px 10px rgba(0,0,0,.08);z-index:100}
.logo{font-size:24px;font-weight:900}.logo span{color:#ff3b30}
.hero{background:linear-gradient(135deg,#111,#ff3b30);color:#fff;padding:28px 15px;border-radius:0 0 25px 25px}
.hero button{background:#ffc107;border:none;padding:13px 30px;border-radius:30px;font-weight:900;font-size:16px;margin-top:10px;cursor:pointer}
.searchBox{background:#fff;padding:12px;position:sticky;top:58px;z-index:99;box-shadow:0 2px 10px rgba(0,0,0,.06)}
.searchBox input{width:88%;padding:13px;border:2px solid #eee;border-radius:30px;text-align:center;outline:none;font-size:15px}
.filters{display:flex;gap:8px;justify-content:center;padding:10px;flex-wrap:wrap}.filters button{border:1px solid #ddd;background:#fff;padding:8px 16px;border-radius:20px;cursor:pointer}.filters button.active{background:#111;color:#fff}
.grid{display:grid;grid-template-columns:1fr 1fr;gap:12px;padding:12px}.card{background:#fff;border-radius:18px;overflow:hidden;padding-bottom:12px;box-shadow:0 4px 15px rgba(0,0,0,.06)}.card img{width:100%;height:180px;object-fit:cover}.card p{font-size:13px;color:#666;padding:0 10px;line-height:1.5}.btn{width:calc(100% - 20px);margin:10px;background:#25D366;color:#fff;border:none;padding:12px;border-radius:12px;font-weight:900;cursor:pointer}
.trust{display:flex;gap:10px;justify-content:center;padding:10px;flex-wrap:wrap}.trust div{background:#fff;padding:12px;border-radius:14px;font-size:13px;flex:1;min-width:100px}
.reviews{background:#fff;margin:12px;padding:15px;border-radius:18px;text-align:right}.reviews b{color:#ffb300}
.footer{background:#111;color:#fff;padding:20px;margin-top:20px;font-size:14px;line-height:1.8}.footer a{color:#ffc107;text-decoration:none}
.modal{display:none;position:fixed;top:0;left:0;width:100%;height:100%;background:rgba(0,0,0,.6);z-index:200;align-items:center;justify-content:center}.modal-content{background:#fff;margin:20px;padding:20px;border-radius:20px;max-width:400px;width:90%;text-align:center}
input,select{width:90%;padding:13px;margin:8px;border:1px solid #ddd;border-radius:12px} .close{float:left;cursor:pointer;font-size:20px}
.delivery{font-size:12px;color:#25D366;font-weight:700}
</style></head><body>
<div class="topbar">🔥 <b>تخفيض حتى 50%</b> - التوصيل مجاني فوق 300 درهم | الدفع عند الاستلام</div>
<div id="app"></div>
<div id="orderModal" class="modal"><div class="modal-content"><span class="close" onclick="closeModal()">✖</span><h2 id="modalTitle">اطلب دابا</h2><p id="modalProduct"></p><input id="cName" placeholder="سميتك الكاملة *"><input id="cPhone" placeholder="نمرتك *"><input id="cCity" placeholder="مدينتك *"><select id="cQty"><option value="1">1 قطعة</option><option value="2">2 قطع</option><option value="3">3 قطع</option></select><p style="font-size:13px">🚚 التوصيل: كازا 20 درهم (24h) | مدن أخرى 35 درهم (48h) | مجاني فوق 300 درهم<br>💵 الدفع عند الاستلام</p><button class="btn" onclick="sendOrder()">تأكيد الطلب عبر واتساب ✅</button></div></div>
<script>
let products=[]; let cat='الكل';
async function load(){ let r=await fetch('/api/products'); products=await r.json(); render(); }
function render(){
 let q=document.getElementById('searchInput')?document.getElementById('searchInput').value:'';
 let filtered=products.filter(p=>(cat=='الكل'||p.cat==cat) && p.name.includes(q));
 let cards='';
 if(filtered.length==0) cards=`<p style="grid-column:1/3">😢 ما لقيناش "${q}"</p>`;
 filtered.forEach(p=>{ cards+=`<div class="card"><img loading="lazy" src="${p.img}" alt="${p.name}"><h3>${p.name}</h3><p>${p.desc||''}</p><p><b style="color:#ff3b30;font-size:18px">${p.price} درهم</b> <s>${p.old||''}</s></p><p class="delivery">🚚 التوصيل 24-48h | 💵 الدفع عند الاستلام</p><button class="btn" onclick="openOrder(${p.id})">اشري الآن 🚀</button></div>`; });
 document.getElementById('app').innerHTML=`<header><div class="logo">SOUK<span>ALI</span></div><div>📞 0770384739</div></header><div class="hero"><h1>سوق علي - تسوق بثقة 🚀</h1><p>أكثر من 1000 زبون راضي - الدفع عند الاستلام - إرجاع مجاني 7 أيام</p><button onclick="document.getElementById('prods').scrollIntoView({behavior:'smooth'})">تسوق الآن 🔥</button></div><div class="searchBox"><input id="searchInput" placeholder="🔍 قلب على أي منتج..." value="${q}" oninput="render()"></div><div class="filters"><button onclick="setCat('الكل')" class="${cat=='الكل'?'active':''}">الكل</button><button onclick="setCat('إلكترونيات')" class="${cat=='إلكترونيات'?'active':''}">إلكترونيات</button></div><div class="trust"><div>✅ دفع عند الاستلام</div><div>🚚 توصيل سريع</div><div>🔄 إرجاع 7 أيام</div></div><h2 id="prods">🔥 العروض الأكثر مبيعا</h2><div class="grid">${cards}</div><div class="reviews"><h3>⭐ آراء الزبناء</h3><p>⭐⭐⭐⭐⭐ <b>يوسف - كازا:</b> "وصلني الطلب فنهارو، ثقة"</p><p>⭐⭐⭐⭐⭐ <b>مريم - الرباط:</b> "الجودة زوينة والثمن مناسب"</p><p>⭐⭐⭐⭐⭐ <b>أمين - فاس:</b> "ثاني مرة كنشري من عندهم"</p></div><div class="reviews"><h3>👤 من نحن؟</h3><p>سوق علي متجر مغربي 100%، كنبيعو منتجات مختارة بعناية، وكنوصلو لجميع المدن. هدفنا: تاخد المنتج اللي بغيتي، بثمن مناسب، وتخلص ملي يوصلك.</p><p><b>سياسة الإرجاع:</b> إلا ما عجبكش المنتج، عندك 7 أيام باش ترجعو.</p><p><b>خدمة الزبناء:</b> واتساب 0770384739 - كنجاوبو فأقل من 5 دقايق</p></div><div class="footer">SOUK ALI © 2026<br><a href="https://wa.me/212770384739">واتساب</a> | <a href="https://instagram.com/soukali">إنستغرام</a> | <a href="https://tiktok.com/@soukali">تيك توك</a><br><a href="/admin">دخول المدير</a><br>🔒 موقع آمن - HTTPS - معلوماتك محمية</div>`;
}
function setCat(c){cat=c;render();}
function openOrder(id){ let p=products.find(x=>x.id==id); window._p=p; document.getElementById('modalProduct').innerText=p.name+' - '+p.price+' درهم'; document.getElementById('orderModal').style.display='flex'; }
function closeModal(){document.getElementById('orderModal').style.display='none';}
function sendOrder(){ let name=document.getElementById('cName').value.trim(),phone=document.getElementById('cPhone').value.trim(),city=document.getElementById('cCity').value.trim(),qty=document.getElementById('cQty').value; if(!name||!phone||!city){alert('عمر سميتك ونمرتك ومدينتك!');return;} let p=window._p; let msg=`سلام سوق علي، بغيت نشري:%0A✅ ${p.name}%0A💰 ${p.price} درهم%0A📦 العدد: ${qty}%0A👤 ${name}%0A📞 ${phone}%0A📍 ${city}%0A💵 الدفع عند الاستلام`; window.open(`https://wa.me/212770384739?text=${msg}`,'_blank'); closeModal(); alert('شكرا '+name+'! غادي نعيطو ليك للتأكيد ✅'); }
load();
</script></body></html>
"""

ADMIN_HTML = """
<!DOCTYPE html><html dir="rtl" lang="ar"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>مدير - SOUK ALI</title>
<style>body{font-family:Arial;background:#f8f9fa;text-align:center}.box{background:#fff;max-width:520px;margin:20px auto;padding:20px;border-radius:18px}input,textarea{width:90%;padding:13px;margin:8px;border:1px solid #ddd;border-radius:12px}button{background:#111;color:#fff;border:none;padding:13px;border-radius:12px;font-weight:900;width:90%;cursor:pointer}.del{background:#ff3b30;width:auto;padding:8px 12px}.pItem{display:flex;justify-content:space-between;align-items:center;border-bottom:1px solid #eee;padding:8px}.pItem img{width:50px;height:50px;object-fit:cover;border-radius:8px}</style></head><body><div class="box"><h2>لوحة المدير - SOUK ALI</h2>
{% if not logged %}<form method="POST" action="/admin/login"><input name="password" type="password" placeholder="المودباس" required><button>دخول ✅</button>{% if error %}<p style="color:red">{{error}}</p>{% endif %}</form>
{% else %}<form method="POST" action="/admin/add"><input name="name" placeholder="سمية المنتج *" required><input name="price" type="number" placeholder="الثمن *" required><input name="old" type="number" placeholder="الثمن القديم"><input name="img" placeholder="رابط التصويرة"><textarea name="desc" placeholder="الوصف - المقاس، المواصفات..."></textarea><input name="cat" placeholder="التصنيف - إلكترونيات" value="إلكترونيات"><button>زيد المنتج ✅</button></form><hr><h3>المنتجات ({{products|length}})</h3>{% for p in products %}<div class="pItem"><div style="display:flex;gap:10px;align-items:center"><img src="{{p.img}}"><span>{{p.name}} - {{p.price}} درهم</span></div><form method="POST" action="/admin/delete/{{p.id}}" style="width:auto"><button class="del">مسح</button></form></div>{% endfor %}<br><a href="/admin/logout">خروج 🔒</a> | <a href="/">رجع للموقع</a>{% endif %}</div></body></html>
"""

@app.route("/manifest.json")
def manifest(): return jsonify(MANIFEST)
@app.route("/sw.js")
def sw(): return Response(SW, mimetype="application/javascript")
@app.route("/api/products")
def api_products(): return jsonify(load_products())
@app.route("/")
def home(): return render_template_string(HTML)
@app.route("/admin")
def admin(): return render_template_string(ADMIN_HTML, logged=session.get("admin")==True, products=load_products(), error=request.args.get("error"))
@app.route("/admin/login", methods=["POST"])
def admin_login():
    if request.form.get("password")==ADMIN_PASS:
        session["admin"]=True; return redirect("/admin")
    return redirect("/admin?error=المودباس غالط!")
@app.route("/admin/logout")
def admin_logout(): session.pop("admin",None); return redirect("/")
@app.route("/admin/add", methods=["POST"])
def admin_add():
    if session.get("admin")!=True: return redirect("/admin")
    products=load_products(); nid=max([p.get("id",0) for p in products],default=0)+1
    products.append({"id":nid,"name":request.form.get("name"),"price":int(request.form.get("price") or 0),"old":request.form.get("old") or "","img":request.form.get("img") or "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=600","desc":request.form.get("desc") or "","cat":request.form.get("cat") or "إلكترونيات"})
    save_products(products); return redirect("/admin")
@app.route("/admin/delete/<int:pid>", methods=["POST"])
def admin_delete(pid):
    if session.get("admin")!=True: return redirect("/admin")
    save_products([p for p in load_products() if p.get("id")!=pid]); return redirect("/admin")

if __name__=="__main__":
    port=int(os.environ.get("PORT",5000)); app.run(host="0.0.0.0",port=port)
    {
  "version": 2,
  "builds": [{ "src": "app.py", "use": "@vercel/python" }],
  "routes": [{ "src": "/(.*)", "dest": "app.py" }]
    }
