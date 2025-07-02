# syntax=docker/dockerfile:1
# based on
# https://docs.docker.com/compose/gettingstarted/
# and some housekeeping
ARG BASEIMAGE
FROM ${BASEIMAGE}

COPY data /data

WORKDIR /code
RUN apk add --no-cache gcc musl-dev linux-headers
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt
EXPOSE 5000

CMD ["flask", "run"]