#!/bin/sh

USER=test
PASSWORD=test
echo "Creating user ${USER}"
adduser -D ${USER} && echo "${USER}:${PASSWORD}" | chpasswd
echo "Fixing permissions for user ${USER}"
chown -R ${USER}:${USER} /home/${USER}
exec "$@"
