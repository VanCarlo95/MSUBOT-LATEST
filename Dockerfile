# FROM python:3.9-slim

# RUN apt-get update \
#     && apt-get install -y --no-install-recommends install \
#         build-essential \
#         curl \
#         git \
#         jq \
#         gcc \
#         libpq-dev \

# WORKDIR /app

# RUN pip install --no-cache-dir --upgrade pip

# RUN pip install rasa 3.6.20

# ADD config.yml /app/config.yml
# ADD domain.yml /app/domain.yml
# ADD credentials.yml /app/credentials.yml
# ADD endpoints.yml /app/endpoints.yml

# Use the official Rasa image as the base image
FROM rasa/rasa:3.6.20

# Set the working directory
WORKDIR /app

# Copy the Rasa project files into the container
COPY . /app

# Install additional Python dependencies (if any)
RUN pip install --no-cache-dir -r requirements.txt

# Train the Rasa model
RUN rasa train

# Expose the port Rasa will run on
EXPOSE 5005

# Set the command to run the Rasa server
CMD ["run", "--enable-api", "--cors", "*"]