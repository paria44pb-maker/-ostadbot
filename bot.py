#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CryptoPulse AI v9.0 — Main Loader — 18 Parts — Creator Page — Webhook
"""
import os, sys, time, asyncio, threading, traceback, warnings, importlib, signal
from datetime import datetime
from pathlib import Path

warnings.filterwarnings("ignore")
for name in ['telegram','httpx','httpcore','urllib3','asyncio','aiohttp']:
    import logging
    logging.getLogger(name).setLevel(logging.CRITICAL)

# Fix env
for old, new in [("Telegram _bot_token","BOT_TOKEN"),("telegram_bot_token","BOT_TOKEN"),("TELEGRAM_BOT_TOKEN","BOT_TOKEN")]:
    if old in os.environ and os.environ.get(old,"").strip():
        if new not in os.environ or not os.environ.get(new,"").strip():
            os.environ[new] = os.environ[old]

BOT_TOKEN = os.environ.get("BOT_TOKEN","")
CREATOR_NAME = os.environ.get("CREATOR_NAME","Farhad Behmard")
CREATOR_TG = os.environ.get("CREATOR_TELEGRAM","@Amir92aa")

# FastAPI
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

@api_app.get("/", response_class=HTMLResponse)
async def root():
    uptime = (datetime.now() - startup_time).total_seconds()
    u = f"{int(uptime//86400)}d {int((uptime%86400)//3600)}h {int((uptime%3600)//60)}m"
    ok = sum(1 for v in status.values() if "✅" in str(v))
    total = len(status) or 18
    return f"""<!DOCTYPE html><html lang="fa" dir="rtl"><head><meta charset="UTF-8"><title>CryptoPulse AI v9.0</title>
