# Use an official Python runtime as a parent image
FROM python:3.8

# Set the working directory in the container
WORKDIR /app

# Install system libraries (libgl1-mesa-glx is needed for OpenGL)
RUN apt-get update && apt-get install -y libgl1-mesa-glx

# Copy the requirements file into the container
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
RUN pip install -r requirements.txt -v

# Copy the Python script into the container
COPY convert.py .

# Define an environment variable for the input image path
ENV INPUT_IMAGE /app/input_image.jpg

# Define an environment variable for the output image path
ENV OUTPUT_IMAGE /app/output_image.jpg

# Run the Python script when the container launches
CMD ["python", "convert.py"]
