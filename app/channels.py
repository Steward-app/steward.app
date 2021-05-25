from absl import logging, flags
from box import Box

import grpc

from grpc_opentracing import open_tracing_client_interceptor
from grpc_opentracing.grpcext import intercept_channel

from proto.steward import registry_pb2_grpc

from app.resolver import consul_resolve


FLAGS = flags.FLAGS

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
    def __init__(self, consul=False, tracer=None):
        self.interceptor = None

        # Init tracing if enabled
        if tracer:
            logging.info('gRPC channel tracing enabled')
            self.interceptor = open_tracing_client_interceptor(tracer)
        # not auto filled in, call refresh() or refresh_all()
        self.uri = Box()
        self.channel = Box()
        if consul:
            self.consul = True
            logging.info('Using Consul to resolve backends.')
        else:
            for service, stub in services.items():
                self.uri[service] = '{}:{}'.format(FLAGS.monolithic_host, FLAGS.monolithic_port)
                self.channel[service] = self._get_channel(service, stub)

    def refresh(self, service):
        if self.consul:
            self.uri[service] = self.registry_resolve(service)
            stub = services[service]
            self.channel[service] = self._get_channel(service, stub)
            logging.info('Resolved service {tag} to {uri}'.format(
                tag = service,
                uri = self.uri[service]
            ))

    def refresh_all(self):
        if self.consul:
            for service in services:
                self.refresh(service)
    
    def registry_resolve(self, tag):
        if self.consul:
            service = f'registry.{tag}.{FLAGS.consul_service}'
            return consul_resolve(service)
        else:
            return self.monolithic

    def _get_channel(self, service, stub):
        channel = grpc.insecure_channel(self.uri[service])
        if self.interceptor:
            logging.info(f'Tracing channel for {service}')
            channel = intercept_channel(channel, self.interceptor)
        return stub(channel)
