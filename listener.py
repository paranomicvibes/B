import socket
import subprocess
import datetime

def handle_client(client_socket, client_address, log_file):
    print(f"Accepted connection from {client_address}")

    # Log connection information to the text file
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"{timestamp} - Accepted connection from {client_address}\n"
    log_file.write(log_entry)

    # Spawn a subprocess to capture data from the connected IP
    subprocess.Popen(['tcpdump', f'-i any src {client_address[0]}'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    # Handle the connection and save data to a file
    data = client_socket.recv(1024)
    print(f"Received data: {data.decode()}")
    log_entry = f"{timestamp} - Received data: {data.decode()}\n"
    log_file.write(log_entry)

    # Save data to a file
    save_file_name = f"data_from_{client_address[0]}_{timestamp.replace(' ', '_').replace(':', '-')}.txt"
    with open(save_file_name, 'wb') as save_file:
        save_file.write(data)
        print(f"Data saved to file: {save_file_name}")

    client_socket.send(b"Welcome to the server!\n")
    client_socket.close()

def start_server(host, port):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen(5)

    print(f"Server listening on {host}:{port}")

    log_file = open("server_log.txt", "a")

    while True:
        client_socket, client_address = server_socket.accept()
        handle_client(client_socket, client_address, log_file)

if __name__ == "__main__":
    host = "0.0.0.0"  # Listen on all available interfaces

    # Prompt the user to input the port
    while True:
        try:
            port = int(input("Enter the port number: "))
            break
        except ValueError:
            print("Invalid port number. Please enter a valid integer.")

    start_server(host, port)