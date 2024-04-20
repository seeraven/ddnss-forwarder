ARG PYTHON_VERSION
FROM python:${PYTHON_VERSION}

ADD . /ddnss-forwarder
WORKDIR /ddnss-forwarder

RUN make system-setup-prod

WORKDIR /ddnss-forwarder/src
ENTRYPOINT [ "/usr/local/bin/python3", "/ddnss-forwarder/src/ddnss_forwarder.py"]
