#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CryptoPulse AI v9.0 — Main Loader — 18 Parts — Creator Page — Webhook
"""
import os, sys, time, asyncio, threading, traceback, warnings, importlib, signal, socket
from datetime import datetime

warnings.filterwarnings("ignore")
for name in ['telegram','httpx','httpcore','urllib3','asyncio','aiohttp','uvicorn','fastapi']:
    import logging
    logging.getLogger(name).setLevel(logging.CRITICAL)

# ============================================================
#                    FIX ALL TOKEN NAMES
# ============================================================
def fix_tokens():
    """Fix all possible token environment variable names"""
    token = ""
    
    # Try all possible names
    possible_names = [
        "BOT_TOKEN",
        "Telegram _bot_token",
        "telegram_bot_token", 
        "TELEGRAM_BOT_TOKEN",
        "BOT_TOKEN_MAIN",
        "API_TOKEN",
        "bot_token",
        "tg_token",
        "TOKEN",
        "BOT_API_KEY",
        "TELEGRAM_TOKEN",
    ]
    
    for name in possible_names:
        value = os.environ.get(name, "").strip()
        if value and ":" in value and len(value) > 30:
            token = value
            break
    
    # Set BOT_TOKEN for compatibility
    if token:
        os.environ["BOT_TOKEN"] = token
    
    # Also search all env vars
    if not token:
        for key, value in os.environ.items():
            if ":" in str(value) and len(str(value)) > 40 and "bot" in key.lower():
                token = str(value)
                os.environ["BOT_TOKEN"] = token
                break
    
    return token

BOT_TOKEN = fix_tokens()

# ============================================================
#                    CREATOR INFO
# ============================================================
CREATOR_NAME = os.environ.get("CREATOR_NAME", "Farhad Behmard")
CREATOR_TG = os.environ.get("CREATOR_TELEGRAM", "@Amir92aa")
CREATOR_GH = os.environ.get("CREATOR_GITHUB", "github.com/farhadbehmard")

# ============================================================
#                    FASTAPI APP
# ============================================================
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, HTMLResponse
import uvicorn

api_app = FastAPI(title="CryptoPulse AI v9.0")
api_app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

telegram_app = None
bot_ready = False
startup_time = datetime.now()
loaded = {}
status = {}

# ============================================================
#                    ROUTES
# ============================================================
@api_app.get("/", response_class=HTMLResponse)
async def root():
    uptime = (datetime.now() - startup_time).total_seconds()
    u = f"{int(uptime//86400)}d {int((uptime%86400)//3600)}h {int((uptime%3600)//60)}m"
    ok = sum(1 for v in status.values() if "✅" in str(v))
    total = len(status) or 18
    return f"""<!DOCTYPE html><html lang="fa" dir="rtl"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0"><title>CryptoPulse AI v9.0</title><style>*{{margin:0;padding:0;box-sizing:border-box}}body{{font-family:system-ui;background:linear-gradient(135deg,#0a0a1a,#1a1a3a,#0d0d2b);color:#e0e0e0;min-height:100vh;display:flex;justify-content:center;align-items:center;padding:20px}}.container{{max-width:800px;width:100%;background:rgba(20,20,50,.9);border-radius:24px;padding:40px;box-shadow:0 20px 60px rgba(0,0,0,.5);border:1px solid rgba(100,150,255,.2)}}h1{{font-size:32px;background:linear-gradient(135deg,#00d4ff,#7b2ff7,#ff2d95);-webkit-background-clip:text;-webkit-text-fill-color:transparent;text-align:center;margin-bottom:10px}}.badge{{display:inline-block;padding:8px 20px;border-radius:20px;font-weight:700;margin:5px;font-size:14px}}.online{{background:rgba(0,255,100,.2);color:#00ff64;border:1px solid #00ff64}}.starting{{background:rgba(255,200,0,.2);color:#ffc800;border:1px solid #ffc800}}.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:15px;margin:25px 0}}.card{{background:rgba(30,30,60,.8);border-radius:16px;padding:20px;text-align:center;border:1px solid rgba(100,150,255,.15)}}.val{{font-size:28px;font-weight:800;background:linear-gradient(135deg,#00d4ff,#7b2ff7);-webkit-background-clip:text;-webkit-text-fill-color:transparent}}.lbl{{font-size:12px;color:#999;margin-top:5px;text-transform:uppercase}}.creator{{background:rgba(30,30,60,.6);border-radius:16px;padding:20px;margin-top:20px;border:1px solid rgba(100,150,255,.15)}}.creator h3{{color:#fff;margin-bottom:10px}}.creator p{{color:#aaa;font-size:14px;margin:5px 0}}.endpoints{{margin-top:25px;padding:15px;background:rgba(0,0,0,.3);border-radius:12px;font-family:monospace;font-size:13px;color:#aaa;line-height:1.8}}.endpoints span{{color:#00d4ff}}.footer{{text-align:center;margin-top:25px;font-size:12px;color:#666}}.progress-bar{{width:100%;height:6px;background:rgba(255,255,255,.1);border-radius:3px;margin:10px 0;overflow:hidden}}.progress-fill{{height:100%;background:linear-gradient(90deg,#00d4ff,#7b2ff7);border-radius:3px;transition:width 0.5s}}</style></head><body><div class="container"><h1>🚀 CryptoPulse AI v9.0</h1><p style="text-align:center;color:#888;margin:10px 0">God Mode Edition — 18 Parts</p><div style="text-align:center"><span class="badge {'online' if bot_ready else 'starting'}">{'🟢 ONLINE' if bot_ready else '🟡 STARTING'}</span><span class="badge online">🤖 AI</span><span class="badge online">🧠 God Mode</span></div><div class="progress-bar"><div class="progress-fill" style="width:{(ok/max(total,1))*100}%"></div></div><div style="text-align:center;color:#888;font-size:12px">{ok}/{total} Modules Loaded</div><div class="grid"><div class="card"><div class="val">{ok}/{total}</div><div class="lbl">Modules</div></div><div class="card"><div class="val">{u}</div><div class="lbl">Uptime</div></div><div class="card"><div class="val">9.0</div><div class="lbl">Version</div></div><div class="card"><div class="val">{'✅' if bot_ready else '⏳'}</div><div class="lbl">Status</div></div></div><div class="creator"><h3>👑 {CREATOR_NAME}</h3><p>📱 Telegram: <a href="https://t.me/{CREATOR_TG.replace('@','')}" style="color:#00d4ff;text-decoration:none">{CREATOR_TG}</a></p><p>💻 GitHub: <a href="https://{CREATOR_GH}" style="color:#00d4ff;text-decoration:none">{CREATOR_GH}</a></p></div><div class="endpoints"><div>🔗 <span>GET /</span> — Creator Page (HTML)</div><div>🔗 <span>GET /api</span> — API Status (JSON)</div><div>🔗 <span>GET /health</span> — Health Check</div><div>🔗 <span>GET /status</span> — Full Status</div><div>🔗 <span>POST /webhook</span> — Telegram Webhook</div></div><div class="footer">© {datetime.now().year} CryptoPulse AI. All rights reserved. | Powered by God Mode AI</div></div></body></html>"""

