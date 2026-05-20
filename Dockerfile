FROM python:3.11

WORKDIR /app



COPY . .

EXPOSE 5000

CMD ["python", "app.py"]
