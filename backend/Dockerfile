# Dockerfile

# Use official Python image
FROM python:3.11-slim

# Install PDM and dependencies
RUN pip install pdm


# Set working directory
WORKDIR /app

# Copy app
COPY ./pyproject.toml ./pdm.lock ./
RUN pdm install --no-editable --no-self

COPY . .
RUN pdm install --prod \
  && rm -rf /root/.cache

# Expose the port Uvicorn will run on
EXPOSE 8000

# Command to run the app with hot reload disabled (for production)
CMD ["pdm", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
