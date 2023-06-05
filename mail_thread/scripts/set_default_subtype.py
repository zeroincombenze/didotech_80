#!/usr/bin/env python
"""
    Copyright (c) Didotech srl

Example config.py:
    config = {
        'host': 'localhost',  # optional
        'port': 8069,         # optional
        'database': '<database name>',
        'username': 'admin',  # optional
        'password': 'admin'
    }

"""

import jsonrpclib


class OdooRpc(object):
    def __init__(self, config):
        host = config.get('host', 'localhost')
        port = config.get('port', '8069')
        db_name = config.get('database')
        user = config.get('username', 'admin')
        password = config.get('password')
        protocol = config.get('ssl', False) and 'https' or 'http'

        # server proxy object
        url = "{protocol}://{host}:{port}/jsonrpc".format(protocol=protocol, host=host, port=port)
        self.server = jsonrpclib.Server(url)

        # log in the given database
        self.uid = self.server.call(service="common", method="login", args=[db_name, user, password])
        self.password = password
        self.db_name = db_name

    # helper function for invoking model methods
    def execute(self, model, method, *args):
        args = [self.db_name, self.uid, self.password, model, method] + list(args)
        return self.server.call(service="object", method="execute", args=args)


if __name__ == '__main__':
    config_file = 'config'
    configuration = __import__(config_file)
    odoo = OdooRpc(configuration.config)

    result = odoo.execute('crm.lead', 'set_default_subtype', {})

    if result:
        print('Updated...')
