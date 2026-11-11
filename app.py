from flask import Flask, render_template_string
app = Flask(__name__)

HTML = """
<!DOCTYPE html>
<html dir="rtl" lang="ar"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Souk Ali</title>
<style>body{font-family:Arial;margin:0;background:#f2f2f2;text-align:center} .top{background:#111;color:#fff;padding:15px;font-size:22px;font-weight:bold} .top span{color:#ffc107} .card{background:#fff;width:300px;margin:10px;display:inline-block;border-radius:15px;overflow:hidden;box-shadow:0 4px 10px rgba(0,0,0,.1);padding-bottom:15px} .card img{width:100%;height:220px;object-fit:cover} button{background:#25D366;color:#fff;border:none;padding:11px 25px;border-radius:30px;font-weight:bold} input{width:90%;padding:12px;margin:8px;border:1px solid #ddd;border-radius:10px} .box{background:#fff;max-width:400px;margin:20px auto;padding:20px;border-radius:15px} .del{background:#ff3b30;margin-top:5px}</style>
</head><body>
<div class="top">SOUK <span>ALI</span></div>
<div id="site"></div>
<script>
let products = JSON.parse(localStorage.getItem('souk_products') || '[]');
if(products.length==0){
 products=[
  {name:'سماعة بلوتوث Pro',price:199,img:'https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=500'},
  {name:'ساعة ذكية',price:299,img:'https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=500'},
  {name:'حقيبة ظهر',price:149,img:'https://images.unsplash.com/photo-1553062407-98eeb64c6a62?w=500'}
 ];
 localStorage.setItem('souk_products',JSON.stringify(products));
}
function show(){
 let h='';
 products.forEach((p,i)=>{
  h+=`<div class="card"><img src="${p.img}"><h3>${p.name}</h3><p style="color:#e91e63;font-weight:bold">${p.price} درهم</p><a href="https://wa.me/212600000000?text=بغيت نشري ${p.name}"><button>اطلب عبر واتساب ✅</button></a></div>`;
 });
 document.getElementById('site').innerHTML=h;
}
if(location.pathname.includes('admin')){
 document.body.innerHTML=`<div class="top">لوحة تحكم - SOUK ALI</div><div class="box"><h3>زيد منتج جديد</h3><input id="n" placeholder="سميت المنتج مثلا: صباط رياضي"><input id="pr" type="number" placeholder="الثمن مثلا: 199"><input id="im" placeholder="رابط التصويرة - كوبيه من Google"><button onclick="add()">زيد المنتج +</button><p style="font-size:13px;color:#888">باش تجيب رابط تصويرة: دخل Google Images، قلب على المنتج، كليكي عليه و دير Copy Image Address و كوليه هنا</p><hr><h3>المنتجات ديالك (${products.length})</h3><div id="list"></div><a href="/">رجع للموقع</a></div>`;
 function add(){
  let n=document.getElementById('n').value, pr=document.getElementById('pr').value, im=document.getElementById('im').value;
  if(!n||!pr||!im){alert('عمر كلشي!');return}
  products.push({name:n,price:pr,img:im}); localStorage.setItem('souk_products',JSON.stringify(products)); alert('تزاد!'); location.reload();
 }
 let l=''; products.forEach((p,i)=>{l+=`<p>${p.name} - ${p.price} درهم <button class="del" onclick="del(${i})">مسح</button></p>`}); document.getElementById('list').innerHTML=l;
 window.del=(i)=>{products.splice(i,1); localStorage.setItem('souk_products',JSON.stringify(products)); location.reload()};
} else { show(); }
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
