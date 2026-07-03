#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CryptoPulse AI v9.0 — bot.py — 18 Parts Creator — DEBUG MODE
"""
import os, sys, time, asyncio, threading, traceback, warnings, importlib, signal
from datetime import datetime

warnings.filterwarnings("ignore")
import logging
for name in ['telegram','httpx','httpcore','urllib3','asyncio','aiohttp','uvicorn','fastapi']:
    logging.getLogger(name).setLevel(logging.CRITICAL)

# Fix tokens
for old, new in [("Telegram _bot_token","BOT_TOKEN"),("telegram_bot_token","BOT_TOKEN"),("TELEGRAM_BOT_TOKEN","BOT_TOKEN")]:
    if old in os.environ and os.environ.get(old,"").strip():
        if new not in os.environ or not os.environ.get(new,"").strip():
            os.environ[new] = os.environ[old]

BOT_TOKEN = os.environ.get("BOT_TOKEN","")
CREATOR_NAME = os.environ.get("CREATOR_NAME","Farhad Behmard")
CREATOR_TG = os.environ.get("CREATOR_TELEGRAM","@Amir92aa")
CREATOR_GH = os.environ.get("CREATOR_GITHUB","github.com/farhadbehmard")

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

@api_app.get("/", response_class=HTMLResponse)
async def root():
    uptime = (datetime.now() - startup_time).total_seconds()
    u = f"{int(uptime//86400)}d {int((uptime%86400)//3600)}h {int((uptime%3600)//60)}m"
    ok = sum(1 for v in status.values() if "✅" in str(v))
    total = len(status) or 18
    return f"""<!DOCTYPE html><html lang="fa" dir="rtl"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0"><title>CryptoPulse AI v9.0</title><style>*{{margin:0;padding:0}}body{{font-family:system-ui;background:linear-gradient(135deg,#0a0a1a,#1a1a3a,#0d0d2b);color:#e0e0e0;min-height:100vh;display:flex;justify-content:center;align-items:center;padding:20px}}.container{{max-width:800px;width:100%;background:rgba(20,20,50,.9);border-radius:24px;padding:40px;box-shadow:0 20px 60px rgba(0,0,0,.5);border:1px solid rgba(100,150,255,.2)}}h1{{font-size:32px;background:linear-gradient(135deg,#00d4ff,#7b2ff7,#ff2d95);-webkit-background-clip:text;-webkit-text-fill-color:transparent;text-align:center}}.badge{{display:inline-block;padding:8px 20px;border-radius:20px;font-weight:700;margin:5px}}.online{{background:rgba(0,255,100,.2);color:#00ff64;border:1px solid #00ff64}}.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:15px;margin:25px 0}}.card{{background:rgba(30,30,60,.8);border-radius:16px;padding:20px;text-align:center;border:1px solid rgba(100,150,255,.15)}}.val{{font-size:28px;font-weight:800;background:linear-gradient(135deg,#00d4ff,#7b2ff7);-webkit-background-clip:text;-webkit-text-fill-color:transparent}}.lbl{{font-size:12px;color:#999;margin-top:5px;text-transform:uppercase}}.creator{{background:rgba(30,30,60,.6);border-radius:16px;padding:20px;margin-top:20px;border:1px solid rgba(100,150,255,.15)}}.creator h3{{color:#fff}}.creator p{{color:#aaa;font-size:14px;margin:5px 0}}a{{color:#00d4ff;text-decoration:none}}.endpoints{{margin-top:25px;padding:15px;background:rgba(0,0,0,.3);border-radius:12px;font-family:monospace;font-size:13px;color:#aaa;line-height:1.8}}span{{color:#00d4ff}}.footer{{text-align:center;margin-top:25px;font-size:12px;color:#666}}</style></head><body><div class="container"><h1>🚀 CryptoPulse AI v9.0</h1><p style="text-align:center;color:#888">God Mode Edition — 18 Parts</p><div style="text-align:center"><span class="badge online">{'🟢 ONLINE' if bot_ready else '🟡 STARTING'}</span><span class="badge online">🤖 AI</span><span class="badge online">🧠 God Mode</span></div><div class="grid"><div class="card"><div class="val">{ok}/{total}</div><div class="lbl">Modules</div></div><div class="card"><div class="val">{u}</div><div class="lbl">Uptime</div></div><div class="card"><div class="val">9.0</div><div class="lbl">Version</div></div><div class="card"><div class="val">{'✅' if bot_ready else '⏳'}</div><div class="lbl">Bot</div></div></div><div class="creator"><h3>👑 {CREATOR_NAME}</h3><p>📱 Telegram: <a href="https://t.me/{CREATOR_TG.replace('@','')}">{CREATOR_TG}</a></p><p>💻 GitHub: <a href="https://{CREATOR_GH}">{CREATOR_GH}</a></p></div><div class="endpoints"><div>🔗 <span>GET /</span> — Creator Page</div><div>🔗 <span>GET /health</span> — Health</div><div>🔗 <span>GET /status</span> — Status</div><div>🔗 <span>POST /webhook</span> — Webhook</div></div><div class="footer">© {datetime.now().year} CryptoPulse AI. Powered by God Mode</div></div></body></html>"""

