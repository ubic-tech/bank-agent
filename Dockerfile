FROM python:3.8

ARG wdir=/usr/src/app

WORKDIR $wdir

COPY . $wdir

RUN pip install -r $wdir/requirements.txt

ENTRYPOINT ["uvicorn"]