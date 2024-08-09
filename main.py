import requests
import time
import schedule
import socket
import json
from decimal import Decimal, getcontext
from dotenv import load_dotenv
import os

load_dotenv()

# Define constants
CLORE_API_TOKEN = os.getenv('CLORE_API_TOKEN')
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
THRESHOLD_PERCENTAGE = Decimal('0.1')  # Set threshold as 10% of total spend
MAX_RETRIES = 3

# Function to save JSON data to a file
def save_to_file(data, filename):
    with open(filename, 'w') as file:
        json.dump(data, file, indent=4)

# Function to send message via Telegram Bot API
def send_telegram_message(message):
    url = f'https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage'
    payload = {
        'chat_id': TELEGRAM_CHAT_ID,
        'text': message
    }
    response = requests.post(url, data=payload)
    if response.status_code != 200:
        print(f"Failed to send Telegram message: {response.text}")
    else:
        print(f"Telegram message sent: {message}")

# Function to perform API requests with retry logic
def perform_api_request(url, headers):
    for attempt in range(MAX_RETRIES):
        time.sleep(1)
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            if data.get('code') == 0:
                return data
            else:
                print(f"API error: {data}")
                if data.get('code') == 1:
                    send_telegram_message(f"Database error: {data}")
                    time.sleep(2 ** attempt)  # Exponential backoff
                else:
                    send_telegram_message(f"Unexpected API error: {data}")
                    save_to_file(data, 'raw_orders_response.json')
                    return None
        else:
            print(f"Failed to fetch data: {response.text}")
            send_telegram_message(f"Failed to fetch data: {response.text}")
            time.sleep(2 ** attempt)  # Exponential backoff
    return None

# Function to get total spends from orders
def get_total_spends():
    print("Fetching total spends from orders...")
    headers = {'auth': CLORE_API_TOKEN}
    url = 'https://api.clore.ai/v1/my_orders'
    data = perform_api_request(url, headers)
    
    if not data or 'orders' not in data or not isinstance(data['orders'], list):
        error_message = f'Missing or invalid "orders" key in response: {data}'
        print(error_message)
        send_telegram_message(error_message)
        return 0
    
    total_spend = sum(Decimal(str(order.get('price', '0'))) for order in data['orders'])
    print(f"Total spend: {total_spend}")
    return total_spend

# Function to check wallet balances
def check_wallet_balances():
    print("Checking wallet balances...")
    headers = {'auth': CLORE_API_TOKEN}
    url = 'https://api.clore.ai/v1/wallets'
    data = perform_api_request(url, headers)
    
    if not data:
        return 0
    
    total_balance = sum(Decimal(str(wallet.get('balance', '0'))) for wallet in data.get('wallets', []))
    total_spend = get_total_spends()
    low_balance_threshold = total_spend * THRESHOLD_PERCENTAGE
    
    print(f"Total balance: {total_balance} BTC, Threshold: {low_balance_threshold} BTC")
    if total_balance < low_balance_threshold:
        alert_message = f'Low balance alert! Total balance: {total_balance} BTC, Threshold: {low_balance_threshold} BTC'
        send_telegram_message(alert_message)

    return total_balance

# Function to check if SSH port is open
def check_ssh_ports():
    print("Checking SSH ports...")
    headers = {'auth': CLORE_API_TOKEN}
    url = 'https://api.clore.ai/v1/my_orders'
    data = perform_api_request(url, headers)
    
    if not data or 'orders' not in data or not isinstance(data['orders'], list):
        error_message = f'Missing or invalid "orders" key in response: {data}'
        send_telegram_message(error_message)
        return
    
    for order in data['orders']:
        pub_cluster = order.get('pub_cluster', [])
        tcp_ports = order.get('tcp_ports', [])
        
        for cluster in pub_cluster:
            for port_mapping in tcp_ports:
                local_port, public_port = map(int, port_mapping.split(':'))
                if local_port == 22:  # Check if this is the SSH port
                    try:
                        sock = socket.create_connection((cluster, public_port), timeout=5)
                        sock.close()
                        print(f'SSH port {public_port} on {cluster} is open.')
                    except (socket.timeout, ConnectionRefusedError, OSError) as e:
                        error_message = f'Order ID {order["id"]} seems to be offline.'
                        send_telegram_message(error_message)
    send_telegram_message("Instance(s) are online (by ssh port check)")

# Function to perform all checks and notify
def perform_checks():
    send_telegram_message("Performing checks...")
    total_balance = check_wallet_balances()
    total_spend = get_total_spends()
    check_ssh_ports()
    send_telegram_message(f"Checked balances and spends. Total balance: {total_balance}, Total spend: {total_spend}")
    send_telegram_message("No problems found!")

# Schedule the checks to run every hour
schedule.every().hour.do(perform_checks)

# Run the scheduler
while True:
    schedule.run_pending()
    time.sleep(1)
