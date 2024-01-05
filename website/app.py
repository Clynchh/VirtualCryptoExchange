from flask import Blueprint, render_template, request, flash, session, redirect, url_for
from flask_login import login_required, current_user, logout_user, login_user
app = Blueprint('app', __name__)
from .mktcap import get_mkt_cap
from .metadata import moving_average, day_vol, price_change
from .mean_reversion import generate_report, format_2dp
import sqlite3
from requests import get
import json
from random import randint
from werkzeug.security import generate_password_hash, check_password_hash



@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template("index.html", user=current_user, authenticated=False)


@app.route('/login', methods=['GET', 'POST'])
def login():
    connection = sqlite3.connect("C:\\Users\\corey\\OneDrive\\Desktop\\Database_Working\\website\\exchange.db")
    cursor = connection.cursor()
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        cursor.execute("""
        SELECT username FROM users WHERE username=?
        """, (username,))
        user = cursor.fetchone()
        cursor.execute("""
        SELECT hashed_password FROM users where username = ?""", (username,))
        hashed_pass = cursor.fetchone()
        connection.commit()
        connection.close()

        if user != None:
            if check_password_hash(hashed_pass[0], password):
                flash('Logged in successfully', category='success')
                return redirect(url_for('app.assets'))
            else:
                flash('incorrect password', category='error')
        else:
            flash('username does not exist', category='error')
        session["username"] = username
    return render_template("login.html", user=current_user)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('app.login'))

@app.route('/sign-up', methods=['GET', 'POST'])
def sign_up():
    connection = sqlite3.connect("C:\\Users\\corey\\OneDrive\\Desktop\\Database_Working\\website\\exchange.db")
    cursor = connection.cursor()
    if request.method == 'POST':
        first_name = request.form.get('first-name')
        username = request.form.get('username')
        password = request.form.get('password')
        confirmed_pass = request.form.get('password-confirm')

        cursor.execute("""
        SELECT username FROM users WHERE username=?
        """,(username,))
        user = cursor.fetchone()
        

        if user != None:
            flash('Username already exists', category='error')
        elif len(first_name) < 2 or len(first_name) > 25:
            flash("Name must be between 2 and 25 chars long", category='error')
        elif len(username) < 2 or len(username) > 25:
            flash("Username must be between 2 and 25 chars long", category='error')
        elif len(password) < 8 or len(password) > 25:
            flash("password must be between 8 and 25 chars long", category='error')
        elif password != confirmed_pass:
            flash("Passwords do not match", category='error')
        else:
            hashed_password = generate_password_hash(password, method='sha256')
            user_id = randint(1,1000000)
            new_user = """
            INSERT INTO users (user_id, username, first_name, hashed_password)
            VALUES (?, ?, ?, ?)
            """
            
            
            cursor.execute(new_user, (user_id, username, first_name, hashed_password))
            user_portfolio = """
            INSERT INTO portfolio (user_id, asset_id, quantity)
            SELECT users.user_id, ?, ?
            FROM users
            WHERE users.user_id = ?;
            """
            for i in range(17):
                if i == 0:
                    quantity = 1000
                else:
                    quantity = 0
                cursor.execute(user_portfolio, (i, quantity, user_id))
            connection.commit()
            connection.close()
            session["username"] = username
            flash("Account Created", category='success')
            return redirect(url_for('app.assets'))



    return render_template("sign_up.html", user=current_user)



symbols = get_mkt_cap().keys()
mkt_caps = get_mkt_cap().values()


symbol_names = {
    'BTC': 'Bitcoin',
    'ETH': 'Ethereum',
    'BNB': 'Binance Coin',
    'ADA': 'Cardano',
    'SOL': 'Solana',
    'XRP': 'Ripple',
    'DOT': 'Polkadot',
    'DOGE': 'Dogecoin',
    'MATIC': 'Polygon',
    'LINK': 'ChainLink',
    'LTC': 'Litecoin',
    'VET': 'VeChain',
    'CAKE': 'Pancake Swap',
    'ENJ': 'Enjin Coin',
    'RUNE': 'ThorChain',
    'LUNA': 'Terra'
}

symbols = [
    'BTC',
    'ETH',
    'BNB',
    'ADA',
    'SOL',
    'XRP',
    'DOT',
    'DOGE',
    'MATIC',
    'LINK',
    'LTC',
    'VET',
    'CAKE',
    'ENJ',
    'RUNE',
    'LUNA'
]

