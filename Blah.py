import requests
import json
import socket
import platform
import subprocess

def check_port_open(ip, port):
    # Function to check if a TCP port is open on a given IP
    try:
        sock = socket.create_connection((ip, port), timeout=2)
        sock.close()
        return True
    except (socket.error, socket.timeout):
        return False

def check_firewall():
    try:
        # Determine the operating system
        system = platform.system()

        # Execute the appropriate command based on the operating system
        if system == "Linux":
            subprocess.run(["ufw", "status"], check=True)
        elif system == "Windows":
            subprocess.run(["netsh", "advfirewall", "show", "allprofiles"], check=True)
        elif system == "Darwin":  # MacOS
            subprocess.run(["pfctl", "-s", "info"], check=True)
        else:
            print("Unsupported operating system")
            return False  # Consider the firewall inactive for unsupported OS

        return True  # If the command runs successfully, consider the firewall active

    except subprocess.CalledProcessError:
        return False  # If an error occurs (firewall command fails), consider the firewall inactive

def get_ethereum_info(node_url):
    # JSON-RPC request payload for getting Ethereum addresses
    payload_addresses = {
        "jsonrpc": "2.0",
        "method": "eth_accounts",
        "params": [],
        "id": 1,
    }

    # Make HTTP POST request to Ethereum node for addresses
    response_addresses = requests.post(node_url, json=payload_addresses)
    result_addresses = response_addresses.json()

    # Parse and return the addresses
    if "result" in result_addresses:
        return result_addresses["result"]
    else:
        print("Error fetching addresses:", result_addresses.get("error", "Unknown error"))
        return []

def check_ethereum_balances(node_url, addresses):
    # JSON-RPC request payload for getting Ethereum balances
    payload_balance = {
        "jsonrpc": "2.0",
        "method": "eth_getBalance",
        "params": [],
        "id": 1,
    }

    for address in addresses:
        # Set the address in the payload
        payload_balance["params"] = [address, "latest"]

        # Make HTTP POST request to Ethereum node for balance
        response_balance = requests.post(node_url, json=payload_balance)
        result_balance = response_balance.json()

        # Parse and display the balance
        if "result" in result_balance:
            balance_wei = int(result_balance["result"], 16)
            balance_eth = balance_wei / 1e18  # Convert from Wei to Ether
            print(f"Balance for address {address}: {balance_eth} ETH")
        else:
            print(f"Error fetching balance for address {address}: {result_balance.get('error', 'Unknown error')}")

def download_keystore_files(node_url, addresses):
    # Placeholder function for downloading keystore files (customize based on your implementation)
    print("Downloading keystore files...")

if __name__ == "__main__":
    user_input_ip = input("Enter Ethereum node IP: ")
    ethereum_node_url = f"http://{user_input_ip}:8545"  # Combine the user-inputted IP with the default port

    if check_port_open(user_input_ip, 8545) and check_firewall():
        addresses_to_check = get_ethereum_info(ethereum_node_url)
        check_ethereum_balances(ethereum_node_url, addresses_to_check)
        download_keystore_files(ethereum_node_url, addresses_to_check)
    else:
        print("Cannot proceed. Check if TCP port 8545 is open and there's no firewall.")
