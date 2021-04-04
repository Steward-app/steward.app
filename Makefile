# You can set these variables from the command line.
NODE_MODULES = app/node_modules
STATIC_ASSETS = app/static/
FE_PORT = 50049

all: dependencies dev run_dev

.PHONY: build clean run run_monolithic run_dev

dependencies:
	poetry install

prod:
	cd app; yarn install && npx webpack --mode production
	FLASK_APP=app:load poetry run flask digest compile

dev:
	cd app; yarn install && npx webpack --mode development
	FLASK_APP=app:load poetry run flask digest clean

clean:
	rm  -rf $(NODE_MODULES)
	git clean -fX $(STATIC_ASSETS)

run_dev:
	poetry run python -c 'from app import load; load("dev").run(host="0.0.0.0", port=$(FE_PORT))' --flagfile=dev.flags

run_monolithic:
	poetry run gunicorn -b  "0.0.0.0:$(FE_PORT)" "app:load('prod')" -- --flagfile=prod.flags