graph_colors = {
    'btc': '#D97000',
    'eth': '#808080',
    'bnb': '#FFCC00',
    'ada': '#001B7C',
    'sol': '#00E0D9',
    'xrp': '#000000',
    'dot': '#FF00AD',
    'doge': '#FAF580',
    'matic': '#C068FF',
    'link': '#A7BEFE',
    'ltc': '#0000FF',
    'vet': '#FFFFFF',
    'cake': '#C4A484',
    'enj': '#4F008F',
    'rune': '#005F53',
    'luna': '#555555'
}


def verify_order(symbol, asset_id):
    if request.method == 'POST':
        if request.form['place-order'] == "BUY":
            buy(symbol, asset_id)
        elif request.form['place-order'] == "SELL":
            sell(symbol, asset_id)

def buy(symbol, asset_id):
    connection = sqlite3.connect("C:\\Users\\corey\\OneDrive\\Desktop\\Database_Working\\website\\exchange.db")
    cursor = connection.cursor()
    current_username = session["username"]

    cursor.execute("""
    SELECT user_id FROM users WHERE username=?
    """, (current_username,))
    current_user_id = cursor.fetchone()[0]
    cursor.execute(
        """SELECT quantity FROM portfolio
         WHERE user_id=? AND asset_id=?""", (current_user_id, asset_id)
    )
    current_asset_quantity = cursor.fetchone()[0]
    buy_quantity = request.form.get('quantity')
    if buy_quantity.replace('.', '', 1).isdigit():
        new_quantity = current_asset_quantity + float(buy_quantity)

        cursor.execute(
            """SELECT quantity
            FROM portfolio 
            WHERE user_id=?
            AND asset_id=0""",(current_user_id,))
        user_balance = cursor.fetchone()[0]  

        url = "https://api.binance.com/api/v3/avgPrice?symbol={symbol}GBP".format(symbol=symbol)
        asset_response = get(url).json()
        asset_price = float(asset_response['price'])
        order_price = float(buy_quantity) * asset_price
        if user_balance >= order_price:
            user_balance -= order_price
            cursor.execute(
                    """
                    UPDATE portfolio
                    SET quantity = ?
                    WHERE user_id= ?
                    AND asset_id=0
                    """, (user_balance, current_user_id))
            cursor.execute(
                """
                UPDATE portfolio
                SET quantity = ?
                WHERE user_id = ?
                AND asset_id=?
                """, (new_quantity, current_user_id, asset_id))
            connection.commit()
            connection.close()
            flash("Order Placed", category="success")
        else:
            flash("Insufficient Funds", category="error")
    else:
        flash("Quantity has to be a positive number", category="error")

def sell(symbol, asset_id):
    connection = sqlite3.connect("C:\\Users\\corey\\OneDrive\\Desktop\\Database_Working\\website\\exchange.db")
    cursor = connection.cursor()
    sell_quantity = request.form.get("quantity")
    if sell_quantity.replace('.', '', 1).isdigit():
        current_username = session["username"]
        cursor.execute("""
        SELECT user_id FROM users WHERE username=?
        """, (current_username,))
        current_user_id = cursor.fetchone()[0]
        cursor.execute(
        """SELECT quantity FROM portfolio
         WHERE user_id=? AND asset_id=?""", (current_user_id, asset_id)
        )
        current_asset_quantity = cursor.fetchone()[0]
        new_quantity = current_asset_quantity - float(sell_quantity)
        
        cursor.execute(
            """SELECT quantity
            FROM portfolio 
            WHERE user_id=?
            AND asset_id=0""", (current_user_id,))
        user_balance = cursor.fetchone()[0]
        url = "https://api.binance.com/api/v3/avgPrice?symbol={symbol}GBP".format(symbol=symbol)
        asset_response = get(url).json()
        asset_price = float(asset_response['price'])
        order_price = float(sell_quantity) * asset_price
        user_balance += order_price
        if current_asset_quantity >= float(sell_quantity):
            cursor.execute(
                        """
                        UPDATE portfolio
                        SET quantity = ?
                        WHERE user_id= ?
                        AND asset_id=0
                        """, (user_balance, current_user_id))
            cursor.execute("""
                    UPDATE portfolio
                    SET quantity = ?
                    WHERE user_id = ?
                    AND asset_id=?
                    """, (new_quantity, current_user_id, asset_id))
            connection.commit()
            connection.close()
            flash("Order Placed", category="success")
        else: flash("You do not have enough of this crypto asset", category="error")
    else:
        flash("Quantity has to be a positive number", category="error")




