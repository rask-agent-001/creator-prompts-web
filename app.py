#!/usr/bin/env python3
"""
Adult Creator Prompt Packs — Sales Web App
Single-file Flask app with email capture + Gumroad delivery
"""

import os
import sqlite3
import time
import uuid
from datetime import datetime, timedelta
from functools import wraps
from flask import (
    Flask, request, redirect, url_for, render_template,
    make_response, jsonify, abort
)

# ── Config ──────────────────────────────────────────────────────────────
NOTION_TOKEN = os.environ.get("NOTION_TOKEN", "")
NOTION_TEMPLATE_LINK = os.environ.get(
    "NOTION_TEMPLATE_LINK",
    "https://www.notion.so/39221620b5ab816e93aeea319b5eba98"
)

# Prompt pack Gumroad links
TIKTOK_PACK_LINK = os.environ.get(
    "TIKTOK_PACK_LINK",
    "https://bonsabster.gumroad.com/l/dwswu"
)
YOUTUBE_PACK_LINK = os.environ.get(
    "YOUTUBE_PACK_LINK",
    "https://bonsabster.gumroad.com/l/zogyka"
)
BUNDLE_LINK = os.environ.get(
    "BUNDLE_LINK",
    "https://bonsabster.gumroad.com/l/udogc"
)

SECRET_KEY = os.environ.get("SECRET_KEY", "creator-prompts-secret-2026")
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "creator123")
DB_PATH = os.environ.get("DB_PATH", "sales.db")

PORT = int(os.environ.get("PORT", 5000))
VERCEL = os.environ.get("VERCEL", "false").lower() == "true"

app = Flask(__name__, template_folder="templates")
app.secret_key = SECRET_KEY

