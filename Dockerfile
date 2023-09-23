FROM python:3.10

WORKDIR /app
COPY requirements.txt .
COPY . .

RUN pip install --upgrade pip \
    &&  pip install -r requirements.txt

CMD ["python3", "-m", "bot"]