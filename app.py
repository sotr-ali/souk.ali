from flask import Flask, render_template_string
app = Flask(__name__)

HTML = """
<!DOCTYPE html>
<html dir="rtl" lang="ar"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>SOUK ALI | سوق علي - أفضل الأسعار في المغرب</title>
<style>
*{box-sizing:border-box} body{font-family:'Segoe UI',Arial;margin:0;background:#f8f9fa;color:#111}
.topbar{background:#111;color:#fff;text-align:center;padding:8px;font-size:13px} .topbar b{color:#ffc107}
header{position:sticky;top:0;background:#fff;display:flex;justify-content:space-between;align-items:center;padding:12px 15px;box-shadow:0 2px 10px rgba(0,0,0,.08);z-index:10}
.logo{font-size:24px;font-weight:900} .logo span{color:#ff3b30} .logo small{display:block;font-size:11px;color:#888;font-weight:400}
.search{flex:1;margin:0 10px} .search input{width:100%;padding:11px;border-radius:30px;border:1px solid #ddd;background:#f2f2f2}
.hero{background:linear-gradient(135deg,#111 0%,#ff3b30 100%);color:#fff;padding:30px 15px;text-align:center;border-radius:0 0 25px 25px}
.hero h1{margin:0;font-size:30px;line-height:1.3} .hero p{opacity:.9} .hero button{background:#ffc107;color:#111;border:none;padding:13px 30px;border-radius:30px;font-weight:900;font-size:16px;margin-top:10px}
.badges{display:flex;justify-content:center;gap:8px;margin:15px 10px;flex-wrap:wrap} .badge{background:#fff;padding:8px 12px;border-radius:30px;font-size:12px;font-weight:bold;box-shadow:0 2px 8px rgba(0,0,0,.06)}
.cat{display:flex;gap:8px;overflow:auto;padding:10px 15px} .cat button{white-space:nowrap;border:1px solid #ddd;background:#fff;padding:8px 16px;border-radius:30px}
.cat button.active{background:#111;color:#fff}
.grid{display:grid;grid-template-columns:1fr 1fr;gap:12px;padding:12px} @media(min-width:600px){.grid{grid-template-columns:repeat(3,1fr);max-width:1000px;margin:auto}}
.card{background:#fff;border-radius:18px;overflow:hidden;box-shadow:0 4px 15px rgba(0,0,0,.06);position:relative;padding-bottom:12px}
.card img{width:100%;height:180px;object-fit:cover} .discount{position:absolute;top:10px;right:10px;background:#ff3b30;color:#fff;padding:4px 8px;border-radius:20px;font-size:12px;font-weight:bold} .new{position:absolute;top:10px;left:10px;background:#25D366;color:#fff;padding:4px 8px;border-radius:20px;font-size:12px}
.card h3{margin:8px 10px 2px;font-size:15px} .stars{color:#ffc107;font-size:13px;margin:0 10px} .price{margin:5px 10px} .price b{color:#ff3b30;font-size:19px} .price s{color:#999;font-size:13px} .stock{font-size:12px;color:#25D366;margin:0 10px;font-weight:bold}
.btn{width:calc(100% - 20px);margin:10px;background:#25D366;color:#fff;border:none;padding:12px;border-radius:12px;font-weight:900;font-size:15px}
.btn2{background:#111}
.trust{background:#fff;margin:15px;border-radius:18px;padding:20px;text-align:center} .trust h2{margin:0}
footer{background:#111;color:#aaa;text-align:center;padding:25px 15px;margin-top:20px;font-size:13px}
.float{position:fixed;bottom:20px;left:20px;background:#25D366;color:#fff;width:60px;height:60px;border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:30px;box-shadow:0 5px 20px rgba(0,0,0,.3);z-index:20;text-decoration:none}
input{width:90%;padding:13px;margin:8px;border:1px solid #ddd;border-radius:12px} .box{background:#fff;max-width:420px;margin:20px auto;padding:20px;border-radius:18px} #preview{width:100%;border-radius:12px;display:none}
</style></head><body>
<div class="topbar">🔥 <b>تخفيض حتى 50%</b> - التوصيل مجاني للطلبات فوق 300 درهم - الدفع عند الاستلام</div>
<div id="app"></div>
<a class="float" href="https://wa.me/212770384739?text=سلام عليكم، بغيت نسول على المنتجات">💬</a>
<script>
let products = JSON.parse(localStorage.getItem('souk_products') || '[]');
if(products.length==0){
 products=[
  {name:'سماعة بلوتوث Pro Max',price:199,old:349,img:'https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=600',cat:'إلكترونيات'},
  {name:'ساعة ذكية Ultra',price:299,old:499,img:'https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=600',cat:'إلكترونيات'},
  {name:'حقيبة ظهر أصلية',price:149,old:250,img:'https://images.unsplash.com/photo-1553062407-98eeb64c6a62?w=600',cat:'موضة'},
  {name:'نظارات شمسية فاخرة',price:99,old:180,img:'https://images.unsplash.com/photo-1572635196237-14b3f281503f?w=600',cat:'موضة'}
 ];
 localStorage.setItem('souk_products',JSON.stringify(products));
}
let selectedImg='';
let filterCat='الكل';
function render(){
 let list = products.filter(p=> filterCat=='الكل' || p.cat==filterCat);
 let cards='';
 list.forEach(p=>{
  let disc = p.old ? Math.round((1-p.price/p.old)*100) : 0;
  cards+=`<div class="card">${disc?`<div class="discount">-${disc}%</div>`:''}<div class="new">جديد</div><img src="${p.img}"><h3>${p.name}</h3><div class="stars">⭐⭐⭐⭐⭐ (128)</div><div class="price"><b>${p.price} درهم</b> ${p.old?`<s>${p.old} درهم</s>`:''}</div><p class="stock">✅ متوفر - التوصيل 24 ساعة</p><a href="https://wa.me/212770384739?text=سلام عليكم، بغيت نشري ${encodeURIComponent(p.name)} ب ${p.price} درهم"><button class="btn">اطلب الآن عبر واتساب 🛒</button></a></div>`;
 });
 document.getElementById('app').innerHTML=`
 <header><div class="logo">SOUK<span>ALI</span><small>سوق علي - المغرب</small></div><div class="search"><input oninput="search(this.value)" placeholder="🔍 قلب على أي منتج..."></div><div style="font-size:22px">🛒</div></header>
 <div class="hero"><h1>تسوق بثقة،<br>توصيل سريع لباب دارك 🚀</h1><p>أكثر من 1000 زبون راضي - الدفع عند الاستلام - إرجاع مجاني</p><a href="#products"><button>تسوق الآن 🔥</button></a></div>
 <div class="badges"><div class="badge">🚚 توصيل سريع</div><div class="badge">💵 الدفع عند الاستلام</div><div class="badge">✅ منتجات أصلية</div><div class="badge">⭐ تقييم 4.9</div></div>
 <div class="cat"><button class="${filterCat=='الكل'?'active':''}" onclick="setCat('الكل')">الكل</button><button class="${filterCat=='إلكترونيات'?'active':''}" onclick="setCat('إلكترونيات')">📱 إلكترونيات</button><button class="${filterCat=='موضة'?'active':''}" onclick="setCat('موضة')">👕 موضة</button></div>
 <h2 id="products" style="padding:0 15px">🔥 العروض الأكثر مبيعا</h2>
 <div class="grid">${cards}</div>
 <div class="trust"><h2>علاش يختارونا الناس؟</h2><p>📦 <b>توصيل سريع</b> لجميع المدن<br>💵 <b>خلص ملي توصلك</b> السلعة<br>🔄 <b>إرجاع مجاني</b> إلا ما عجباتكش<br>📞 <b>دعم 7/7</b> على واتساب 0770384739</p><a href="https://wa.me/212770384739?text=سلام عليكم، بغيت نسول"><button class="btn btn2" style="width:250px">تواصل معانا واتساب</button></a></div>
 <footer><b style="color:#fff;font-size:18px">SOUK ALI</b><br>سوق علي - أفضل متجر إلكتروني في المغرب<br>واتساب: 0770384739<br>© 2026 جميع الحقوق محفوظة</footer>`;
}
function setCat(c){filterCat=c; render();}
function search(v){
 let filtered = products.filter(p=> p.name.includes(v));
 let cards='';
 filtered.forEach(p=>{cards+=`<div class="card"><img src="${p.img}"><h3>${p.name}</h3><div class="price"><b>${p.price} درهم</b></div><a href="https://wa.me/212770384739?text=بغيت نشري ${encodeURIComponent(p.name)}"><button class="btn">اطلب الآن</button></a></div>`});
 if(v) document.querySelector('.grid').innerHTML=cards; else render();
}
if(location.pathname.includes('admin')){
 document.getElementById('app').innerHTML=`<header><div class="logo">SOUK<span>ALI</span></div></header><div class="box"><h2>➕ زيد منتج جديد</h2><input id="n" placeholder="سميت المنتج مثلا: سماعة JBL"><input id="pr" type="number" placeholder="الثمن الجديد 199"><input id="old" type="number" placeholder="الثمن القديم 349 (اختياري)"><select id="cat" style="width:90%;padding:12px;border-radius:12px;border:1px solid #ddd"><option>إلكترونيات</option><option>موضة</option></select><p style="text-align:right;font-weight:bold">📷 تصويرة من التيليفون:</p><input id="file" type="file" accept="image/*"><img id="preview"><button class="btn" onclick="add()">زيد المنتج ✅</button><hr><h3>منتجاتك (${products.length})</h3><div id="list"></div><a href="/">رجع للموقع</a></div>`;
 document.getElementById('file').addEventListener('change', function(e){
  let f=e.target.files[0]; if(!f) return; let r=new FileReader();
  r.onload=function(ev){selectedImg=ev.target.result; document.getElementById('preview').src=selectedImg; document.getElementById('preview').style.display='block';};
  r.readAsDataURL(f);
 });
 window.add=()=>{
  let n=document.getElementById('n').value, pr=document.getElementById('pr').value, old=document.getElementById('old').value, cat=document.getElementById('cat').value;
  if(!n||!pr||!selectedImg){alert('عمر السمية و الثمن و ختار تصويرة!');return}
  products.push({name:n,price:pr,old:old||'',img:selectedImg,cat:cat}); localStorage.setItem('souk_products',JSON.stringify(products)); alert('تزاد! 🔥'); location.reload();
 };
 let l=''; products.forEach((p,i)=>{l+=`<p>${p.name} - ${p.price} درهم <button onclick="del(${i})" style="background:red;color:#fff;border:none;padding:5px 10px;border-radius:8px">مسح</button></p>`}); document.getElementById('list').innerHTML=l;
 window.del=(i)=>{products.splice(i,1); localStorage.setItem('souk_products',JSON.stringify(products)); location.reload()};
} else { render(); }
</script>
</body></html>
"""

@app.route("/")
@app.route("/admin")
@app.route("/api/index")
@app.route("/<path:path>")
def home(path=None):
    return render_template_string(HTML)
if __name__ == "__main__":
    app.run()
