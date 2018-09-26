#!/usr/bin/env bash

VERSION="1.2.1"
BIN_PATH="/usr/bin/git-secrets"
DOWNLOAD_URL="https://raw.githubusercontent.com/awslabs/git-secrets/$VERSION/git-secrets"


DIR=$(dirname "$(readlink -f "$0")")
echo "Working in directory $DIR"
git config --remove-section secrets || true

echo "Installing git-secrets v.$VERSION"
wget $DOWNLOAD_URL -O $BIN_PATH
chmod a+x /usr/bin/git-secrets

cat "$DIR/.gitforbidden" | while read line
do
   echo "Adding regex pattern: $line"
   git secrets --add "$line"
done

echo "Adding aws patterns"
git secrets --register-aws

echo "Registering hook"
git secrets --install -f

echo "Git secrets have been configured"
