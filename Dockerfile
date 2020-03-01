FROM python:3.7
LABEL maintainer="Abhilash K R"

WORKDIR /app

COPY requirements.txt /app
ADD app /app/app
COPY config.py /app
COPY run.py /app

RUN pip install -r requirements.txt
EXPOSE 5000
RUN sleep 5
CMD python run.py