# ── Database ────────────────────────────────────────────────────────────
def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS subscribers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            name TEXT,
            source TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS page_views (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            path TEXT,
            ip_hash TEXT,
            user_agent TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS sales (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT,
            amount INTEGER,
            product TEXT,
            gumroad_id TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

init_db()

# ── Helpers ─────────────────────────────────────────────────────────────
def hash_ip(ip):
    import hashlib
    return hashlib.sha256(ip.encode()).hexdigest()[:16]

def log_view(path):
    try:
        conn = get_db()
        c = conn.cursor()
        c.execute(
            "INSERT INTO page_views (path, ip_hash, user_agent) VALUES (?, ?, ?)",
            (path, hash_ip(request.remote_addr), request.user_agent.string[:200])
        )
        conn.commit()
        conn.close()
    except Exception:
        pass

def get_stats():
    conn = get_db()
    c = conn.cursor()
    views = c.execute("SELECT COUNT(*) FROM page_views").fetchone()[0]
    subscribers = c.execute("SELECT COUNT(*) FROM subscribers").fetchone()[0]
    sales = c.execute("SELECT COUNT(*) FROM sales").fetchone()[0]
    revenue = c.execute("SELECT COALESCE(SUM(amount), 0) FROM sales").fetchone()[0]
    conn.close()
    return {
        "views": views,
        "subscribers": subscribers,
        "sales": sales,
        "revenue": revenue / 100,
        "revenue_fmt": f"${revenue/100:.2f}"
    }

def get_recent_sales(limit=10):
    conn = get_db()
    c = conn.cursor()
    rows = c.execute(
        "SELECT * FROM sales ORDER BY created_at DESC LIMIT ?", (limit,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]

def add_sale(email, amount, product, gumroad_id=""):
    conn = get_db()
    c = conn.cursor()
    c.execute(
        "INSERT INTO sales (email, amount, product, gumroad_id) VALUES (?, ?, ?, ?)",
        (email, amount, product, gumroad_id)
    )
    conn.commit()
    conn.close()

def email_exists(email):
    conn = get_db()
    c = conn.cursor()
    exists = c.execute(
        "SELECT 1 FROM subscribers WHERE email = ?", (email,)
    ).fetchone() is not None
    conn.close()
    return exists

# ── Routes ───────────────────────────────────────────────────────────────
@app.route("/")
def landing():
    log_view("/")
    return render_template("landing.html",
        tiktok_link=TIKTOK_PACK_LINK,
        youtube_link=YOUTUBE_PACK_LINK,
        bundle_link=BUNDLE_LINK
    )

@app.route("/tiktok")
def tiktok_pack():
    log_view("/tiktok")
    return render_template("landing.html",
        tiktok_link=TIKTOK_PACK_LINK,
        youtube_link=YOUTUBE_PACK_LINK,
        bundle_link=BUNDLE_LINK,
        focus="tiktok"
    )

@app.route("/youtube-shorts")
def youtube_pack():
    log_view("/youtube-shorts")
    return render_template("landing.html",
        tiktok_link=TIKTOK_PACK_LINK,
        youtube_link=YOUTUBE_PACK_LINK,
        bundle_link=BUNDLE_LINK,
        focus="youtube"
    )

@app.route("/bundle")
def bundle():
    log_view("/bundle")
    return render_template("landing.html",
        tiktok_link=TIKTOK_PACK_LINK,
        youtube_link=YOUTUBE_PACK_LINK,
        bundle_link=BUNDLE_LINK,
        focus="bundle"
    )

@app.route("/buy/tiktok")
def buy_tiktok():
    log_view("/buy/tiktok")
    return redirect(TIKTOK_PACK_LINK)

@app.route("/buy/youtube-shorts")
def buy_youtube():
    log_view("/buy/youtube-shorts")
    return redirect(YOUTUBE_PACK_LINK)

@app.route("/buy/bundle")
def buy_bundle():
    log_view("/buy/bundle")
    return redirect(BUNDLE_LINK)

@app.route("/subscribe", methods=["POST"])
def subscribe():
    email = request.form.get("email", "").strip()
    name = request.form.get("name", "").strip()
    source = request.form.get("source", "landing")

    if not email or "@" not in email:
        return redirect(request.referrer or "/")

    try:
        conn = get_db()
        c = conn.cursor()
        c.execute(
            "INSERT OR IGNORE INTO subscribers (email, name, source) VALUES (?, ?, ?)",
            (email, name, source)
        )
        conn.commit()
        conn.close()
    except Exception:
        pass

    return redirect("/#waitlist" if source == "hero_waitlist" else "/")

@app.route("/webhook/gumroad", methods=["POST"])
def gumroad_webhook():
    """Handle Gumroad post-purchase webhook to record sales."""
    # In production, verify the webhook signature
    # For now, accept basic notification
    data = request.get_json(silent=True) or {}
    
    if data.get("event") == "sale":
        sale = data.get("sale", {})
        email = sale.get("email", "")
        amount = int(float(sale.get("amount_cents", 0)))
        product_id = sale.get("product_id", "")
        
        # Determine which product from the ID
        product_name = "Unknown"
        if "tiktok" in product_id.lower() or "dwswu" in str(sale.get("permalink", "")):
            product_name = "TikTok Pack"
        elif "youtube" in product_id.lower() or "zogyka" in str(sale.get("permalink", "")):
            product_name = "YouTube Shorts Pack"
        elif "bundle" in product_id.lower() or "udogc" in str(sale.get("permalink", "")):
            product_name = "Bundle"
        
        add_sale(email, amount, product_name, str(sale.get("id", "")))
        
    return jsonify({"status": "ok"})

@app.route("/health")
def health():
    stats = get_stats()
    return jsonify({
        "status": "ok",
        "views": stats["views"],
        "subscribers": stats["subscribers"],
        "sales": stats["sales"],
        "revenue": stats["revenue_fmt"]
    })

@app.route("/admin")
def admin():
    key = request.args.get("key", "")
    if key != ADMIN_PASSWORD:
        return "Unauthorized", 401
    
    stats = get_stats()
    recent = get_recent_sales()
    return render_template("admin.html",
        stats=stats,
        recent_sales=recent
    )

# ── Start ───────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=None)
    args = parser.parse_args()
    port = args.port if args.port else PORT
    app.run(host="0.0.0.0", port=port, debug=False)