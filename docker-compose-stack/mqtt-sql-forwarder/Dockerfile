FROM python:3.8-alpine

# add packages needed to install msodbcsql drives and to build pyodbc
RUN apk update \
    && apk add curl sudo build-base unixodbc-dev unixodbc \
    && rm -rf /var/cache/apk/*

#Download and install msodbcsql driver
RUN curl -O https://download.microsoft.com/download/e/4/e/e4e67866-dffd-428c-aac7-8d28ddafb39b/msodbcsql17_17.6.1.1-1_amd64.apk \
    && sudo apk add --allow-untrusted msodbcsql17_17.6.1.1-1_amd64.apk

COPY . /app
WORKDIR /app
RUN pip install -r requirements.txt

CMD ["python3", "-u", "mqtt_sql_forwarder.py"]
