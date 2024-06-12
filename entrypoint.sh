#!/usr/bin/env bash

# Exit immediately if a command exits with a non-zero status
set -o errexit
# Ensure that ERR traps are inherited by functions, command substitutions, and subshell environments
set -o errtrace
# Treat unset variables as an error when substituting
set -o nounset
# Consider a pipeline to fail if any of the commands fail
set -o pipefail
# Print shell input lines as they are read
#set -o verbose
# Print commands and their arguments as they are executed
#set -o xtrace

export PYTHONPATH=/app

cd /app
python main.py
