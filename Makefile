.PHONY: help setup run test test-verbose docker-build docker-run clean

help:
	@echo "MboFlow Team Developer Commands:"
	@echo "  make setup        - Create virtual environment and install all dependencies"
	@echo "  make run          - Launch local backend and interactive banking interface"
	@echo "  make test         - Run complete 50-test automated verification suite"
	@echo "  make docker-build - Build production multi-stage container"
	@echo "  make docker-run   - Run container with docker compose"
	@echo "  make clean        - Remove caches, temporary test artifacts, and build files"

setup:
	@bash setup.sh || setup.bat

run:
	@bash run.sh || run.bat

test:
	@pytest tests/

test-verbose:
	@pytest -v -s tests/

docker-build:
	docker compose build

docker-run:
	docker compose up -d

clean:
	rm -rf .pytest_cache __pycache__ */__pycache__ */*/__pycache__ .playwright
