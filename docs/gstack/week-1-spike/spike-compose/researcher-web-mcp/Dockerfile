FROM python:3.12-slim

WORKDIR /app

RUN pip install --no-cache-dir 'mcp>=1.2.0' 'httpx>=0.27'

COPY server.py /app/server.py

EXPOSE 8000

CMD ["python", "/app/server.py"]
