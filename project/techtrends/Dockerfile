FROM python:3.8

WORKDIR /app

ADD / ./

RUN pip3 install -r requirements.txt
RUN python3 init_db.py

COPY . .

CMD [ "python3", "app.py"]
