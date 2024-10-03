FROM python:3.12-slim

WORKDIR /app

COPY . /app

RUN pip install --no-cache-dir -r requirements.txt --proxy=http://192.168.100.210:3128

EXPOSE 5000

CMD ["python", "-m", "flask", "--app", "server", "run", "--host", "0.0.0.0", "--port", "9300"]