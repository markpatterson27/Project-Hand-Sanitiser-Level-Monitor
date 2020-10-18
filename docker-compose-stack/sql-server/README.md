# Docker SQL Server

Docker container for running SQL Server.

## Files

| File | Description |
| --- | --- |
| configure-db.sh | bash script waits for sql server to start, then runs setup .sql files |
| create-database.sql | setup .sql file that creates the database |
| Dockerfile | Dockerfile to build container |
| entrypoint.sh | bash script that replaces default entrypoint.sh. script calls configure-db.sh and starts sql server |

<br />

## References

- https://hub.docker.com/_/microsoft-mssql-server
- https://github.com/microsoft/mssql-docker/tree/master/linux/preview/examples/mssql-customize
