# Dockerfile

FROM python:3.14-slim AS builder
  
# Install build tooling required for C-extension dependencies.
RUN apt-get update \
  && apt-get install -y --no-install-recommends build-essential \
  && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pdm

WORKDIR /app

COPY ./pyproject.toml ./pdm.lock ./
RUN pdm install --no-editable --no-self --prod

COPY . .
RUN pdm install --prod \
  && rm -rf /root/.cache


FROM python:3.14-slim AS runtime

RUN apt-get update \
  && apt-get install -y --no-install-recommends libpq5 \
  && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pdm

WORKDIR /app

COPY --from=builder /app /app

# Expose the port Uvicorn will run on.
EXPOSE 8000

COPY ./docker/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh
ENTRYPOINT ["/entrypoint.sh"]
