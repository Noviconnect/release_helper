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

# Function to log messages to stderr
function log() {
  echo -e "$@" >&2
}

# Function to handle errors
function _error() {
  local exit_code=$1
  local line_number=$2

  log "****** Failed ******"
  if [ "$exit_code" != "0" ]; then
    log "Exit code $exit_code occurred on line number $line_number"
  fi
}
# Trap ERR signal and call the _error function
trap '_error $? $LINENO' ERR

# Function to log script completion
function _finish() {
  log "-- $0 completed --"
}
# Trap EXIT signal and call the _finish function
trap _finish EXIT

function update-graphql-schema() {
  local url="https://raw.githubusercontent.com/linear/linear/master/packages/sdk/src/schema.graphql"
  local OUTPUT_FILE="src/release_helper/issue_management/linear/schema.graphql"
  curl -L "$url" -o "$OUTPUT_FILE"
}

function generate-linear-client() {
  ariadne-codegen --config src/release_helper/issue_management/linear/graphql_generator.toml client
}

function run() {
  cd src
  poetry run python -m release_helper.main
}

function help() {
  log "$0 <task> <args>"
  log "Tasks:"
  compgen -A function | grep -v '^_' | cat
}

TIMEFORMAT="Task completed in %3lR"
time "${@:-help}"
