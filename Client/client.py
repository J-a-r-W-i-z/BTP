import socket
import cv2
import numpy as np

# Define server settings
SERVER_HOST = '10.147.212.32'
SERVER_PORT = 8080

# Load the image you want to send
image_path = 'image.jpg'
image = cv2.imread(image_path)

# Check if the image is loaded successfully
if image is None:
    print(f"Error: Unable to load the image from {image_path}")
else:
    # Encode the image as a JPEG
    _, img_encoded = cv2.imencode(".jpg", image)

    # Create a socket to connect to the server
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((SERVER_HOST, SERVER_PORT))

    # Send the image data to the server with a custom termination sequence
    CHUNK_SIZE = 1024
    for i in range(0, len(img_encoded), CHUNK_SIZE):
        chunk = img_encoded[i:i + CHUNK_SIZE]
        client_socket.sendall(chunk)
    
    # Send the termination sequence to indicate the end of the image data
    client_socket.sendall(b"IMAGE_END")

    # Receive the processed image data from the server
    response = b""
    while True:
        chunk = client_socket.recv(1024)
        if not chunk:
            break
        response += chunk

    # Decode the received image and display it
    if len(response) > 0:
        received_image = cv2.imdecode(np.frombuffer(response, dtype=np.uint8), cv2.IMREAD_GRAYSCALE)
        cv2.imshow("Received Image", received_image)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
    else:
        print("Error receiving processed image")

    # Close the client socket
    client_socket.close()
