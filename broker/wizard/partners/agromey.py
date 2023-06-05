# -*- encoding: utf-8 -*-
# =============================================================================
# For copyright and license notices, see __openerp__.py file in root directory
# =============================================================================

from collections import OrderedDict
import datetime
import xmltodict
import json
import os
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT
from openerp.exceptions import Warning
from .main import DistributionList


def translate_from_italian(text, language_code, customer_name=''):
    universal_dictionary = {
        'Italia': {
            'en_US': 'Italy',
            'nl_NL': 'Italie'
        },
        'Malta': {
            'en_US': 'Malta',
            'nl_NL': 'Malta'
        }
    }

    if text in universal_dictionary and language_code in universal_dictionary[text]:
        return universal_dictionary[text][language_code]
    else:
        raise Warning("Unable to find a translation for '{}' to '{} ({})".format(text, language_code, customer_name))


class Agromey(DistributionList):
    """
    {
        "default_transmission": "Agromey",
        "ADMIN": "AGRO2016",
        "file_path2": "/fornitori/agromey/orders/",
        "file_path": "/Users/andrei/Programming/lp/tmp_80"
    }
    """
    def __init__(self, show_prices, truck_info, currency_symbol, ignore_truck_info, dvce):
        super(Agromey, self).__init__(show_prices, truck_info, ignore_truck_info, dvce)

        self.root = OrderedDict()
        self.currency = currency_symbol
        self.delivery_carrier = False
        self.broker_order = False

    def supplier_header(self, broker_order):
        super(Agromey, self).supplier_header(broker_order)
        self.broker_order = broker_order

        self.transmission = json.loads(self.supplier.transmission)
        if not self.transmission.get('ADMIN'):
            raise Warning("'ADMIN' parameter is missing in transmission config")

        # Sign on Message Sent Request
        self.root['SIGNONMSGSRQ'] = OrderedDict(SONRQ=OrderedDict())

        self.root['SIGNONMSGSRQ']['SONRQ']['DTCLIENT'] = datetime.datetime.now().replace(microsecond=0).isoformat()
        self.root['SIGNONMSGSRQ']['SONRQ']['USERID'] = ''
        self.root['SIGNONMSGSRQ']['SONRQ']['USERPASS'] = ''
        self.root['SIGNONMSGSRQ']['SONRQ']['ADMIN'] = self.transmission['ADMIN']
        self.root['SIGNONMSGSRQ']['SONRQ']['APPID'] = '--'
        self.root['SIGNONMSGSRQ']['SONRQ']['APPVER'] = '--'

        # if broker_order.delivery_date and not self.show_prices:
        #     delivery_date = datetime.datetime.strptime(broker_order.delivery_date, DEFAULT_SERVER_DATETIME_FORMAT)
        #     self.root['SIGNONMSGSRQ']['delivery_date'] = delivery_date.strftime(DEFAULT_SERVER_DATE_FORMAT)

    def body_start(self):
        self.root['EBUSMSGSRQ'] = OrderedDict(EBUSTRNRQ=[])

    def customer_start(self, sale_order, address, customer_ref):
        super(Agromey, self).customer_start(sale_order, address, customer_ref)
        self.delivery = OrderedDict()

        # Purchase Order name
        self.delivery['TRNUID'] = self.name

        # Fixed Business Object value
        self.delivery['BUSOBJ'] = 'SO1'

        if not sale_order.date_order:
            self.info.append(u"Sale order '{}' Date is not set".format(sale_order.name))

        # if not sale_order.delivery_date:
        #     self.info.append(u"Sale order '{}' Delivery Date is not set".format(sale_order.name))

        customer_info = self.supplier.get_customer_ref(sale_order.partner_id.id)
        if not customer_info:
            # self.info.append(u"Customer Info missing for '{}'".format(sale_order.partner_id.name))
            raise Warning(u"Customer Info missing for '{}'. This field can't be empty".format(sale_order.partner_id.name))
        elif not customer_info.delivery_ref:
            self.info.append(u"Delivery Reference missing for '{}'".format(sale_order.partner_id.name))
            # raise Warning(u"Delivery Reference missing for '{}'".format(sale_order.partner_id.name))
        elif not customer_info.invoice_ref:
            self.info.append(u"Invoice Reference missing for '{}'".format(sale_order.partner_id.name))
            # raise Warning(u"Invoice Reference missing for '{}'".format(sale_order.partner_id.name))

        if sale_order.delivery_date:
            delivery_date = datetime.datetime.strptime(sale_order.delivery_date,
                                                       DEFAULT_SERVER_DATETIME_FORMAT)
        elif self.broker_order.delivery_date:
            delivery_date = datetime.datetime.strptime(self.broker_order.delivery_date,
                                                       DEFAULT_SERVER_DATETIME_FORMAT)
        else:
            raise Warning(u"Delivery date is missing. This field can't be left empty")

        self.delivery['ROWMODRQ'] = OrderedDict([
            ('@ALLOWADD', 'YES'),
            ('RECID', sale_order.name),
            ('RPL_DEL', customer_info.delivery_ref or customer_info.customer_ref),
            ('RPL_INV', customer_info.invoice_ref or customer_info.customer_ref),
            ('ORD_DATE', sale_order.date_order and datetime.datetime.strptime(
                sale_order.date_order, DEFAULT_SERVER_DATETIME_FORMAT).strftime('{^%Y-%m-%d}') or ''),
            ('DEL_DATE', delivery_date.strftime('{^%Y-%m-%d}')),
            ('SEL_CODE', address.country_id.code),
            ('COST_CODE', translate_from_italian(address.country_id.name, 'nl_NL', sale_order.partner_id.name).upper()),
            ('EMP_NR', 'VERONA'),
            ('COMMENT1', sale_order.note or 'ARRIVO {delivery_date}'.format(
                delivery_date=delivery_date.strftime('%d-%m')
            )),
            ('SO_LINE', [])
        ])

        # if not self.delivery['ROWMODRQ']['COMMENT1']:
        #     del self.delivery['ROWMODRQ']['COMMENT1']

    def customer_end(self):
        self.root['EBUSMSGSRQ']['EBUSTRNRQ'].append(self.delivery)

    def sale_order_line(self, line, box_qty):
        delivery_date = line.order_id.delivery_date or self.broker_order.delivery_date

        order_line = OrderedDict([
            # RECID=line.id,
            ('ART_CODE', line.product_id.get_partner_code_name(self.supplier.id)['code']),
            ('ART_DESC1', line.product_id.description or line.product_id.name),
            ('DEL_DATE', datetime.datetime.strptime(delivery_date, DEFAULT_SERVER_DATETIME_FORMAT).strftime('{^%Y-%m-%d}')),
            ('ORD_QTY', box_qty),
            # ART_QTY=box_qty,
            ('K1_KILO', line.product_id.product_uib),
            ('K1_PX_PKG', line.price_unit)
        ])

        if not order_line['ART_CODE']:
            self.info.append(u"Product '{}' has no code defined for '{}'".format(line.product_id.default_code, self.supplier.name))

        # if line.note and self.show_prices:
        #     order_line['note'] = line.note
        # if line.delivery_note and not self.show_prices:
        #     order_line['note'] = line.delivery_note

        self.delivery['ROWMODRQ']['SO_LINE'].append(order_line)

    def save(self, file_data):
        encoded_xml = xmltodict.unparse({'AVXML': self.root}, pretty=True, encoding='Windows-1252').encode('Windows-1252')
        file_data.write(encoded_xml)

    def transmit(self, out_data):
        if self.transmission.get('file_path'):
            if not os.path.isdir(os.path.join(self.transmission['file_path'], 'to_av')):
                os.mkdir(os.path.join(self.transmission['file_path'], 'to_av'))

            file(os.path.join(self.transmission['file_path'], 'to_av', self.name + u'.xml'), 'w').write(out_data)
            return True
        else:
            self.info.append("'file_path' parameter is missing in transmission config")
            return False
