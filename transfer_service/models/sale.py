# -*- coding: utf-8 -*-
# #############################################################################
#
#    Copyright (C) 2015-2016 Didotech srl (<http://www.didotech.com>)
#    All Rights Reserved
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# #############################################################################.

from openerp import models, fields, api, _
import openerp.addons.decimal_precision as dp
from openerp import exceptions
from datetime import datetime
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT
import time


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    transfer = fields.Boolean(_('Transfer'), default=True)
    transfer_date = fields.Datetime(_('Travel date and time'))
    next_transfer_date = fields.Datetime(_('Travel Date'), compute='_compute_next_transfer_date')

    passenger_qty = fields.Integer(_('Pax'))
    bag_qty = fields.Integer(_('Bag'))
    passengers = fields.Text(_('Passengers'))
    computed_passengers = fields.Text(_('Passengers'), compute='_compute_passengers')

    passenger_name = fields.Char(_('Contact Name'))
    passenger_phone = fields.Char(_('Phone'))
    passenger_email = fields.Char(_('Email'))

    task_ids = fields.Many2many('project.task', string=_('Tasks'), compute='_compute_tasks')

    @api.one
    def _compute_passengers(self):
        self.computed_passengers = self.passengers

        if not self.computed_passengers:
            for line in self.order_line:
                if line.passengers:
                    self.computed_passengers = line.passengers
                    break
                elif line.template_line:
                    for t_line in line.template_line:
                        if t_line.passengers:
                            self.computed_passengers = t_line.passengers
                            break

    @api.one
    def _compute_next_transfer_date(self):
        if self.transfer_date:
            self.next_transfer_date = self.transfer_date

        for line in self.order_line:
            if self.next_transfer_date and self.next_transfer_date > line.template_or_transfer_date or not self.next_transfer_date:
                self.next_transfer_date = line.template_or_transfer_date

    @api.one
    def _compute_tasks(self):
        tasks = self.env['project.task'].search([('sale_line_id', 'in', self.order_line.ids)])
        if tasks:
            self.task_ids = tasks.ids

    @api.one
    def create_tasks_from_order(self):
        for line in self.order_line:
            if line.product_id.type == 'service' and line.product_id.auto_create_task and line.has_template:
                for sub_line in line.template_line:
                    if not sub_line.transfer_date and not self.transfer_date:
                        raise exceptions.Warning(_('Please set transfer date'))
                    task = self.env['project.task'].create({
                        'name': sub_line.transfer_template_line_id.itinerary_id.name or sub_line.transfer_template_line_id.product_id.name,
                        'date_deadline': sub_line.transfer_date or self.transfer_date,
                        'transfer_date': sub_line.transfer_date or self.transfer_date,
                        'planned_hours': sub_line.transfer_template_line_id.itinerary_id.duration / 60 or 1,
                        'remaining_hours': sub_line.transfer_template_line_id.itinerary_id.duration / 60 or 1,
                        'partner_id': line.order_id.partner_id.id,
                        'user_id': sub_line.product_id.product_manager.id,
                        'description': sub_line.product_id.name,
                        'project_id': False,
                        'company_id': self.env.user.company_id.id,
                        'origin_line': 'sale.order.template.line, {0}'.format(sub_line.id),
                        'sale_line_id': line.id,
                        'service_supplier_id': sub_line.service_supplier_id and sub_line.service_supplier_id.id or False,
                        'driver_id': sub_line.driver_id and sub_line.driver_id.id or False
                    })
                    task.set_draft()
            elif line.product_id.type == 'service' and line.product_id.auto_create_task and line.itinerary_id:
                if not line.transfer_date and not self.transfer_date:
                    raise exceptions.Warning(_('Please set transfer date'))
                task = self.env['project.task'].create({
                    'name': line.itinerary_id.name,
                    'date_deadline': line.transfer_date or self.transfer_date,
                    'transfer_date': line.transfer_date or self.transfer_date,
                    'planned_hours': line.itinerary_id.duration / 60,
                    'remaining_hours': line.itinerary_id.duration / 60,
                    'partner_id': line.order_id.partner_id.id,
                    'user_id': line.product_id.product_manager.id,
                    'description': line.product_id.name,
                    'project_id': False,
                    'company_id': self.env.user.company_id.id,
                    'origin_line': 'sale.order.line, {0}'.format(line.id),
                    'sale_line_id': line.id,
                    'service_supplier_id': line.service_supplier_id and line.service_supplier_id.id or False,
                    'driver_id': line.driver_id and line.driver_id.id or False,
                })
                task.set_draft()

    @api.one
    def action_button_confirm(self):
        if self.order_policy not in ('prepaid', ):
            self.create_tasks_from_order()
        return super(SaleOrder, self).action_button_confirm()

    @api.one
    def set_invoiced(self):
        if self.order_policy in ('prepaid', ):
            self.create_tasks_from_order()

    @api.model
    def create(self, values):
        order = super(SaleOrder, self).create(values)
        if not order.client_order_ref:
            order.client_order_ref = order.name
        return order

    @api.multi
    def action_create_additional_order(self, defaults):
        if self.transfer:
            defaults['order_line'] = False
            defaults['client_order_ref'] = self.client_order_ref
        new_order = super(SaleOrder, self).copy(defaults)
        return {
            'name': _('Sale Order'),
            'view_type': 'form',
            'view_mode': 'form, tree',
            'res_id': new_order.id,
            'res_model': 'sale.order',
            'view_id': False,
            'views': False,
            'type': 'ir.actions.act_window',
        }

    @api.multi
    def copy_quotation(self):
        messages = self.message_ids
        defaults = {
            'client_order_ref': self.client_order_ref
        }
        new_order = self.copy(defaults)
        messages.write({'res_id': new_order.id})
        new_order.message_post(_("Quotation created from Order {name}.".format(name=self.name)))
        self.message_post(_("Quotation {name} created from this order .".format(name=new_order.name)))
        view_ref = self.env['ir.model.data'].get_object_reference('sale', 'view_order_form')
        view_id = view_ref and view_ref[1] or False,
        return {
            'type': 'ir.actions.act_window',
            'name': _('Sales Order'),
            'res_model': 'sale.order',
            'res_id': new_order.id,
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': view_id,
            'target': 'current',
            'nodestroy': True,
        }

    @api.multi
    def add_template(self):
        return {
            'type': 'ir.actions.act_window',
            'name': _('Select Template'),
            'res_model': 'wizard.select.template',
            'view_type': 'form',
            'view_mode': 'form',
            # 'view_id': view_id,
            'target': 'new',
            # 'target': 'current',
            'context': "{'default_order_id': active_id}"
        }

    @api.multi
    def action_cancel(self):
        tasks_to_delete = []
        for order in self:
            for line in order.order_line:
                tasks = self.env['project.task'].search([('sale_line_id', '=', line.id)])
                for task in tasks:
                    if task.state == 'done':
                        raise exceptions.Warning(_("You can't delete order with tasks that are already done"))
                tasks_to_delete += tasks

        super(SaleOrder, self).action_cancel()

        for task in tasks_to_delete:
            if task.purchase_order_id and task.purchase_order_id.state == 'draft':
                task.purchase_order_id.action_cancel_draft()
                task.set_cancelled()
            elif task.purchase_order_id and task.purchase_order_id.state == 'cancel':
                continue
            elif task.purchase_order_id:
                raise exceptions.Warning(_("Task {task.name} can't be deleted because Purchase Order '{task.purchase_order_id.name}' is in state '{task.purchase_order_id.state}'").format(task=task))
            else:
                task.set_cancelled()

    @api.model
    def _prepare_union_invoice(self, orders, lines):
        """Prepare the dict of values to create the new invoice for a
           sales order. This method may be overridden to implement custom
           invoice generation (making sure to call super() to establish
           a clean extension chain).

           :param recordsest orders: sale.order records to invoice. Should be of the same partner
           :param list(int) line: list of invoice line IDs that must be
                                  attached to the invoice
           :return: dict of value to create() the invoice
        """

        journals = self.env['account.journal'].search(
            [('type', '=', 'sale'), ('company_id', '=', orders[0].company_id.id)],
            limit=1)
        if not journals:
            raise exceptions.Warning(
                _('Please define sales journal for this company: "%s" (id:%d).') % (orders[0].company_id.name, orders[0].company_id.id))

        return {
            'name': ', '.join([order.client_order_ref or '' for order in orders]),
            'origin': ', '.join([order.name for order in orders]),
            'type': 'out_invoice',
            'reference': ', '.join([order.client_order_ref or order.name for order in orders]),
            'account_id': orders[0].partner_id.property_account_receivable.id,
            'partner_id': orders[0].partner_invoice_id.id,
            'journal_id': journals.id,
            'invoice_line': [(6, 0, lines)],
            'currency_id': orders[0].pricelist_id.currency_id.id,
            'comment': ', '.join([order.note for order in orders if order.note]),
            'payment_term': orders[0].payment_term and orders[0].payment_term.id or False,
            'fiscal_position': orders[0].fiscal_position.id or orders[0].partner_id.property_account_position.id,
            'date_invoice': self._context.get('date_invoice', False),
            'company_id': orders[0].company_id.id,
            'user_id': orders[0].user_id and orders[0].user_id.id or False,
            'section_id': orders[0].section_id.id   # Sales Team
        }

    @api.model
    def _make_union_invoice(self, orders, lines):
        invoice_obj = self.env['account.invoice']
        # invoice_line_obj = self.env['account.invoice.line']

        for order in orders:
            invoiced_sale_lines = self.env['sale.order.line'].search([('order_id', '=', order.id), ('invoiced', '=', True)])
            from_line_invoice_ids = []
            for invoiced_sale_line_id in invoiced_sale_lines:
                for invoice_line_id in invoiced_sale_line_id.invoice_lines:
                    if invoice_line_id.invoice_id.id not in from_line_invoice_ids:
                        from_line_invoice_ids.append(invoice_line_id.invoice_id.id)
            for preinv in order.invoice_ids:
                if preinv.state not in ('cancel',) and preinv.id not in from_line_invoice_ids:
                    for preline in preinv.invoice_line:
                        # Andrei: if we got an error here, than try to uncomment next line. Sorry, hard to test
                        # inv_line_id = invoice_line_obj.copy(preline.id, {'invoice_id': False, 'price_unit': -preline.price_unit})
                        inv_line_id = preline.copy({'invoice_id': False, 'price_unit': -preline.price_unit})
                        lines.append(inv_line_id)

        invoice_values = self._prepare_union_invoice(orders, lines)

        invoice = invoice_obj.create(invoice_values)
        # Use old API:
        data = self.pool['account.invoice'].onchange_payment_term_date_invoice(self._cr, self._uid, [invoice.id], invoice_values['payment_term'], time.strftime(DEFAULT_SERVER_DATE_FORMAT))

        if data.get('value', False):
            invoice.write(data['value'])

        invoice.button_compute()
        return invoice

    def connect_invoice(self, invoice):
        self.write({'invoice_ids': [(4, invoice.id)]})

        invoice_lines = [invoice.invoice_line for invoice in self.invoice_ids]
        invoice_lines = reduce(lambda x, y: x + y, invoice_lines)

        invoiced_lines = [invoice_line.origin_line.id for invoice_line in invoice_lines if
                          invoice_line.origin_line and invoice_line.origin_line._name == 'sale.order.line']

        if set(self.order_line.ids).intersection(invoiced_lines) == set(self.order_line.ids):
            self.write({'state': 'progress'})


