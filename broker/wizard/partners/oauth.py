# -*- coding: utf-8 -*-
# =============================================================================
# For copyright and license notices, see __openerp__.py file in root directory
# =============================================================================
#
#   Swagger:
#      https://demo.skreprvis.nl/api/docs
#

import requests
import json
import datetime
from collections import namedtuple
from pprint import pprint
import logging
import io

_logger = logging.getLogger(__name__)
_logger.setLevel(logging.DEBUG)


Token = namedtuple('Token', [
    'access_token',
    'token_type',
    'refresh_token',
    'expire'
])


class Communication(object):
    def __init__(self, config):
        self.debug = config.get('debug', False)
        if self.debug:
            logging.debug('Using Communication in debug mode')

        self.token_url = 'http{ssl}://{host}/oauth/v2/token'.format(
            ssl=config.get('ssl') and 's' or '',
            host=config['host']
        )
        self.base_url = 'http{ssl}://{host}/api/v1'.format(
            ssl=config.get('ssl') and 's' or '',
            host=config['host']
        )

        self.headers = {'content-type': 'application/json'}

        self.host = config['host']
        self.username = config['username']
        self.password = config['password']
        self.client_id = config['client_id']
        self.client_secret = config['client_secret']

        self.token = self.request_token()

    def request_token(self):
        """
            {
                "access_token": "NmY0OTNjZTlkNzY2YjQ3NWI3ODM5YTg3NWE0MGNjNDlmNzg1MjAwZjRjNWE3ZDE2NWRhMDJmNTg4MzBhZjk1Ng",
                "expires_in": 3600,
                "token_type": "bearer",
                "scope": null,
                "refresh_token": "OTY0ZjgyNDU1NzU1YmIyMGY2MGIxODk3NTc1OGU3ODJiMzM4NDYxZjRkZDIyOWVlOGMwNDM3NjVmMGZhMWRmNQ"
            }
            :return:
        """

        payload = {
            'grant_type': 'password',
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'username': self.username,
            'password': self.password
        }
        response = requests.post(
            self.token_url,
            headers=self.headers,
            data=json.dumps(payload),
            verify=False
        )

        if response.status_code == 200:
            content = json.loads(response.content)
            if self.debug:
                _logger.debug('Received Access token')
            return Token(
                content.get('access_token'),
                content.get('token_type', 'bearer'),
                content.get('refresh_token'),
                datetime.datetime.now() + datetime.timedelta(seconds=content.get('expires_in'))
            )
        else:
            return False

    def refresh_token(self):
        payload = {
            'grant_type': 'refresh_token',
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'refresh_token': self.token.refresh_token
        }

        response = requests.post(
            self.token_url,
            headers=self.headers,
            data=json.dumps(payload),
            verify=False
        )

        if response.status_code == 200:
            content = json.loads(response.content)
            self.token = Token(
                content.get('access_token'),
                # content.get('token_type', 'bearer'),
                content.get('refresh_token'),
                datetime.datetime.now() + datetime.timedelta(seconds=content.get('expires_in'))
            )
            return True
        else:
            return False

    # def search(self, endpoint, name):
    #     # Not activated
    #     response = requests.get(
    #         '{base}/{end}'.format(base=self.base_url, end=endpoint),
    #         headers=self.auth_header(),
    #         # data=json.dumps(payload),
    #         verify=False
    #     )
    #     print response
    #     if response.status_code == 200:
    #         content = json.loads(response.content)
    #         print content

    def auth_header(self):
        headers = self.headers

        if self.token.expire < datetime.datetime.now():
            self.refresh_token()

        headers['Authorization'] = '{} {}'.format(self.token.token_type.capitalize(), self.token.access_token)
        return headers

    def get_record(self, endpoint, record_id=False, page=False):
        endpoint = endpoint.strip('/')
        url = '{base}/{end}'.format(base=self.base_url, end=endpoint)
        if record_id:
            url += '/{record}'.format(record=record_id)

        if page:
            url += '?page={page}'.format(page=page)

        response = requests.get(
            url,
            headers=self.auth_header(),
            verify=False
        )

        if self.debug:
            _logger.debug("Trying to get record from '{endpoint}'".format(endpoint=url))
            _logger.debug('Received {code}'.format(code=response.status_code))

        if response.status_code == 200:
            content = json.loads(response.content)
            return content
        elif response.status_code == 500:
            print "Internal server error"
            return False
        else:
            return False

    def transmit_order(self, payload):
        response = requests.post(
            '{base}/{end}'.format(base=self.base_url, end='orders'),
            headers=self.auth_header(),
            data=json.dumps(payload),
            verify=False
        )

        if response.status_code == 201:
            """
            {
                u'status': u'success',
                u'ordernumber': 126778,
                u'id': 126277
            }
            """
            content = json.loads(response.content)
            return content
        elif response.status_code == 400:
            content = json.loads(response.content)
            print content['message']
            raise Warning(content['message'], str(payload))
            return False
        elif response.status_code == 401:
            print 'UNAUTHORIZED'
            raise Warning("Authentication failed")
            return False
        elif response.status_code == 500:
            # content = json.loads(response.content)
            # print content['message']
            raise Warning('Internal Server Error')
            return False
        else:
            return False


