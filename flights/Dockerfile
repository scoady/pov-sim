# Use the official Python 3.8 image as the base image
FROM python:3.8-slim-buster

# Set the working directory inside the container
WORKDIR /python-docker

# Copy the requirements file into the container
COPY requirements.txt requirements.txt

# Install the required dependencies
RUN pip3 install -r requirements.txt

# Bootstrap OpenTelemetry auto-instrumentation
RUN opentelemetry-bootstrap -a install

# Copy the rest of your application code into the container
COPY . .

# Expose port 5001
EXPOSE 5001


# Specify the command to run your Flask app with OpenTelemetry instrumentation
CMD ["opentelemetry-instrument", "python3", "-m", "flask", "run", "--host=0.0.0.0", "--port=5001"]
