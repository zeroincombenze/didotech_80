# -*- encoding: utf-8 -*-
# =============================================================================
# For copyright and license notices, see __openerp__.py file in root directory
# =============================================================================

from xlwt import Workbook, easyxf, Formula
import datetime
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT
from .main import DistributionList


class Excel(DistributionList):
    bold = easyxf('font: bold on')
    bold_right = easyxf('font: bold on; align: horiz right; borders: top thin, bottom thin, left thin, right thin')
    bold_left = easyxf('font: bold on; align: horiz left; borders: top thin, bottom thin, left thin, right thin')
    normal = easyxf('font: bold off; borders: top thin, bottom thin, left thin, right thin')
    normal_no_top = easyxf('font: bold off; borders: bottom thin, left thin, right thin')
    normal_right = easyxf('font: bold off; align: horiz right; borders: top thin, bottom thin, left thin, right thin')

    table = {
        0: {'width': 4000},
        1: {'width': 11000},
        2: {'width': 3000},
        3: {'width': 3000},
        4: {'width': 3000},
        5: {'width': 3000},
    }

    def __init__(self, show_prices, truck_info, currency_symbol, ignore_truck_info, dvce):
        super(Excel, self).__init__(show_prices, truck_info, ignore_truck_info, dvce)
        self.book = Workbook(encoding='utf-8')
        self.ws = self.book.add_sheet('1')

        for column in range(0, 5):
            self.ws.col(column).width = self.table[column]['width']

        self.currency = easyxf('align: horiz right; borders: top thin, bottom thin, left thin, right thin',
                               num_format_str=u'{symbol}#,##0.00'.format(symbol=currency_symbol))
        self.first_row = 0
        self.download_only = True
        self.grand_first_row = 0
        self.grand_last_row = 0

    def supplier_header(self, broker_order):
        super(Excel, self).supplier_header(broker_order)
        if self.show_prices:
            self.ws.write(self.row, 0, broker_order.name, self.bold_right)
            self.ws.write(self.row, 1, broker_order.supplier_id.name, self.bold)
        else:
            self.ws.write(self.row, 1, broker_order.supplier_id.name, self.bold)

        self.row += 1

        if broker_order.delivery_date and not self.show_prices:
            self.ws.write(self.row, 0, 'Delivery Date:', self.normal_right)
            delivery_date = datetime.datetime.strptime(broker_order.delivery_date, DEFAULT_SERVER_DATETIME_FORMAT)
            self.ws.write(self.row, 1, delivery_date.strftime(DEFAULT_SERVER_DATE_FORMAT))
            self.row += 1

        if not self.ignore_truck_info and not self.truck_info.name == '-':
            self.ws.write(self.row, 0, 'Truck info:', self.normal_right)
            self.ws.write(self.row, 1, self.truck_info.name)
            self.row += 1

        if self.dvce:
            self.ws.write(self.row, 0, 'DVCE:', self.normal_right)
            self.ws.write(self.row, 1, self.dvce)
            self.row += 1

        self.row += 1

    def customer_start(self, sale_order, address, customer_ref):
        super(Excel, self).customer_start(sale_order, address, customer_ref)

        if self.show_prices:
            partner_name = sale_order.partner_id.name
        else:
            customer_info = self.supplier.get_customer_ref(address.id)
            if customer_info:
                customer_ref = customer_info.customer_ref

            partner_name = address.name

        if customer_ref:
            partner_name = u"({ref}) {name}".format(ref=customer_ref, name=partner_name)
        else:
            partner_name = partner_name

        if self.show_prices:
            self.ws.write(self.row, 0, sale_order.name, self.bold_right)

        self.ws.write(self.row, 1, partner_name, self.bold)

        self.row += 1

        self.ws.write(self.row, 1,
                      u"{address.street} {address.zip} {address.city}{province} {address.country_id.name}".format(
                          address=address, province=address.province and ' (' + address.province.code + ')' or ''))

        self.row += 1

        if sale_order.delivery_date and not self.show_prices:
            delivery_date = datetime.datetime.strptime(sale_order.delivery_date, DEFAULT_SERVER_DATETIME_FORMAT)
            delivery_date = delivery_date.strftime(DEFAULT_SERVER_DATE_FORMAT)
            self.ws.write(self.row, 0, 'Delivery Date:', self.normal_right)
            self.ws.write(self.row, 1, delivery_date)
            self.row += 1

        if sale_order.delivery_note:
            self.ws.write(self.row, 0, u"Note", self.normal_right)
            self.ws.write(self.row, 1, sale_order.delivery_note)
            self.row += 1

        if sale_order.partner_shipping_id.auth_number and not self.show_prices:
            self.ws.write(self.row, 0, u"Auth Number", self.normal_right)
            self.ws.write(self.row, 1, sale_order.partner_shipping_id.auth_number)
            self.row += 1

        self.table_header()

        self.first_row = self.row + 1

        if not self.grand_first_row:
            self.grand_first_row = self.row + 1

    def customer_end(self):
        self.order_total(self.first_row, self.row)
        self.grand_last_row = self.row - 1

    def table_header(self):
        self.ws.write(self.row, 0, '', self.bold_left)
        self.ws.write(self.row, 1, '', self.bold_left)
        self.ws.write(self.row, 2, 'Casse', self.bold_left)
        self.ws.write(self.row, 3, 'Peso cassa', self.bold_left)
        self.ws.write(self.row, 4, 'Peso totale (kg)', self.bold_left)
        if self.show_prices:
            self.ws.write(self.row, 5, 'Price', self.bold_left)

        self.row += 1

    def sale_order_line(self, line, box_qty):
        if self.show_prices:
            # Line.id is used to import lines in purchase order
            self.ws.write(self.row, 0, line.id, self.normal)
        else:
            self.ws.write(self.row, 0, line.product_id.get_partner_code_name(self.supplier.id)['code'], self.normal)

        self.ws.write(self.row, 1, line.product_id.description or line.product_id.name, self.normal)
        self.ws.write(self.row, 2, box_qty, self.normal)
        self.ws.write(self.row, 3, line.product_id.product_uib, self.normal)

        # self.ws.write(self.row, 4, Formula("C{row}*D{row})".format(row=self.row + 1)), self.normal)
        self.ws.write(self.row, 4, line.total_weight, self.normal)

        if self.show_prices:
            self.ws.write(self.row, 5, line.price_unit, self.currency)

        # Truck info (enable for debug)
        # self.ws.write(self.row, 6, line.truck_info_id and line.truck_info_id.name, self.currency)

        if line.note and self.show_prices:
            self.row += 1
            self.ws.write(self.row, 0, u'Note:', self.normal_right)
            self.ws.write(self.row, 1, line.note, self.normal)
        if line.delivery_note and not self.show_prices:
            self.row += 1
            self.ws.write(self.row, 0, u'Note:', self.normal_right)
            self.ws.write(self.row, 1, line.delivery_note, self.normal)

        self.row += 1

    def order_total(self, first_row, last_row):
        self.ws.write(self.row, 0, '', self.normal)
        self.ws.write(self.row, 1, u'Total', self.bold_right)
        self.ws.write(self.row, 2, Formula('SUM(C{first}:C{last})'.format(first=first_row, last=last_row)), self.bold_right)
        self.ws.write(self.row, 3, '', self.normal)
        self.ws.write(self.row, 4, Formula('SUM(E{first}:E{last})'.format(first=first_row, last=last_row)), self.bold_right)
        if self.show_prices:
            self.ws.write(self.row, 5, '', self.normal)

        self.row += 2

    def grand_total(self):
        self.ws.write(self.row, 1, u'Grand Total', self.bold_right)
        # self.ws.write(self.row, 2, self.total_boxes, self.bold_right)
        self.ws.write(
            self.row, 2,
            Formula('SUM(C{first}:C{last})/2'.format(first=self.grand_first_row, last=self.grand_last_row)),
            self.bold_right
        )
        self.ws.write(self.row, 3, '', self.normal)
        # self.ws.write(self.row, 4, self.total_weight, self.bold_right)
        self.ws.write(
            self.row, 4,
            Formula('SUM(E{first}:E{last})/2'.format(first=self.grand_first_row, last=self.grand_last_row)),
            self.bold_right
        )

    def save(self, file_data):
        self.book.save(file_data)


