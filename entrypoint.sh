#!/usr/bin/env bash

# env var check
[ -z "$HELPER_GITHUB_TOKEN" ] && echo "Missing required env var 'HELPER_GITHUB_TOKEN'" && exit 1
[ -z "$HELPER_REPOSITORY" ] && echo "Missing required env var 'HELPER_REPOSITORY'" && exit 1
[ -z "$HELPER_LINEAR_TOKEN" ] && echo "Missing required env var 'HELPER_LINEAR_TOKEN'" && exit 1
[ -z "$HELPER_SLACK_BOT_TOKEN" ] && echo "Missing required env var 'HELPER_SLACK_BOT_TOKEN'" && exit 1

python /release_helper/main.py
