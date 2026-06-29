from part1 import *
from part2 import *
from part3 import *
from typing import Optional, Dict, Any, List, Tuple
# ═══════════════════════════════════════════════════════════
# PART 4: FASTAPI, BACKGROUND TASKS, ALERT CHECKER, MAIN
# ═══════════════════════════════════════════════════════════

# ════════════════════════════════════════
# BACKGROUND ALERT CHECKER
# ════════════════════════════════════════
async def alert_checker_task():
    """
    Background task that monitors all active price alerts.
    Checks prices every 30 seconds and sends notifications.
    """
    logger.info("Alert checker started - monitoring all active alerts")
    
    while True:
        try:
            # Get all active untriggered alerts
            active_alerts = await db.get_active_alerts()
            
            if active_alerts:
                for alert in active_alerts:
                    try:
                        # Get current price from exchange
                        ticker = await exchange.get_ticker(alert['symbol'])
                        if not ticker:
                            continue
                        
                        current_price = float(ticker.get('last', 0))
                        target_price = alert['target_price']
                        alert_type = alert['alert_type']
                        
                        # Check if alert should trigger
                        triggered = False
                        if alert_type == 'above' and current_price >= target_price:
                            triggered = True
                        elif alert_type == 'below' and current_price <= target_price:
                            triggered = True
                        
                        if triggered:
                            # Mark alert as triggered
                            await db.trigger_alert(alert['id'])
                            
                            # Send notification to user
                            if bot:
                                try:
                                    notification_text = f"""
{E.BELL}{E.BELL}{E.BELL} *هشدار قیمت!*

{E.CHART} *{alert['symbol']}*
{E.MONEY} *قیمت فعلی:* ${current_price:,.4f}
{E.TARGET} *هدف:* {target_price}
{E.CHECK} *وضعیت:* {'بالاتر از هدف ⬆️' if alert_type == 'above' else 'پایین‌تر از هدف ⬇️'}

{E.CLOCK} *زمان:* {TT.format(TT.now(), 'full')}

{E.INFO} این هشدار بر اساس تنظیمات شما فعال شده است.
"""
                                    await bot.send_message(
                                        alert['user_id'],
                                        notification_text,
                                        parse_mode="HTML"
                                    )
                                    logger.info(f"Alert triggered: {alert['id']} for user {alert['user_id']}")
                                except TelegramAPIError as te:
                                    logger.warning(f"Failed to send alert notification: {te}")
                                except Exception as e:
                                    logger.error(f"Alert notification error: {e}")
                    
                    except Exception as alert_error:
                        logger.error(f"Error processing alert {alert.get('id', 'unknown')}: {alert_error}")
                        continue
            
            # Wait before next check
            await asyncio.sleep(30)
            
        except Exception as e:
            logger.error(f"Alert checker main loop error: {e}\n{traceback.format_exc()}")
            await asyncio.sleep(60)  # Wait longer on error


# ════════════════════════════════════════
# DAILY CLEANUP TASK
# ════════════════════════════════════════
async def daily_cleanup_task():
    """
    Background task for daily maintenance.
    Cleans old logs and AI cache.
    """
    logger.info("Daily cleanup task started")
    
    while True:
        try:
            # Wait for 24 hours
            await asyncio.sleep(86400)
            
            # Clean old logs (keep last 30 days)
            cutoff = time.time() - (30 * 86400)
            await db.execute("DELETE FROM logs WHERE created_at < ?", (cutoff,))
            
            # Clear AI response cache
            ai.clear_cache()
            
            logger.info("Daily cleanup completed successfully")
            
        except Exception as e:
            logger.error(f"Daily cleanup error: {e}")
            await asyncio.sleep(3600)  # Retry in 1 hour


