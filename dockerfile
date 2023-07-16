# Use an official Python runtime as the base image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements.txt file to the container
COPY requirements.txt .

# Install the project dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the .env file to the container
COPY .env .

# Copy the entire project directory to the container
COPY . .

# Run the Python project
CMD ["python3", "-u", "main.py"]