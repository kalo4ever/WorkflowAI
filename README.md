# Workflow AI

## Usage

### Quick start

The docker compose file is provided as a quick way to spin up a local instance of WorkflowAI.
It is configured to be self contained viable from the start.

```
cp .env.sample .env
docker-compose build && docker-compose up
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

### Setting up providers

This project supports a variety of LLM providers.

Each provider has a different set of credentials and configuration. Providers that have the required environment
variables are loaded by default (see the [sample env](.env.sample) for the available variables). Providers can
also be configured per tenant through the UI.
