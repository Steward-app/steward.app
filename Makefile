# You can set these variables from the command line.
NODE_MODULES = static/node_modules
FE_PORT = 50049

all: dependencies app run_dev

.PHONY: app clean run run_monolithic run_dev

dependencies:
	python3 -m pip install -r requirements.txt

app:
	cd app; yarn install --modules-folder $(NODE_MODULES)
	FLASK_APP=app:load flask assets build

clean:
	rm  -rf app/$(NODE_MODULES)

run_dev:
	python3 -c 'from app import load; load("dev").run(host="0.0.0.0", port=$(FE_PORT))' --flagfile=dev.flags

run_monolithic:
	gunicorn -b  "0.0.0.0:$(FE_PORT)" "app:load('prod')" -- --flagfile=prod.flags
