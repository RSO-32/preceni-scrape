# Base image
FROM python:3.12-alpine

# Set the working directory
WORKDIR /app

# Copy files to the working directory
COPY . .

# Install required packages
RUN apk add gcc python3-dev musl-dev linux-headers

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# For production, install Gunicorn
RUN pip install gunicorn

# Expose the Flask application port
EXPOSE 5000

# Run the Flask application using Gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:5004", "app:app"]