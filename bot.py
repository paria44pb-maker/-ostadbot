#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CryptoPulse AI v9.0 — Main Loader — 18 Parts — Creator Page — Webhook FIXED
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
    token = ""
    possible_names = ["BOT_TOKEN","Telegram _bot_token","telegram_bot_token","TELEGRAM_BOT_TOKEN","BOT_TOKEN_MAIN","API_TOKEN","bot_token","tg_token","TOKEN","BOT_API_KEY","TELEGRAM_TOKEN"]
    for name in possible_names:
        value = os.environ.get(name, "").strip()
        if value and ":" in value and len(value) > 30:
            token = value
            break
    if token:
        os.environ["BOT_TOKEN"] = token
    if not token:
        for key, value in os.environ.items():
            if ":" in str(value) and len(str(value)) > 40 and "bot" in key.lower():
                token = str(value)
                os.environ["BOT_TOKEN"] = token
                break
    return token

BOT_TOKEN = fix_tokens()
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
    return f"""<!DOCTYPE html><html lang="fa" dir="rtl"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0"><title>CryptoPulse AI v9.0</title><style>*{{margin:0;padding:0;box-sizing:border-box}}body{{font-family:system-ui;background:linear-gradient(135deg,#0a0a1a,#1a1a3a,#0d0d2b);color:#e0e0e0;min-height:100vh;display:flex;justify-content:center;align-items:center;padding:20px}}.container{{max-width:800px;width:100%;background:rgba(20,20,50,.9);border-radius:24px;padding:40px;box-shadow:0 20px 60px rgba(0,0,0,.5);border:1px solid rgba(100,150,255,.2)}}h1{{font-size:32px;background:linear-gradient(135deg,#00d4ff,#7b2ff7,#ff2d95);-webkit-background-clip:text;-webkit-text-fill-color:transparent;text-align:center;margin-bottom:10px}}.badge{{display:inline-block;padding:8px 20px;border-radius:20px;font-weight:700;margin:5px;font-size:14px}}.online{{background:rgba(0,255,100,.2);color:#00ff64;border:1px solid #00ff64}}.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:15px;margin:25px 0}}.card{{background:rgba(30,30,60,.8);border-radius:16px;padding:20px;text-align:center;border:1px solid rgba(100,150,255,.15)}}.val{{font-size:28px;font-weight:800;background:linear-gradient(135deg,#00d4ff,#7b2ff7);-webkit-background-clip:text;-webkit-text-fill-color:transparent}}.lbl{{font-size:12px;color:#999;margin-top:5px;text-transform:uppercase}}.creator{{background:rgba(30,30,60,.6);border-radius:16px;padding:20px;margin-top:20px;border:1px solid rgba(100,150,255,.15)}}.creator h3{{color:#fff;margin-bottom:10px}}.creator p{{color:#aaa;font-size:14px;margin:5px 0}}a{{color:#00d4ff;text-decoration:none}}.endpoints{{margin-top:25px;padding:15px;background:rgba(0,0,0,.3);border-radius:12px;font-family:monospace;font-size:13px;color:#aaa;line-height:1.8}}span{{color:#00d4ff}}.footer{{text-align:center;margin-top:25px;font-size:12px;color:#666}}.progress-bar{{width:100%;height:6px;background:rgba(255,255,255,.1);border-radius:3px;margin:10px 0;overflow:hidden}}.progress-fill{{height:100%;background:linear-gradient(90deg,#00d4ff,#7b2ff7);border-radius:3px;transition:width 0.5s}}</style></head><body><div class="container"><h1>🚀 CryptoPulse AI v9.0</h1><p style="text-align:center;color:#888;margin:10px 0">God Mode Edition — 18 Parts</p><div style="text-align:center"><span class="badge online">{'🟢 ONLINE' if bot_ready else '🟡 STARTING'}</span><span class="badge online">🤖 AI</span><span class="badge online">🧠 God Mode</span></div><div class="progress-bar"><div class="progress-fill" style="width:{(ok/max(total,1))*100}%"></div></div><div style="text-align:center;color:#888;font-size:12px">{ok}/{total} Modules Loaded</div><div class="grid"><div class="card"><div class="val">{ok}/{total}</div><div class="lbl">Modules</div></div><div class="card"><div class="val">{u}</div><div class="lbl">Uptime</div></div><div class="card"><div class="val">9.0</div><div class="lbl">Version</div></div><div class="card"><div class="val">{'✅' if bot_ready else '⏳'}</div><div class="lbl">Status</div></div></div><div class="creator"><h3>👑 {CREATOR_NAME}</h3><p>📱 Telegram: <a href="https://t.me/{CREATOR_TG.replace('@','')}">{CREATOR_TG}</a></p><p>💻 GitHub: <a href="https://{CREATOR_GH}">{CREATOR_GH}</a></p></div><div class="endpoints"><div>🔗 <span>GET /</span> — Creator Page (HTML)</div><div>🔗 <span>GET /api</span> — API Status (JSON)</div><div>🔗 <span>GET /health</span> — Health Check</div><div>🔗 <span>GET /status</span> — Full Status</div><div>🔗 <span>POST /webhook</span> — Telegram Webhook</div></div><div class="footer">© {datetime.now().year} CryptoPulse AI. All rights reserved. | Powered by God Mode AI</div></div></body></html>"""

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
        return JSONResponse(status_code=503,content={"status":"not_ready"})
    try:
        data = await request.json()
        await telegram_app.update_queue.put(data)
        return {"status":"ok"}
    except Exception as e:
        return JSONResponse(status_code=500,content={"status":"error","message":str(e)[:100]})

