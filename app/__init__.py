#!/usr/bin/env python3

__version__ = "0.3.4"

import sys
from absl import logging, flags
from flask import Flask, render_template, flash, redirect, request, send_from_directory

from app.extensions import lm, mail, bcrypt, flask_static_digest

from app.channels import Channels
from app.resolver import consul_resolve

import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration

import jaeger_client
from flask_opentracing import FlaskTracing

FLAGS = flags.FLAGS
flags.DEFINE_string('sentry', None, 'Sentry endpoint')
flags.DEFINE_bool('jaeger', False, 'Enable Jaeger tracing')
flags.DEFINE_bool('consul', False, 'Enable Consul discovery of services via DNS.')
flags.DEFINE_string('b', None, 'Ignored for gunicorn compatibility')


# init channel resolutions in the global scope so they're available everywhere
channels = None

def init_tracer():
    config = {
        'sampler': {
            'type': 'const',
            'param': 1,
        },
        'logging': True,
    }

    if FLAGS.consul:
        jaeger_host, jaeger_port = consul_resolve('jaeger').split(':')
        logging.info(f'Sending Jaeger tracing to {jaeger_host}:{jaeger_port}')
        config['local_agent'] = {
                'reporting_host': jaeger_host,
                'reporting_port': jaeger_port,
        }
    config_obj = jaeger_client.Config(config, service_name = 'steward.app')
    return config_obj.initialize_tracer()

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


    app = Flask(__name__)
    app.config.from_object('websiteconfig')

    # gRPC channel init
    global channels
    kwargs = {}
    if FLAGS.consul:
        kwargs['consul'] = True
    if FLAGS.jaeger:
        tracer = init_tracer()
        kwargs['tracer'] = tracer
        flask_tracer = FlaskTracing(tracer, True, app)
        logging.info('Flask tracing enabled')
    channels = Channels(**kwargs)
    channels.refresh_all()


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

