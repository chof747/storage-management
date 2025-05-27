#!/bin/sh

BASEDIR=$(dirname "$0")
source ${BASEDIR}/../.env

GREEN='\033[0;32m'
NC='\033[0m' # No Color

PREFIX="sqlite:///"
DATABASE_PATH="${BASEDIR}/../${DATABASE_URL#$PREFIX}"
MIG_DATABASE_PATH=$(dirname "${DATABASE_PATH}")"/migtest.db"

cp $DATABASE_PATH $MIG_DATABASE_PATH

echo "Starting Migration ..."
alembic upgrade head && \
echo "${GREEN}Upgrade successfull${NC}, running downgrade ...\n" \
alembic downgrade -1 && \
echo "${GREEN}Downgrade also successful, Migration Complete!${NC}" 

mv $MIG_DATABASE_PATH $DATABASE_PATH
