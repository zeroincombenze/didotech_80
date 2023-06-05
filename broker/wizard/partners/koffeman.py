# -*- encoding: utf-8 -*-
# =============================================================================
# For copyright and license notices, see __openerp__.py file in root directory
# =============================================================================
#

import json
import datetime
from .main import DistributionList
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT
from openerp.exceptions import Warning
from .oauth import Communication
import pprint


class CustomerOrder(dict):
    def __init__(self, customer_ref, order_date, sale_order):
        super(CustomerOrder, self).__init__()
        self['customer'] = customer_ref
        self['date'] = {
            'year': str(order_date.year),
            'month': str(order_date.month),
            'day': str(order_date.day)
        }
        self['row'] = {}
        self.counter = self.count()
        self.sale_order = sale_order

    def count(self, start=0):
        start -= 1
        while True:
            start += 1
            yield start

    def __setitem__(self, key, value):
        if key == 'row' and 'row' in self.__dict__.keys():
            self.__dict__[key][str(self.counter.next())] = value
        else:
            super(CustomerOrder, self).__setattr__(key, value)

    def __str__(self):
        return json.dumps(self.get())

    def as_dict(self):
        return {
            'customer': self.customer,
            'date': self.date,
            'row': self.row
        }


class Koffeman(DistributionList):
    def __init__(self, show_prices, truck_info, currency_symbol, ignore_truck_info, dvce):
        super(Koffeman, self).__init__(show_prices, truck_info, ignore_truck_info, dvce)

        self.orders = []
        self.order = None
        self.koffeman = None

    def supplier_header(self, broker_order):
        super(Koffeman, self).supplier_header(broker_order)
        access = json.loads(self.supplier.transmission)
        self.koffeman = Communication(access)

    def customer_start(self, sale_order, address, customer_ref):
        super(Koffeman, self).customer_start(sale_order, address, customer_ref)

        delivery_date = sale_order.delivery_date or self.delivery_date

        if delivery_date:
            order_date = datetime.datetime.strptime(delivery_date, DEFAULT_SERVER_DATETIME_FORMAT)
        else:
            raise Warning(u"Sale order '{}' Delivery Date is not set".format(sale_order.name))

        # Verify customer_ref:
        if not self.koffeman.get_record('customers/code', customer_ref):
            raise Warning(u"Please check reference for customer '{}'".format(sale_order.partner_id.name))

        self.order = CustomerOrder(customer_ref, order_date, sale_order)

    def sale_order_line(self, line, box_qty):
        partner_product_code = line.product_id.get_partner_code_name(self.supplier.id)['code']
        if not partner_product_code:
            raise Warning(u"Please set reference for product '{}'".format(line.product_id.name))

        self.order['row'] = {
            'product': partner_product_code,
            # 'amount': str(line.price_subtotal),
            # This is total in kilograms!!!
            'amount': str(box_qty * line.product_id.product_uib),
            'price': str(line.price_unit),
            'extra': line.product_id.name
        }

    def customer_end(self):
        self.orders.append({
            'order': self.order.as_dict(),
            'origin': self.order.sale_order
        })

    def save(self, file_data):
        file_data.write(pprint.pformat(self.orders, indent=4))

    def transmit(self, out_data):
        for order in self.orders:
            reply = self.koffeman.transmit_order({'order': order['order']})
            if reply['status'] == 'success':
                order['origin'].supplier_order_number = reply['ordernumber']
                order['origin'].supplier_order_id = reply['id']
        return True
