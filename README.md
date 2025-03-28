# Workflow AI

## Usage

### Quick start

The docker compose file is provided as a quick way to spin up a local instance of WorkflowAI.
It is configured to be self contained viable from the start.

```sh
# Create a base environment file that will be used by the docker compose
# You should likely update the .env file to include some provider keys
cp .env.sample .env
# Build the client and api docker image
# By default the docker compose builds development images, see the `target` keys
docker-compose build
# [Optional] Start the dependencies in the background, this way we can shut down the app while
# keeping the dependencies running
docker-compose up -d clickhouse azurite redis mongo
# Start the docker images
docker-compose up
# The WorkflowAI api is also a WorkflowAI user
# Since all the agents the api uses are hosted in WorkflowAI
# So you'll need to create a Workflow AI api key
# Open http://localhost:3000/organization/settings/api-keys and create an api key
# Then update the WORKFLOWAI_API_KEY in your .env file
open http://localhost:3000/organization/settings/api-keys
# The kill the containers (ctrl c) and restart them
docker-compose up
```

> Although it is configured for local development via hot reloads and volumes, Docker introduces significant
> latencies for development. Detailed setup for both the [client](./client/README.md) and [api](./api/README.md)
> are provided in their respective READMEs.

### Structure

#### API

The [api](./api/README.md) provides is the python backend for WorkflowAI. It is structured
as a [FastAPI](https://fastapi.tiangolo.com/) server and
a [TaskIQ](https://github.com/taskiq-python/taskiq) based worker.

#### Client

The [client](./client/README.md) is a NextJS app that serves as a frontend

#### Dependencies

- **MongoDB**: we use [MongoDB](https://www.mongodb.com/) to store all the internal data
- **Clickhouse**: [Clickhouse](https://clickhouse.com/) is used to store the run data. We
  first stored the run data in Mongo but it quickly got out of hand with storage costs
  and query duration.
- **Redis**: We use Redis as a broker for messages for taskiq. TaskIQ supports a number
  of different message broker.
- **Azure Blob Storage** is used to store files.

<!-- TODO: switch to S3 when  -->

### Setting up providers

This project supports a variety of LLM providers.

Each provider has a different set of credentials and configuration. Providers that have the required environment
variables are loaded by default (see the [sample env](.env.sample) for the available variables). Providers can
also be configured per tenant through the UI.
