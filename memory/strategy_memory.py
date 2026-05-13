# strategy_memory.py
# تحلیل عملکرد استراتژی‌ها

from memory.trade_memory import load_memory


def strategy_stats():

    trades = load_memory()

    if len(trades) == 0:
        return {
            "total": 0,
            "wins": 0,
            "losses": 0,
            "winrate": 0
        }

    wins = 0
    losses = 0

    for trade in trades:

        if trade.get("profit", 0) > 0:
            wins += 1
        else:
            losses += 1

    total = wins + losses

    winrate = (wins / total) * 100

    return {
        "total": total,
        "wins": wins,
        "losses": losses,
        "winrate": round(winrate, 2)
    }
