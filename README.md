# release_helper docker action

A tool to check related tickets are in a ready state for deployment.

## Inputs

### `github-token`

**Required** release_helper github token. Default `"NOT_SET"`.

### `repository`

**Required** release_helper repository. Default `"NOT_SET"`.

### `linear-token`

**Required** release_helper linear token. Default `"NOT_SET"`.

### `slack-bot-token`

**Required** release_helper slack bot token. Default `"NOT_SET"`.


## Outputs



## Example usage

```yaml
uses: Noviconnect/release_helper@main
with:
  github-token: '<your token>'
  repository: '<repo>'
  linear-token: '<your token>'
  slack-bot-token: '<your token>'
```
