#!/usr/bin/env bash

VERSION="1.2.1"
BIN_DIRECTORY=$(dirname $(which git))
BIN_PATH="$BIN_DIRECTORY/git-secrets"
DOWNLOAD_URL="https://raw.githubusercontent.com/awslabs/git-secrets/$VERSION/git-secrets"

DIR=$(dirname "$(readlink -f "$0")")
echo "Working in directory $DIR"

if [ ! -f $BIN_PATH ]; then
    echo "Installing git-secrets v.$VERSION to $BIN_PATH from $DOWNLOAD_URL"
    wget $DOWNLOAD_URL -O $BIN_PATH
    chmod a+x $BIN_PATH
else
    echo "git-secrets script already exists: $BIN_PATH"
fi

echo "Flushing git-secrets configuration"
git config --remove-section secrets || true

cat "$DIR/.gitforbidden" | while read line
do
   echo "Adding regex pattern: $line"
   git secrets --add "$line"
done

if [ -f "$DIR/.gitallowed" ]; then
    echo "Using whitelisted instructions from $DIR/.gitallowed"
fi

echo "Adding aws patterns"
git secrets --register-aws

echo "Registering hook"
git secrets --install -f

echo "Git secrets have been configured"
echo "Configuration: "
git secrets --list

if [ ! -z $USER ]; then
    echo "Thank you for using pre-commit hooks, $USER"
fi