class ExcelPurchaseOrder(DistributionList):
    bold = easyxf('font: bold on')
    bold_right = easyxf('font: bold on; align: horiz right; borders: top thin, bottom thin, left thin, right thin')
    bold_left = easyxf('font: bold on; align: horiz left; borders: top thin, bottom thin, left thin, right thin')
    normal = easyxf('font: bold off; borders: top thin, bottom thin, left thin, right thin')
    normal_no_top = easyxf('font: bold off; borders: bottom thin, left thin, right thin')
    normal_right = easyxf('font: bold off; align: horiz right; borders: top thin, bottom thin, left thin, right thin')

    table = {
        0: {'width': 1500},
        1: {'width': 2000},
        2: {'width': 11000},
        3: {'width': 2000},
        4: {'width': 3500},
        5: {'width': 3000},
        6: {'width': 3000},
    }

    def __init__(self, show_prices, truck_info, currency_symbol, ignore_truck_info, dvce):
        super(ExcelPurchaseOrder, self).__init__(show_prices, truck_info, ignore_truck_info, dvce)
        self.book = Workbook(encoding='utf-8')
        self.ws = self.book.add_sheet('1')

        for column in range(0, 5):
            self.ws.col(column).width = self.table[column]['width']

        self.currency = easyxf('align: horiz right; borders: top thin, bottom thin, left thin, right thin',
                               num_format_str=u'{symbol}#,##0.00'.format(symbol=currency_symbol))
        self.currency_bold = easyxf('font: bold on; align: horiz right; borders: top thin, bottom thin, left thin, right thin',
                               num_format_str=u'{symbol}#,##0.00'.format(symbol=currency_symbol))

        self.first_row = 0
        self.grand_first_row = 0
        self.grand_last_row = 0
        self.download_only = True

    def supplier_header(self, broker_order):
        super(ExcelPurchaseOrder, self).supplier_header(broker_order)

        self.ws.write(self.row, 1, broker_order.name, self.bold_right)
        self.ws.write(self.row, 2, broker_order.supplier_id.name, self.bold)

        self.row += 1
        self.row += 1

    def customer_start(self, sale_order, address, customer_ref):
        super(ExcelPurchaseOrder, self).customer_start(sale_order, address, customer_ref)

        # partner_name = sale_order.partner_id.name
        partner_name = address.name

        self.ws.write(self.row, 1, sale_order.name, self.bold_right)

        self.ws.write(self.row, 2, partner_name, self.bold)
        self.row += 1

        self.table_header()

        self.first_row = self.row + 1

        if not self.grand_first_row:
            self.grand_first_row = self.row + 1

    def customer_end(self):
        self.order_total(self.first_row)
        self.grand_last_row = self.row - 1

    def table_header(self):
        self.ws.write(self.row, 1, '', self.bold_left)
        self.ws.write(self.row, 2, '', self.bold_left)
        self.ws.write(self.row, 3, 'Casse', self.bold_left)
        self.ws.write(self.row, 4, 'Peso totale (kg)', self.bold_left)
        self.ws.write(self.row, 5, 'Price', self.bold_left)
        self.ws.write(self.row, 6, 'Total Price', self.bold_left)

        self.row += 1

    def sale_order_line(self, line, box_qty):
        self.ws.write(self.row, 0, line.id, self.normal)
        self.ws.write(self.row, 1, line.product_id.get_partner_code_name(self.supplier.id)['code'], self.normal)
        self.ws.write(self.row, 2, line.product_id.description or line.product_id.name, self.normal)
        self.ws.write(self.row, 3, box_qty or 0, self.normal)
        self.ws.write(self.row, 4, line.total_weight or 0, self.normal)
        self.ws.write(self.row, 5, line.price_unit, self.currency)
        self.ws.write(self.row, 6, Formula("E{row}*F{row})".format(row=self.row + 1)), self.currency)

        self.row += 1

    def order_total(self, first_row):
        last_row = self.row
        if first_row <= last_row:
            self.ws.write(self.row, 0, '', self.normal)
            self.ws.write(self.row, 1, '', self.normal)
            self.ws.write(self.row, 2, u'Total', self.bold_right)
            # if first_row > last_row:
            #     self.ws.write(self.row, 3, 0, self.bold_right)
            #     self.ws.write(self.row, 6, 0, self.currency_bold)
            # else:
            self.ws.write(self.row, 3, Formula('SUM(D{first}:D{last})'.format(first=first_row, last=last_row)), self.bold_right)
            self.ws.write(self.row, 4, Formula('SUM(E{first}:E{last})'.format(first=first_row, last=last_row)), self.bold_right)
            self.ws.write(self.row, 5, '', self.normal)
            self.ws.write(self.row, 6, Formula('SUM(G{first}:G{last})'.format(first=first_row, last=last_row)), self.currency_bold)

            self.row += 2
        else:
            self.row += 1

    def grand_total(self):
        self.ws.write(self.row, 2, u'Grand Total', self.bold_right)
        self.ws.write(self.row, 3, self.total_boxes, self.bold_right)
        self.ws.write(self.row, 4,
                      Formula('SUM(E{first}:E{last})/2'.format(first=self.grand_first_row, last=self.grand_last_row)), self.normal)
        self.ws.write(self.row, 5, '', self.normal)
        self.ws.write(self.row, 6,
                      Formula('SUM(G{first}:G{last})/2'.format(first=self.grand_first_row, last=self.grand_last_row)),
                      self.currency_bold)

    def save(self, file_data):
        self.book.save(file_data)
