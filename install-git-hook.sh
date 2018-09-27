#!/usr/bin/env bash

VERSION="1.2.1"
BIN_DIRECTORY=$(dirname $(which git))
BIN_PATH="$BIN_DIRECTORY/git-secrets"
DOWNLOAD_URL="https://raw.githubusercontent.com/awslabs/git-secrets/$VERSION/git-secrets"

if [ ! -f $BIN_PATH ]; then
    echo "Installing git-secrets v.$VERSION to $BIN_PATH from $DOWNLOAD_URL"
    wget $DOWNLOAD_URL -O $BIN_PATH
    RETCODE=$?
    if [ "$RETCODE" -ne "0" ]; then
        echo "Please run this script in privileged mode"
        exit 1
    fi
    chmod a+x $BIN_PATH
else
    echo "git-secrets script already exists: $BIN_PATH"
fi

DIR=$(dirname "$(readlink -f "$0")")
echo "Working in directory $DIR"

echo "Flushing git-secrets configuration"
git config --remove-section secrets || true

cat "$DIR/.gitforbidden" | while read line
do
    if [[ ! "$line" =~ ^#.* ]]; then
        echo "Adding forbidden regex pattern: $line"
        git secrets --add "$line"
    fi
done

cat "$DIR/.gitwhitelisted" | while read line
do
    if [[ ! "$line" =~ ^#.* ]]; then
        echo "Adding allowed regex pattern: $line"
        git secrets --add -a "$line"
    fi
done

echo "Adding aws patterns"
git secrets --register-aws

echo "Registering hook"
git secrets --install -f

echo "Git secrets have been configured"
echo "Configuration: "
git secrets --list

echo "Allowing reset git hooks without privileged mode"
chmod a+rw .git/hooks/commit-msg
chmod a+rw .git/hooks/pre-commit
chmod a+rw .git/hooks/prepare-commit-msg

if [ ! -z $USER ]; then
    echo "Thank you for using pre-commit hooks, $USER"
fi