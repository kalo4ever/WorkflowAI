![header](/assets/readme-header.png)

WorkflowAI is an open-source platform where product and engineering teams collaborate to build and iterate on AI features.

[![License: Apache 2.0](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)

## Demo

[embed video]

## Key Features

- build AI features in a few minutes, no code required.
- use SDK when you need.
- playground where you can compare models side-by-side.
- model agnostic, use any LLM you want.
- open-source, you can host it on your own infrastructure.
- observability, automatically logs all the runs.
- structured outputs, no more parsing JSON.
- Easy integration with SDKs for Python, Typescript and a REST API.
- update prompts and models without deploying new code.
- provider fallback
- built-in tools (web search, scraping)

## Deploy WorkflowAI

### WorkflowAI Cloud

100% managed, no infrastructure to setup. Free, no markup on LLM calls... SOC2 compliant and running on a [high-availability infrastructure](https://docs.workflowai.com/workflowai-cloud/reliability). No training on your data, ever.

### Self-hosted

### Quick start

The Docker Compose file is provided as a quick way to spin up a local instance of WorkflowAI.
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
docker-compose up -d clickhouse minio redis mongo
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

> For now, we rely on public read access to the storage in the frontend. The URLs are not discoverable though so it should be ok until we implement temporary leases for files.
> On minio that's possible with the following commands

```sh
# Run sh inside the running minio container
docker-compose exec minio sh
# Create an alias for the bucket
mc anonymous set download myminio/workflowai-task-runs
# Set download permissions
mc alias set myminio http://minio:9000 minio miniosecret
```

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
- **Minio** is used to store files but any _S3 compatible storage_ will do. We also have a plugin for _Azure Blob Storage_.
  The selected storage depends on the `WORKFLOWAI_STORAGE_CONNECTION_STRING` env variable. A variable starting with
  `s3://` will result in the S3 storage being used.

### Setting up providers

This project supports a variety of LLM providers.

Each provider has a different set of credentials and configuration. Providers that have the required environment
variables are loaded by default (see the [sample env](.env.sample) for the available variables). Providers can
also be configured per tenant through the UI.


## Support

To find answers to your questions, please refer to the [Documentation](https://docs.workflowai.com).

## License

WorkflowAI is licensed under the [Apache 2.0 License](./LICENSE).
