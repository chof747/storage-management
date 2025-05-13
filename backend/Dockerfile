# Dockerfile

# Use official Python image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy app
COPY . .

# Install PDM and dependencies
RUN pip install pdm \
  && pdm install --prod \
  && rm -rf /root/.cache

# Expose the port Uvicorn will run on
EXPOSE 8000

# Command to run the app with hot reload disabled (for production)
CMD ["pdm", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
