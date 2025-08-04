FROM pytorch/pytorch:2.3.0-cuda12.1-cudnn8-runtime


#RUN apt-get update && apt-get install -y python3-dev

WORKDIR /app


COPY ./requirements.txt /app/requirements.txt

RUN pip install --upgrade pip

RUN pip install --no-cache-dir -r /app/requirements.txt

COPY . /app

CMD ["python", "web_app.py"]