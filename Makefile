# This file is licensed under the Affero General Public License version 3 or
# later. See the LICENSE file.

# Dev env management
dev-setup:
	poetry install

dev-build:
	docker build docker -f docker/Dockerfile.dev -t talked

dev-run: dev-build
	docker run --rm -it -v "$(pwd):/home/talked/talked" -e "UID=$(id -u)" -e "GID=$(id -g)" -p "5000:5000" talked
