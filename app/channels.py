from absl import logging, flags
from dns import resolver

FLAGS = flags.FLAGS

flags.DEFINE_string('consul', None, 'Define ip address to enable Consul service disovery. A hostname will not work.')
flags.DEFINE_integer('consul_port', 8600, 'Consul port')
flags.DEFINE_string('consul_service', 'steward-registry', 'Consul service')
flags.DEFINE_string('monolithic_host', 'localhost', 'Host to use for monolithic deployments')
flags.DEFINE_integer('monolithic_port', 50050, 'Port to use for monolithic deployments')

class Channels():
    def __init__(self):
        if FLAGS.consul:
            self.resolver = resolver.Resolver()
            self.resolver.port = FLAGS.consul_port
            self.resolver.nameservers = [FLAGS.consul]
            logging.info('Using Consul host: {host}'.format(host=FLAGS.consul))
        else:
            self.monolithic = '{host}:{port}'.format(host=FLAGS.monolithic_host, port=FLAGS.monolithic_port)
            self.user = self.monolithic
            self.maintenance = self.monolithic
            self.asset = self.monolithic
            self.schedule = self.monolithic


    def resolve(self, tag):
        if FLAGS.consul:
            address = '{tag}.{service}.service.consul.'.format(tag=tag, service=FLAGS.consul_service)
            srv = self.resolver.query(address, 'SRV')[0]
            ip = self.resolver.query(srv.target, 'A')[0]
            return '{host}:{port}'.format(host=ip, port=srv.port)
        else:
            return self.monolithic
    
    def resolve_all(self, env='dev'):
        if FLAGS.consul:
            self.user = self.resolve('registry.user.{env}'.format(env=env))
            self.maintenance = self.resolve('registry.maintenance.{env}'.format(env=env))
            self.asset = self.resolve('registry.asset.{env}'.format(env=env))
            self.schedule = self.resolve('registry.schedule.{env}'.format(env=env))
        logging.info('Resolved channels (env={env}):\n user_server: {user}\n maintenance_server: {maintenance}\n asset_server: {asset}\n schedule_server: {schedule}'.format(
            env=env,
            user=self.user,
            maintenance=self.maintenance,
            asset=self.asset,
            schedule=self.schedule
        ))
