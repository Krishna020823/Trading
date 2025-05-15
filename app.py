from SmartApi import SmartConnect
import pyotp
import json
import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning

# Disable SSL warnings
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

# Monkey patch requests to disable SSL verification globally
old_request = requests.Session.request
def new_request(self, *args, **kwargs):
    kwargs['verify'] = False
    return old_request(self, *args, **kwargs)
requests.Session.request = new_request

# Function to place an order
def place_order(angleone, symbol, transaction_type, quantity, price):
    order_params = {
        "variety": "NORMAL",
        "tradingsymbol": symbol,
        "symboltoken": "2885",
        "transactiontype": transaction_type,
        "exchange": "NSE",
        "ordertype": "LIMIT",
        "producttype": "INTRADAY",
        "duration": "DAY",
        "price": price,
        "quantity": quantity
    }
    order_id = angleone.placeOrder(order_params)
    return order_id

# Main function to log in and place a trade
def main():
    try:
        with open("angleone_login_details.json", "r") as f:
            login_credential = json.load(f)
    except FileNotFoundError:
        print("Login credentials file not found.")
        return

    try:
        angleone = SmartConnect(api_key=login_credential["api_key"])
        generate_session = angleone.generateSession(
            login_credential["user_id"],
            login_credential["pin"],
            pyotp.TOTP(login_credential["totp_code"]).now()
        )['data']
        generate_tokens = angleone.generateToken(generate_session['refreshToken'])["data"]
        access_token = generate_tokens['jwtToken']
        refresh_token = generate_tokens['refreshToken']
        feed_token = angleone.getfeedToken()
        print("Login successful.")

        # Example trade parameters
        symbol = "RELIANCE-EQ"
        transaction_type = "BUY"  # or "SELL"
        quantity = 1
        price = 2000  # Example price
        order_id = place_order(angleone, symbol, transaction_type, quantity, price)
        print(f"Order placed successfully. Order ID: {order_id}")
    except Exception as e:
        print(f"Login or order placement failed: {e}")

if __name__ == "__main__":
    main()
