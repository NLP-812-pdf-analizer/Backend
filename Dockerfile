FROM python:3.12-slim

#RUN apt-get update && apt-get install -y python3-dev

WORKDIR /app

COPY ./requirements.txt /app/requirements.txt

RUN pip install --upgrade pip

RUN pip install --no-cache-dir -r /app/requirements.txt

COPY . /app

CMD ["python3", "web_app.py"]