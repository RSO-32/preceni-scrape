# Base image
FROM python:3.12-alpine

# Set the working directory
WORKDIR /app

# Copy files to the working directory
COPY . .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Run python app
CMD ["python", "scrape.py"]
