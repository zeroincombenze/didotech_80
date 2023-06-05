# -*- encoding: utf-8 -*-
# =============================================================================
# For copyright and license notices, see __openerp__.py file in root directory
# =============================================================================

from openerp import models, fields, api
from openerp.tools.translate import _
import openerp.addons.decimal_precision as dp


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.depends(
        'order_line.total_weight',
        'order_line.price_unit',
        'order_line.tax_id',
        'order_line.discount',
        'order_line.product_uom_qty'
    )
    def _amount_all_wrapper(self):
        """ Wrapper because of direct method passing as parameter for function fields """
        if isinstance(self.id, (int, float)):
            self.env.invalidate_all()
            result = super(SaleOrder, self)._amount_all('any field', 'args')[self.id]
            self.amount_untaxed = result['amount_untaxed']
            self.amount_tax = result['amount_tax']
            self.amount_total = result['amount_total']

    broker_order_id = fields.Many2one('broker.purchase.order', string=_('Purchase Order'))
    delivery_date = fields.Datetime('Delivery Date', required=False, readonly=False)
    delivery_note = fields.Text(_('Delivery Note'))

    amount_untaxed = fields.Float(compute=_amount_all_wrapper)
    amount_tax = fields.Float(compute=_amount_all_wrapper)
    amount_total = fields.Float(compute=_amount_all_wrapper)

    supplier_order_number = fields.Char('Supplier Order', readonly=True)
    supplier_order_id = fields.Integer('Supplier Order ID', readonly=True)

    @api.multi
    def patch(self, values):
        if values.get('order_line'):
            sale_order_line_obj = self.env['sale.order.line']
            for value_line in values['order_line']:
                if value_line.get('line_id'):
                    order_line = sale_order_line_obj.browse(value_line['line_id'])
                    del value_line['line_id']
                    if value_line:
                        order_line.write(value_line)
                    else:
                        order_line.unlink()
                else:
                    value_line['order_id'] = self.id
                    sale_order_line_obj.create(value_line)

            del values['order_line']

        if values:
            self.write(values)

        return self.env['rest.ful'].get(self.ids)

    @api.multi
    def get_biggest_screen_ref(self):
        screen_ref = 0
        for line in self.order_line:
            if screen_ref < line.screen_ref:
                screen_ref = line.screen_ref

        return screen_ref

    @api.multi
    def sale_order_on_truck(self, truck_info):
        return self.env['sale.order.line'].search(
            [('order_id', '=', self.id), ('truck_info_id', 'in', truck_info.ids)])

    @api.multi
    def write(self, values):
        if values.get('broker_order_id'):
            for order in self:
                customer_supplier_info = self.env['broker.purchase.order'].browse(values['broker_order_id']).supplier_id.get_customer_ref(order.partner_id.id)
                if customer_supplier_info and customer_supplier_info.payment_term_id:
                    order.payment_term = customer_supplier_info.payment_term_id.id

        return super(SaleOrder, self).write(values)

    @api.model
    def _prepare_invoice(self, order, lines):
        values = super(SaleOrder, self)._prepare_invoice(order, lines)
        if order.broker_order_id.supplier_id:
            values['supplier_id'] = order.broker_order_id.supplier_id.id
        return values

    @api.multi
    def confirm_order(self):
        view_rec = self.env['ir.model.data'].get_object_reference('broker', 'confirm_orders_form')
        if view_rec:
            view_id = view_rec and view_rec[1] or False

        return {
            'type': 'ir.actions.act_window',
            'name': _('Confirm Orders'),
            'res_model': 'wizard.confirm.orders',
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': [view_id],
            'target': 'new',
            'res_id': False,
            'context': {'model': self._name, 'active_id': self.id}
        }


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    carrier_id = fields.Many2one("delivery.carrier", string="Delivery Method")
    truck_info_id = fields.Many2one('broker.truck.info', string=_('Truck info'))
    note = fields.Text(_('Note'))
    delivery_note = fields.Text(_('Delivery Note'))
    product_uib = fields.Float(related='product_id.product_uib', string=_('Box weight (kg)'), readonly=True)
    # product_uib = fields.Float(string=_('Box weight (kg)'))
    price_subtotal = fields.Float(compute='get_amount_line', string='Subtotal', digits_compute=dp.get_precision('Account'))
    screen_ref = fields.Integer(_('Screen Ref'), default=0)
    total_weight = fields.Float(_('Total weight'))

    @api.one
    def get_amount_line(self):
        tax_obj = self.env['account.tax']

        price = self.price_unit * (1 - (self.discount or 0.0) / 100.0)

        if self.product_uib:
            # taxes = tax_obj.compute_all(price, self.product_uom_qty * self.product_uib, self.product_id, self.order_id.partner_id)
            taxes = tax_obj.compute_all(price, self.total_weight, self.product_id, self.order_id.partner_id)
        else:
            taxes = tax_obj.compute_all(price, self.product_uom_qty, self.product_id, self.order_id.partner_id)

        cur = self.order_id.pricelist_id.currency_id
        self.price_subtotal = cur.round(taxes['total'])

    @api.model
    def create(self, values):
        if values.get('truck_info'):
            truck_info = values['truck_info']
            del values['truck_info']
        else:
            truck_info = '-'

        values['truck_info_id'] = self.env['broker.truck.info'].get_create(truck_info).id
        new_line = super(SaleOrderLine, self).create(values)

        if new_line.order_id.broker_order_id and new_line.screen_ref > new_line.order_id.broker_order_id.last_screen_ref:
            new_line.order_id.broker_order_id.last_screen_ref = new_line.screen_ref

        # if not new_line.product_uib and new_line.product_id and new_line.product_id.product_uib:
        #     new_line.product_uib = new_line.product_id.product_uib

        if not new_line.total_weight and new_line.product_id and new_line.product_id.product_uib:
            new_line.total_weight = new_line.product_id.product_uib * new_line.product_uom_qty

        return new_line

    def product_id_change(self, cr, uid, ids, pricelist, product_id, qty=0,
                          uom=False, qty_uos=0, uos=False, name='', partner_id=False,
                          lang=False, update_tax=True, date_order=False, packaging=False, fiscal_position=False,
                          flag=False, context=None):

        values = super(SaleOrderLine, self).product_id_change(cr, uid, ids, pricelist, product_id, qty=qty, uom=uom,
                                                              qty_uos=qty_uos, uos=uos, name=name, partner_id=partner_id,
                                                              lang=lang, update_tax=update_tax, date_order=date_order,
                                                              packaging=packaging, fiscal_position=fiscal_position,
                                                              flag=flag, context=context)
        # print values
        if product_id:
            product = self.pool['product.product'].browse(cr, uid, product_id, context)
            if product.product_uib:
                # values['value']['product_uib'] = product.product_uib
                values['value']['total_weight'] = product.product_uib * qty

        return values

    # @api.one
    # @api.onchange('product_uib')
    # def on_change_product_uib(self):
    #     self.total_weight = self.product_uom_qty * self.product_uib

    @api.model
    def _prepare_order_line_invoice_line(self, line, account_id=False):
        values = super(SaleOrderLine, self)._prepare_order_line_invoice_line(line, account_id)

        if line.product_id and line.product_id.product_uib:
            values['quantity'] = line.total_weight or line.product_uom_qty * line.product_id.product_uib

        return values
