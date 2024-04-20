# ----------------------------------------------------------------------------
# Makefile for ddnss-forwarder
#
# Copyright (c) 2024 by Clemens Rabe <clemens.rabe@gmail.com>
# All rights reserved.
# ----------------------------------------------------------------------------


# ----------------------------------------------------------------------------
#  SETTINGS
# ----------------------------------------------------------------------------
APP_NAME               := ddnss-forwarder
APP_VERSION            := 0.0.1

ALL_TARGET             := check-style.venv
SCRIPT                 := src/ddnss_forwarder.py

MAKE4PY_DOCKER_IMAGE   := make4py-ddnss-forwarder
UBUNTU_DIST_VERSIONS   := 20.04 22.04
ENABLE_WINDOWS_SUPPORT := 0


# ----------------------------------------------------------------------------
#  MAKE4PY INTEGRATION
# ----------------------------------------------------------------------------
include .make4py/make4py.mk


# ----------------------------------------------------------------------------
#  OWN TARGETS
# ----------------------------------------------------------------------------
.PHONY: system-setup-prod pip-install-prod build-docker

pip-install-prod:
	@echo "-------------------------------------------------------------"
	@echo "Installing package requirements (production)..."
	@echo "-------------------------------------------------------------"
	@pip install -r pip_deps/requirements-linux-py3.10.12.txt

system-setup-prod: pip-setup pip-install-prod pip-upgrade-stuff

build-docker:
	@docker build -t $(APP_NAME):$(APP_VERSION) --build-arg PYTHON_VERSION=3.10 .

run-docker:
	@docker run -d --restart=always --name=ddnss-forwarder $(APP_NAME):$(APP_VERSION)


# ----------------------------------------------------------------------------
#  EOF
# ----------------------------------------------------------------------------