class SaleOrderLine(models.Model):
    _name = 'sale.order.line'
    _inherit = ['sale.order.line', 'transfer.transfer']

    product_id = fields.Many2one('product.product', domain=[('sale_ok', '=', True), ('template_ids', '=', False)])
    # show_details = fields.Boolean(_('Show details'))
    template_line = fields.One2many('sale.order.template.line', 'order_line_id', string=_('Template Lines'))
    has_template = fields.Boolean(compute='compute_has_template', string=_('Has template'), store=True)
    fixed_price = fields.Boolean(_('Fixed Price'), default=False)
    # transfer = fields.Boolean(_('Transfer'), related='order_id.transfer')
    template_or_transfer_date = fields.Datetime(compute='compute_template_date', string=_('Travel date and time'), store=False)
    commissions = fields.Float(_('Commissions'))

    @api.one
    @api.depends('template_line', 'transfer_date')
    def compute_template_date(self):
        if self.template_line:
            self.template_or_transfer_date = self.template_line[0].transfer_date
        else:
            self.template_or_transfer_date = self.transfer_date

    @api.one
    @api.depends('template_line')
    def compute_has_template(self):
        self.has_template = self.template_line and True or False

    @api.one
    @api.depends('product_id')
    def compute_supplier_ids(self):
        self.service_supplier_ids = [seller.name.id for seller in self.product_id.seller_ids]

    @api.multi
    def product_id_change(self, pricelist, product_id, qty=0,
                          uom=False, qty_uos=0, uos=False, name='', partner_id=False,
                          lang=False, update_tax=True, date_order=False,
                          packaging=False, fiscal_position=False, flag=False):

        result = super(SaleOrderLine, self).product_id_change(pricelist, product_id, qty=qty,
                                                              uom=uom, qty_uos=qty_uos, uos=uos,
                                                              name=name, partner_id=partner_id,
                                                              lang=lang, update_tax=update_tax,
                                                              date_order=date_order,
                                                              packaging=packaging,
                                                              fiscal_position=fiscal_position,
                                                              flag=flag)

        if product_id:
            product = self.env['product.product'].browse(product_id)
            if product.seller_ids:
                # crazy situation - name is integer
                # result['value']['service_supplier_id'] = product.seller_ids[0].name.id
                result['value']['service_supplier_id'] = False
                result['value']['service_supplier_ids'] = [seller.name.id for seller in product.seller_ids]

            if self._context.get('itinerary_id'):
                product = self.env['product.product'].browse(product_id)
                partner = self.env['res.partner'].browse(partner_id)
                itinerary = self.env['transfer.itinerary'].browse(self._context['itinerary_id'])
                price_quantity = self.env['transfer.price'].get_price_and_quantity(
                    product, partner, itinerary,
                    price_date=datetime.strptime(date_order, DEFAULT_SERVER_DATETIME_FORMAT).date()
                )

                # self.product_uom_qty = price_quantity['product_uom_qty']
                if price_quantity['price_unit']:
                    result['value']['price_unit'] = price_quantity['price_unit']
                    result['value']['product_uom_qty'] = 1

        return result

    @api.one
    @api.onchange('product_uom_qty')
    def on_change_qty(self):
        if self.product_id and not self.fixed_price:
            result = self.product_id_change(self.order_id.pricelist_id.id, self.product_id.id, self.product_uom_qty,
                                            self.product_uom.id, self.product_uos_qty, self.product_uos.id,
                                            self.name, self.order_id.partner_id.id, False, False,
                                            self.order_id.date_order, False, self.order_id.fiscal_position.id,
                                            True)
            for key, value in result['value'].items():
                setattr(self, key, value)

    @api.onchange('itinerary_id')
    def set_service_qty(self):
        self.fixed_price = False

        if self.itinerary_id and self.product_id:
            price_quantity = self.env['transfer.price'].get_price_and_quantity(
                self.product_id, self.order_id.partner_id, self.itinerary_id,
                price_date=self.transfer_date and datetime.strptime(self.transfer_date, DEFAULT_SERVER_DATETIME_FORMAT).date()
                              or datetime.strptime(self.order_id.date_order, DEFAULT_SERVER_DATETIME_FORMAT).date()
            )
            self.product_uom_qty = price_quantity['product_uom_qty']
            if price_quantity['price_unit']:
                self.price_unit = price_quantity['price_unit']
                self.fixed_price = True

    @api.model
    def _prepare_order_line_invoice_line(self, line, account_id=False):
        invoice_line = super(SaleOrderLine, self)._prepare_order_line_invoice_line(line, account_id=account_id)
        invoice_line['origin_line'] = 'sale.order.line, {line_id}'.format(line_id=line.id)
        return invoice_line

    @api.multi
    def sale_order_line_copy(self):
        if self.order_id.state == 'draft':
            new_line = self.copy()
            if self.has_template:
                for t_line in self.template_line:
                    new_t_line = t_line.copy()
                    new_t_line.order_line_id = new_line.id
            return {
                'type': 'ir.actions.act_window',
                'name': _('Sales Order'),
                'res_model': 'sale.order',
                'res_id': self.order_id.id,
                'view_type': 'form',
                'view_mode': 'form',
                'target': 'current',
                'nodestroy': True, }
        else:
            raise exceptions.Warning(_("This sale order is not in draft state"))

    @api.multi
    def sale_order_line_mirror(self):
        if self.order_id.state == 'draft' and self.itinerary_id and self.itinerary_id.mirror:
            new_line = self.copy()
            mirror = self.env['transfer.itinerary'].search([
                ('start_city_id', '=', self.itinerary_id.end_city_id.id),
                ('end_city_id', '=', self.itinerary_id.start_city_id.id)
            ])
            new_line.itinerary_id = mirror.id
            return {
                'type': 'ir.actions.act_window',
                'name': _('Sales Order'),
                'res_model': 'sale.order',
                'res_id': self.order_id.id,
                'view_type': 'form',
                'view_mode': 'form',
                'target': 'current',
                'nodestroy': True, }
        else:
            raise exceptions.Warning(_("This sale order is not in draft state or sale order line has no mirrored itinerary"))

    # New API gives wrong results. Sorry :(
    def copy_data(self, cr, uid, origin_id, default=None, context=None):
        origin_line = self.browse(cr, uid, origin_id, context)
        if origin_line.template_line:
            if not default:
                default = {}
            new_template_line_ids = []
            for template_line in origin_line.template_line:
                new_template_line = template_line.copy()
                new_template_line_ids.append(new_template_line.id)

            default['template_line'] = [
                [6, False, new_template_line_ids]
            ]
        return super(SaleOrderLine, self).copy_data(cr, uid, origin_id, default=default, context=context)


