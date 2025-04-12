
FROM python:3.11-slim

WORKDIR /app
COPY . /app

RUN pip install pdm && pdm install

CMD ["pdm", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
