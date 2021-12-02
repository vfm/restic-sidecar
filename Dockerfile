FROM alpine as build
ARG RESTIC_VERSION=0.12.1
RUN wget https://github.com/restic/restic/releases/download/v${RESTIC_VERSION}/restic_${RESTIC_VERSION}_linux_amd64.bz2 -O restic.bz2 \
 && bzip2 -d restic.bz2 \
 && chmod +x restic

FROM python:3-slim as run
COPY --from=build restic /usr/local/bin/restic

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY restic-sidecar.py .

EXPOSE 9000
ENTRYPOINT ["/usr/local/bin/python", "restic-sidecar.py"]