class SaleOrderTemplateLine(models.Model):
    _name = 'sale.order.template.line'
    _description = "Lines connected to Product 'Template'"
    _inherit = ['transfer.transfer']

    order_line_id = fields.Many2one('sale.order.line', _('Sale Order Line'), required=True, ondelete='cascade')
    order_id = fields.Many2one('sale.order', related='order_line_id.order_id', store=False)
    transfer_template_line_id = fields.Many2one('transfer.template.line', _('Transfer Template Line'), required=True)

    name = fields.Text('Description', required=True, readonly=True)
    product_id = fields.Many2one('product.product', _('Service'), domain=[('type', '=', 'service')], required=True)
    price_unit = fields.Float('Unit Price', required=True, digits_compute=dp.get_precision('Product Price'), readonly=True)
    product_uom = fields.Many2one('product.uom', 'Unit of Measure ', required=True, readonly=True)
    product_uom_qty = fields.Float(_('Quantity'), digits_compute=dp.get_precision('Product UoS'), required=True, readonly=True)
    product_uos = fields.Many2one('product.uom', 'Product UoS')
    product_uos_qty = fields.Float(_('Quantity (UoS)'), digits_compute=dp.get_precision('Product UoS'), readonly=True)
    tax_id = fields.Many2many('account.tax', 'sale_order_line_transfer_tax', 'order_line_id', 'tax_id', 'Taxes', readonly=True)
    th_weight = fields.Float('Weight', readonly=True)
    commissions = fields.Float(_('Commissions'))