@api_app.get("/api")
async def api():
    uptime = (datetime.now() - startup_time).total_seconds()
    return {"bot":"CryptoPulse AI","version":"9.0.0","creator":CREATOR_NAME,"telegram":CREATOR_TG,"github":CREATOR_GH,"status":"online" if bot_ready else "starting","bot_ready":bot_ready,"uptime_seconds":uptime,"modules_loaded":sum(1 for v in status.values() if "✅" in str(v)),"modules_total":len(status) or 18,"timestamp":datetime.now().isoformat()}

@api_app.get("/health")
async def health():
    ok = sum(1 for v in status.values() if "✅" in str(v))
    return {"status":"healthy" if bot_ready and ok>=15 else "degraded" if ok>=9 else "starting","bot_ready":bot_ready,"modules":f"{ok}/{len(status) or 18}"}

@api_app.get("/status")
async def full_status():
    return {"bot_ready":bot_ready,"uptime":(datetime.now()-startup_time).total_seconds(),"modules":status,"token_set":"✅" if BOT_TOKEN else "❌","creator":CREATOR_NAME,"parts_loaded":sum(1 for v in status.values() if "✅" in str(v)),"parts_total":len(status) or 18}

@api_app.post("/webhook")
async def webhook(request: Request):
    global telegram_app
    if not bot_ready or not telegram_app:
        return JSONResponse(status_code=503,content={"status":"not_ready","message":"Bot still starting"})
    try:
        data = await request.json()
        await telegram_app.update_queue.put(data)
        return {"status":"ok"}
    except Exception as e:
        return JSONResponse(status_code=500,content={"status":"error","message":str(e)[:100]})

