FROM python:3.7.8-alpine3.12

COPY . /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 5000

WORKDIR /usr/src/app

CMD ["python", "init_webservice.py"]