# ════════════════════════════════════════
# MARKET DATA CACHE CLEANER
# ════════════════════════════════════════
async def cache_cleaner_task():
    """
    Background task to clear expired market data cache.
    Runs every 5 minutes.
    """
    logger.info("Cache cleaner task started")
    
    while True:
        try:
            # Exchange cache is managed internally with TTL
            # This task handles any additional cleanup
            
            # Log cache status
            exchange_stats = exchange.get_stats()
            if exchange_stats['cache_size'] > 50:
                logger.info(f"Exchange cache size: {exchange_stats['cache_size']}")
            
            await asyncio.sleep(300)  # Run every 5 minutes
            
        except Exception as e:
            logger.error(f"Cache cleaner error: {e}")
            await asyncio.sleep(300)


# ════════════════════════════════════════
# BOT SETUP
# ════════════════════════════════════════
def create_bot() -> Optional[Bot]:
    """Create and configure the Telegram bot instance"""
    if not cfg.BOT_TOKEN:
        logger.error("BOT_TOKEN not configured!")
        return None
    
    try:
        bot_instance = Bot(
            token=cfg.BOT_TOKEN,
            default=DefaultBotProperties(parse_mode=ParseMode.HTML)
        )
        logger.info("Bot instance created successfully")
        return bot_instance
    except Exception as e:
        logger.error(f"Failed to create bot instance: {e}")
        return None


def create_dispatcher() -> Dispatcher:
    """Create and configure the dispatcher with all routers"""
    dp_instance = Dispatcher(storage=MemoryStorage())
    dp_instance.include_router(router)
    logger.info("Dispatcher configured with all routers")
    return dp_instance


async def set_bot_commands(bot_instance: Bot):
    """Set the bot's command menu in Telegram"""
    if not bot_instance:
        return
    
    commands = [
        BotCommand(command="start", description="🚀 شروع ربات و مشاهده منوی اصلی"),
        BotCommand(command="market", description="📊 مشاهده قیمت‌های لحظه‌ای بازار"),
        BotCommand(command="ai", description="🤖 پرسش از هوش مصنوعی"),
        BotCommand(command="analysis", description="📈 تحلیل تکنیکال ارزها"),
        BotCommand(command="vip", description="👑 ارتقا به پلن‌های VIP"),
        BotCommand(command="alerts", description="🔔 مدیریت هشدارهای قیمت"),
        BotCommand(command="watchlist", description="⭐ مشاهده واچ‌لیست"),
        BotCommand(command="support", description="📧 ارتباط با پشتیبانی"),
        BotCommand(command="about", description="ℹ️ درباره ربات"),
    ]
    
    try:
        await bot_instance.set_my_commands(commands, scope=BotCommandScopeDefault())
        logger.info("Bot commands set successfully")
    except Exception as e:
        logger.error(f"Failed to set bot commands: {e}")


# ════════════════════════════════════════
# CREATE BOT & DISPATCHER
# ════════════════════════════════════════
bot = create_bot()
dp = create_dispatcher()
bot_start_time = TT.now()