# ============================================================
#                    18 PARTS
# ============================================================
PARTS = [
    (1,"part1","Database & Models"),
    (2,"part2","Config & Settings"),
    (3,"part3","i18n & Languages"),
    (4,"part4","Utils & Helpers"),
    (5,"part5","Exchange & Market"),
    (6,"part6","AI & ML"),
    (7,"part7","Technical Analysis"),
    (8,"part8","Signals Engine"),
    (9,"part9","Telegram Handlers"),
    (10,"part10","Trading Engine"),
    (11,"part11","Payments System"),
    (12,"part12","Media & Content"),
    (13,"part13","Notifications"),
    (14,"part14","Monitoring"),
    (15,"part15","Backup & Recovery"),
    (16,"part16","Admin Intelligence"),
    (17,"part17","Advanced Analysis"),
    (18,"part18","God Mode Intelligence"),
]

def load_parts():
    print("\n📦 Loading 18 Parts:\n")
    for pid, name, desc in PARTS:
        try:
            mod = importlib.import_module(name)
            loaded[name] = mod
            if hasattr(mod,"start"):
                try:
                    result = mod.start()
                    if callable(result):
                        result()
                except:
                    pass
            status[name] = f"✅ {desc}"
            print(f"   ✅ Part {pid:2d} — {desc}")
        except Exception as e:
            status[name] = f"⚠️ {desc}"
            print(f"   ⚠️ Part {pid:2d} — {desc} — {str(e)[:60]}")
        time.sleep(0.02)
    
    ok = sum(1 for v in status.values() if "✅" in str(v))
    print(f"\n   📊 Loaded: {ok}/{len(PARTS)}\n")

async def start_bot():
    global telegram_app, bot_ready
    
    if not BOT_TOKEN:
        print("❌ BOT_TOKEN is not set!")
        return False
    
    part9 = loaded.get("part9")
    if not part9:
        print("❌ part9 not loaded!")
        return False
    
    if not hasattr(part9,"get_application"):
        print("❌ part9.get_application() not found!")
        return False
    
    app = part9.get_application()
    if not app:
        print("❌ Could not get application from part9!")
        return False
    
    print("🔄 Initializing...")
    await app.initialize()
    print("▶️  Starting...")
    await app.start()
    
    # Try webhook first
    domain = (
        os.environ.get("RAILWAY_PUBLIC_DOMAIN","") or
        os.environ.get("RAILWAY_STATIC_URL","").replace("https://","") or
        os.environ.get("RENDER_EXTERNAL_URL","").replace("https://","")
    )
    
    if domain and domain.strip():
        url = f"https://{domain.strip()}/webhook"
        try:
            await app.bot.delete_webhook(drop_pending_updates=True)
            await asyncio.sleep(0.5)
            result = await app.bot.set_webhook(url=url, drop_pending_updates=True)
            if result:
                print(f"   🔗 Webhook: {url}")
                telegram_app = app
                bot_ready = True
                return True
        except:
            pass
    
    # Fallback to polling
    try:
        await app.updater.start_polling(drop_pending_updates=True)
        print("   📡 Mode: Polling")
        telegram_app = app
        bot_ready = True
        return True
    except Exception as e:
        print(f"   ❌ Polling failed: {e}")
        return False

