#!/usr/bin/env python3

__version__ = "0.3.2"

import sys
from absl import logging, flags
from flask import Flask, render_template, flash, redirect, request, send_from_directory

from app.extensions import lm, mail, bcrypt, flask_static_digest

from app.channels import Channels

import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration

import jaeger_client
from flask_opentracing import FlaskTracing

FLAGS = flags.FLAGS
flags.DEFINE_string('sentry', None, 'Sentry endpoint')
flags.DEFINE_bool('jaeger', None, 'Enable Jaeger tracing')
flags.DEFINE_string('b', None, 'Ignored for gunicorn compatibility')


# init channel resolutions in the global scope so they're available everywhere
channels = None

def init_tracer():
    config = jaeger_client.Config(
        config = {
            'sampler': {
                'type': 'const',
                'param': 1,
            },
            'logging': True,
        },
        service_name = 'steward.app'
    )
    return config.initialize_tracer()

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
            dsn = FLAGS.sentry,
            integrations = [ FlaskIntegration() ],
            environment = env,
            release = __version__
        )

    global channels
    channels = Channels()
    channels.refresh_all()

    app = Flask(__name__)
    app.config.from_object('websiteconfig')

    if FLAGS.jaeger:
        tracing = FlaskTracing(init_tracer, True, app)

    lm.init_app(app)
    mail.init_app(app)
    bcrypt.init_app(app)
    flask_static_digest.init_app(app)


    from app import user, maintenance, asset, pwa
    app.register_blueprint(user.bp)
    app.register_blueprint(maintenance.bp)
    app.register_blueprint(asset.bp)
    app.register_blueprint(pwa.bp)

    @app.route('/')
    def root():
        return render_template('index.html')

    @app.route('/favicon.ico')
    def favicon():
        return send_from_directory('static', 'img/icons/favicon.ico')


    return app

