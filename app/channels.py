from absl import logging, flags
from dns import resolver

FLAGS = flags.FLAGS

flags.DEFINE_bool('consul', False, 'Enable Consul service disovery')

class Channels():
    def __init__(self):
        if FLAGS.consul:
            self.resolver = resolver.Resolver()
            self.resolver.port = 8600
            self.resolver.nameservers = ["127.0.0.1"]
        else:
            self.monolithic = 'localhost:50050'
            self.user = self.monolithic
            self.maintenance = self.monolithic
            self.asset = self.monolithic
            self.schedule = self.monolithic


    def resolve(self, tag):
        if FLAGS.consul:
            address = '{tag}.steward-registry.service.consul.'.format(tag=tag)
            srv = self.resolver.query(address, 'SRV')[0]
            ip = self.resolver.query(srv.target, 'A')[0]
            return '{host}:{port}'.format(host=ip, port=srv.port)
        else:
            return self.monolithic
    
    def resolve_all(self):
        if FLAGS.consul:
            self.user = self.resolve('registry.user')
            self.maintenance = self.resolve('registry.maintenance')
            self.asset = self.resolve('registry.asset')
            self.schedule = self.resolve('registry.schedule')
        logging.info('Resolved channels:\n user_server: {user}\n maintenance_server: {maintenance}\n asset_server: {asset}\n schedule_server: {schedule}'.format(
            user=self.user,
            maintenance=self.maintenance,
            asset=self.asset,
            schedule=self.schedule
        ))
