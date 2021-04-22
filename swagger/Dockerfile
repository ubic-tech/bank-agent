FROM python:3.8

ARG filename
ARG wdir=/usr/src/app

WORKDIR $wdir

COPY requirements.txt $wdir
RUN pip install -r $wdir/requirements.txt

COPY $filename.py $wdir
ENV FILENAME ${filename}
CMD exec uvicorn $FILENAME:app --host 0.0.0.0 --port 8000
