# You can set these variables from the command line.
NODE_MODULES = node_modules
FE_PORT = 50049

all: dependencies dev run_dev

.PHONY: build clean run run_monolithic run_dev

dependencies:
	python3 -m pip install -r requirements.txt

prod:
	cd app; yarn install && npx webpack --mode production
	FLASK_APP=app:load flask digest compile

dev:
	cd app; yarn install && npx webpack --mode development
	FLASK_APP=app:load flask digest clean

clean:
	rm  -rf $(NODE_MODULES)

run_dev:
	python3 -c 'from app import load; load("dev").run(host="0.0.0.0", port=$(FE_PORT))' --flagfile=dev.flags

run_monolithic:
	gunicorn -b  "0.0.0.0:$(FE_PORT)" "app:load('prod')" -- --flagfile=prod.flags