if '__main__' == __name__:
    # client_id = u'1_5tl0x6gi5mkg8kwg4kg0okow4w4g8sc8o4c04ckowcwo840ok8'
    # client_secret = u'4l33i5qrve048sc4c84kkc0oocwks0044k8448w48s84wscs8c'
    # username = u'andrei'
    # password = u'andrei'
    # host = 'demo.skreprvis.nl'

    config_test = {
        "default_transmission": "Koffeman",
        "client_id": "1_5tl0x6gi5mkg8kwg4kg0okow4w4g8sc8o4c04ckowcwo840ok8",
        "client_secret": "4l33i5qrve048sc4c84kkc0oocwks0044k8448w48s84wscs8c",
        "username": "andrei",
        "password": "andrei",
        "host": "demo.skreprvis.nl",
        "communication": "koffeman",
        "ssl": True,
        "debug": True
    }

    config = {
        "default_transmission": "Koffeman",
        "client_id": "1_5tl0x6gi5mkg8kwg4kg0okow4w4g8sc8o4c04ckowcwo840ok8",
        "client_secret": "4l33i5qrve048sc4c84kkc0oocwks0044k8448w48s84wscs8c",
        "username": "agroapi",
        "password": "Hcrazhz7",
        "host": "koffeman.skreprvis.nl",
        "communication": "koffeman",
        "ssl": False,
        "debug": True
    }

    tr = Communication(config)

    # Ex. Sale Order
#     out_data = {
#         'order': {
#             'customer': '1',
#             'date': {
#                 'year': '2017',
#                 'month': '3',
#                 'day': '16'
#             },
#             'row': {
#                 '0': {
#                     'product': '17',
#                     'amount': '10',
#                     'price': '10'
#                 }
#             }
#         }
#     }
    # 09 - customer code (wrong)
    out_data = {
      'order': {
        'customer': u'09',
        'date': {'month': '8', 'day': '29', 'year': '2017'},
        'row': {
            '0': {'price': '12.35', 'product': u'467', 'amount': '651.59'},
            '1': {'price': '2.5', 'product': u'335', 'amount': '112.5'},
            '2': {'price': '8.75', 'product': u'366', 'amount': '87.5'},
            '3': {'price': '10.25', 'product': u'1720', 'amount': '230.83'}
        }
      }
    }

    # Sent Order:
    # print(tr.transmit_order(out_data))

    # Customers (Koffeman)
    # - Linemar S.r.l.
    # customer = tr.get_record('customers/code', '26')
    # pprint(customer)
    #
    # customer = tr.get_record('customers/code', '06')
    # pprint(customer)

    # product = tr.get_record('products/code', 1393)
    # pprint(product)

    # product = tr.get_record('products/code', 100038)
    # pprint(product)
    # product = tr.get_record('products/code', 32)
    # pprint(product)
    #
    # product = tr.get_record('products/code', 1290)
    # pprint(product)
    #
    # product = tr.get_record('products/code', 248)
    # pprint(product)

    product = tr.get_record('products/code', 119)
    pprint(product)

    # products = tr.get_record('products')
    # # pprint(products)
    # # for product in products['products']:
    # #     print('{code};{name}'.format(code=product['product']['code'], name=product['product']['name']))
    #
    # k = 0
    #
    # with open('prodotti.csv', 'w') as fd:
    #     for page in range(1, products['numPages'] + 1):
    #         products = tr.get_record('products', page=page)
    #
    #         for product in products['products']:
    #             # pprint(product)
    #             k += 1
    #             row = u'{k};{code};{name}'.format(k=k, code=product['product']['code'], name=product['translation']['name'])
    #             print(row)
    #             fd.write(row + '\n')

    # customers = tr.get_record('customers')
    # k = 0
    #
    # with io.open('customers.csv', 'w') as fd:
    #     for page in range(1, customers['pages'] + 1):
    #         customers = tr.get_record('customers', page=page)
    #         for customer in customers['customers']:
    #             pprint(customer)
    #             k += 1
    #             row = u'{k};{code};{name}'.format(
    #                 k=k,
    #                 code=customer['code'],
    #                 name=customer['name']
    #             )
    #             print(row)
    #             fd.write(row + u'\n')
