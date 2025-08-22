# Dockerfile

# Use official Python image
FROM python:3.11-slim

# Install PDM and dependencies
RUN pip install pdm


# Set working directory
WORKDIR /app

# Copy app
COPY ./pyproject.toml ./pdm.lock ./
RUN pdm install --no-editable --no-self --prod

COPY . .
RUN pdm install --prod \
  && rm -rf /root/.cache

# Expose the port Uvicorn will run on
EXPOSE 8000


COPY ./docker/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh
ENTRYPOINT ["/entrypoint.sh"]