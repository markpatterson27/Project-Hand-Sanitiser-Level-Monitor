FROM mcr.microsoft.com/mssql/server:2019-latest

# Create a config directory
RUN mkdir -p /usr/config
WORKDIR /usr/config

# copy config files
COPY . /usr/config

# Grant permissions for our scripts to be executable. Need to be root user to perform permission change.
USER root
RUN chmod +x /usr/config/entrypoint.sh
RUN chmod +x /usr/config/configure-db.sh
USER mssql

ENTRYPOINT ["./entrypoint.sh"]