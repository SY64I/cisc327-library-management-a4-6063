FROM python:3.12-slim

WORKDIR cisc327-library-management-a2-6063

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . .

EXPOSE 5000

CMD ["python", "app.py"]