@app.route('/assets', methods=['GET', 'POST'])
def assets():
    return render_template('assets.html', user=current_user, currency_metadata=zip(symbols, mkt_caps), symbol_names=symbol_names, authenticated=True)



@app.route('/portfolio', methods=['GET', 'POST'])
def portfolio():
    connection = sqlite3.connect("C:\\Users\\corey\\OneDrive\\Desktop\\Database_Working\\website\\exchange.db")
    cursor = connection.cursor()
    current_username = session["username"]
    cursor.execute("""
    SELECT user_id FROM users WHERE username=?
    """, (current_username,))
    current_user_id = cursor.fetchone()[0]
    cursor.execute("""
    SELECT quantity FROM portfolio
    WHERE user_id=?
    """, (current_user_id,))
    tuple_user_assets = cursor.fetchall()
    user_assets = ([i[0] for i in tuple_user_assets])
    user_assets.pop(0)
    user_assets_in_GBP = []
    for i, crypto in enumerate(symbols):
        params = {"symbol": crypto+"GBP"}
        price_url = "https://api.binance.com/api/v3/avgPrice"
        price_response = get(price_url, params).json()
        price = float(price_response["price"])
        converted_crypto = user_assets[i] * price
        converted_crypto = float(format(converted_crypto, ".2f"))
        user_assets_in_GBP.append(converted_crypto)
    current_username = session["username"]
    crypto_balance = sum(user_assets_in_GBP)
    cursor.execute("""
    SELECT user_id FROM users WHERE username=?
    """, (current_username,))
    current_user_id = cursor.fetchone()[0]
    cursor.execute(
    """SELECT quantity
    FROM portfolio 
    WHERE user_id=?
    AND asset_id=0""", (current_user_id,))
    gbp_balance = cursor.fetchone()[0]
    portfolio_value = crypto_balance+gbp_balance
    gbp_balance = format(gbp_balance, ".2f")
    portfolio_value = float(format(portfolio_value, ".3f"))
    portfolio_performance = ((portfolio_value-1000)/1000)*100
    portfolio_performance = format(portfolio_performance, ".5f")
    connection.commit()
    connection.close()
    #portfolio report here#
    user_portfolio = {}
    for i, symbol in enumerate(symbols):
        user_portfolio[symbol] = user_assets[i]

    report = generate_report(user_portfolio)

    return render_template('portfolio.html', user=current_user, authenticated=True, user_assets_in_GBP=user_assets_in_GBP, portfolio_value=portfolio_value, portfolio_performance=portfolio_performance, gbp_balance=gbp_balance, report=report)

@app.route('/rankings', methods=['GET', 'POST'])
def rankings():
    connection = sqlite3.connect("C:\\Users\\corey\\OneDrive\\Desktop\\Database_Working\\website\\exchange.db")
    cursor = connection.cursor()
    cursor.execute("""
    SELECT username FROM users
    """)
    tuple_usernames = cursor.fetchall()
    usernames = [''.join(i) for i in tuple_usernames]
    user_portfolios = {}
    for i, user in enumerate(usernames):
        cursor.execute("""
        SELECT user_id FROM users
        WHERE username=?
        """, (user,))
        user_id = cursor.fetchone()[0]
        cursor.execute("""
        SELECT quantity FROM portfolio
        WHERE user_id=?
        """, (user_id,))
        tuple_user_assets = cursor.fetchall()
        user_assets = ([i[0] for i in tuple_user_assets])
        user_assets.pop(0)
        user_assets_in_GBP = []
        for j, crypto in enumerate(symbols):
            params = {"symbol": crypto+"GBP"}
            price_url = "https://api.binance.com/api/v3/avgPrice"
            price_response = get(price_url, params).json()
            price = float(price_response["price"])
            converted_crypto = user_assets[j] * price
            converted_crypto = float(format(converted_crypto, ".2f"))
            user_assets_in_GBP.append(converted_crypto)
        crypto_balance = sum(user_assets_in_GBP)
        portfolio_info = []
        cursor.execute(
        """SELECT quantity
        FROM portfolio 
        WHERE user_id=?
        AND asset_id=0""", (user_id,))
        gbp_balance = cursor.fetchone()[0]
        portfolio_value = crypto_balance+gbp_balance
        portfolio_value = float(format(portfolio_value, ".2f"))
        portfolio_info.append(portfolio_value)
        portfolio_performance = ((portfolio_value-1000)/1000)*100
        portfolio_performance = format(portfolio_performance, ".4f")
        portfolio_info.append(portfolio_performance)
        user_portfolios[user] = portfolio_info

    sorted_user_portfolios = sorted(user_portfolios.items(), key=lambda k: k[1][0], reverse=True)
    print(sorted_user_portfolios)

        

    connection.commit()
    connection.close()
    return render_template('rankings.html', user=current_user, authenticated=True, user_portfolios=sorted_user_portfolios)


