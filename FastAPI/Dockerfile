FROM ubuntu:latest

RUN apt update

RUN apt install -y python3 python3-pip 

COPY ./main.py /

COPY ./requirements.txt /

RUN python3 -m pip install -r requirements.txt

RUN python3 -m pip install ../python-client

CMD ["uvicorn", "--host=0.0.0.0", "--port=8001", "main:app"]