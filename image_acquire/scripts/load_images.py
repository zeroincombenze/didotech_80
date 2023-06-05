#!/usr/bin/env python
"""
    Copyright (c) Didotech srl

    This script supports Python 2.6+ and Python 3.x

    Works with jpeg and png images

    -c (--config) - configuration file
    -d (--dir) - directory containing images

Example config.py:
    config = {
        'host': 'localhost',
        'port': 8069,
        'database': '<database name>',
        'username': 'admin',
        'password': 'admin'
    }

"""
from __future__ import print_function

import jsonrpclib
import os
import getopt
import sys
import base64


class OdooRpc(object):
    def __init__(self, host, port, db_name, user, password):
        # server proxy object
        url = "http://{host}:{port}/jsonrpc".format(host=host, port=port)
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

    config = 'config'
    image_dir = os.getcwd()

    try:
        opts, args = getopt.getopt(sys.argv[1:], "c:d:", ['config=', 'dir='])
        for o, a in opts:
            if o in ("-c", "--config"):
                print('Config:', a)
                config = a
            elif o in ('-d', '--dir',):
                image_dir = a

    except getopt.GetoptError:
        print('Usage: ', sys.argv[0], ' --config=[config_name]')
        print('config_name without .py extension')

    config = __import__(config)

    odoo = OdooRpc(
        config.config.get('host'),
        config.config.get('port') or '8069',
        config.config.get('database'),
        config.config.get('username'),
        config.config.get('password')
    )

    for name in os.listdir(image_dir):
        name, extension = name.rsplit('.', 1)
        if extension.lower() in ('jpeg', 'jpg', 'png'):
            image = open(os.path.join(image_dir, '{}.{}'.format(name, extension)), 'rb').read()
            result = odoo.execute('image.acquisition', 'create', {
                'name': name,
                'image': base64.b64encode(image).decode('utf-8')
            })

            if result:
                print(name, ' sent...')
