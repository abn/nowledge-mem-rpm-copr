.DEFAULT_GOAL := help

# Configuration variables
COPR_REPO ?= abn/nowledge-mem
RPMBUILDER_IMAGE ?= quay.io/abn/rpmbuilder:fedora-latest
SPEC_FILE := nowledge-mem.spec
VERSION_URL := https://nowled.ge/download-mem-rpm

.PHONY: help setup resolve-version download-upstream srpm build-test build-container tag-release copr-build clean

help: ## Display available Makefile targets
	@echo "Nowledge Mem RPM Packaging & COPR Build Automation"
	@echo ""
	@echo "Usage: make <target>"
	@echo ""
	@echo "Targets:"
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

setup: ## Set up Python environment and copr-cli dependencies
	@echo "Setting up Python virtual environment..."
	@python3 -m venv .venv
	@.venv/bin/pip install --upgrade pip
	@.venv/bin/pip install copr-cli rich
	@echo "Setup complete. Run '.venv/bin/copr-cli --help' to verify."

resolve-version: ## Check and resolve the latest online version from https://nowled.ge/download-mem-rpm
	@python3 update_version.py --check-only

download-upstream: ## Fetch latest version from https://nowled.ge/download-mem-rpm and download binary RPM
	@python3 update_version.py

srpm: download-upstream ## Generate Source RPM (SRPM) for COPR submission
	@mkdir -p build/SRPMS
	@echo "Building SRPM..."
	@rpmbuild -bs \
		--define "_topdir $(shell pwd)/build" \
		--define "_sourcedir $(shell pwd)/build" \
		--define "_srcrpmdir $(shell pwd)/build" \
		$(SPEC_FILE)
	@echo "SRPM build complete in build/"

build-test: srpm ## Perform local test build using Tito
	@echo "Running local Tito test build..."
	@tito build --test --srpm --output=build/

build-container: srpm ## Perform containerized RPM build using quay.io/abn/rpmbuilder:fedora-latest
	@echo "Running containerized build using $(RPMBUILDER_IMAGE)..."
	@podman run --rm \
		-v $(shell pwd):/sources:z \
		-v $(shell pwd)/build:/output:z \
		$(RPMBUILDER_IMAGE) \
		tito build --test --srpm --output=build/
	@echo "Containerized build finished successfully."

tag-release: download-upstream ## Tag a new version release using Tito
	@if [ -n "$$(git status --porcelain nowledge-mem.spec)" ]; then \
		VERSION=$$(python3 -c "import re; print(re.search(r'^Version:\s*([^\s]+)', open('nowledge-mem.spec').read(), re.MULTILINE).group(1))"); \
		git add nowledge-mem.spec; \
		git commit -m "chore: bump version to $$VERSION"; \
		tito tag --use-version "$$VERSION" --use-release '1%{?dist}' --accept-auto-changelog; \
		echo "Tagged new version $$VERSION with Tito."; \
	else \
		echo "No spec file changes to tag."; \
	fi

copr-build: srpm setup ## Dispatch SRPM build to Fedora COPR
	@echo "Dispatching build to COPR ($(COPR_REPO))..."
	@.venv/bin/python3 dispatch_copr.py --repo $(COPR_REPO)

clean: ## Clean build artifacts and temp files
	@rm -rf build/ .cover .mbx
	@echo "Cleaned build artifacts."