<style>*{{margin:0;padding:0;box-sizing:border-box}}body{{font-family:system-ui;background:linear-gradient(135deg,#0a0a1a,#1a1a3a,#0d0d2b);color:#e0e0e0;min-height:100vh;display:flex;justify-content:center;align-items:center;padding:20px}}
.container{{max-width:800px;width:100%;background:rgba(20,20,50,.9);border-radius:24px;padding:40px;box-shadow:0 20px 60px rgba(0,0,0,.5),0 0 100px rgba(0,150,255,.1);border:1px solid rgba(100,150,255,.2)}}h1{{font-size:32px;background:linear-gradient(135deg,#00d4ff,#7b2ff7,#ff2d95);-webkit-background-clip:text;-webkit-text-fill-color:transparent;text-align:center}}.badge{{display:inline-block;padding:8px 20px;border-radius:20px;font-weight:700;margin:5px}}.online{{background:rgba(0,255,100,.2);color:#00ff64;border:1px solid #00ff64}}.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:15px;margin:25px 0}}.card{{background:rgba(30,30,60,.8);border-radius:16px;padding:20px;text-align:center;border:1px solid rgba(100,150,255,.15)}}.val{{font-size:28px;font-weight:800;background:linear-gradient(135deg,#00d4ff,#7b2ff7);-webkit-background-clip:text;-webkit-text-fill-color:transparent}}.lbl{{font-size:12px;color:#999;margin-top:5px;text-transform:uppercase}}.creator{{background:rgba(30,30,60,.6);border-radius:16px;padding:20px;margin-top:20px;border:1px solid rgba(100,150,255,.15)}}.creator h3{{color:#fff}}.creator p{{color:#aaa;font-size:14px;margin:5px 0}}.endpoints{{margin-top:25px;padding:15px;background:rgba(0,0,0,.3);border-radius:12px;font-family:monospace;font-size:13px;color:#aaa}}span{{color:#00d4ff}}.footer{{text-align:center;margin-top:25px;font-size:12px;color:#666}}</style></head><body>
<div class="container"><h1>🚀 CryptoPulse AI v9.0</h1>
<p style="text-align:center;color:#888;margin:10px 0">God Mode Edition</p>
<div style="text-align:center"><span class="badge online">{'🟢 ONLINE' if bot_ready else '🟡 STARTING'}</span><span class="badge online">🤖 AI</span><span class="badge online">🧠 God Mode</span></div>
<div class="grid"><div class="card"><div class="val">{ok}/{total}</div><div class="lbl">Modules</div></div><div class="card"><div class="val">{u}</div><div class="lbl">Uptime</div></div><div class="card"><div class="val">9.0</div><div class="lbl">Version</div></div><div class="card"><div class="val">{'✅' if bot_ready else '⏳'}</div><div class="lbl">Bot</div></div></div>
<div class="creator"><h3>👑 {CREATOR_NAME}</h3><p>📱 Telegram: {CREATOR_TG}</p></div>
<div class="endpoints"><div>🔗 <span>GET /</span> — Creator Page</div><div>🔗 <span>GET /health</span> — Health</div><div>🔗 <span>GET /status</span> — Status</div><div>🔗 <span>POST /webhook</span> — Telegram Webhook</div></div>
<div class="footer">© {datetime.now().year} CryptoPulse AI. Powered by God Mode</div></div></body></html>"""

@api_app.get("/health")
async def health():
    ok = sum(1 for v in status.values() if "✅" in str(v))
    return {"status":"healthy" if bot_ready and ok>=15 else "degraded" if ok>=9 else "starting","modules":f"{ok}/{len(status) or 18}"}

@api_app.get("/status")
async def full_status():
    return {"bot_ready":bot_ready,"uptime":(datetime.now()-startup_time).total_seconds(),"modules":status,"token":"✅" if BOT_TOKEN else "❌","creator":CREATOR_NAME}

@api_app.post("/webhook")
async def webhook(request: Request):
    global telegram_app
    if not bot_ready or not telegram_app:
        return JSONResponse(status_code=503,content={"status":"not_ready"})
    try:
        data = await request.json()
        await telegram_app.update_queue.put(data)
        return {"status":"ok"}
    except:
        return JSONResponse(status_code=500,content={"status":"error"})

# Parts
PARTS = [
    (1,"part1","Database"),(2,"part2","Config"),(3,"part3","i18n"),(4,"part4","Utils"),
    (5,"part5","Exchange"),(6,"part6","AI"),(7,"part7","Technical"),(8,"part8","Signals"),
    (9,"part9","Handlers"),(10,"part10","Trading"),(11,"part11","Payments"),(12,"part12","Media"),
    (13,"part13","Notifications"),(14,"part14","Monitoring"),(15,"part15","Backup"),
    (16,"part16","Intelligence"),(17,"part17","Advanced Analysis"),(18,"part18","God Mode"),
]

def load_parts():
    for pid, name, desc in PARTS:
        try:
            mod = importlib.import_module(name)
            loaded[name] = mod
            if hasattr(mod,"start"):
                try: mod.start()
                except: pass
            status[name] = f"✅ {desc}"
            print(f"   ✅ Part {pid:2d} — {desc}")
        except Exception as e:
            status[name] = f"⚠️ {desc}"
            print(f"   ⚠️ Part {pid:2d} — {desc} — {str(e)[:40]}")
        time.sleep(0.02)

async def start_bot():
    global telegram_app, bot_ready
    part9 = loaded.get("part9")
    if not part9 or not hasattr(part9,"get_application"):
        return False
    app = part9.get_application()
    if not app:
        return False
    await app.initialize()
    await app.start()
    domain = os.environ.get("RAILWAY_PUBLIC_DOMAIN","") or os.environ.get("RAILWAY_STATIC_URL","").replace("https://","")
    if domain and domain.strip():
        url = f"https://{domain.strip()}/webhook"
        await app.bot.delete_webhook(drop_pending_updates=True)
        await asyncio.sleep(0.5)
        await app.bot.set_webhook(url=url, drop_pending_updates=True)
        print(f"   🔗 Webhook: {url}")
    else:
        await app.updater.start_polling(drop_pending_updates=True)
        print("   📡 Mode: Polling")
    telegram_app = app
    bot_ready = True
    return True

def run_server():
    port = int(os.environ.get("PORT","8080"))
    print(f"\n🌐 Creator Page: http://0.0.0.0:{port}")
    uvicorn.run(api_app, host="0.0.0.0", port=port, log_level="warning", access_log=False)

async def main():
    global startup_time
    startup_time = datetime.now()
    print(f"""
╔══════════════════════════════════════════════════╗
║   🚀 CryptoPulse AI v9.0 — God Mode            ║
║   👑 {CREATOR_NAME} — {CREATOR_TG}              ║
║   📦 Loading 18 Parts...                        ║
╚══════════════════════════════════════════════════╝
⏰ {startup_time.strftime('%Y-%m-%d %H:%M:%S')}
🔑 Token: {'✅ ' + BOT_TOKEN[:8] + '...' if BOT_TOKEN else '❌ NOT SET!'}
""")
    threading.Thread(target=run_server, daemon=True).start()
    await asyncio.sleep(2)
    load_parts()
    ok = sum(1 for v in status.values() if "✅" in str(v))
    print(f"\n📊 Loaded: {ok}/{len(PARTS)}\n")
    print("🤖 Starting...")
    if await start_bot():
        print("✅ ONLINE\n")
    else:
        print("⚠️ Bot failed — API still running\n")
    while True:
        await asyncio.sleep(60)

if __name__ == "__main__":
    signal.signal(signal.SIGINT, lambda s,f: sys.exit(0))
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 Stopped")
    except Exception as e:
        print(f"\n❌ {e}")
        traceback.print_exc()
