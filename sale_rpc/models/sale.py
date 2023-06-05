# -*- encoding: utf-8 -*-
# =============================================================================
# For copyright and license notices, see __openerp__.py file in root directory
# =============================================================================

from openerp import models, api, fields, _
from datetime import datetime
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT
from exceptions import *
import json
import logging
_logger = logging.getLogger(__name__)
_logger.setLevel(logging.DEBUG)


class DeliveryCarrier(models.Model):
    _inherit = 'delivery.carrier'

    @api.model
    def get_default_carrier_id(self):
        carriers = self.search([])
        return carriers and carriers[0].id or False


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    promocode = fields.Char(related='pricelist_id.code', readonly=True)

    class Meta:
        context = {
            'model': 'sale.order',
            'fields': (
                'name', 'partner_id', 'partner_shipping_id', 'date_order', 'order_line', 'payment_term',
                'payment_acquirer', 'state', 'amount_untaxed', 'amount_tax', 'amount_total',
                'carrier_id', 'note', 'pricelist_id'
            ),
            'fields_map': {
                'order_line': (
                    'name', 'product_tmpl_id', 'product_id', 'product_uom_qty', 'price_unit', 'shipping', 'note'
                ),
                'partner_id': ('name',),
                'product_tmpl_id': ('name', 'taxes'),
                'product_id': ('name', 'image_medium', 'lst_price'),
                'payment_term': ('name',),
                'carrier_id': ('name',),
                'partner_shipping_id': (
                    'name', 'street', 'street2', 'zip', 'city', 'region', 'country_id', 'email', 'phone', 'mobile',
                    'fiscalcode', 'vat'
                ),
                'country_id': ('name',),
                'pricelist_id': ('name', 'code')
            }
        }

    @api.model
    def create(self, values):
        """
        {'campaign_id': False,
         'carrier_id': False,
         'categ_ids': [[6, False, []]],
         'client_order_ref': False,
         'date_order': '2015-11-03 09:00:46',
         'fiscal_position': False,
         'incoterm': False,
         'medium_id': False,
         'message_follower_ids': False,
         'message_ids': False,
         'note': False,
         'order_line': [
             [0,
                 False,
                 {'delay': 7,
                  'discount': 0,
                  'name': '[W102] W102 155/70R13',
                  'note': False,
                  'price_unit': 0,
                  'product_id': 193,      -> product_variant_id
                  'product_packaging': False,
                  'product_uom': 1,
                  'product_uom_qty': 4,
                  'product_uos': False,
                  'product_uos_qty': 4,
                  'route_id': False,
                  'tax_id': [[6, False, [1]]],
                  'th_weight': 0}],
             [0,
                 False,
                 {'delay': 0,
                  'discount': 0,
                  'name': 'Product description',
                  'note': False,
                  'price_unit': 230,
                  'product_id': False,
                  'product_packaging': False,
                  'product_uom': 1,
                  'product_uom_qty': 1,
                  'product_uos': False,
                  'product_uos_qty': 1,
                  'route_id': False,
                  'tax_id': [[6, False, []]],
                  'th_weight': 0}]
         ],
         'order_policy': 'manual',
         'origin': False,
         'partner_id': 14,
         'partner_invoice_id': 14,
         'partner_shipping_id': 14,
         'payment_term': False,
         'picking_policy': 'direct',
         'pricelist_id': 1,
         'project_id': False,
         'section_id': False,
         'source_id': False,
         'user_id': 1,
         'warehouse_id': 1}
        """

        if values.get('ecommerce'):
            del values['ecommerce']
            partner_obj = self.env['res.partner']

            payment_acquirers = self.env['payment.acquirer'].search([('website_published', '=', True)])
            for acquirer in payment_acquirers:
                if hasattr(acquirer, 'payment_term_id') and acquirer.payment_term_id:
                    payment_term = acquirer.payment_term_id.id
                    break
            else:
                payment_term = False

            carriers = self.env['delivery.carrier'].search([])

            default_order = {
                # 'campaign_id': False,  # *
                'carrier_id': carriers and carriers[0].id or False,
                # 'categ_ids': [[6, False, []]],  # *
                'client_order_ref': False,
                'date_order': datetime.now().strftime(DEFAULT_SERVER_DATETIME_FORMAT),
                'fiscal_position': False,
                'incoterm': False,
                # 'medium_id': False,  # *
                'message_follower_ids': False,
                'message_ids': False,
                'note': False,
                'order_line': [],
                'order_policy': 'manual',
                'origin': False,
                'payment_term': payment_term,
                'picking_policy': 'direct',
                'project_id': False,
                'section_id': False,
                # 'source_id': False,  # *
                'user_id': 1,
                'warehouse_id': 1
            }

            if not values.get('partner_id'):
                if values.get('partner'):
                    partner = values['partner']
                    if partner.get('ext_partner_id'):
                        res_partner = partner_obj.search([('ext_partner_id', '=', partner['ext_partner_id'])])
                        if res_partner:
                            if not partner_obj.get_hash(partner) == res_partner.data_hash:
                                res_partner.write(partner)
                        else:
                            res_partner = partner_obj.create(partner)

                        values['partner_id'] = res_partner.id
                        values['pricelist_id'] = values.get('pricelist_id', res_partner.property_product_pricelist.id)
                    else:
                        _logger.error(u"ext_partner_id is mandatory if partner properties are present")
                        return False

                    del values['partner']
                else:
                    values['partner_id'] = self._uid

            if values.get('promocode'):
                pricelist = self.env['product.pricelist'].get_pricelist(values['promocode'], values['partner_id'])
                if pricelist.get('pricelist'):
                    values['pricelist_id'] = pricelist['pricelist'].id

                if pricelist.get('info'):
                    info = pricelist['info']

                del values['promocode']

            if values.get('shipping_address'):
                shipping_address = partner_obj.search([
                    ('data_hash', '=', partner_obj.get_hash(values['shipping_address'])),
                    '|',
                    ('id', '=', values['partner_id']),
                    ('parent_id', '=', values['partner_id']),
                ])

                if not shipping_address:
                    shipping_address = partner_obj.search([
                        ('name', '=', 'Shipping address'),
                        ('parent_id', '=', values['partner_id'])
                    ])

                    if shipping_address:
                        shipping_address.write(values['shipping_address'])
                    else:
                        values['shipping_address']['parent_id'] = values['partner_id']
                        values['shipping_address']['name'] = 'Shipping address'
                        shipping_address = partner_obj.create(values['shipping_address'])
                values['partner_shipping_id'] = shipping_address.id

                del values['shipping_address']

            if not values.get('carrier_id'):
                values['carrier_id'] = self.env['delivery.carrier'].get_default_carrier_id()

            if values.get('order_line'):
                for line in values['order_line']:
                    default_line = {
                        'delay': 0,
                        'discount': 0,
                        'name': 'no name',
                        'description': 'no description',
                        'note': False,
                        'price_unit': 0,
                        'product_id': False,
                        'product_packaging': False,
                        'product_uom': 1,
                        'product_uom_qty': 1,
                        'product_uos': False,
                        'product_uos_qty': 1,
                        'route_id': False,
                        'tax_id': [[6, False, []]],
                        'th_weight': 0
                    }

                    if line[2].get('product_variant_id'):
                        product = self.env['product.product'].browse(line[2]['product_variant_id'])
                        del line[2]['product_variant_id']

                        line[2] = self.env['sale.order.line'].collect_missing_values(
                            product,
                            line[2],
                            pricelist_id=values.get('pricelist_id', False),
                            partner_id=values['partner_id']
                        )

                    elif line[2].get('ext_product_id'):
                        product = self.env['product.product'].external_get_or_create(line[2])
                        del line[2]['ext_product_id']

                        line[2] = self.env['sale.order.line'].collect_missing_values(
                            product,
                            line[2],
                            pricelist_id=values.get('pricelist_id', False),
                            partner_id=values['partner_id']
                        )

                    elif 'tax_id' not in line[2]:
                        # Get default taxes:
                        tax_ids = self.env['ir.values'].get_default(
                            'product.template', 'taxes_id', company_id=self.env.user.company_id.id
                        )
                        line[2]['tax_id'] = [(6, 0, tax_ids)]

                    if not line[2].get('name') and line[2].get('description'):
                        line[2]['name'] = line[2].get('description')
                        del line[2]['description']

                    default_line.update(line[2])
                    line[2] = default_line

            default_order.update(values)
            values = default_order

        new_order = super(SaleOrder, self).create(values)
        if self.env.user.company_id.auto_delivery_cost:
            new_order.delivery_set()
        return new_order

    @api.model
    def json_create(self, values):
        try:
            new_order = self.create(values)
            if new_order:
                return json.loads(self.env['rest.ful'].with_context(self.Meta.context).get(new_order.id))
            else:
                return {'error': 'Unable to create Sale Order', 'status': 400}
        except AttributeError:
            return {'error': 'Unable to create Sale Order, check your data', 'status': 400}
        except:
            return {'error': 'Unable to create Sale Order, something goes wrong', 'status': 400}
        else:
            return {'error': 'Unable to create Sale Order', 'status': 400}

    @api.multi
    def json_write(self, values):
        try:
            self.write(values)
            return json.loads(self.env['rest.ful'].with_context(self.Meta.context).get(self.id))
        except:
            return {'error': 'Unable to update Sale Order, something goes wrong', 'status': 400}

    @api.multi
    def json_unlink(self):
        try:
            self.unlink()
            return {'results': 'Sale Order deleted successfully', 'status': 200}
        except:
            return {'error': 'Unable to update Sale Order, something goes wrong', 'status': 400}

    @api.model
    def json_list(self, partner_remote_id=False):
        if partner_remote_id:
            partner = self.env['res.partner'].search([('ext_partner_id', '=', partner_remote_id)])
            if partner:
                sale_orders = self.search([('partner_id', '=', partner.id)])
                if sale_orders:
                    return json.loads(self.env['rest.ful'].with_context(self.Meta.context).get(sale_orders.ids))
                else:
                    return {'results': [], 'status': 200, 'count': 0}
            else:
                return {'error': "Partner with this ID does not exists in Odoo database", 'status': 404}
        else:
            return {'error': "Partner is required", 'status': 400}

    @api.one
    def eorder_confirm(self):
        # print('STATE:', self.state)
        self.signal_workflow('order_confirm')
        # print('STATE (2):', self.state)
        if self.pricelist_id:
            self.pricelist_id.update_blacklist(self.partner_id.id)

    @api.one
    def add_payment(self, values=None):
        # print('STATE:', self.state)
        self.signal_workflow('manual_invoice')
        # print('STATE (2):', self.state)

        if values is None:
            values = {}

        for invoice in self.invoice_ids:
            # print('Invoice STATE (1):', invoice.state)
            invoice.signal_workflow('invoice_open')
            # print('Invoice STATE (2):', invoice.state)

            # payment_method can be bank or cash
            journal = self.env['account.journal'].search([('type', '=', values.get('payment_method') or 'bank')])

            voucher_lines = self.env['account.voucher'].recompute_voucher_lines(
                self.partner_id.id,
                journal.id,
                values.get('amount') or invoice.residual,
                invoice.currency_id.id,
                'receipt',
                values.get('payment_date') or datetime.now().date().strftime(DEFAULT_SERVER_DATE_FORMAT)
            )['value']['line_cr_ids']

            line_cr_ids = [[0, False, line_cr] for line_cr in voucher_lines]

            # create payment
            voucher_values = {
                'partner_id': self.partner_id.id,
                'amount': values.get('amount') or invoice.residual,
                'analytic_id': False,
                'comment': 'Write-Off',
                 'is_multi_currency': False,
                'journal_id': journal.id,
                'name': False,
                'date': values.get('payment_date') or datetime.now().date().strftime(DEFAULT_SERVER_DATE_FORMAT),
                'line_cr_ids': line_cr_ids,
                'line_dr_ids': [],
                'account_id': journal.default_credit_account_id.id or journal.default_debit_account_id.id,
                'narration': False,
                'reference': False,
                'type': 'receipt',
                'writeoff_acc_id': False,
                'pre_line': True,
                'payment_option': 'without_writeoff',
            }

            voucher = self.env['account.voucher'].create(voucher_values)
            # print('Voucher CREATED')

            voucher.signal_workflow('proforma_voucher')

            # print('Invoice STATE (3):', invoice.state)

            # print('Order STATE (4):', self.state)
            # print('INVOICED:', self.invoiced)

        return True

    @api.one
    def change(self, values):
        # deprecated
        if values.get('payment_acquirer_id'):
            acquirer = self.env['payment.acquirer'].browse(values['payment_acquirer_id'])
            self.payment_term = acquirer.payment_term_id.id
            del values['payment_acquirer_id']

        if values.get('partner_id'):
            partner_values = self.onchange_partner_id(values['partner_id'])['value']
            if not partner_values['payment_term']:
                del partner_values['payment_term']
            values.update(partner_values)

        return self.write(values)

    @api.one
    def patch(self, values):
        info = ''
        if values.get('payment_acquirer_id'):
            acquirer = self.env['payment.acquirer'].browse(values['payment_acquirer_id'])
            self.payment_term = acquirer.payment_term_id.id
            del values['payment_acquirer_id']

        if values.get('partner_id'):
            partner_values = self.onchange_partner_id(values['partner_id'])['value']
            if not partner_values['payment_term']:
                del partner_values['payment_term']
            values.update(partner_values)

        if values.get('promocode') and values['promocode'] != self.pricelist_id.code:
            pricelist = self.env['product.pricelist'].get_pricelist(values['promocode'], values.get('partner_id', self.partner_id.id))
            if pricelist.get('pricelist') and pricelist['pricelist'].id != self.pricelist_id.id:
                values['pricelist_id'] = pricelist['pricelist'].id
                for order_line in self.order_line:
                    order_line.price_unit = pricelist['pricelist'].price_get(
                        order_line.product_id.id, order_line.product_uom_qty or 1.0,
                        self.partner_id.id)[pricelist['pricelist'].id]

            if pricelist.get('info'):
                info = pricelist['info']

            del values['promocode']

        self.write(values)

        if self.env.user.company_id.auto_delivery_cost:
            self.delivery_set()

        result = self.env['rest.ful'].get(self.ids)
        _logger.info('Patch Result', unicode(result))
        if info:
            reply = json.loads(result)
            reply['info'] = info
            result = json.dumps(reply)

        return result

    @api.multi
    def payment_acquirer(self):
        payment_acquirer = self.env['payment.acquirer'].search([('payment_term_id', '=', self.payment_term.id)])
        return {'name': payment_acquirer.name, 'acquirer_id': payment_acquirer.id}

    # @api.one
    # def delivery_set(self):
    #     pdb.set_trace()
    #     if not self.carrier_id:
    #         self.carrier_id = self.env['delivery.carrier'].get_default_carrier().id
    #     return super(SaleOrder, self).delivery_set()


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    product_tmpl_id = fields.Many2one(related='product_id.product_tmpl_id', string='Product Template')
    note = fields.Text(_('Notes'))

    @api.multi
    def shipping(self):
        return self.order_id.carrier_id and self.order_id.carrier_id.product_id.id == self.product_id.id or False

    @api.model
    def collect_missing_values(self, product, values, pricelist_id=False, partner_id=False):
        values.update({
            'name': product.name,
            'description': product.description,
            'product_id': product.id
        })

        if 'tax_id' not in values:
            partner = self.env['res.partner'].browse(partner_id)
            taxes = partner.property_account_position.map_tax(product.taxes_id)
            values['tax_id'] = [(6, 0, taxes.ids)]

        if 'price_unit' not in values:
            if pricelist_id:
                price_list = self.env['product.pricelist'].browse(pricelist_id)
                values['price_unit'] = price_list.price_get(
                    product.id, values['product_uom_qty'] or 1.0,
                    partner_id
                )[price_list.id]
            else:
                values['price_unit'] = product.product_tmpl_id.get_price(
                    partner_id=partner_id, quantity=values['product_uom_qty']
                )[0]

        return values