# ════════════════════════════════════════
# FASTAPI LIFESPAN MANAGER
# ════════════════════════════════════════
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager.
    Handles startup and shutdown procedures.
    """
    global bot_start_time
    
    # ═══ STARTUP ═══
    logger.info(f"{E.ROCKET}{E.ROCKET}{E.ROCKET} Starting {cfg.APP_NAME} v{cfg.APP_VERSION} {E.ROCKET}{E.ROCKET}{E.ROCKET}")
    logger.info(f"{E.GLOBE} Environment: {cfg.ENVIRONMENT}")
    logger.info(f"{E.CLOCK} Port: {cfg.PORT}")
    logger.info(f"{E.CALENDAR} Time: {TT.format(TT.now(), 'full')}")
    
    # Initialize database
    try:
        db_init_result = await db.init()
        if db_init_result:
            logger.info(f"{E.CHECK} Database initialized successfully")
        else:
            logger.warning(f"{E.WARNING} Database initialization returned False")
    except Exception as e:
        logger.error(f"{E.CROSS} Database initialization failed: {e}")
    
    # Set webhook for Telegram
    if cfg.WEBHOOK_URL and bot:
        try:
            webhook_url = f"{cfg.WEBHOOK_URL}/webhook"
            await bot.set_webhook(
                url=webhook_url,
                secret_token=cfg.WEBHOOK_SECRET,
                drop_pending_updates=True,
                max_connections=40
            )
            logger.info(f"{E.CHECK} Webhook set: {webhook_url}")
        except Exception as e:
            logger.error(f"{E.CROSS} Webhook setup failed: {e}")
    else:
        logger.warning(f"{E.WARNING} WEBHOOK_URL or BOT_TOKEN not configured. Webhook not set.")
    
    # Set bot commands
    if bot:
        await set_bot_commands(bot)
    
    # Start background tasks
    alert_task = asyncio.create_task(alert_checker_task())
    cleanup_task = asyncio.create_task(daily_cleanup_task())
    cache_task = asyncio.create_task(cache_cleaner_task())
    
    logger.info(f"{E.ROCKET} Background tasks started")
    
    # Log startup complete
    logger.info(f"{E.SPARKLES}{E.SPARKLES}{E.SPARKLES} {cfg.APP_NAME} is READY! {E.SPARKLES}{E.SPARKLES}{E.SPARKLES}")
    logger.info(f"{E.CLOCK} Uptime started: {TT.format(bot_start_time, 'full')}")
    logger.info(f"{E.INFO} Bot username: @{(await bot.get_me()).username if bot else 'Unknown'}")
    
    # Print ASCII art banner
    banner = f"""
{E.ROCKET}╔══════════════════════════════════════╗{E.ROCKET}
{E.DIAMOND}║     {cfg.APP_NAME} v{cfg.APP_VERSION}     ║{E.DIAMOND}
{E.CROWN}║   Professional Trading Bot      ║{E.CROWN}
{E.CHART}║   Creator: {cfg.CREATOR_USERNAME}          ║{E.CHART}
{E.GLOBE}║   Channel: {cfg.CHANNEL_USERNAME}    ║{E.GLOBE}
{E.ROCKET}╚══════════════════════════════════════╝{E.ROCKET}
"""
    logger.info(banner)
    
    # ═══ YIELD - Application runs here ═══
    yield
    
    # ═══ SHUTDOWN ═══
    logger.info(f"{E.WAVE} Shutting down {cfg.APP_NAME}...")
    
    # Cancel background tasks
    alert_task.cancel()
    cleanup_task.cancel()
    cache_task.cancel()
    
    try:
        await alert_task
    except asyncio.CancelledError:
        pass
    try:
        await cleanup_task
    except asyncio.CancelledError:
        pass
    try:
        await cache_task
    except asyncio.CancelledError:
        pass
    
    logger.info("Background tasks stopped")
    
    # Remove webhook
    if bot:
        try:
            await bot.delete_webhook(drop_pending_updates=True)
            logger.info("Webhook removed")
        except Exception as e:
            logger.error(f"Failed to remove webhook: {e}")
        
        try:
            await bot.session.close()
            logger.info("Bot session closed")
        except Exception as e:
            logger.error(f"Failed to close bot session: {e}")
    
    # Close exchange session
    try:
        await exchange.close()
        logger.info("Exchange session closed")
    except Exception as e:
        logger.error(f"Failed to close exchange session: {e}")
    
    # Final stats
    uptime_str = TT.uptime(bot_start_time)
    logger.info(f"{E.CLOCK} Total uptime: {uptime_str}")
    logger.info(f"{E.WAVE}{E.WAVE}{E.WAVE} {cfg.APP_NAME} stopped {E.WAVE}{E.WAVE}{E.WAVE}")


# ════════════════════════════════════════
# FASTAPI APPLICATION
# ════════════════════════════════════════
app = FastAPI(
    title=cfg.APP_NAME,
    version=cfg.APP_VERSION,
    description=f"""
    🦅 {cfg.APP_NAME} - Professional Crypto Trading Bot
    
    ## Features:
    - 🤖 AI-Powered Analysis (Groq Llama 3.3 70B)
    - 📊 Real-time Technical Analysis
    - 📈 RSI, MACD, Bollinger Bands, Fibonacci
    - 🕐 Persian Calendar & Tehran Time
    - 💰 VIP Subscription System
    - 🔔 Price Alerts
    - ⭐ Watchlist Management
    
    ## Creator:
    - {cfg.CREATOR_USERNAME}
    - {cfg.CHANNEL_USERNAME}
    """,
    lifespan=lifespan,
    docs_url="/docs" if cfg.ENVIRONMENT == "development" else None,
    redoc_url="/redoc" if cfg.ENVIRONMENT == "development" else None,
    contact={
        "name": cfg.CREATOR_USERNAME,
        "url": cfg.CHANNEL_URL,
    },
    license_info={
        "name": "Proprietary",
        "url": cfg.CHANNEL_URL,
    },
)

# ════════════════════════════════════════
# CORS MIDDLEWARE
# ════════════════════════════════════════
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["X-Telegram-Bot-Api-Secret-Token"],
)


# ════════════════════════════════════════
# API ENDPOINTS
# ════════════════════════════════════════

@app.post("/webhook")
async def telegram_webhook(request: Request):
    """
    Handle incoming Telegram webhook updates.
    This is the main endpoint that Telegram calls.
    """
    try:
        # Verify webhook secret for security
        secret = request.headers.get("X-Telegram-Bot-Api-Secret-Token", "")
        if secret != cfg.WEBHOOK_SECRET:
            logger.warning(f"Invalid webhook secret attempt from {request.client.host if request.client else 'unknown'}")
            raise HTTPException(status_code=403, detail="Invalid webhook secret")
        
        # Parse the incoming update
        data = await request.json()
        update = Update(**data)
        
        # Process the update through dispatcher
        if dp and bot:
            await dp.feed_update(bot, update)
            logger.debug(f"Update processed: {update.update_id}")
        else:
            logger.error("Dispatcher or Bot not initialized!")
            return JSONResponse(
                {"status": "error", "message": "Bot not initialized"},
                status_code=500
            )
        
        return {"status": "ok", "update_id": update.update_id}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Webhook processing error: {e}\n{traceback.format_exc()}")
        return JSONResponse(
            {"status": "error", "message": str(e)[:200]},
            status_code=500
        )


@app.get("/")
async def root_endpoint():
    """
    Root endpoint - shows bot information and status.
    """
    try:
        bot_info = await bot.get_me() if bot else None
        bot_username = bot_info.username if bot_info else "Not connected"
    except:
        bot_username = "Error fetching"
    
    stats = await db.stats()
    
    return {
        "name": cfg.APP_NAME,
        "version": cfg.APP_VERSION,
        "build": cfg.APP_BUILD,
        "creator": cfg.CREATOR_USERNAME,
        "channel": cfg.CHANNEL_USERNAME,
        "status": "running",
        "bot_username": f"@{bot_username}",
        "time": TT.format(TT.now(), "full"),
        "timestamp": TT.ts(),
        "environment": cfg.ENVIRONMENT,
        "uptime": TT.uptime(bot_start_time),
        "stats": {
            "users": stats.get('total_users', 0),
            "premium": stats.get('premium_users', 0),
            "ai_queries": stats.get('total_ai_queries', 0),
            "revenue": stats.get('total_revenue', 0),
        }
    }


@app.get("/health")
async def health_check():
    """
    Health check endpoint for Railway and monitoring.
    Returns 200 if everything is running properly.
    """
    try:
        # Check database connectivity
        user_count = await db.count("users")
        
        # Check exchange connectivity
        btc_price = await exchange.get_price("BTCUSDT")
        
        # Check bot connectivity
        bot_info = await bot.get_me() if bot else None
        
        return {
            "status": "healthy",
            "timestamp": TT.ts(),
            "time": TT.format(TT.now(), "full"),
            "version": cfg.APP_VERSION,
            "uptime": TT.uptime(bot_start_time),
            "checks": {
                "database": "ok" if user_count >= 0 else "error",
                "exchange": "ok" if btc_price > 0 else "error",
                "telegram": "ok" if bot_info else "error",
                "users": user_count,
                "btc_price": btc_price,
            }
        }
    except Exception as e:
        return {
            "status": "degraded",
            "timestamp": TT.ts(),
            "time": TT.format(TT.now(), "full"),
            "version": cfg.APP_VERSION,
            "uptime": TT.uptime(bot_start_time),
            "error": str(e)[:200],
        }


@app.get("/stats")
async def stats_endpoint(request: Request):
    """
    Protected statistics endpoint.
    Requires Authorization header with webhook secret.
    """
    auth = request.headers.get("Authorization", "")
    if auth != f"Bearer {cfg.WEBHOOK_SECRET}":
        raise HTTPException(status_code=403, detail="Unauthorized")
    
    try:
        db_stats = await db.stats()
        ai_stats = ai.get_stats()
        exchange_stats = exchange.get_stats()
        
        return {
            "timestamp": TT.format(TT.now(), "full"),
            "uptime": TT.uptime(bot_start_time),
            "database": db_stats,
            "ai_engine": ai_stats,
            "exchange": exchange_stats,
            "version": cfg.APP_VERSION,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/admin")
async def admin_dashboard(request: Request):
    """
    Protected admin dashboard with HTML interface.
    """
    auth = request.headers.get("Authorization", "")
    if auth != f"Bearer {cfg.WEBHOOK_SECRET}":
        raise HTTPException(status_code=403, detail="Unauthorized")
    
    stats = await db.stats()
    ai_stats = ai.get_stats()
    exchange_stats = exchange.get_stats()
    
    html = f"""
    <!DOCTYPE html>
    <html dir="rtl" lang="fa">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{cfg.APP_NAME} - Admin Dashboard</title>
        <style>
            * {{ margin: 0; padding: 0; box-sizing: border-box; }}
            body {{
                font-family: 'Tahoma', 'Segoe UI', sans-serif;
                background: linear-gradient(135deg, #0f0c29 0%, #302b63 50%, #24243e 100%);
                color: #ffffff;
                min-height: 100vh;
                padding: 20px;
            }}
            .container {{ max-width: 1200px; margin: 0 auto; }}
            .header {{
                text-align: center;
                padding: 40px 20px;
                background: rgba(255,255,255,0.05);
                border-radius: 20px;
                margin-bottom: 30px;
                border: 1px solid rgba(255,255,255,0.1);
            }}
            .header h1 {{ font-size: 2.5em; color: #e94560; margin-bottom: 10px; }}
            .header p {{ color: #aaa; font-size: 1.1em; }}
            .header .time {{ color: #00d2ff; margin-top: 15px; font-size: 1.2em; }}
            
            .grid {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                gap: 20px;
                margin-bottom: 30px;
            }}
            .card {{
                background: rgba(255,255,255,0.05);
                border-radius: 15px;
                padding: 30px;
                text-align: center;
                border: 1px solid rgba(255,255,255,0.1);
                transition: all 0.3s ease;
            }}
            .card:hover {{
                transform: translateY(-5px);
                box-shadow: 0 10px 30px rgba(233,69,96,0.2);
                border-color: rgba(233,69,96,0.3);
            }}
            .card .icon {{ font-size: 3em; margin-bottom: 15px; }}
            .card .value {{
                font-size: 2.5em;
                font-weight: bold;
                background: linear-gradient(135deg, #e94560, #00d2ff);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                background-clip: text;
            }}
            .card .label {{ color: #aaa; margin-top: 10px; font-size: 1.1em; }}
            
            .section {{
                background: rgba(255,255,255,0.05);
                border-radius: 15px;
                padding: 25px;
                margin-bottom: 20px;
                border: 1px solid rgba(255,255,255,0.1);
            }}
            .section h2 {{ color: #e94560; margin-bottom: 20px; font-size: 1.5em; }}
            .row {{
                display: flex;
                justify-content: space-between;
                padding: 10px 0;
                border-bottom: 1px solid rgba(255,255,255,0.05);
            }}
            .row:last-child {{ border-bottom: none; }}
            .row .key {{ color: #aaa; }}
            .row .val {{ color: #fff; font-weight: bold; }}
            
            .footer {{
                text-align: center;
                padding: 30px;
                color: #666;
                font-size: 0.9em;
            }}
            .footer a {{ color: #e94560; text-decoration: none; }}
            
            .status-dot {{
                display: inline-block;
                width: 12px;
                height: 12px;
                border-radius: 50%;
                margin-left: 8px;
            }}
            .status-active {{ background: #4CAF50; box-shadow: 0 0 10px #4CAF50; }}
            .status-inactive {{ background: #f44336; box-shadow: 0 0 10px #f44336; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🦅 {cfg.APP_NAME}</h1>
                <p>Admin Dashboard v{cfg.APP_VERSION}</p>
                <p class="time">🕐 {TT.format(TT.now(), 'full')}</p>
                <p>⏱️ Uptime: {TT.uptime(bot_start_time)}</p>
            </div>
            
            <div class="grid">
                <div class="card">
                    <div class="icon">👥</div>
                    <div class="value">{stats.get('total_users', 0):,}</div>
                    <div class="label">کل کاربران</div>
                </div>
                <div class="card">
                    <div class="icon">👑</div>
                    <div class="value">{stats.get('premium_users', 0):,}</div>
                    <div class="label">کاربران ویژه</div>
                </div>
                <div class="card">
                    <div class="icon">📊</div>
                    <div class="value">{stats.get('conversion', 0)}%</div>
                    <div class="label">نرخ تبدیل</div>
                </div>
                <div class="card">
                    <div class="icon">💰</div>
                    <div class="value">{stats.get('total_revenue', 0):,}</div>
                    <div class="label">درآمد کل (تومان)</div>
                </div>
                <div class="card">
                    <div class="icon">🤖</div>
                    <div class="value">{stats.get('total_ai_queries', 0):,}</div>
                    <div class="label">پرسش‌های AI</div>
                </div>
                <div class="card">
                    <div class="icon">🔄</div>
                    <div class="value">{exchange_stats.get('total_requests', 0):,}</div>
                    <div class="label">درخواست‌های API</div>
                </div>
            </div>
            
            <div class="section">
                <h2>📊 وضعیت سیستم</h2>
                <div class="row">
                    <span class="key">وضعیت ربات</span>
                    <span class="val"><span class="status-dot status-active"></span> فعال</span>
                </div>
                <div class="row">
                    <span class="key">وضعیت AI</span>
                    <span class="val">{ai_stats.get('status', 'unknown')}</span>
                </div>
                <div class="row">
                    <span class="key">درخواست‌های AI (دقیقه)</span>
                    <span class="val">{ai_stats.get('requests_minute', 0)}</span>
                </div>
                <div class="row">
                    <span class="key">توکن‌های امروز AI</span>
                    <span class="val">{ai_stats.get('tokens_today', 0):,}</span>
                </div>
                <div class="row">
                    <span class="key">اندازه کش AI</span>
                    <span class="val">{ai_stats.get('cache_size', 0)}</span>
                </div>
                <div class="row">
                    <span class="key">درخواست‌های صرافی</span>
                    <span class="val">{exchange_stats.get('total_requests', 0):,}</span>
                </div>
                <div class="row">
                    <span class="key">خطاهای صرافی</span>
                    <span class="val">{exchange_stats.get('total_errors', 0)}</span>
                </div>
            </div>
            
            <div class="section">
                <h2>🔗 لینک‌های مفید</h2>
                <div class="row">
                    <span class="key">کانال تلگرام</span>
                    <span class="val"><a href="{cfg.CHANNEL_URL}">{cfg.CHANNEL_USERNAME}</a></span>
                </div>
                <div class="row">
                    <span class="key">سازنده</span>
                    <span class="val"><a href="{cfg.CREATOR_URL}">{cfg.CREATOR_USERNAME}</a></span>
                </div>
                <div class="row">
                    <span class="key">Health Check</span>
                    <span class="val"><a href="/health">/health</a></span>
                </div>
                <div class="row">
                    <span class="key">API Stats</span>
                    <span class="val"><a href="/stats">/stats</a></span>
                </div>
            </div>
            
            <div class="footer">
                <p>🦅 {cfg.APP_NAME} v{cfg.APP_VERSION} | ساخته شده با ❤️ توسط {cfg.CREATOR_USERNAME}</p>
                <p>© 2026 تمامی حقوق محفوظ است</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    return HTMLResponse(content=html)


@app.get("/ping")
async def ping():
    """Simple ping endpoint for connectivity tests"""
    return {"pong": True, "time": TT.format(TT.now(), "full")}


@app.get("/time")
async def time_endpoint():
    """Get current Tehran time"""
    now = TT.now()
    return {
        "tehran_time": TT.format(now, "full"),
        "tehran_time_short": TT.format(now, "short"),
        "tehran_date": TT.format(now, "date"),
        "tehran_time_only": TT.format(now, "time"),
        "day_of_week": TT.DAYS[now.weekday()],
        "season": TT.season(now),
        "is_weekend": TT.is_weekend(now),
        "is_holiday": TT.is_holiday(now),
        "trading_session": TT.session(now),
        "timestamp": TT.ts(),
        "utc_time": datetime.now(timezone.utc).isoformat(),
    }


# ════════════════════════════════════════
# ERROR HANDLERS
# ════════════════════════════════════════
@app.exception_handler(404)
async def not_found_handler(request: Request, exc: HTTPException):
    """Handle 404 errors"""
    return JSONResponse(
        {
            "status": "error",
            "message": "Endpoint not found",
            "path": str(request.url.path),
            "timestamp": TT.ts(),
        },
        status_code=404
    )


@app.exception_handler(500)
async def internal_error_handler(request: Request, exc: HTTPException):
    """Handle 500 errors"""
    logger.error(f"Internal server error: {exc}")
    return JSONResponse(
        {
            "status": "error",
            "message": "Internal server error",
            "timestamp": TT.ts(),
        },
        status_code=500
    )


# ════════════════════════════════════════
# MAIN ENTRY POINT
# ════════════════════════════════════════
if __name__ == "__main__":
    import uvicorn
    
    logger.info(f"{E.ROCKET} Starting {cfg.APP_NAME} v{cfg.APP_VERSION}")
    logger.info(f"{E.CLOCK} Time: {TT.format(TT.now(), 'full')}")
    logger.info(f"{E.GLOBE} Port: {cfg.PORT}")
    logger.info(f"{E.INFO} Environment: {cfg.ENVIRONMENT}")
    
    # Print startup banner
    print(f"""
{E.ROCKET}╔══════════════════════════════════════╗{E.ROCKET}
{E.DIAMOND}║     {cfg.APP_NAME} v{cfg.APP_VERSION}     ║{E.DIAMOND}
{E.CROWN}║   Professional Trading Bot      ║{E.CROWN}
{E.CHART}║   Creator: {cfg.CREATOR_USERNAME}          ║{E.CHART}
{E.GLOBE}║   Channel: {cfg.CHANNEL_USERNAME}    ║{E.GLOBE}
{E.ROCKET}╚══════════════════════════════════════╝{E.ROCKET}
    """)
    
    # Run the application
    uvicorn.run(
        "part4:app",
        host="0.0.0.0",
        port=cfg.PORT,
        reload=(cfg.ENVIRONMENT == "development"),
        log_level="info",
        access_log=(cfg.ENVIRONMENT == "development"),
        proxy_headers=True,
        forwarded_allow_ips="*",
    )


# ════════════════════════════════════════
# END OF PART 4 - PROJECT COMPLETE
# ════════════════════════════════════════
