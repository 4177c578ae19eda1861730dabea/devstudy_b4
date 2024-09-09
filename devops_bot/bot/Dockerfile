FROM python:3.9-slim
WORKDIR /app
COPY . .
RUN apt update && apt-get install -y libpq-dev gcc
RUN pip install psycopg2 paramiko python-dotenv python-telegram-bot==13.7
CMD ["python", "app.py"]
