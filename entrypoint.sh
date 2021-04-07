#!/bin/bash

poetry run gunicorn -b 0.0.0.0:${PORT:-50049} "app:load('prod')" -- $@
