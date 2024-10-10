FROM ubuntu

COPY src /opt/app/src/

COPY requirements.txt /opt/app

WORKDIR /opt/app/src

RUN mkdir /opt/app/src/data

RUN apt update

RUN apt upgrade -y

RUN apt install python3 -y

RUN apt install python3-pip -y

RUN apt install python3.12-venv -y

RUN python3 -m venv venv

RUN venv/bin/python -m pip install -r /opt/app/requirements.txt

CMD [ "venv/bin/python", "-m" , "flask", "run", "--host=0.0.0.0", "--port=5000"]