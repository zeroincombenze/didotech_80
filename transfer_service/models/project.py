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
# #############################################################################

from openerp import models, fields, api, _
from datetime import datetime
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT
from openerp import exceptions
from datetime import timedelta
from openerp import addons
from openerp.exceptions import Warning

import pdb


class ProjectTask(models.Model):
    _inherit = 'project.task'

    @api.multi
    def get_referenceable_models(self):
        return addons.base.res.res_request.referencable_models(self, self._cr, self._uid, self._context)

    origin_line = fields.Reference(get_referenceable_models, _('Origin'))

    transfer_date = fields.Datetime(_('Transfer Date'))
    transfer_date_date = fields.Date(string=_('Transfer Date'), compute='_compute_transfer_date', store=False)
    itinerary_id = fields.Many2one(comodel_name='transfer.itinerary', compute='_compute_from_origin')
    client_passenger = fields.Text(_(u'Client & Passenger'), compute='_compute_from_origin')
    client_order_ref = fields.Char(_('Practice'), compute='_compute_from_origin', store=True)
    pax_bag = fields.Text(_('pax./bag.'), compute='_compute_from_origin')

    product_id = fields.Many2one('product.product', string=_('Service'), compute='_compute_from_origin')

    supplier = fields.Text(_('Car and Driver'), compute='_compute_supplier', readonly=True, store=True)
    service_supplier_id = fields.Many2one('res.partner', _('Service Supplier'), domain="[('id', 'in', service_supplier_ids[0][2])]")
    driver_id = fields.Many2one('res.partner', _('Driver'), domain="[('id', 'in', driver_ids[0][2])]")

    row_color = fields.Char(_('Row color'), compute='_compute_color', store=False)
    purchase_order_id = fields.Many2one('purchase.order', _('Purchase Order'), required=False)
    state = fields.Char(related='stage_id.state', string=_('State'), readonly=True)

    taking = fields.Float(compute='_compute_from_origin', string=_('Taking'), inverse="_write_taking")
    passenger_qty = fields.Integer(_('Pax'), compute='_compute_from_origin', inverse="_write_passenger_qty")
    bag_qty = fields.Integer(_('Bag'), compute='_compute_from_origin', inverse="_write_bag_qty")
    passengers = fields.Text(_('Passengers'), compute='_compute_from_origin', inverse="_write_passenger")

    passenger_name = fields.Char(_('Contact Name'), compute='_compute_from_origin', inverse="_write_passenger_name")
    passenger_phone = fields.Char(_('Phone'), compute='_compute_from_origin', inverse="_write_passenger_phone")
    passenger_email = fields.Char(_('Email'), compute='_compute_from_origin', inverse="_write_passenger_email")

    start_address = fields.Text(_('Departure Address'), compute='_compute_from_origin', inverse="_write_start_address")
    finish_address = fields.Text(_('Destination Address'), compute='_compute_from_origin', inverse="_write_finish_address")
    connection = fields.Text(_('Flight / Train / Ship'), compute='_compute_from_origin', inverse="_write_connection")
    note = fields.Text(_('Note'), compute='_compute_from_origin', inverse="_write_note")

    sale_line_id = fields.Many2one('sale.order.line', 'Sales Order Line', ondelete='set null', store=True)
    invoiced = fields.Boolean(related='sale_line_id.invoiced', string=_('Invoiced'), store=True, track_visibility='always')

    transfer_date_from = fields.Date(compute=lambda *a, **k: {}, method=True, string="Transfer date from")
    transfer_date_to = fields.Date(compute=lambda *a, **k: {}, method=True, string="Transfer date to")

    commissions = fields.Float(_('Commissions'), compute='_compute_from_origin', inverse="_write_commissions")

    price_subtotal = fields.Float(related='sale_line_id.price_subtotal', string=_('Subtotal'), readonly=True)
    tax_id = fields.Many2many(related='sale_line_id.tax_id', string=_('Taxes'), readonly=True)
    tax_amount = fields.Float(_('Taxes'), compute='_compute_amounts')
    total_amount = fields.Float(_('Total'), compute='_compute_amounts')

    _order = 'transfer_date, id'

    @api.one
    def _compute_amounts(self):
        precision = self.env['decimal.precision'].precision_get('Account')
        for tax in self.tax_id:
            self.tax_amount += tax.amount * 100

        self.total_amount = round(self.price_subtotal * (1 + self.tax_amount / 100), precision)

    @api.one
    def _write_commissions(self):
        self.origin_line.commissions = self.passengers

    @api.one
    def _write_bag_qty(self):
        self.origin_line.bag_qty = self.bag_qty

    @api.one
    def _write_taking(self):
        self.origin_line.taking = self.taking

    @api.one
    def _write_passenger_qty(self):
        self.origin_line.passenger_qty = self.passenger_qty

    @api.one
    def _write_passenger(self):
        self.origin_line.passengers = self.passengers

    @api.one
    def _write_passenger_name(self):
        self.origin_line.passenger_name = self.passenger_name

    @api.one
    def _write_passenger_phone(self):
        self.origin_line.passenger_phone = self.passenger_phone

    @api.one
    def _write_passenger_email(self):
        self.origin_line.passenger_email = self.passenger_email

    @api.one
    def _write_start_address(self):
        self.origin_line.start_address = self.start_address

    @api.one
    def _write_finish_address(self):
        self.origin_line.finish_address = self.finish_address

    @api.one
    def _write_connection(self):
        self.origin_line.connection = self.connection

    @api.one
    def _write_note(self):
        self.origin_line.note = self.note

    @api.one
    @api.depends(
        'origin_line',
        'sale_line_id'
    )
    def _compute_from_origin(self):
        if self.origin_line:
            self.itinerary_id = self.origin_line.itinerary_id and self.origin_line.itinerary_id.id
            self.product_id = self.origin_line.product_id.id
            self.client_order_ref = self.origin_line.order_id.client_order_ref or self.origin_line.order_id.name

            self.connection = self.origin_line.connection \
                or hasattr(self.origin_line, 'order_line_id') and self.origin_line.order_line_id.connection or ''

            self.note = self.origin_line.note \
                or hasattr(self.origin_line, 'order_line_id') and self.origin_line.order_line_id.note \
                or self.origin_line.order_id.note

            self.taking = self.origin_line.taking

            self.passengers = self.origin_line.passengers \
                or hasattr(self.origin_line, 'order_line_id') and self.origin_line.order_line_id.passengers \
                or self.origin_line.order_id.passengers

            self.passenger_name = self.origin_line.passenger_name \
                or hasattr(self.origin_line, 'order_line_id') and self.origin_line.order_line_id.passenger_name \
                or self.origin_line.order_id.passenger_name
            self.passenger_phone = self.origin_line.passenger_phone \
                or hasattr(self.origin_line, 'order_line_id') and self.origin_line.order_line_id.passenger_phone \
                or self.origin_line.order_id.passenger_phone

            self.passenger_email = self.origin_line.passenger_email \
                or hasattr(self.origin_line, 'order_line_id') and self.origin_line.order_line_id.passenger_email \
                or self.origin_line.order_id.passenger_email

            self.start_address = self.origin_line.start_address \
                or hasattr(self.origin_line, 'order_line_id') and self.origin_line.order_line_id.start_address or ''
            self.finish_address = self.origin_line.finish_address \
                or hasattr(self.origin_line, 'order_line_id') and self.origin_line.order_line_id.finish_address or ''

            self.note = self.origin_line.note

            self.commissions = self.origin_line.commissions \
                or hasattr(self.origin_line, 'order_line_id') and self.origin_line.order_line_id.commissions or 0.0

            if self.origin_line.passenger_qty or self.origin_line.bag_qty:
                self.bag_qty = self.origin_line.bag_qty
                self.passenger_qty = self.origin_line.passenger_qty
            elif hasattr(self.origin_line, 'order_line_id') \
                    and (self.origin_line.order_line_id.passenger_qty or self.origin_line.order_line_id.bag_qty):
                self.bag_qty = self.origin_line.order_line_id.bag_qty
                self.passenger_qty = self.origin_line.order_line_id.passenger_qty
            elif self.origin_line.order_id.passenger_qty or self.origin_line.order_id.bag_qty:
                self.bag_qty = self.origin_line.order_id.bag_qty
                self.passenger_qty = self.origin_line.order_id.passenger_qty
            else:
                self.passenger_qty = self.origin_line.passenger_qty or self.origin_line.order_id.passenger_qty
                self.bag_qty = self.origin_line.bag_qty or self.origin_line.order_id.bag_qty

            self.pax_bag = 'Pax: {pax_qty}\nBag: {bag_qty}'.format(
                pax_qty=self.passenger_qty, bag_qty=self.bag_qty
            )

            self.client_passenger = u'{client}{passengers}'.format(
                client=self.origin_line.order_id.partner_id.name_get()[0][1],
                passengers=self.passengers and '\n\n' + self.passengers or ''
            )

    @api.one
    @api.depends(
        'service_supplier_id',
        'driver_id'
    )
    def _compute_supplier(self):
        driver = self.driver_id and '\n' + self.driver_id.name or ''
        self.supplier = u'{supplier}{driver}'.format(supplier=self.service_supplier_id and self.service_supplier_id.name or '', driver=driver)

    @api.one
    @api.depends(
        'stage_id'
    )
    def _compute_color(self):
        self.row_color = self.stage_id.color or 'black'

    @api.one
    @api.depends('transfer_date')
    def _compute_transfer_date(self):
        transfer_date = datetime.strptime(self.transfer_date, DEFAULT_SERVER_DATETIME_FORMAT)
        self.transfer_date_date = transfer_date.strftime(DEFAULT_SERVER_DATE_FORMAT)

    @api.multi
    def action_assign(self):
        assert len(self) == 1, 'This option should only be used for a single id at a time.'

        price = False
        quantity = False

        if self.origin_line.itinerary_id:
            price_quantity = self.env['transfer.price'].get_price_and_quantity(
                self.origin_line.product_id,
                self.service_supplier_id,
                self.origin_line.itinerary_id,
                price_date=datetime.strptime(self.transfer_date, DEFAULT_SERVER_DATETIME_FORMAT).date()
            )

            price = price_quantity['price_unit']
            quantity = price_quantity['product_uom_qty']

        pricelist = self.service_supplier_id.property_product_pricelist_purchase

        if not price:
            product_uom_qty = self.origin_line.product_uom_qty or 1.0
            if pricelist:
                transfer_date = self.origin_line.transfer_date or self.origin_line.order_id.transfer_date
                date_order_str = datetime.strptime(transfer_date, DEFAULT_SERVER_DATETIME_FORMAT).strftime(DEFAULT_SERVER_DATE_FORMAT)
                price = pricelist.with_context({
                    'uom': self.origin_line.product_id.uom_id.id,
                    'date': date_order_str
                }).price_get(
                    self.origin_line.product_id.id,
                    product_uom_qty,
                    self.origin_line.order_id.partner_id.id or False,
                )[pricelist.id]
            else:
                price = self.origin_line.product_id.standard_price

        taxes = self.env['account.fiscal.position'].map_tax(self.origin_line.product_id.supplier_taxes_id)

        order_line = {
            'product_id': self.origin_line.product_id.id,
            'product_qty': quantity or self.origin_line.product_uom_qty or 1.0,
            'product_uom': self.origin_line.product_id.uom_id.id,
            'partner_id': self.origin_line.order_id.partner_id.id,
            'invoiced': False,
            # 'account_analytic_id':
            'price_unit': price,
            'taxes_id': map(lambda x: x.id, taxes),
            'name': self.origin_line.itinerary_id.name or self.origin_line.product_id.name,
            'date_planned': self.origin_line.transfer_date or self.origin_line.order_id.transfer_date
        }

        journals = self.env['account.journal'].search([
            ('type', '=', 'purchase'),
            ('company_id', '=', self.origin_line.order_id.company_id.id)
        ], limit=1)
        if not journals:
            raise exceptions.Warning(_('Define purchase journal for this company: "%s" (id:%d).') %
                                     (self.origin_line.order.company_id.name, self.origin_line.order.company_id.id))

        location = self.env['stock.location'].search([('usage', '=', 'internal')])

        partner_ref = '{0}{1}'.format(self.origin_line.itinerary_id and self.origin_line.itinerary_id.name + ' ' or '', self.origin_line.order_id.partner_id.name)

        purchase_order = self.env['purchase.order'].create({
            'origin': 'Project Task, ' + str(self.id),
            'partner_ref': partner_ref,
            'date_order': datetime.now().strftime(DEFAULT_SERVER_DATETIME_FORMAT),
            'partner_id': self.service_supplier_id.id,
            'fiscal_position': self.service_supplier_id.property_account_position and self.service_supplier_id.property_account_position.id or False,
            # 'amount_untaxed': product_uom_qty,
            'amount_untaxed': price * order_line['product_qty'],
            'journal_id': len(journals) and journals[0].id or False,
            'bid_validity': datetime.strptime(self.origin_line.transfer_date, DEFAULT_SERVER_DATETIME_FORMAT).strftime(DEFAULT_SERVER_DATE_FORMAT),
            'order_line': [(0, 0, order_line)],
            'location_id': location.id,
            'pricelist_id': pricelist.id,
        })
        self.purchase_order_id = purchase_order.id
        self.set_assigned()

        return {
            'domain': str([('id', '=', purchase_order.id)]),
            'view_type': 'form',
            'view_mode': 'form,tree',
            'res_model': 'purchase.order',
            'view_id': False,
            'type': 'ir.actions.act_window',
            'name': _('Request for Quotation'),
            'res_id': purchase_order.id
        }

    @api.multi
    def action_change_supplier(self):
        assert len(self) == 1, 'This option should only be used for a single id at a time.'
        assign_id = self.env['assign.supplier'].create({
            'task_id': self.id
        })
        return {
            'name': _('Select Supplier'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'assign.supplier',
            'view_id': False,
            'target': 'new',
            'res_id': assign_id.id,
            'context': {
                'product_id': self.origin_line.product_id.id
            }
        }

    @api.model
    def close_expired_tasks(self):
        # 1 day means yesterday
        closing_date = datetime.now() - timedelta(days=self.env.user.company_id.closing_delay)
        stages = self.env['project.task.type'].search([('state', 'in', ('draft', 'assigned', 'confirmed'))])
        stage_ids = map(lambda x: x.id, stages)
        expired_tasks = self.search([
            ('transfer_date', '<', closing_date.strftime(DEFAULT_SERVER_DATETIME_FORMAT)),
            ('stage_id', 'in', stage_ids)
        ])
        for task in expired_tasks:
            task.set_closed()

    @api.multi
    def close_tasks(self):
        if self._context['active_ids']:
            tasks = self.browse(self._context['active_ids'])
            for task in tasks:
                task.set_closed()

    @api.one
    def set_state(self, state):
        states = {
            'draft': {'name': 'Draft', 'color': 'red', 'sequence': 1},
            'assigned': {'name': 'Assigned', 'color': 'orange', 'sequence': 2},
            'confirmed': {'name': 'Confirmed', 'color': 'green', 'sequence': 5},
            'cancel': {'name': 'Cancelled', 'color': 'grey', 'sequence': 99},
            'done': {'name': 'Done', 'color': 'darkblue', 'sequence': 100},
        }
        stage = self.stage_id.search([('state', '=', state)])
        if not stage:
            stage = self.stage_id.create({
                'name': states[state]['name'],
                'color': states[state]['color'],
                'state': state,
                'sequence': states[state]['sequence'],
                'case_default': True
            })

        self.stage_id = stage.id

    @api.one
    def set_draft(self):
        self.set_state('draft')

    @api.one
    def set_assigned(self):
        self.set_state('assigned')

    @api.one
    def set_confirmed(self):
        self.set_state('confirmed')

    @api.one
    def set_cancelled(self):
        if self.service_supplier_id and self.origin_line:
            self.origin_line.service_supplier_id = self.service_supplier_id.id
        if self.driver_id and self.origin_line:
            self.origin_line.driver_id = self.driver_id.id

        self.set_state('cancel')

    @api.one
    def set_closed(self):
        self.set_state('done')

    @api.multi
    def create_invoice(self):
        invoices = {}

        if self._context.get('active_ids'):
            tasks = self.browse(self._context['active_ids'])
        else:
            tasks = self

        for task in tasks:
            if not task.invoiced and task.state == 'done' and task.origin_line:
                # Group invoice lines by order:
                # key = task.origin_line.order_id.id
                # Group invoice lines by partner:
                key = task.origin_line.order_id.partner_id.id

                if invoices.get(key):
                    if invoices[key].get(task.origin_line._name):
                        invoices[key][task.origin_line._name] += task.origin_line
                    else:
                        invoices[key][task.origin_line._name] = task.origin_line
                else:
                    invoices[key] = {task.origin_line._name: task.origin_line}

        if invoices:
            new_invoice_ids = []
            for key, origin_lines_mix in invoices.items():
                invoice_line_ids = []
                black_list = []
                orders = []
                for line_type, origin_lines in origin_lines_mix.items():
                    for line in origin_lines:
                        if line._name == 'sale.order.line':
                            invoice_line_ids += line.invoice_line_create()
                            orders += [origin_line.order_id for origin_line in origin_lines]
                        elif line._name == 'sale.order.template.line' and line.id not in black_list:
                            # set([3, 4, 5, 6, 7]).intersection([4, 5, 6, 9]) == set([4, 5, 6, 9])
                            if set(origin_lines.ids).intersection(line.order_line_id.template_line.ids) == set(line.order_line_id.template_line.ids):
                                invoice_line_ids += line.order_line_id.invoice_line_create()
                                # Exclude values from origin_lines
                                black_list += line.order_line_id.template_line.ids
                                orders += [origin_line.order_id for origin_line in origin_lines]

                if invoice_line_ids and orders:
                    # Using set to remove duplicate orders
                    orders = list(set(orders))

                    new_invoice = self.env['sale.order']._make_union_invoice(orders, invoice_line_ids)
                    new_invoice_ids.append(new_invoice.id)

                    for order in orders:
                        # Connect invoice with sale.order
                        order.connect_invoice(new_invoice)
                        # order.invoice_ids = [(4, new_invoice.id)]
                        #
                        # invoice_lines = [invoice.invoice_line for invoice in order.invoice_ids]
                        # invoice_lines = reduce(lambda x, y: x + y, invoice_lines)
                        #
                        # invoiced_lines = [invoice_line.origin_line.id for invoice_line in invoice_lines if invoice_line.origin_line and invoice_line.origin_line._name == 'sale.order.line']
                        #
                        # if set(order.order_line.ids).intersection(invoiced_lines) == set(order.order_line.ids):
                        #     order.state = 'progress'

            if new_invoice_ids and len(new_invoice_ids) == 1:
                res = self.env['ir.model.data'].get_object_reference('account', 'invoice_form')
                res_id = res and res[1] or False

                return {
                    'name': _('Customer Invoices'),
                    'view_type': 'form',
                    'view_mode': 'form',
                    'res_model': 'account.invoice',
                    'view_id': [res_id],
                    'type': 'ir.actions.act_window',
                    'target': 'current',
                    'res_id': new_invoice.id,
                    'context': "{'type':'out_invoice'}",
                    'domain': str([('id', '=', new_invoice.id)])
                }
            elif new_invoice_ids and len(new_invoice_ids) > 1:
                res = self.env['ir.model.data'].get_object_reference('account', 'invoice_form')
                res_id = res and res[1] or False

                return {
                    'name': _('Customer Invoices'),
                    'view_type': 'form',
                    'view_mode': 'tree',
                    'res_model': 'account.invoice',
                    'view_id': [res_id],
                    'type': 'ir.actions.act_window',
                    'target': 'current',
                    'res_id': False,
                    'context': "{'type':'out_invoice'}",
                    'domain': str([('id', 'in', new_invoice_ids)])
                }
        else:
            raise Warning(_("The selection contains no tasks ready to be invoiced"))

    @api.model
    def origin_search(self, query):
        origin_models = {
            'sale.order': '',
            'sale.order.line': 'order_id',
            'sale.order.template.line': 'order_id'
        }
        sale_orders = self.env['sale.order']

        for model, attribute in origin_models.items():
            query_models = self.env[model].search([query])
            if attribute:
                # pdb.set_trace()
                sale_orders = reduce(lambda x, y_model: x + getattr(y_model, attribute), query_models, sale_orders)
            else:
                sale_orders += query_models

        return 'sale_line_id.order_id', 'in', sale_orders.ids

    def search(self, cr, uid, args, offset=0, limit=0, order=None, count=False, context=None):
        new_args = []
        for query in args:
            if query[0] == 'passengers':
                query = self.origin_search(cr, uid, query)
            new_args.append(query)
        return super(ProjectTask, self).search(cr, uid, new_args, offset=offset, limit=limit, order=order, count=count, context=context)


class ProjectTaskType(models.Model):
    _name = 'project.task.type'
    _inherit = ['project.task.type', 'row.color']

    state = fields.Char(_('State'))

    @api.one
    @api.constrains('state')
    def _check_state_unique(self):
        states = self.search([('state', '=', self.state)])

        if len(states) > 1:
            raise exceptions.ValidationError(_("State '{state}' already exists").format(state=self.state))