#the next 16 routes are for each specific currency's trading page

#1
@app.route('/trading/BTCGBP', methods=['GET', 'POST'])
def trading_BTC():
    verify_order("BTC", 1)
    return render_template('/trading/BTCGBP.html', user=current_user, mkt_cap=(get_mkt_cap()["BTC"]), graph_color=graph_colors['btc'], MA_200=moving_average("BTC", 200), MA_50=moving_average("BTC", 50), day_vol=day_vol("BTC"), day_change=price_change("BTC", "d"), week_change=price_change("BTC", "w"), authenticated=True)

#2
@app.route('/trading/ETHGBP', methods=['GET', 'POST'])
def trading_ETH():
    verify_order("ETH", 2)
    return render_template('/trading/ETHGBP.html', user=current_user, mkt_cap=(get_mkt_cap()["ETH"]), graph_color=graph_colors['eth'], MA_200=moving_average("ETH", 200), MA_50=moving_average("ETH", 50), day_vol=day_vol("ETH"), day_change=price_change("ETH", "d"), week_change=price_change("ETH", "w"), authenticated=True)

#3
@app.route('/trading/BNBGBP', methods=['GET', 'POST'])
def trading_BNB():
    verify_order("BNB", 3)
    return render_template('/trading/BNBGBP.html', user=current_user, mkt_cap=(get_mkt_cap()["BNB"]), graph_color=graph_colors['bnb'], MA_200=moving_average("BNB", 200), MA_50=moving_average("BNB", 50), day_vol=day_vol("BNB"), day_change=price_change("BNB", "d"), week_change=price_change("BNB", "w"), authenticated=True)

#4
@app.route('/trading/XRPGBP', methods=['GET', 'POST'])
def trading_XRP():
    verify_order("XRP", 6)
    return render_template('/trading/XRPGBP.html', user=current_user, mkt_cap=(get_mkt_cap()["XRP"]), graph_color=graph_colors['xrp'], MA_200=moving_average("XRP", 200), MA_50=moving_average("XRP", 50), day_vol=day_vol("XRP"), day_change=price_change("XRP", "d"), week_change=price_change("XRP", "w"), authenticated=True)

#5
@app.route('/trading/ADAGBP', methods=['GET', 'POST'])
def trading_ADA():
    verify_order("ADA", 4)
    return render_template('/trading/ADAGBP.html', user=current_user, mkt_cap=(get_mkt_cap()["ADA"]), graph_color=graph_colors['ada'], MA_200=moving_average("ADA", 200), MA_50=moving_average("ADA", 50), day_vol=day_vol("ADA"), day_change=price_change("ADA", "d"), week_change=price_change("ADA", "w"), authenticated=True)

#6
@app.route('/trading/SOLGBP', methods=['GET', 'POST'])
def trading_SOL():
    verify_order("SOL", 5)
    return render_template('/trading/SOLGBP.html', user=current_user, mkt_cap=(get_mkt_cap()["SOL"]), graph_color=graph_colors['sol'], MA_200=moving_average("SOL", 200), MA_50=moving_average("SOL", 50), day_vol=day_vol("SOL"), day_change=price_change("SOL", "d"), week_change=price_change("SOL", "w"), authenticated=True)

#7
@app.route('/trading/DOTGBP', methods=['GET', 'POST'])
def trading_DOT():
    verify_order("DOT", 7)
    return render_template('/trading/DOTGBP.html', user=current_user, mkt_cap=(get_mkt_cap()["DOT"]), graph_color=graph_colors['dot'], MA_200=moving_average("DOT", 200), MA_50=moving_average("DOT", 50), day_vol=day_vol("DOT"), day_change=price_change("DOT", "d"), week_change=price_change("DOT", "w"), authenticated=True)

#8
@app.route('/trading/DOGEGBP', methods=['GET', 'POST'])
def trading_DOGE():
    verify_order("DOGE", 8)
    return render_template('/trading/DOGEGBP.html', user=current_user, mkt_cap=(get_mkt_cap()["DOGE"]), graph_color=graph_colors['doge'], MA_200=moving_average("DOGE", 200), MA_50=moving_average("DOGE", 50), day_vol=day_vol("DOGE"), day_change=price_change("DOGE", "d"), week_change=price_change("DOGE", "w"), authenticated=True)

