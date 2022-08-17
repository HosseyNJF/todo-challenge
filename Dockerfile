FROM python:3.10

RUN mkdir /opt/app
WORKDIR /opt/app

COPY requirements.txt setup.py ./
RUN pip install -U pip
RUN pip install -r requirements.txt
RUN pip install -e .

COPY todo todo/
COPY migrations migrations/

EXPOSE 5000

CMD gunicorn -b 0.0.0.0:5000 todo.wsgi:app