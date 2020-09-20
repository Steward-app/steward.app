# You can set these variables from the command line.
NODE_MODULES = static/node_modules
FE_PORT = 5000

dependencies:
	sudo pip3 install -r requirements.txt

.PHONY: app clean run run_monolithic
app:
	cd app; yarn install --modules-folder $(NODE_MODULES)
	cd app; FLASK_APP=__init__.py flask assets build


clean:
	rm  -rf app/$(NODE_MODULES)

run:
	export FLASK_APP=app.app
	flask run -h 0.0.0.0

run_monolithic:
	python3 -c 'from app import app; app.run(host="0.0.0.0", load_dotenv=False, port=$(FE_PORT))'