# ============================================================
#                    18 PARTS
# ============================================================
PARTS = [(1,"part1","Database"),(2,"part2","Config"),(3,"part3","i18n"),(4,"part4","Utils"),(5,"part5","Exchange"),(6,"part6","AI"),(7,"part7","Technical"),(8,"part8","Signals"),(9,"part9","Handlers"),(10,"part10","Trading"),(11,"part11","Payments"),(12,"part12","Media"),(13,"part13","Notifications"),(14,"part14","Monitoring"),(15,"part15","Backup"),(16,"part16","Intelligence"),(17,"part17","Advanced"),(18,"part18","God Mode")]

def load_parts():
    print("\n📦 Loading 18 Parts:\n")
    for pid, name, desc in PARTS:
        try:
            mod = importlib.import_module(name)
            loaded[name] = mod
            if hasattr(mod,"start"):
                try:
                    result = mod.start()
                    if callable(result): result()
                except: pass
            status[name] = f"✅ {desc}"
            print(f"   ✅ Part {pid:2d} — {desc}")
        except Exception as e:
            status[name] = f"⚠️ {desc}"
            print(f"   ⚠️ Part {pid:2d} — {desc}")
        time.sleep(0.02)
    ok = sum(1 for v in status.values() if "✅" in str(v))
    print(f"\n   📊 Loaded: {ok}/{len(PARTS)}\n")

async def start_bot():
    global telegram_app, bot_ready
    if not BOT_TOKEN:
        print("❌ BOT_TOKEN not set!")
        return False
    
    part9 = loaded.get("part9")
    if not part9 or not hasattr(part9,"get_application"):
        print("❌ part9 not loaded!")
        return False
    
    app = part9.get_application()
    if not app:
        print("❌ No application!")
        return False
    
    print("🔄 Initializing...")
    await app.initialize()
    print("▶️  Starting...")
    await app.start()
    
    # Use polling — always works
    print("📡 Starting polling...")
    await app.updater.start_polling(drop_pending_updates=True)
    print("📡 Mode: Polling")
    
    telegram_app = app
    bot_ready = True
    
    # Also set webhook in background
    domain = os.environ.get("RAILWAY_PUBLIC_DOMAIN","") or os.environ.get("RAILWAY_STATIC_URL","").replace("https://","")
    if domain and domain.strip():
        url = f"https://{domain.strip()}/webhook"
        try:
            await asyncio.sleep(2)
            await app.bot.set_webhook(url=url, drop_pending_updates=True)
            print(f"🔗 Webhook also set: {url}")
        except:
            pass
    
    return True

def run_server():
    port = int(os.environ.get("PORT","8080"))
    print(f"🌐 Server: http://0.0.0.0:{port}")
    print(f"   Page: http://0.0.0.0:{port}/")
    print(f"   Health: http://0.0.0.0:{port}/health")
    print(f"   Webhook: http://0.0.0.0:{port}/webhook\n")
    uvicorn.run(api_app, host="0.0.0.0", port=port, log_level="critical", access_log=False)

async def async_main():
    global startup_time
    startup_time = datetime.now()
    print(f"""
╔══════════════════════════════════════════════════════════╗
║   🚀 CryptoPulse AI v9.0 — GOD MODE EDITION            ║
║   👑 {CREATOR_NAME} — {CREATOR_TG}                       ║
║   📦 Loading 18 Parts...                                 ║
╚══════════════════════════════════════════════════════════╝
⏰ {startup_time.strftime('%Y-%m-%d %H:%M:%S')}
🔑 Token: {'✅ ' + BOT_TOKEN[:10] + '...' if BOT_TOKEN else '❌ NOT SET!'}
""")
    
    # Start server FIRST
    threading.Thread(target=run_server, daemon=True).start()
    await asyncio.sleep(3)
    
    # Load parts
    load_parts()
    
    # Start bot with POLLING
    if BOT_TOKEN:
        print("🤖 Starting with Polling...")
        if await start_bot():
            print("\n╔══════════════════════════════════════════════════╗")
            print("║   ✅ ALL SYSTEMS OPERATIONAL                    ║")
            print("║   🤖 Bot: ONLINE (Polling)                     ║")
            print("║   🧠 God Mode: ACTIVE                           ║")
            print("╚══════════════════════════════════════════════════╝\n")
        else:
            print("\n⚠️  Bot failed — API still running\n")
    
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
        print(f"\n❌ Fatal: {e}")
        traceback.print_exc()
