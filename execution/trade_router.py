from execution.nobitex_client import execute_trade

MODE = "paper"

paper_positions = []


def execute_paper_trade(side, symbol, amount, price):

    trade = {
        "side": side,
        "symbol": symbol,
        "amount": amount,
        "price": price,
        "status": "open"
    }

    paper_positions.append(trade)

    print("PAPER TRADE:", trade)

    return trade


def execute_live_trade(side, symbol, amount, price=None):

    result = execute_trade(
        side=side,
        amount=amount,
        symbol=symbol,
        price=price
    )

    print("LIVE TRADE:", result)

    return result


def route_trade(side, symbol, amount, price):

    if MODE == "paper":
        return execute_paper_trade(side, symbol, amount, price)

    if MODE == "live":
        return execute_live_trade(side, symbol, amount, price)
