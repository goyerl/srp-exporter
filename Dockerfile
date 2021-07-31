FROM python:slim-buster

COPY exporter.py .
COPY requirements.txt .

RUN pip install -r requirements.txt

CMD [ "python3", "exporter.py"]