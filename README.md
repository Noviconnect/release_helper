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
      HELPER_SLACK_BOT_TOKEN: '${{ secrets.HELPER_SLACK_BOT_TOKEN }}'
      HELPER_SLACK_CHANNEL_NAME: '#production-deploys'
```
