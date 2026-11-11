import os
import json
from flask import Flask, render_template_string, jsonify, Response, request, session, redirect, url_for

app = Flask(__name__)

ADMIN_PASS = os.environ.get("ADMIN_PASS", "ob10m")
app.secret_key = os.environ.get("SECRET_KEY", "souk-ali-secret-12345")
WHATSAPP_NUMBER = "212770384739"

PRODUCTS_FILE = "products.json"

# المنتجات الافتراضية - مقادة لـ Vercel
DEFAULT_PRODUCTS = [
    {"id": 1, "name": "سماعة بلوتوث Pro Max", "price": 199, "old": 349, "img": "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=600"},
    {"id": 2, "name": "ساعة ذكية Ultra", "price": 299, "old": 499, "img": "https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=600"},
]

def load_products():
    try:
        if os.path.exists(PRODUCTS_FILE):
            with open(PRODUCTS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
    except:
        pass
    return DEFAULT_PRODUCTS.copy()

def save_products(products):
    try:
        with open(PRODUCTS_FILE, "w", encoding="utf-8") as f:
            json.dump(products, f, ensure_ascii=False, indent=2)
    except:
        pass

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
.appBtn{background:#fff!important;color:#111!important;border:none;padding:12px 22
