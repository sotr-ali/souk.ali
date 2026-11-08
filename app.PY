from flask import Flask, render_template_string

app = Flask(__name__)

products = [
    {"id": 1, "name": "منتج 1 - سماعة", "price": 199, "img": "https://via.placeholder.com/300"},
    {"id": 2, "name": "منتج 2 - ساعة", "price": 299, "img": "https://via.placeholder.com/300"},
    {"id": 3, "name": "منتج 3 - حقيبة", "price": 149, "img": "https://via.placeholder.com/300"},
]

HTML = """
<!DOCTYPE html>
<html dir="rtl" lang="ar">
<head><meta charset="utf-8"><title>Souk Ali</title>
<style>body{font-family:Arial;text-align:center;background:#f5f5f5} .card{background:white;display:inline-block;margin:10px;padding:15px;border-radius:10px;width:250px} img{width:100%;border-radius:10px} button{background:#25D366;color:white;border:none;padding:10px 20px;border-radius:5px;font-size:16px}</style>
</head>
<body>
<h1>Souk Ali - متجر علي</h1>
<p>مرحبا بيك فالمتجر ديالي</p>
{% for p in products %}
<div class="card">
<img src="{{p.img}}">
<h3>{{p.name}}</h3>
<p>{{p.price}} درهم</p>
<a href="https://wa.me/212600000000?text=بغيت نشري {{p.name}}"><button>شراء عبر واتساب</button></a>
</div>
{% endfor %}
</body></html>
"""

@app.route("/")
def home():
    return render_template_string(HTML, products=products)

if __name__ == "__main__":
    app.run()
