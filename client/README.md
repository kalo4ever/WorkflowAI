# WorkflowAI Client

A Next.js application that serves as a UI client for [WorkflowAI](https://workflowai.com).

## Setup

### Prerequisites

- Node.js 18+
- Yarn 4+ (the version is frozen in this project so you just need a version of yarn that understands the .yarn/releases directory)
- An API instance. See [workflowai-api](https://github.com/WorkflowAI/workflowai-api) on how to build your own
- A [Clerk](clerk.com) project setup for authentication, and the publishable and secret key

### Getting started

The [.env.sample](.env.sample) file contains examples of the environment variables you will need to set.

```sh
# Install dependencies, project uses yarn 4
yarn install

# Copy the sample file
cp .env.sample .env
# - You might need to override NEXT_PUBLIC_WORKFLOWAI_API_URL to point to your API instance
#   if you don't have one running locally
# - set NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY and CLERK_SECRET_KEY from your Clerk project

# Run the client in development mode
yarn dev
```

> A docker-compose.yml file is provided to allow running in a containerized environment.
> `docker-compose build && docker-compose up app` will build the client and start it.

## Structure

The project is a basic Next.js application setup with the app router.

### Authentication

Although all user management is deferred to Clerk, this project re-signs a JWT before
interacting with the API.

For production, an ECDSA key should be generated and set as the `WORKFLOWAI_API_SIGN_KEY` env var.

```sh
# Generate an ECDSA key, encode and copy it
openssl ecparam -genkey -name prime256v1 -noout | openssl pkcs8 -topk8 -nocrypt | base64 | pbcopy
```

<!-- TODO: add documetation about bypassing auth -->
