FROM python:3-slim

WORKDIR /app

COPY . .
RUN pip3 install -r requirements.txt

CMD ["python3", "-u", "/app/bot.py"]
