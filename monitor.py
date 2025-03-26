import subprocess
import time
import yaml
import requests
import platform
from datetime import datetime

# Load configuration from YAML
# def load_config():
#     with open("config.yaml", "r") as file:
#         return yaml.safe_load(file)

# Function to run ping command
def ping_device(target, duration=600):
    print(f"Pinging {target} ")
    
    packet_loss_detected = False

    command = ["ping", "-n", "4", target] if platform.system().lower() == "windows" else ["ping", "-c", "4", target]
    
    try:
        output = subprocess.run(command, capture_output=True, text=True, check=True)
        print(output.stdout)  # Print the ping result
    except subprocess.CalledProcessError:
        packet_loss_detected = True
        print(f"Failed to reach {target} or packet loss detected at {datetime.now()}")


    # while time.time() < end_time:
    #     result = subprocess.run(["ping", "-c", "1", target], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    #     if "0% packet loss" not in result.stdout:
    #         print(f"[ALERT] Packet loss detected for {target} at {datetime.now()}")
    #         packet_loss_detected = True
    #     time.sleep(1)  # Ping every second
    
    return packet_loss_detected

# Function to run traceroute command
def traceroute_device(target):
    print(f"Running traceroute on {target}")
    #end_time = time.time() + duration

    # result=subprocess.run(["traceroute", target], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    # print(result)
    # time.sleep(10)  # Run traceroute every 10 seconds
    command = ["tracert", target] if platform.system().lower() == "windows" else ["traceroute", target]

    try:
        # Run the traceroute command and capture output
        result = subprocess.run(command, capture_output=True, text=True, check=True)
        print(result.stdout)  # Print traceroute output
    except subprocess.CalledProcessError as e:
        print(f"Traceroute failed: {e}")

# Function to log an incident in ServiceNow
def log_incident(target, config):
    print(f"Logging incident for {target} in ServiceNow...")
    url = f"https://{config['service_now']['instance']}/api/now/table/{config['service_now']['table']}"
    auth = (config['service_now']['username'], config['service_now']['password'])
    headers = {"Content-Type": "application/json"}
    
    data = {
        "impact": config["service_now"]["impact"],
        "urgency": config["service_now"]["urgency"],
        "short_description": config["service_now"]["short_description"],
        "description": f"Packet loss detected on {target} at {datetime.now()}"
    }
    
    response = requests.post(url, json=data, auth=auth, headers=headers)
    
    if response.status_code == 201:
        print("Incident logged successfully.")
    else:
        print(f"Failed to log incident: {response.text}")

# Main function to run monitoring
def main():
    config = {
    "targets": ["64.233.180.138"],
    "service_now": {
        "instance": "dev262979.service-now.com",

        "table": "incident",
        "impact": "3",
        "urgency": "3",
        "short_description": "Packet loss detected"
    }
}
    for target in config["targets"]:
        packet_loss = ping_device(target)
        traceroute_device(target)
        if packet_loss:
            log_incident(target, config)
    #log_incident(config["targets"][0], config)
if __name__ == "__main__":
    main()