#9
@app.route('/trading/MATICGBP', methods=['GET', 'POST'])
def trading_MATIC():
    verify_order("MATIC", 9)
    return render_template('/trading/MATICGBP.html', user=current_user, mkt_cap=(get_mkt_cap()["MATIC"]), graph_color=graph_colors['matic'], MA_200=moving_average("MATIC", 200), MA_50=moving_average("MATIC", 50), day_vol=day_vol("MATIC"), day_change=price_change("DOGE", "d"), week_change=price_change("DOGE", "w"), authenticated=True)

#10
@app.route('/trading/LTCGBP', methods=['GET', 'POST'])
def trading_LTC():
    verify_order("LTC", 11)
    return render_template('/trading/LTCGBP.html', user=current_user, mkt_cap=(get_mkt_cap()["LTC"]), graph_color=graph_colors['ltc'], MA_200=moving_average("LTC", 200), MA_50=moving_average("LTC", 50), day_vol=day_vol("LTC"), day_change=price_change("LTC", "d"), week_change=price_change("LTC", "w"), authenticated=True)

#11
@app.route('/trading/LINKGBP', methods=['GET', 'POST'])
def trading_LINK():
    verify_order("LINK", 10)
    return render_template('/trading/LINKGBP.html', user=current_user, mkt_cap=(get_mkt_cap()["LINK"]), graph_color=graph_colors['link'], MA_200=moving_average("LINK", 200), MA_50=moving_average("LINK", 50), day_vol=day_vol("LINK"), day_change=price_change("LINK", "d"), week_change=price_change("LINK", "w"), authenticated=True)

#12
@app.route('/trading/VETGBP', methods=['GET', 'POST'])
def trading_VET():
    verify_order("VET", 12)
    return render_template('/trading/VETGBP.html', user=current_user, mkt_cap=(get_mkt_cap()["VET"]), graph_color=graph_colors['vet'], MA_200=moving_average("VET", 200), MA_50=moving_average("VET", 50), day_vol=day_vol("VET"), day_change=price_change("VET", "d"), week_change=price_change("VET", "w"), authenticated=True)

#13
@app.route('/trading/CAKEGBP', methods=['GET', 'POST'])
def trading_CAKE():
    verify_order("CAKE", 13)
    return render_template('/trading/CAKEGBP.html', user=current_user, mkt_cap=(get_mkt_cap()["CAKE"]), graph_color=graph_colors['cake'], MA_200=moving_average("CAKE", 200), MA_50=moving_average("CAKE", 50), day_vol=day_vol("CAKE"), day_change=price_change("CAKE", "d"), week_change=price_change("CAKE", "w"), authenticated=True)

#14
@app.route('/trading/ENJGBP', methods=['GET', 'POST'])
def trading_ENJ():
    verify_order("ENJ", 14)
    return render_template('/trading/ENJGBP.html', user=current_user, mkt_cap=(get_mkt_cap()["ENJ"]), graph_color=graph_colors['enj'], MA_200=moving_average("ENJ", 200), MA_50=moving_average("ENJ", 50), day_vol=day_vol("ENJ"), day_change=price_change("ENJ", "d"), week_change=price_change("ENJ", "w"), authenticated=True)

#15
@app.route('/trading/RUNEGBP', methods=['GET', 'POST'])
def trading_RUNE():
    verify_order("RUNE", 15)
    return render_template('/trading/RUNEGBP.html', user=current_user, mkt_cap=(get_mkt_cap()["RUNE"]), graph_color=graph_colors['rune'], MA_200=moving_average("RUNE", 200), MA_50=moving_average("RUNE", 50), day_vol=day_vol("RUNE"), day_change=price_change("RUNE", "d"), week_change=price_change("RUNE", "w"), authenticated=True)

#16    
@app.route('/trading/LUNAGBP', methods=['GET', 'POST'])
def trading_LUNA():
    verify_order("LUNA", 16)
    return render_template('/trading/LUNAGBP.html', user=current_user, mkt_cap=(get_mkt_cap()["LUNA"]), graph_color=graph_colors['luna'], MA_200=moving_average("LUNA", 200), MA_50=moving_average("LUNA", 50), day_vol=day_vol("LUNA"), day_change=price_change("LUNA", "d"), week_change=price_change("LUNA", "w"), authenticated=True)








