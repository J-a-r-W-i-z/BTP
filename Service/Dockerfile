# Use an official Python image for ARM as the base image
FROM sgtwilko/rpi-raspbian-opencv

# Set the working directory in the container
WORKDIR /app

# Copy the Python script into the container
COPY convert.py .

# Define an environment variable for the input image path (you can modify this)
ENV INPUT_IMAGE /app/input_image.jpg

# Define an environment variable for the output image path (you can modify this)
ENV OUTPUT_IMAGE /app/output_image.jpg

# Run the Python script when the container launches
CMD ["python", "convert.py"]