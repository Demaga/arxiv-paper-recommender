FROM python:3.11

WORKDIR /app

COPY requirements.txt /app/requirements.txt

RUN pip install -r requirements.txt

ADD main.py /app/main.py


CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "3000", "--reload"]
