FROM python:3.12-slim

WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Create a non-root user and switch to it
RUN useradd -m appuser
USER appuser

# Set environment variables for Azure App Service
ENV HOST=0.0.0.0
ENV PORT=80
ENV WEBSITES_PORT=80
ENV WEBSITE_SITE_NAME=ai-content-creator-app
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Make sure the app binds to port 80
EXPOSE 80

# Set startup command
CMD ["python", "server.py"] 