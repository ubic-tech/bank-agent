FROM python:3.8

ARG wdir=/usr/src/app

WORKDIR $wdir

COPY . $wdir
ENV MONGO_HOST localhost
ENV MONGO_PORT 27017
ENV BANK_UUID 111aaaaa-1af0-489e-b761-d40344c12e70
RUN pip install -r $wdir/requirements.txt

CMD ["uvicorn", "main::app", "--host", "0.0.0.0", "--port", "8081"]