# A dagster orchestrator configuration with external metadata store

*Date:* 2025-07-02  
*Author:* MvS  
*keywords:* etl/elt orchestration, dagster, docker-compose

## Description

A docker-compose based dagster stack consisting of daemon, webserver and code store using a
`Makefile` and an `.env` file for convenience and basic security.

## Configuring and running the dagster stack

1. Copy `.env.dist` to `.env` and add postgres DB credentials for metadata storage
2. Using DB management tool of choice: log into postgres instance as administrator. Note: `./compose/host-image/config/database.sql` contains necessary commands to:
    - establish database for dagster meta data storage,
    - create technical user corresponding to credentials in .env file,
3. Run `make run-compose` and let the stack come online.
4. Log into webserver using a webbrowser under [link](http://localhost:3000) to start running dagster jobs.
5. Use <kbd>CTRL</kbd>+<kbd>C</kbd> to shut down the stack
6. Invoke `make clean` to remove the stack

### Manual access to container

Using compose:  
`docker-compose exec <container-name> env SAMPLEPAR="testing" bash`

Using docker:  
`docker exec -it <container-name> bash`
