# Use Python as base image
FROM python:3.9

RUN python -m pip install rasa

# Set the working directory inside the container
WORKDIR /app

# Copy only the requirements file first
COPY requirements.txt . 

# Upgrade pip and install necessary system packages
RUN pip install --upgrade pip \
    && pip install --no-cache-dir rasa tensorflow numpy

# Now copy the rest of the project files
COPY . .

# Install the remaining dependencies
RUN pip install --upgrade -r requirements.txt

# Expose Rasa's default API port
EXPOSE 5005

# Start Rasa
CMD ["rasa", "run", "--enable-api", "--cors", "*"]
