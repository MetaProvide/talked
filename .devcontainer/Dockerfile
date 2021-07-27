# See here for image contents: https://github.com/microsoft/vscode-dev-containers/tree/v0.187.0/containers/ubuntu/.devcontainer/base.Dockerfile

# [Choice] Ubuntu version: bionic, focal
ARG VARIANT="focal"
FROM mcr.microsoft.com/vscode/devcontainers/base:0-${VARIANT}

ENV DEBIAN_FRONTEND=noninteractive
ENV POETRY_VIRTUALENVS_CREATE=false

# hadolint ignore=DL3013
RUN apt-get update; \
    apt-get install -y --no-install-recommends \
        python3 \
        python3-pip \
        firefox-geckodriver \
        pulseaudio \
        xvfb \
        ffmpeg \
    ; \
    pip3 install --no-cache-dir poetry; \
    rm -rf /var/lib/apt/lists/*;
