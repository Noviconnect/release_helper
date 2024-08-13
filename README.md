# release_helper docker action

A tool to check related tickets are in a ready state for deployment.

## Inputs

### `github-token`

**Required** release_helper github token.

### `linear-token`

**Required** release_helper linear token.

### `slack-bot-token`

**Required** release_helper slack bot token.

### `slack-channel-name`

**Required** release_helper slack channel name, include the #.

## Outputs

## Example usage

```yaml
- name: release_helper
  uses: Noviconnect/release_helper@v1
  env:
      HELPER_GITHUB_TOKEN: '${{ github.token }}'
      HELPER_LINEAR_TOKEN: '${{ secrets.HELPER_LINEAR_TOKEN }}'
      HELPER_SLACK_BOT_TOKEN: '${{ secrets.SLACK_BOT_TOKEN }}'
      HELPER_SLACK_CHANNEL_NAME: '#production-deploys'
```

## Development Guide

This section provides a comprehensive guide on how to set up and develop the release_helper project.

### Prerequisites

- Docker
- Docker Compose
- Poetry (for local development without Docker)

### Getting Started

1. Clone the repository:
   ```
   git clone https://github.com/Noviconnect/release_helper.git
   cd release_helper
   ```

2. Set up environment variables:
   This is WIP as a practice hasn't been introduced to this repository just yet.

### Building the Project

To build the Docker image for the project, run:

```
./taskfile.sh build
```

This command uses Docker Compose to build the image defined in the `Dockerfile`. It will install all the necessary dependencies and set up the environment for the release_helper.

### Running the Project

To run the release_helper, use the following command:

```
./taskfile.sh run
```

This command starts the Docker container and runs the main.py script. It will process any potential releases, check the status of related tickets, and send notifications as configured.

### Additional Development Tasks

The `taskfile.sh` script provides several other useful commands for development:

- `./taskfile.sh clean`: Removes the `.cache` directory.
- `./taskfile.sh install`: Installs project dependencies using Poetry (for local development).
- `./taskfile.sh generate-linear-client`: Generates the Linear API client using ariadne-codegen.

### Local Development

If you prefer to develop without Docker:

1. Install Poetry: https://python-poetry.org/docs/#installation
2. Install dependencies: `poetry install`
3. Activate the virtual environment: `poetry shell`
4. Run the script: `python main.py`

### Updating the Linear API Client

If you need to update the Linear API client:

1. Modify the GraphQL schema or queries in `release_helper/issue_management/linear/queries.graphql`
2. Run `./taskfile.sh generate-linear-client`
3. The updated client will be generated in `release_helper/issue_management/linear/graphql_client/`

### Testing

Currently, there are no specific test commands defined in the taskfile. It's recommended to add unit tests and integration tests to ensure the reliability of the release_helper.

### Linting and Formatting

The project uses Ruff for linting and formatting. The configuration can be found in `ruff.toml`. To run linting and formatting:

1. Install Ruff: `pip install ruff`
2. Run linter: `ruff check .`
3. Run formatter: `ruff format .`
