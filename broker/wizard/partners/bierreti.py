# -*- encoding: utf-8 -*-
# =============================================================================
# For copyright and license notices, see __openerp__.py file in root directory
# =============================================================================

from collections import OrderedDict
from .main import DistributionList
import requests
import datetime
import xmltodict
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT
from openerp.exceptions import Warning
import json


class Bierreti(DistributionList):
    """
    {
        "default_transmission": "Bierreti",
        "url": "http://95.226.149.130/orderservice/orderservice.asmx/RiceviOrdini",
        "user": "andrei",
        "password": "ordini"
    }
    """

    def __init__(self, show_prices, truck_info, currency_symbol, ignore_truck_info, dvce):
        super(Bierreti, self).__init__(show_prices, truck_info, ignore_truck_info, dvce)

        self.root = OrderedDict()
        self.currency = currency_symbol

    def supplier_header(self, broker_order):
        super(Bierreti, self).supplier_header(broker_order)
        self.delivery_carrier = broker_order.carrier_id.partner_id

        self.root['header'] = OrderedDict(name=broker_order.supplier_id.name)

        # This is inversed logic, because Bierreti is not a customer, but it's OK
        supplier_info = broker_order.supplier_id.get_customer_ref(self.delivery_carrier.id)
        if supplier_info:
            self.root['header']['supplier_ref'] = supplier_info.customer_ref
        else:
            if self.delivery_carrier:
                raise Warning("{carrier} missing reference for {supplier}".format(
                    carrier=self.delivery_carrier.name or '',
                    supplier=broker_order.supplier_id.name
                ))
            else:
                raise Warning("Missing carrier info. Is delivery method selected correctly?")

        # From 1.04.2017 instead of delivery_date we are using date_cmr
        # if broker_order.delivery_date and not self.show_prices:
        #     delivery_date = datetime.datetime.strptime(broker_order.delivery_date, DEFAULT_SERVER_DATETIME_FORMAT)
        #     self.root['header']['delivery_date'] = delivery_date.strftime(DEFAULT_SERVER_DATE_FORMAT)
        if not self.show_prices:
            if broker_order.date_cmr:
                date_cmr = datetime.datetime.strptime(broker_order.date_cmr, DEFAULT_SERVER_DATETIME_FORMAT)
                self.root['header']['delivery_date'] = date_cmr.strftime(DEFAULT_SERVER_DATE_FORMAT)
            else:
                raise Warning("Please set date_cmr.")

        if not self.ignore_truck_info and not self.truck_info.name == '-':
            self.root['header']['truck_info'] = self.truck_info.name

        if self.dvce:
            self.root['header']['dvce'] = self.dvce

    def body_start(self):
        self.root['delivery'] = []

    def customer_start(self, sale_order, address, customer_ref):
        super(Bierreti, self).customer_start(sale_order, address, customer_ref)
        self.delivery = OrderedDict()

        if self.delivery_carrier:
            code = self.delivery_carrier.get_customer_ref(address.id)
            if code and code.customer_ref:
                self.delivery['code'] = code.customer_ref

        if customer_ref:
            self.delivery['customer_ref'] = customer_ref

        self.delivery['name'] = sale_order.partner_id.name
        if sale_order.partner_shipping_id.auth_number and not self.show_prices:
            self.delivery['auth_number'] = sale_order.partner_shipping_id.auth_number

        if self.show_prices:
            self.delivery['order'] = sale_order.name

        self.delivery['address'] = {
            'street': address.street,
            'zip': address.zip,
            'city': address.city,
            'province': address.province and address.province.code or '',
            'country': address.country_id.code
        }

        # if sale_order.delivery_date and not self.show_prices:
        #     delivery_date = datetime.datetime.strptime(sale_order.delivery_date, DEFAULT_SERVER_DATETIME_FORMAT)
        #     self.delivery['delivery_date'] = delivery_date.strftime(DEFAULT_SERVER_DATE_FORMAT)

        if sale_order.delivery_note:
            self.delivery['note'] = sale_order.delivery_note

        self.delivery['product'] = []

    def customer_end(self):
        self.root['delivery'].append(self.delivery)

    def sale_order_line(self, line, box_qty):
        order_line = OrderedDict(
            product=line.product_id.description or line.product_id.name,
            box_qty=box_qty,
            box_weight=line.product_id.product_uib,
            weight=line.total_weight
        )

        if self.show_prices:
            order_line['price_unit'] = line.price_unit

        if line.note and self.show_prices:
            order_line['note'] = line.note
        if line.delivery_note and not self.show_prices:
            order_line['note'] = line.delivery_note

        self.delivery['product'].append(order_line)

    def save(self, file_data):
        encoded_xml = xmltodict.unparse({'ditribution_list': self.root}, pretty=True).encode('utf-8')
        file_data.write(encoded_xml)

    def transmit(self, out_data):
        transmission = self.delivery_carrier.transmission and json.loads(self.delivery_carrier.transmission)
        if transmission.get('url') and transmission.get('user') and transmission.get('password'):
            headers = {'content-type': 'application/x-www-form-urlencoded'}
            values = {
                'utente': transmission['user'],
                'pass': transmission['password'],
                'tabella': out_data
            }
            response = requests.post(transmission['url'], headers=headers, data=values)
            if response.status_code in (200, 201):
                self.info.append('La lista di distribuzione inviata correttamente')
                return True
            elif response.status_code == 400:
                if hasattr(response, 'reason'):
                    self.info.append(response.reason)
                else:
                    self.info.append('Bad request')
                return False
            elif response.status_code == 401:
                self.info.append('Access is denied due to invalid credentials')
                return False
            elif response.status_code == 404:
                self.info.append("Something goes wrong, we received '{code}'".format(code=response.status_code))
            else:
                self.info.append("Something goes wrong, we received '{code}'".format(code=response.status_code))
                if hasattr(response, 'text'):
                    xmltodict.parse(response.text)['string']['#text']
                return False
        else:
            self.info.append(_("Some parameter (url/user/password) is wrong in transmission config"))
            return False
