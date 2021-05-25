from absl import logging
from dns import resolver

resolver = resolver.Resolver()

def consul_resolve(service):
    address = f'{service}.service.consul.'
    srv = resolver.resolve(address, 'SRV')[0]
    ip = resolver.resolve(srv.target, 'A')[0]
    logging.debug(f'Resolved: {address} -> {ip}:{srv.port}')
    return f'{ip}:{srv.port}'
