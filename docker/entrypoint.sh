#!/bin/sh
set -eu

UID=${UID:-1000}
GID=${GID:-1000}

usermod -o -u "$UID" talked
groupmod -o -g "$GID" talked

exec su talked
