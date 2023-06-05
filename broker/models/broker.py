# -*- encoding: utf-8 -*-
# =============================================================================
# For copyright and license notices, see __openerp__.py file in root directory
# =============================================================================

from openerp import models, fields, api
from openerp.tools.translate import _
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT
from datetime import datetime, timedelta
from openerp import exceptions
import os
import xmltodict

import logging
_logger = logging.getLogger(__name__)
_logger.setLevel(logging.DEBUG)


class BrokerPurchaseOrder(models.Model):
    _name = 'broker.purchase.order'
    _description = 'Purchase Order for Broker operations'
    _inherit = ['mail.thread']

    name = fields.Char('Order Reference', required=False, copy=False,
                       readonly=True, states={'draft': [('readonly', False)], 'sent': [('readonly', False)]},
                       select=True, default='/')
    order_ids = fields.One2many('sale.order', 'broker_order_id', string=_('Sale Orders'))
    state = fields.Selection('_get_states', string=_('State'), readonly=True, default='draft', track_visibility='always')
    date_order = fields.Datetime('Date', required=False, readonly=True, select=True, states={'draft': [('readonly', False)], 'sent': [('readonly', False)]}, copy=False)
    delivery_date = fields.Datetime('Delivery Date', required=False, readonly=False)
    date_cmr = fields.Datetime('Date CMR', required=False, readonly=False)
    supplier_id = fields.Many2one('res.partner', string=_('Supplier'), readonly=True,
                                  states={'draft': [('readonly', False)]}, required=True,
                                  track_visibility='always', domain=[('supplier', '=', True)])
    user_id = fields.Many2one('res.users', _('Salesperson'), states={'draft': [('readonly', False)], 'sent': [('readonly', False)]}, select=True, track_visibility='onchange')
    last_screen_ref = fields.Integer(_('Screen Ref'), default=0)
    carrier_id = fields.Many2one('delivery.carrier', string="Delivery Method")
    transmitted_to_carrier = fields.Boolean(_('Transmitted to Carrier'), readonly=True)
    transmitted_to_supplier = fields.Boolean(_('Transmitted to Supplier'), readonly=False)

    _order = 'delivery_date desc'

    def _get_states(self):
        return (
            ('draft', 'Draft'),
            ('sent', 'Sent'),
            ('waiting', 'Waiting'),
            ('rejected', 'Rejected'),
            ('accepted', 'Accepted'),
            ('confirmed', 'Confirmed'),
            ('done', 'Done'),
            ('cancel', 'Cancelled')
        )

    @api.model
    def create(self, values):
        """
        If 'force_create' parameter is set, even if less than 10 minutes pass after the last order creation it will be accepted.
        """
        if values.get('name', '/') == '/':
            values['name'] = self.env['ir.sequence'].get('broker.purchase.order') or '/'

        if not values.get('force_create'):
            recent_date = datetime.now() - timedelta(seconds=600)
            duplicated_orders = self.search([('supplier_id', '=', values['supplier_id']), ('create_date', '>', recent_date.strftime(DEFAULT_SERVER_DATETIME_FORMAT))])
            if duplicated_orders:
                raise exceptions.ValidationError(_("Seems to be the same order sent twice (less than 10 min pass)"))
        else:
            del values['force_create']

        if 'carrier_id' not in values:
            carriers = self.env['delivery.carrier'].search([], order='sequence')
            if carriers:
                values['carrier_id'] = carriers[0].id

        if values.get('orders'):
            values['last_screen_ref'] = 0
            orders = self.env['sale.order']
            for sale_order in values['orders']:
                # Create shipping address from Sale Order data:
                # if order_line[2].get('shipping_address'):
                #     shipping_address = partner_obj.search([
                #         '|',
                #         ('id', '=', order_line[2]['partner_id']),
                #         ('parent_id', '=', order_line[2]['partner_id']),
                #         ('type', '=', 'delivery')
                #     ])
                #
                #     if not shipping_address:
                #         shipping_address = partner_obj.search([
                #             ('name', '=', 'Shipping address'),
                #             ('parent_id', '=', order_line[2]['partner_id'])
                #         ])
                #
                #         if shipping_address:
                #             shipping_address.write(values['shipping_address'])
                #         else:
                #             values['shipping_address']['parent_id'] = order_line[2]['partner_id']
                #             values['shipping_address']['name'] = 'Shipping address'
                #             shipping_address = partner_obj.create(values['shipping_address'])
                #     values['partner_shipping_id'] = shipping_address.id
                #
                #     del values['shipping_address']

                orders += self.env['sale.order'].create(sale_order)
                if orders[-1].get_biggest_screen_ref() > values['last_screen_ref']:
                    values['last_screen_ref'] = orders[-1].get_biggest_screen_ref()

            del values['orders']
            values['order_ids'] = [[6, False, orders.ids]]
        elif values.get('order_ids') and values.get('supplier_id'):
            supplier = self.env['res.partner'].browse(values['supplier_id'])
            for order in values['order_ids']:
                if order[0] in (0, 1) and order[2].get('partner_id'):
                    customer_info = supplier.get_customer_ref(order[2]['partner_id'])
                    if customer_info and customer_info.payment_term_id:
                        order[2]['payment_term'] = customer_info.payment_term_id.id

        return super(BrokerPurchaseOrder, self).create(values)

    @api.multi
    def write(self, values):
        if values.get('order_ids'):
            for order in values['order_ids']:
                if order[0] in (0, 1) and order[2].get('partner_id'):
                    customer_info = self.supplier_id.get_customer_ref(order[2]['partner_id'])
                    if customer_info and customer_info.payment_term_id:
                        order[2]['payment_term'] = customer_info.payment_term_id.id
        return super(BrokerPurchaseOrder, self).write(values)

    @api.multi
    def create_distribution_list(self):
        view_rec = self.env['ir.model.data'].get_object_reference('broker', 'distribution_list_export_form')
        if view_rec:
            view_id = view_rec and view_rec[1] or False

        return {
            'type': 'ir.actions.act_window',
            'name': _('Download distribution list'),
            'res_model': 'wizard.distribution.list',
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': [view_id],
            'target': 'new',
            # 'res_id': wizard.id,
            'res_id': False,
            'context': {'delivery': True}
        }

    @api.multi
    def create_purchase_order(self):
        view_rec = self.env['ir.model.data'].get_object_reference('broker', 'distribution_list_export_form')
        if view_rec:
            view_id = view_rec and view_rec[1] or False

        return {
            'type': 'ir.actions.act_window',
            'name': _('Download distribution list'),
            'res_model': 'wizard.distribution.list',
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': [view_id],
            'target': 'new',
            # 'res_id': wizard.id,
            'res_id': False,
            'context': {'show_prices': True}
        }

    @api.multi
    def confirm_all_orders(self):
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
        }

    @api.multi
    def import_purchase_order(self):
        view_rec = self.env['ir.model.data'].get_object_reference('broker', 'import_purchase_order_form')
        if view_rec:
            view_id = view_rec and view_rec[1] or False

        return {
            'type': 'ir.actions.act_window',
            'name': _('Confirm Orders'),
            'res_model': 'wizard.import.purchase.order',
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': [view_id],
            'target': 'new',
            'res_id': False,
        }

    @api.multi
    def get_trucks_info(self):
        self._cr.execute("""SELECT truck_info_id FROM sale_order_line
            WHERE order_id in ({orders})
            GROUP BY truck_info_id
        """.format(orders=', '.join([str(order_id) for order_id in self.order_ids.ids])))

        results = []
        for truck_info in self._cr.fetchall():
            if truck_info[0]:
                results.append(truck_info[0])
            else:
                raise exceptions.ValidationError("Missing Truck information on some order lines")

        return results

    @api.multi
    def patch(self, values):
        if values.get('orders'):
            orders = self.env['sale.order']
            for sale_order in values['orders']:
                if 'order_id' in sale_order:
                    # Update
                    order = self.env['sale.order'].browse(sale_order['order_id'])

                    if sale_order.get('order_line'):
                        sale_order_line_obj = self.env['sale.order.line']
                        for value_line in sale_order['order_line']:
                            if value_line.get('line_id'):
                                order_line = sale_order_line_obj.browse(value_line['line_id'])
                                del value_line['line_id']
                                if value_line:
                                    order_line.write(value_line)
                                else:
                                    order_line.unlink()
                            else:
                                value_line['order_id'] = sale_order['order_id']
                                sale_order_line_obj.create(value_line)
                        orders += order
                    else:
                        del sale_order['order_id']
                        if sale_order:
                            order.write(sale_order)
                            orders += order
                        else:
                            order.unlink()
                else:
                    # create
                    sale_order['name'] = '/'
                    sale_order['user_id'] = self._uid
                    if sale_order.get('order_line'):
                        sale_order['order_line'] = [[0, False, line] for line in sale_order['order_line']]

                    orders += self.env['sale.order'].create(sale_order)

            del values['orders']
            values['order_ids'] = [[6, False, orders.ids]]

        if values:
            self.write(values)

        return self.env['rest.ful'].get(self.ids)

    @api.model
    def process_agromey_reply(self, values):
        from_av = os.path.join(values['path'], 'from_av')
        if not os.path.isdir(from_av):
            os.mkdir(from_av)
        for agrofile in os.listdir(from_av):
            if agrofile.endswith(".xrs"):
                _logger.info(u"Processing Agromey file {} ...".format(agrofile))
                park = False
                file_path = os.path.join(from_av, agrofile)
                agro_xml = xmltodict.parse(file(file_path).read())
                errors = agro_xml['AVXML'].get('ERRORS')
                if errors:
                    if 'ERROR' in errors:
                        for error in errors['ERROR']:
                            order = self.search([('name', '=ilike', error['TRNUID'])])
                            if order:
                                order.message_post(u'{}: {}'.format(error['DATE'], error['MESSAGE']), 'Error')
                                order.state = 'rejected'
                            else:
                                park = True
                    elif 'WARNING' in errors:
                        if 'EBUSMSGSRS' in agro_xml['AVXML'] and 'EBUSTRNRS' in agro_xml['AVXML']['EBUSMSGSRS']:
                            trnuid = agro_xml['AVXML']['EBUSMSGSRS']['EBUSTRNRS'].get('TRNUID')
                            if trnuid:
                                order = self.search([('name', '=ilike', trnuid)])
                                error = errors['WARNING']
                                order.message_post(u'{}: {}'.format(error['DATE'], error['MESSAGE']), 'Warning')
                            else:
                                park = True
                        else:
                            park = True
                elif 'EBUSMSGSRS' in agro_xml['AVXML'] and 'EBUSTRNRS' in agro_xml['AVXML']['EBUSMSGSRS']:
                    if isinstance(agro_xml['AVXML']['EBUSMSGSRS']['EBUSTRNRS'], (list, tuple)):
                        order = self.search([('name', '=ilike', agro_xml['AVXML']['EBUSMSGSRS']['EBUSTRNRS'][0]['TRNUID'])])
                    else:
                        order = self.search([('name', '=ilike', agro_xml['AVXML']['EBUSMSGSRS']['EBUSTRNRS']['TRNUID'])])
                    if order:
                        # order.transmitted_to_supplier = True
                        order.state = 'accepted'
                    else:
                        park = True
                else:
                    park = True

                if park:
                    self.park_file(values['path'], agrofile)
                else:
                    os.unlink(file_path)

    @staticmethod
    def park_file(path, file_name):
        _logger.info(u"Aliens arrived '{}' ...".format(file_name))
        aliens = os.path.join(path, 'aliens')
        if not os.path.isdir(aliens):
            os.mkdir(aliens)

        os.rename(os.path.join(path, 'from_av', file_name), os.path.join(path, 'aliens', file_name))

    @api.multi
    def change_orders_date(self):
        if 'field' in self._context:
            field = self._context['field']
            for purchase_order in self:
                value = getattr(purchase_order, field)
                for order in purchase_order.order_ids:
                    setattr(order, field, value)


class WizardTruckInfo(models.Model):
    _name = 'broker.truck.info'

    name = fields.Char(required=True)

    @api.multi
    def get_create(self, name):
        info = self.search([('name', '=ilike', name)])
        if info:
            return info
        else:
            return self.create({'name': name})


class DeliveryInfo(models.Model):
    _name = 'broker.delivery.info'

    truck_id = fields.Many2one('broker.truck.info')
    purchase_order_id = fields.Many2one('broker.purchase.order')
    name = fields.Char('DVCE', help="Documento veterinario comune di entrata")
