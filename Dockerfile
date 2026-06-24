# Use an official Python runtime as a parent image
FROM python:3.10-slim

# Prevent interactive prompts during apt installations
ENV DEBIAN_FRONTEND=noninteractive

# Install C++ compiler, make, pkg-config, and OpenCV development libraries
RUN apt-get update && apt-get install -y \
    g++ \
    make \
    pkg-config \
    libopencv-dev \
    python3-opencv \
    && rm -rf /var/lib/apt/lists/*

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Compile the C++ CLI Solver for the Linux container environment
RUN make clean && make

# Install any needed Python packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Make port 5001 available to the world outside this container
# (Render/Heroku will override this with their own PORT env variable)
EXPOSE 5001

# Define environment variable
ENV PORT=5001

# Run the application using gunicorn for production
CMD gunicorn --bind 0.0.0.0:$PORT app:app
