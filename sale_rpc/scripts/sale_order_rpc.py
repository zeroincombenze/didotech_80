"""
    Python 2.7:
    pip install jsonrpclib

    Python 3.x:
    pip install git+https://github.com/tcalmant/jsonrpclib.git

    workon testing
"""

import jsonrpclib
# import json
import base64
from pprint import pprint
from collections import namedtuple

Config = namedtuple('Config', ['database', 'host', 'port', 'user', 'password'])


class OdooRpc(object):
    def __init__(self, config):
        # server proxy object
        url = "http://%s:%s/jsonrpc" % (config.host, config.port)
        self.server = jsonrpclib.Server(url)

        # log in the given database
        self.uid = self.server.call(service="common", method="login", args=[config.database, config.user, config.password])
        self.password = config.password
        self.db_name = config.database

    # helper function for invoking model methods
    def rpc(self, model, method, *args):
        args = [self.db_name, self.uid, self.password, model, method] + list(args)
        return self.server.call(service="object", method="execute", args=args)


class JsonRpcSaleOrder(OdooRpc):
    # def __init__(self, config):
    #     super(OdooRpc, self).__init__(config)
    #
    #
    #     self.orders_to_delete = []

    def create(self, values):
        reply = self.rpc('sale.order', 'json_create', values)

        # new_order = json.loads(reply)
        new_order = reply

        assert 'results' in new_order, "Failed to create a new order"

        return new_order['results'][0]

    def write(self, order_id, values, check=False):
        reply = self.rpc('sale.order', 'json_write', order['pk'], values)

        # updated_order = json.loads(reply)['results'][0]
        updated_order = reply['results'][0]
        updated_order_line = updated_order['order_line'][0]

        if check:
            for name, value in check.items():
                assert updated_order_line[name] == value

        return updated_order

    # def test_list_sale_orders(self):
    #     order_list = self.rpc('sale.order', 'json_list', self.remote_partner)
    #     # self.assertTrue('results' in json.loads(order_list), msg="Failed to retrieve order list")
    #     self.assertTrue('results' in order_list, msg="Failed to retrieve order list")


if '__main__' == __name__:
    config = Config(
        database='Digital_0321',
        host='localhost',
        port='8069',
        user='admin',
        password='digitalok2104'
    )

    # Existing product 122
    # values = {
    #     "ecommerce": True,
    #     "order_line": [
    #         [
    #             0,
    #             False,
    #             {
    #                 "product_variant_id": 122,  # product_variant_id (NOT product_tmpl_id!)
    #                 "product_uom_qty": 1,
    #                 # 'ext_product_id': 32
    #             }
    #         ]
    #     ],
    #     "partner": {
    #         "name": "Crazy Tester",
    #         "city": "Padova",
    #         "country": "Italia",
    #         "ext_partner_id": 45
    #     }
    # }

    values = {
        "ecommerce": True,
        "order_line": [
            [
                0,
                False,
                {
                    # "product_variant_id": 122,  # product_variant_id (NOT product_tmpl_id!)
                    "product_uom_qty": 1,
                    'ext_product_id': 32,
                    'price_unit': 32.00,
                    'name': 'Crazy stuff II'
                }
            ]
        ],
        "partner": {
            "name": "Crazy Tester",
            "city": "Padova",
            "country": "Italia",
            "ext_partner_id": 45
        }
    }

    sale_order = JsonRpcSaleOrder(config)

    order = sale_order.create(values)

    pprint(order)

    order_line = order['order_line'][0]

    sale_order.write(order['pk'], {
        "order_line": [
            [1, order_line['pk'], {"product_uom_qty": 5}]
        ]
    }, check={"product_uom_qty": 5})
