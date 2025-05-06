# Start with a base image (Python is commonly used for API applications)
FROM python:3.11-slim

# Set working directory in the container
WORKDIR /app

# Copy requirements file and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of your application code
COPY . .

# Set environment variables if needed
ENV PORT=8080

# Command to run your application
CMD ["sh", "-c", "hyrex init-db && hyrex run-worker hyrex_app:app"]
