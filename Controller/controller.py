import socket
import threading
import cv2
import numpy as np

# Define server settings
HOST = '0.0.0.0'  # Listen on all available network interfaces
PORT = 8080      # Choose a port for your server

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

        # Convert the received image to black and white
        image_np = np.frombuffer(image_data, dtype=np.uint8)
        image = cv2.imdecode(image_np, cv2.IMREAD_COLOR)
        if image is not None:
            gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            _, img_encoded = cv2.imencode(".png", gray_image)
            client_socket.sendall(img_encoded.tobytes())
        else:
            client_socket.sendall(b"Error processing image")
    else:
        client_socket.sendall(b"Error: Image data not received properly")

    client_socket.close()  # Close the client socket when done

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
