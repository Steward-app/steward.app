#!/usr/bin/env python3

__version__ = "0.1.0"

import sys
from absl import logging, flags
from flask import Flask, render_template, flash, redirect, request

from app.app_assets import assets
from app.extensions import lm, mail, bcrypt

from app.channels import Channels

import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration

FLAGS = flags.FLAGS
flags.DEFINE_string('sentry', None, 'Sentry endpoint')
flags.DEFINE_string('b', None, 'Ignored for gunicorn compatibility')


# init channel resolutions in the global scope so they're available everywhere
channels = None

# This loader can be run with a wsgi runner and still receive an argument
def load(env):
    # Flag parsing with wsgi runners is a major pain
    # We identify a flag break '--' and consume only flags after it
    if env != 'dev':
        if '--' in sys.argv:
            separator = sys.argv.index('--')
            args=sys.argv[separator:]
            logging.debug('Prod mode, loading args the hard way: {args}'.format(args=args))
        else:
            args=sys.argv
        FLAGS(args)
    else:
        FLAGS(sys.argv)

    # Init sentry as early as possible to catch as much as possible
    if FLAGS.sentry:
        sentry_sdk.init(
            dsn=FLAGS.sentry,
            integrations=[FlaskIntegration()]
        )

    global channels
    channels = Channels()
    channels.resolve_all(env=env)

    app = Flask(__name__)
    app.config.from_object('websiteconfig')

    assets.init_app(app)
    lm.init_app(app)
    mail.init_app(app)
    bcrypt.init_app(app)


    from app import user, maintenance, asset
    app.register_blueprint(user.bp)
    app.register_blueprint(maintenance.bp)
    app.register_blueprint(asset.bp)

    @app.route('/')
    def root():
        return render_template('index.html')

    return app

