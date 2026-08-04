.PHONY: help run stop build test lint format migrate makemigrations shell dbshell logs seed css css-watch

help:            ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

run:             ## Start all services
	docker compose up -d

stop:            ## Stop all services
	docker compose down

build:           ## Rebuild containers
	docker compose up --build -d

test:            ## Run tests with coverage
	docker compose exec web pytest --cov=apps --cov-report=term-missing

lint:            ## Run linter
	docker compose exec web ruff check .

format:          ## Format code
	docker compose exec web ruff format .

migrate:         ## Run database migrations
	docker compose exec web python manage.py migrate

makemigrations:  ## Create new migrations
	docker compose exec web python manage.py makemigrations

shell:           ## Django shell
	docker compose exec web python manage.py shell

dbshell:         ## Database shell
	docker compose exec db psql -U vendorverse vendorverse

logs:            ## View logs
	docker compose logs -f --tail=100

seed:            ## Seed database with initial data
	docker compose exec web python manage.py seed_data

css:             ## Build Tailwind CSS
	npm run build:css

css-watch:       ## Watch Tailwind CSS (development)
	npm run watch:css