@api_app.get("/health")
async def health():
    ok = sum(1 for v in status.values() if "✅" in str(v))
    return {"status":"healthy" if bot_ready and ok>=9 else "degraded" if ok>=5 else "starting","modules":f"{ok}/{len(status) or 18}"}

@api_app.get("/status")
async def full_status():
    return {"bot_ready":bot_ready,"uptime":(datetime.now()-startup_time).total_seconds(),"modules":status,"token":"✅" if BOT_TOKEN else "❌","creator":CREATOR_NAME}

# ============================================================
#                    18 PARTS - DEBUG MODE
# ============================================================
PARTS = [
    (1,"part1"),(2,"part2"),(3,"part3"),(4,"part4"),(5,"part5"),
    (6,"part6"),(7,"part7"),(8,"part8"),(9,"part9"),(10,"part10"),
    (11,"part11"),(12,"part12"),(13,"part13"),(14,"part14"),(15,"part15"),
    (16,"part16"),(17,"part17"),(18,"part18"),
]

def load_parts():
    print("\n📦 Loading 18 Parts — DEBUG MODE:\n")
    for pid, name in PARTS:
        try:
            mod = importlib.import_module(name)
            loaded[name] = mod
            if hasattr(mod, "start"):
                try:
                    result = mod.start()
                    if callable(result):
                        result()
                except Exception as e:
                    print(f"   ⚠️ Part {pid:2d} — start() error: {e}")
            status[name] = "✅"
            print(f"   ✅ Part {pid:2d} — Loaded")
        except Exception as e:
            status[name] = f"⚠️ {str(e)[:50]}"
            print(f"   ❌ Part {pid:2d} — FAILED: {e}")
            traceback.print_exc()
        time.sleep(0.02)
    
    ok = sum(1 for v in status.values() if "✅" in str(v))
    print(f"\n   📊 Loaded: {ok}/{len(PARTS)}\n")

async def start_bot():
    global telegram_app, bot_ready
    if not BOT_TOKEN:
        print("❌ BOT_TOKEN not set!")
        return False
    
    part9 = loaded.get("part9")
    if not part9:
        print("❌ part9 not loaded!")
        return False
    
    if not hasattr(part9, "get_application"):
        print("❌ part9 has no get_application()!")
        print(f"   Attributes: {[x for x in dir(part9) if not x.startswith('_')][:20]}")
        return False
    
    try:
        app = part9.get_application()
        if not app:
            print("❌ get_application() returned None!")
            return False
        
        print("🔄 Initializing...")
        await app.initialize()
        print("▶️  Starting...")
        await app.start()
        print("📡 Starting Polling...")
        await app.updater.start_polling(drop_pending_updates=True)
        print("📡 Polling Active!")
        telegram_app = app
        bot_ready = True
        return True
    except Exception as e:
        print(f"❌ start_bot error: {e}")
        traceback.print_exc()
        return False

def run_server():
    port = int(os.environ.get("PORT","8080"))
    print(f"\n🌐 Creator Page: http://0.0.0.0:{port}\n")
    uvicorn.run(api_app, host="0.0.0.0", port=port, log_level="critical", access_log=False)

async def async_main():
    global startup_time
    startup_time = datetime.now()
    print(f"""
╔══════════════════════════════════════════════════╗
║   🚀 CryptoPulse AI v9.0 — 18 PARTS            ║
║   👑 {CREATOR_NAME} — {CREATOR_TG}               ║
║   🔍 DEBUG MODE                                ║
╚══════════════════════════════════════════════════╝
⏰ {startup_time.strftime('%Y-%m-%d %H:%M:%S')}
🔑 Token: {'✅ ' + BOT_TOKEN[:10] + '...' if BOT_TOKEN else '❌ NOT SET!'}
""")
    threading.Thread(target=run_server, daemon=True).start()
    await asyncio.sleep(3)
    load_parts()
    if BOT_TOKEN:
        print("🤖 Starting Bot...")
        if await start_bot():
            print("✅ Bot is ONLINE\n")
        else:
            print("⚠️  Bot failed\n")
    while True:
        await asyncio.sleep(60)

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
        print(f"\n❌ {e}")
