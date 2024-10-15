# Release Helper Action

This repository contains a GitHub Action that runs a Python script called `release_helper`.

This GitHub Action is designed to automate the validation process of issues linked to a GitHub release. It ensures that all Linear tickets mentioned in the release notes are in a "completed" status before the release is marked as non-draft. If any tickets are not in a completed state, the action sends a Slack notification to the responsible users, prompting them to take action.

## Usage

To use this action in your repository:

```yaml
jobs:
  run-release-helper:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run Release Helper
        uses: noviconnect/release-helper-action@v1
        with:
          github-token: "some-value"
          linear-token: "some-value"
          slack-bot-token: "some-value"
          slack-channel-name: "some-value"

```

## Inputs

- **`arg1`**: The first argument passed to the `release_helper.py` script.

## Outputs

This action does not produce any outputs.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

# Development

1. Install Poetry: https://python-poetry.org/docs/#installation
2. Install dependencies: `poetry install`
3. Activate the virtual environment: `poetry shell`

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

## Detailed Description

### Overview

This GitHub Action operates as a composite action written in Python. It follows a sequence of steps to validate the status of Linear issues associated with a GitHub release. The action uses the following workflow:

1. **Set Up Python Environment**: The action begins by setting up a Python environment suitable for executing the script.

2. **Fetch the Latest GitHub Release**: The script retrieves the most recent GitHub release and extracts the release notes. These notes were originally drafted by a separate GitHub Action called "release drafter."

3. **Scan for Linear Ticket References**: The release notes are scanned for references to Linear tickets using a regular expression pattern. The pattern matches tickets in the form of a few letters, a dash, and a few numerical digits (e.g., `ABC-123`).

4. **Query Linear API for Issue Status**: For each identified Linear ticket, the script queries the Linear GraphQL API to retrieve the issue's status and associated team.

5. **Check for Completed Status**: Linear tickets have various status types, such as "completed," "in-progress," etc. The script verifies if all identified issues are in a "completed" status type. Examples of completed statuses include "Deployed," "Ready to Deploy," and "Done."

6. **Determine Next Steps**:
   - If **all issues** are in a completed state, the script marks the GitHub release as non-draft. This triggers another GitHub Action to deploy the release to production.
   - If **any issue** is not in a completed state, the script compiles a list of these issues and sends a notification to a Slack channel. The Slack message includes the issue details and mentions the responsible users. The users are identified by querying the Slack API using the email address associated with the Linear issue.

### Updating the Linear API Client

If you need to update the Linear API client:

1. Modify the GraphQL schema or queries in `release_helper/issue_management/linear/queries.graphql`
2. Run `./taskfile.sh generate-linear-client`
3. The updated client will be generated in `release_helper/issue_management/linear/graphql_client/`

### Testing

Currently, there are no specific test commands defined in the taskfile. It's recommended to add unit tests and integration tests to ensure the reliability of the release_helper.

### Linting and Formatting

The project uses Ruff for linting and formatting. The configuration can be found in `ruff.toml`. To run linting and formatting:

1. Activate the virtual environment: `poetry shell`
2. Install Ruff: `pip install ruff`
3. Run linter: `ruff check .`
4. Run formatter: `ruff format .`
