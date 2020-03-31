FROM python:3.7-stretch

RUN useradd -ms /bin/bash gather

WORKDIR /home/gather

COPY requirements.txt requirements.txt
RUN python -m venv venv
RUN venv/bin/pip install -r requirements.txt

COPY app app
COPY gather.py .

RUN chown -R gather:gather ./
USER gather

EXPOSE 5000
ENTRYPOINT ["./venv/bin/python", "gather.py"]
