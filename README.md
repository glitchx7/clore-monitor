# Clore AI Server Monitor

This project is a server monitoring tool designed to check wallet balances and SSH ports for Clore AI servers. It sends notifications via Telegram when certain thresholds are met or issues are detected.

## Features

- Fetch and monitor wallet balances from Clore AI API.
- Calculate and monitor spend thresholds.
- Check if SSH ports are open on specified servers.
- Send alerts and notifications via Telegram.

## Installation

### Prerequisites

- Python 3.6 or higher
- Pip (Python package installer)

### Step-by-Step Guide

1. **Clone the repository:**

   git clone https://github.com/glitchx7/clore-monitor.git
   cd clore-monitor
2. **Create a virtual environment (optional but recommended):**

   python3 -m venv venv
   source venv/bin/activate  # On Windows use      `venv\Scripts\activate`

3. **Install the required packages:**

pip install -r requirements.txt

4. **Set up environment variables:**

##Usage

To run the server monitor, execute the following command:

python main.py

This script will start performing the checks and will notify you via Telegram if any issues are detected or thresholds are met.
##How It Works
Wallet Balance Check:

    -The script checks wallet balances from the Clore AI API.
    -It calculates a threshold (10% of the total spend) and compares it to the current balance.
    -If the balance is below the threshold, an alert is sent via Telegram.

SSH Port Check:

    -The script fetches order information from the Clore AI API.
    -It checks if the SSH port (port 22) is open for each server.
    -If an SSH port is not open, an alert is sent via Telegram.

API Requests with Retry Logic:

    -The script includes a retry mechanism for API requests to handle temporary issues.
    -If an API request fails, it retries up to 3 times with exponential backoff.

##Dependencies

The project relies on the following Python packages:

    requests: For making HTTP requests to the Clore AI and Telegram APIs.
    schedule: For scheduling periodic checks.
    python-dotenv: For loading environment variables from a .env file.
    decimal: For precise arithmetic calculations.

##Contributing

Contributions are welcome! Please feel free to submit a Pull Request or open an issue to discuss improvements or report bugs.

##License

This project is licensed under the MIT License. See the LICENSE file for more details.

   
