MAKEFLAGS += --warn-undefined-variables
.SHELLFLAGS := -eu -o pipefail -c

all: help
.PHONY: all, help, run-compose, run-clean
# https://medium.com/freestoneinfotech/simplifying-docker-compose-operations-using-makefile-26d451456d63

# Use bash for inline if-statements
SHELL:=bash

##@ Helpers
help: ## display this help
	@echo "Docker-Compose Showcase"
	@echo "======================="
	@awk 'BEGIN {FS = ":.*##"; printf "\033[36m\033[0m"} /^[a-zA-Z0-9_%/-]+:.*?##/ { printf "  \033[36m%-25s\033[0m %s\n", $$1, $$2 } /^##@/ { printf "\n\033[1m%s\033[0m\n", substr($$0, 5) } ' $(MAKEFILE_LIST)
	@printf "\n"


stack = 
##@ Setup
run-compose: ## set up stack, vars: stack=[NULL, extended]
	docker-compose -f docker-compose$(stack).yaml build $(c)
	docker-compose -f docker-compose$(stack).yaml up -d $(c)

stack = 
##@ Tear-down
run-clean: ## clean up stack, vars: stack=[NULL, extended]
	docker-compose -f docker-compose$(stack).yaml down $(c)