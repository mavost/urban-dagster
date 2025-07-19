MAKEFLAGS += --warn-undefined-variables
.SHELLFLAGS := -eu -o pipefail -c

all: help
.PHONY: all help run-compose clean
# https://medium.com/freestoneinfotech/simplifying-docker-compose-operations-using-makefile-26d451456d63

# Use bash for inline if-statements
SHELL:=bash

##@ Helpers
help: ## display this help
	@echo "Docker-Compose Showcase"
	@echo "======================="
	@awk 'BEGIN {FS = ":.*##"; printf "\033[36m\033[0m"} /^[a-zA-Z0-9_%/-]+:.*?##/ { printf "  \033[36m%-25s\033[0m %s\n", $$1, $$2 } /^##@/ { printf "\n\033[1m%s\033[0m\n", substr($$0, 5) } ' $(MAKEFILE_LIST)
	@printf "\n"

current_service ?= dagster_user_code

##@ Setup
run-compose: ## set up stack
	docker rmi -f $$(docker images -q $(current_service)) 2>/dev/null || true
	docker-compose -f docker-compose.yaml build $(current_service)
	docker-compose -f docker-compose.yaml up -d $(current_service)

##@ Tear-down
clean: ## clean up stack
	docker-compose -f docker-compose.yaml down