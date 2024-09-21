FROM python:3.12-slim-bookworm

RUN useradd --create-home fuyltower 
USER fuyltower

WORKDIR /fuyltower_status
COPY app.py app.py
COPY templates templates

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

CMD [ "python3", "-m" , "flask", "run", "--host=0.0.0.0"]