def run_server():
    port = int(os.environ.get("PORT","8080"))
    
    # Try multiple ports if 8080 is taken
    for p in [port, 8081, 8082, 8443, 9000]:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.bind(('0.0.0.0', p))
            sock.close()
            port = p
            break
        except:
            continue
    
    print(f"🌐 Server: http://0.0.0.0:{port}")
    print(f"   Creator Page: http://0.0.0.0:{port}/")
    print(f"   Health: http://0.0.0.0:{port}/health")
    print(f"   Status: http://0.0.0.0:{port}/status")
    print(f"   Webhook: http://0.0.0.0:{port}/webhook\n")
    
    try:
        uvicorn.run(api_app, host="0.0.0.0", port=port, log_level="critical", access_log=False)
    except Exception as e:
        print(f"Server error: {e}")

async def async_main():
    global startup_time
    startup_time = datetime.now()
    
    print(f"""
╔══════════════════════════════════════════════════════════╗
║                                                          ║
║   🚀 CryptoPulse AI v9.0 — GOD MODE EDITION            ║
║   ────────────────────────────────────────────────────   ║
║   👑 Creator: {CREATOR_NAME}
║   📱 Telegram: {CREATOR_TG}
║   💻 GitHub: {CREATOR_GH}
║                                                          ║
║   📦 Loading 18 Parts...                                 ║
║   🤖 God Mode Intelligence                               ║
║   🧠 AI-Powered Analysis                                 ║
║   🏦 Multi-Exchange Support                              ║
║                                                          ║
╚══════════════════════════════════════════════════════════╝
⏰ {startup_time.strftime('%Y-%m-%d %H:%M:%S')}

🔑 Token: {'✅ ' + BOT_TOKEN[:10] + '...' if BOT_TOKEN else '❌ NOT SET — Add BOT_TOKEN or Telegram_bot_token in Railway Variables!'}
""")
    
    if not BOT_TOKEN:
        print("\n💡 Please set BOT_TOKEN or Telegram_bot_token in Railway > Variables\n")
        print("   Examples:")
        print("   - Name: BOT_TOKEN | Value: 1234567890:ABCdefGHIjklMNOpqrsTUVwxyz")
        print("   - Name: Telegram_bot_token | Value: 1234567890:ABCdefGHIjklMNOpqrsTUVwxyz")
        print("\n   Server will start but bot will not be active.\n")
    
    # Start API server in thread
    threading.Thread(target=run_server, daemon=True).start()
    await asyncio.sleep(3)
    
    # Load all parts
    load_parts()
    
    # Start bot
    if BOT_TOKEN:
        print("🤖 Starting Telegram...")
        if await start_bot():
            print("\n╔══════════════════════════════════════════════════╗")
            print("║   ✅ ALL SYSTEMS OPERATIONAL                    ║")
            print("║   🤖 Bot: ONLINE                               ║")
            print("║   🧠 God Mode: ACTIVE                           ║")
            print("╚══════════════════════════════════════════════════╝\n")
        else:
            print("\n╔══════════════════════════════════════════════════╗")
            print("║   ⚠️  Bot failed — API still running           ║")
            print("╚══════════════════════════════════════════════════╝\n")
    else:
        print("\n⚠️  No token set — bot will not start\n")
    
    # Keep alive
    while True:
        await asyncio.sleep(3600)

def main():
    try:
        loop = asyncio.get_running_loop()
        loop.create_task(async_main())
        threading.Event().wait()
    except RuntimeError:
        asyncio.run(async_main())

if __name__ == "__main__":
    signal.signal(signal.SIGINT, lambda s,f: sys.exit(0))
    signal.signal(signal.SIGTERM, lambda s,f: sys.exit(0))
    try:
        main()
    except KeyboardInterrupt:
        print("\n🛑 Stopped")
    except Exception as e:
        print(f"\n❌ Fatal: {e}")
        traceback.print_exc()
