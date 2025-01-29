# Use Python as base image
FROM python:3.8

# Set the working directory inside the container
WORKDIR /app

# Copy the project files
COPY . .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose Rasa's default API port
EXPOSE 5005

# Start Rasa
CMD ["rasa", "run", "--enable-api", "--cors", "*"]
