# -*- encoding: utf-8 -*-
# =============================================================================
# For copyright and license notices, see __openerp__.py file in root directory
# =============================================================================

from collections import OrderedDict, defaultdict, namedtuple
from openerp import _

# The same fields as in 'sale.order.line'
Line = namedtuple('Line', [
    'id',
    'product_id',
    'box_qty',
    'price_unit',
    'note',
    'delivery_note',
    'total_weight',
    'order_id',
    'price_subtotal',
    'truck_info_id'
])


class OrderedDefaultDict(OrderedDict, defaultdict):
    def __init__(self, default_factory=None, *args, **kwargs):
        #in python3 you can omit the args to super
        super(OrderedDefaultDict, self).__init__(*args, **kwargs)
        self.default_factory = default_factory


class DistributionList(object):
    def __init__(self, show_prices, truck_info, ignore_truck_info, dvce):
        # If True - Purchase Order, else - Distribution List
        self.show_prices = show_prices
        self.row = 0
        self.total_boxes = 0
        self.total_weight = 0.0
        self.truck_info = truck_info
        self.ignore_truck_info = ignore_truck_info
        self.dvce = dvce
        self.info = []
        self.supplier = False
        self.deduplicated_order = OrderedDefaultDict(dict)
        self.delivery = OrderedDict()
        self.delivery_carrier = False
        self.delivery_date = False
        self.name = False
        self.transmission = False
        self.download_only = False

    def supplier_header(self, broker_order):
        self.supplier = broker_order.supplier_id
        self.name = broker_order.name
        self.delivery_date = broker_order.delivery_date

    def customer_start(self, sale_order, address, customer_ref):
        self.deduplicated_order.clear()

    def table_header(self):
        pass

    def grand_total(self):
        pass

    def body_start(self):
        pass

    def set_total_weight(self, weight):
        self.total_weight += weight

    def main(self, orders):
        self.body_start()
        for sale_order in orders:
            if sale_order.sale_order_on_truck(self.truck_info) or (self.ignore_truck_info and not self.truck_info):
                address = sale_order.partner_shipping_id

                if self.supplier.require_customer_ref:
                    # Modificato 06.07.2017 for Koffeman
                    # customer_ref = self.supplier.get_customer_ref(sale_order.partner_id.id)
                    customer_ref = self.supplier.get_customer_ref(sale_order.partner_shipping_id.id)
                    if customer_ref and customer_ref.customer_ref:
                        customer_ref = customer_ref.customer_ref
                    else:
                        self.info.append(_(u"Missing Customer Ref for customer '{}'").format(sale_order.partner_id.name))
                        customer_ref = ''
                else:
                    customer_ref = ''

                self.customer_start(sale_order, address, customer_ref)

                for line in sale_order.order_line.sorted(key=lambda line: line.product_id.name):
                    if self.ignore_truck_info and not self.truck_info or line.truck_info_id.id in self.truck_info.ids:
                        if line.product_id.product_uib:
                            box_qty = int(line.product_uom_qty)
                        else:
                            box_qty = 0

                        self.total_boxes += box_qty

                        self.set_total_weight(box_qty * line.product_id.product_uib)

                        if self.ignore_truck_info and not self.truck_info:
                            self.set_deduplicated_line(line, box_qty)
                        else:
                            self.sale_order_line(line, box_qty)

                if self.ignore_truck_info and not self.truck_info:
                    for line in self.get_deduplicated_line():
                        self.sale_order_line(line, line.box_qty)

                self.customer_end()

        self.body_end()

    def body_end(self):
        self.grand_total()

    def set_deduplicated_line(self, line, box_qty):
        if line.product_id.id in self.deduplicated_order:
            if line.price_unit in self.deduplicated_order[line.product_id.id]:
                new_box_qty = self.deduplicated_order[line.product_id.id][line.price_unit].box_qty + box_qty
                new_weight = new_box_qty * line.product_id.product_uib
                self.deduplicated_order[line.product_id.id][line.price_unit] = self.deduplicated_order[line.product_id.id][line.price_unit]._replace(
                    box_qty=new_box_qty,
                    total_weight=new_weight
                )
            else:
                self.deduplicated_order[line.product_id.id][line.price_unit] = self.get_line(line, box_qty)
        else:
            self.deduplicated_order[line.product_id.id][line.price_unit] = self.get_line(line, box_qty)

    def get_line(self, line, box_qty):
        return Line(
            line.id,
            line.product_id,
            box_qty,
            line.price_unit,
            line.note,
            line.delivery_note,
            line.total_weight,
            line.order_id,
            line.price_subtotal,
            line.truck_info_id
        )

    def get_deduplicated_line(self):
        for product_id, prices in self.deduplicated_order.items():
            for price, line in prices.items():
                yield line

    def customer_end(self):
        pass

    def sale_order_line(self, line, box_qty):
        pass

    def order_total(self, first_row, last_row):
        pass

    def save(self, file_data):
        pass

    def transmit(self, out_data):
        pass
