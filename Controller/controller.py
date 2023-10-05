import socket
import threading
import paramiko
import os
import re
import time

# Constants
RASPBERRY_PIS = [
    {"ip": "192.168.53.149", "username": "pi1", "password": "raspberry1"},
    {"ip": "192.168.53.183", "username": "pi1", "password": "raspberry1"},
    # Add more Raspberry Pis as needed
]

# Define server settings
HOST = '0.0.0.0'  # Listen on all available network interfaces
PORT = 8084      # Choose a port for your server

# Data structure to store memory usage
memory_usage = {}
for i in range(len(RASPBERRY_PIS)):
    memory_usage[i]=0

# Create a lock
mutex = threading.Lock()

# Function to SSH into the Raspberry Pi and transfer files
def ssh_work(image_path, output_path):

    print("function called")
    # Find Raspberry Pi with maximum free memory
    mutex.acquire()
    min_memory_pi = max(memory_usage, key=lambda k: memory_usage[k])
    mutex.release()

    min_memory_pi =0
    # Connect to the Raspberry Pi
    ssh_client = paramiko.SSHClient()
    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    ssh_client.connect(
        RASPBERRY_PIS[min_memory_pi]["ip"],
        username=RASPBERRY_PIS[min_memory_pi]["username"],
        password=RASPBERRY_PIS[min_memory_pi]["password"],
    )
    print(f'Connected to Raspi No. : {min_memory_pi}')

    # Transfer the input image to the Raspberry Pi
    sftp = ssh_client.open_sftp()
    sftp.chdir("Service")
    sftp.mkdir(image_path)
    sftp.put(image_path+".jpg", f"./{image_path}/input_image.jpg")
    sftp.close()

    print("here")
    # Run docker image
    stdin, stdout, stderr = ssh_client.exec_command(f'docker run -v ~/Service:/app image-bw-converter {image_path}')
    exit_status = stdout.channel.recv_exit_status() 

    print("done")
    # Transfer the output image from Raspberry Pi
    sftp = ssh_client.open_sftp()
    sftp.get(f"Service/{image_path}/output_image.jpg", output_path)
    sftp.close()

    stdin, stdout, stderr = ssh_client.exec_command(f'cd Service; rm -r {image_path}')    

    ssh_client.close()
    return True

# Function to handle client connections
def handle_client(client_socket):
    print(f"[*] Accepted connection from {client_socket.getpeername()}")

    # Receive the image data from the client
    image_data = b""
    image_data_received = False
    while True:
        chunk = client_socket.recv(1024)
        if not chunk:
            break
        image_data += chunk

        # Check for a custom termination sequence indicating the end of the image data
        if b"IMAGE_END" in image_data:
            image_data_received = True
            break

    if image_data_received:
        # Remove the custom termination sequence from the image data
        image_data = image_data.replace(b"IMAGE_END", b"")
        
        # Set path for input and output image
        host, port = client_socket.getpeername()
        input_image_path = "client_"+str(host)+"_"+str(port)
        output_image_path = "client_"+str(host)+"_"+str(port)+ "_output_image.jpg"
        
        with open(input_image_path+".jpg", "wb") as f:
            f.write(image_data)
        f.close()
        
        # Transfer the control to the Raspberry Pi
        if ssh_work(input_image_path, output_image_path):
            print("Raspberry Pi work complete")

        with open(output_image_path, "rb") as f:
            data = f.read()
        
        # Send file back to the client
        client_socket.sendall(data)

    else:
        client_socket.sendall(b"Error: Image data not received properly")

    client_socket.close()  # Close the client socket when done
    os.remove(input_image_path+".jpg")
    os.remove(output_image_path)
    print("Socket Closed")

############################################################################################################
#                            Thread to periodically update memory usage data                               #
############################################################################################################

# Thread to periodically update memory usage data
def update_memory_usage():
    while True:
        print("Getting memory usage...")
        for i in range(len(RASPBERRY_PIS)):
            # Update memory_usage dictionary
            temp = get_memory_usage(i)
            mutex.acquire()
            memory_usage[i] = temp
            mutex.release()
        time.sleep(30)  # Update every 30 seconds

# Replace this function with actual memory usage retrieval logic
def get_memory_usage(pi_idx):
    # Return memory usage as a float (e.g., 0.75 for 75% usage)
    # Connect to the Raspberry Pi
    ssh_client = paramiko.SSHClient()
    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    ssh_client.connect(
        RASPBERRY_PIS[pi_idx]["ip"],
        username=RASPBERRY_PIS[pi_idx]["username"],
        password=RASPBERRY_PIS[pi_idx]["password"],
    )
    # Execute the command to get RAM utilization (using 'free' command)
    stdin, stdout, stderr = ssh_client.exec_command('free -m | grep "Mem:"')

    # Parse the RAM utilization value from the command output
    output = stdout.read().decode('utf-8')
    print(output)
    memory_info = re.findall(r'\d+', output)
    # The "free" memory value is the third value in the list
    free_memory = int(memory_info[2])
    print(free_memory)
    ssh_client.close()

    return free_memory

# Start memory usage update thread
memory_thread = threading.Thread(target=update_memory_usage)
memory_thread.daemon = True
memory_thread.start()

############################################################################################################
#                                                 Ends                                                     #
############################################################################################################

# Create the server socket
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Bind the server to the specified host and port
server.bind((HOST, PORT))

# Listen for incoming connections (maximum of 5 clients in the queue)
server.listen(5)
print(f"[*] Listening on {HOST}:{PORT}")

# Main server loop
while True:
    client_socket, _ = server.accept()

    # Handle each client in a separate thread
    client_handler = threading.Thread(target=handle_client, args=(client_socket,))
    client_handler.start()
