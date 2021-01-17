from absl import logging, flags
from dns import resolver
from box import Box
import grpc

from proto.steward import registry_pb2_grpc

FLAGS = flags.FLAGS

flags.DEFINE_string('consul', None, 'Define ip address to enable Consul service disovery. A hostname will not work.')
flags.DEFINE_integer('consul_port', 8600, 'Consul port')
flags.DEFINE_string('consul_service', 'steward-registry', 'Consul service')
flags.DEFINE_string('monolithic_host', 'localhost', 'Host to use for monolithic deployments')
flags.DEFINE_integer('monolithic_port', 50050, 'Port to use for monolithic deployments')

services = {
        'user': registry_pb2_grpc.UserServiceStub,
        'asset': registry_pb2_grpc.AssetServiceStub,
        'maintenance': registry_pb2_grpc.MaintenanceServiceStub,
        'schedule': registry_pb2_grpc.ScheduleServiceStub
        }

class Channels():
    def __init__(self):
        # not auto filled in, call refresh() or refresh_all()
        self.uri = Box()
        self.channel = Box()
        if FLAGS.consul:
            logging.info('Using Consul host: {host}'.format(host=FLAGS.consul))
            self.resolver = resolver.Resolver()
            self.resolver.port = FLAGS.consul_port
            self.resolver.nameservers = [FLAGS.consul]
        else:
            for service, stub in services.items():
                self.uri[service] = monolithic_uri
                self.channel[service] = self._get_channel(service, stub)

    def refresh(self, service):
        if FLAGS.consul:
            self.uri[service] = self._resolve(service)
            stub = services[service]
            self.channel[service] = self._get_channel(service, stub)
            logging.info('Resolved service {tag} to {uri}'.format(
                tag = service,
                uri = self.uri[service]
            ))

    def refresh_all(self):
        if FLAGS.consul:
            for service in services:
                self.refresh(service)
    
    def _resolve(self, tag):
        if FLAGS.consul:
            address = 'registry.{tag}.{service}.service.consul.'.format(tag=tag, service=FLAGS.consul_service)
            srv = self.resolver.query(address, 'SRV')[0]
            ip = self.resolver.query(srv.target, 'A')[0]
            return '{host}:{port}'.format(host=ip, port=srv.port)
        else:
            return self.monolithic

    def _get_channel(self, service, stub):
        channel = grpc.insecure_channel(self.uri[service])
        return stub(channel)
