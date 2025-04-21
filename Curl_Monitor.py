import subprocess
import time
import json
import threading

def send_request(url, method, headers=None, data=None):
    headers = headers or {}
    command = ['curl', '-s', '-o', '/dev/null', '-w', '%{http_code}:%{time_total}', '-X', method, url]

    for key, value in headers.items():
        command.extend(['-H', f'{key}: {value}'])

    if method.upper() == 'POST' and data:
        command.extend(['-d', json.dumps(data)])

    print(command)
    response = subprocess.run(command, capture_output=True, text=True)

    try:
        status_time = response.stdout.strip().split(':')
        status_code = int(status_time[0])
        time_total = float(status_time[1])
    except (IndexError, ValueError) as e:
        # In case the output doesn't have the expected format
        status_code = None
        time_total = None

    return {
        'response_time': time_total,
        'status_code': status_code,
        'response': response.stdout
    }


# Function to monitor all APIs in the configuration file
def monitor_apis(config):
    while True:
        for api in config['apis']:
            url = api['url']
            method = api['method']
            headers = api.get('headers', {})
            data = api.get('data', None)

            # Send request and log results
            result = send_request(url, method, headers, data)
            log_result(url, result)

        # Wait for the specified interval before running again
        time.sleep(config['monitoring_interval'])

# Function to log results (could be extended to save to a file)
def log_result(url, result):
    print(f"Monitoring URL: {url}")
    print(f"Response Time: {result['response_time']} seconds")
    print(f"Status Code: {result['status_code']}")
    print(f"Response: {result['response']}")
    print('-' * 50)

# Function to load the configuration file
def load_config(config_file):
    with open(config_file, 'r') as file:
        config = json.load(file)
    return config

# Main function to start monitoring
def start_monitoring(config_file):
    config = load_config(config_file)
    monitoring_thread = threading.Thread(target=monitor_apis, args=(config,))
    monitoring_thread.daemon = True  # Allow it to run in the background
    monitoring_thread.start()

    print("Automated monitoring started...")

# Entry point
if __name__ == "__main__":
    config_file = 'config.json'  # Path to the configuration file
    start_monitoring(config_file)
    
    # Keep the main program running while the monitoring thread runs in the background
    while True:
        time.sleep(1000)  # Sleep for a long time to keep the main thread alive