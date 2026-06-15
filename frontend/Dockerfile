FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

COPY ./frontend /app

ENV BACKEND_URL=http://backend:8000

CMD ["streamlit", "run", "app.py", "--server.port", "3000", "--server.address", "0.0.0.0", "--server.headless", "true"]
