import os
from flask import Flask, render_template_string, jsonify, Response, request, session

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "souk-ali-secret-123")
ADMIN_PASS = os.environ.get("ADMIN_PASSWORD", "1234") # بدل 1234 للمودباس ديالك
ADMIN_PATH = "ali-2026-khdam" # هادا هو الرابط السري ديال الأدمن

# المنتجات هنا فالسيرفر - كيبانو عند كلشي
PRODUCTS = [
  {"id": 1, "name": "سماعة بلوتوث Pro Max", "price": 199, "old": 349, "img": "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=600"},
  {"id": 2, "name": "ساعة ذكية Ultra", "price": 299, "old": 499, "img": "https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=600"},
]

MANIFEST = {
  "name": "SOUK ALI", "short_name": "SOUK ALI", "start_url": "/",
  "display": "standalone", "background_color": "#111111", "theme_color": "#111111",
  "icons": [
    {"src": "https://cdn-icons-png.flaticon.com/512/3081/3081559.png","sizes": "192x192","type": "image/png"},
    {"src": "https://cdn-icons-png.flaticon.com/512/3081/3081559.png","sizes": "512x512","type": "image/png"}
  ]
}

SW = """
self.addEventListener('install', e => { self.skipWaiting(); });
self.addEventListener('activate', e => { self.clients.claim(); });
self.addEventListener('fetch', e => { e.respondWith(fetch(e.request).catch(()=> caches.match(e.request))); });
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
let deferredPrompt;
window.addEventListener('beforeinstallprompt', (e)=>{ e.preventDefault(); deferredPrompt=e; });
let products = [];
let selectedImg='';
let searchText = '';
let ADMIN_PATH = 'ali-2026-khdam';
async function load(){
  let r = await fetch('/api/products');
  products = await r.json();
  render();
}
function render(){
 let filtered = products.filter(p => p.name.includes(searchText));
 let cards='';
 if(filtered.length==0){ cards = `<p style="grid-column:1/3">😢 ما لقيناش "${searchText}"</p>`; }
 filtered.forEach(p=>{ cards+=`<div class="card"><img src="${p.img}"><h3>${p.name}</h3><p><b style="color:#ff3b30">${p.price} درهم</b> <s>${p.old||''}</s></p><a href="https://wa.me/212770384739?text=بغيت نشري ${encodeURIComponent(p.name)}"><button class="btn">اطلب عبر واتساب ✅</button></a></div>`; });
 document.getElementById('app').innerHTML=`<header><div class="logo">SOUK<span>ALI</span></div><div>🛒</div></header><div class="hero"><h1>سوق علي - تسوق بثقة 🚀</h1><p>أكثر من 1000 زبون راضي - الدفع عند الاستلام</p><br><button onclick="document.getElementById('prods').scrollIntoView({behavior:'smooth'})">تسوق الآن 🔥</button><br><button class="appBtn" onclick="installApp()">📲 ثبت التطبيق في هاتفك</button></div><div class="searchBox"><input id="searchInput" placeholder="🔍 قلب على أي منتج... سماعة، ساعة..." value="${searchText}" oninput="doSearch(this.value)"></div><h2 id="prods">🔥 العروض الأكثر مبيعا</h2><div class="grid">${cards}</div><p>واتساب: 0770384739</p>`;
 window.doSearch = (v)=>{ searchText=v; render(); let inp=document.getElementById('searchInput'); inp.focus(); inp.setSelectionRange(inp.value.length, inp.value.length); };
 window.installApp = ()=>{ if(deferredPrompt){ deferredPrompt.prompt(); } else { alert('كليكي على ⋮ الفوق و ختار إنشاء اختصار'); } };
}
async function showAdmin(){
 let r = await fetch('/api/products');
 products = await r.json();
 document.getElementById('app').innerHTML=`<div class="box"><h2>➕ زيد منتج</h2><input id="n" placeholder="سميت المنتج"><input id="pr" type="number" placeholder="الثمن"><input id="old" type="number" placeholder="الثمن القديم"><input id="imgurl" placeholder="رابط التصويرة"><input id="file" type="file" accept="image/*"><img id="preview"><button class="btn" onclick="add()">زيد المنتج ✅</button><div id="list"></div><button onclick="logout()" style="background:red;color:#fff;border:none;padding:10px 20px;border-radius:10px;margin-top:10px">خروج 🔒</button><br><a href="/">رجع للموقع</a></div>`;
 document.getElementById('file').addEventListener('change', function(e){ let f=e.target.files[0]; if(!f) return; let r=new FileReader(); r.onload=function(ev){selectedImg=ev.target.result; document.getElementById('preview').src=selectedImg; document.getElementById('preview').style.display='block';}; r.readAsDataURL(f); });
 window.add=async ()=>{ let n=document.getElementById('n').value, pr=document.getElementById('pr').value, old=document.getElementById('old').value, url=document.getElementById('imgurl').value; let img = selectedImg || url; if(!n||!pr||!img){alert('عمر كلشي!');return} await fetch('/api/admin/add', {method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({name:n, price:pr, old:old, img:img})}); alert('تزاد! وغادي يبان عند كلشي ✅'); location.reload(); };
 let l=''; products.forEach((p)=>{l+=`<p>${p.name} <button onclick="del(${p.id})">مسح</button></p>`}); document.getElementById('list').innerHTML=l;
 window.del=async (id)=>{ await fetch('/api/admin/delete/'+id, {method:'POST'}); location.reload(); };
}
async function logout(){ await fetch('/api/admin/logout', {method:'POST'}); location.href='/'; }
if(location.pathname.includes(ADMIN_PATH)){
  fetch('/api/admin/check').then(r=>r.json()).then(d=>{
    if(d.ok){ showAdmin(); }
    else {
      document.getElementById('app').innerHTML=`<div class="box"><div class="lock">🔒</div><h2>دخول المدير فقط</h2><input id="pass" type="password" placeholder="كتب المودباس"><button class="loginBtn" onclick="checkPass()">دخول ✅</button><p id="err" style="color:red"></p><a href="/">رجع للموقع</a></div>`;
      window.checkPass=async ()=>{ let p=document.getElementById('pass').value; let r=await fetch('/api/admin/login', {method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({password:p})}); let j=await r.json
