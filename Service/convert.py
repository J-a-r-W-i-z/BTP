import cv2

def convert_to_bw(input_path, output_path):
    # Read the input image
    image = cv2.imread(input_path)

    if image is None:
        print("Error: Unable to read the image.")
        return

    # Convert the image to grayscale
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Save the black and white image
    cv2.imwrite(output_path, gray_image)

if __name__ == "__main__":
    input_path = "input_image.jpg"  # Replace with the path to your input image
    output_path = "output_image.jpg"  # Replace with the desired output path
    convert_to_bw(input_path, output_path)
    print(f"Image converted to black and white and saved as {output_path}")
