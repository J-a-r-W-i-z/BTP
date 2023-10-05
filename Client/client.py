import socket
import cv2
import numpy as np

# Define server settings
SERVER_HOST = '172.22.3.174'
SERVER_PORT = 8084

# Load the image you want to send
image_path = 'image.jpg'
image = cv2.imread(image_path)

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

image_data = image_data.replace(b"IMAGE_END", b"")

# Decode the received image and display it
if len(image_data) > 0:
    received_image = cv2.imdecode(np.frombuffer(image_data, dtype=np.uint8), cv2.IMREAD_GRAYSCALE)
    cv2.imshow("Received Image", received_image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
else:
    print("Error receiving processed image")

print("Socket closed")
exit()
