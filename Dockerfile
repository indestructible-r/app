FROM python:3.11-slim

WORKDIR /app

RUN pip install --no-cache-dir uv

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV PYTHONPATH=/app
ENV CONFIG_PATH=/app/config.docker.yaml

EXPOSE 8000

CMD ["python", "-m", "app.main"]