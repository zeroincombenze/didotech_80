# -*- coding: utf-8 -*-
# #############################################################################
#
#    Copyright (C) 2015 Didotech srl (<http://www.didotech.com>)
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
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT
from datetime import datetime
from openerp import exceptions


class CreateQuotation(models.TransientModel):
    _name = 'wizard.create.quotation'

    partner_id = fields.Many2one('res.partner', _('Customer'), domain=[('customer', '=', True)])
    quotation_line_ids = fields.One2many('wizard.quotation.line', 'create_quotation_id', string=_('Quotation Lines'))
    template_id = fields.Many2one('transfer.template', _('Template'), required=True)
    order_id = fields.Many2one('sale.order', _('Connect to existent Sale Order'), required=False)
    transfer_date = fields.Datetime(_('Travel date and time'))
    descriptive_itinerary_id = fields.Many2one('transfer.itinerary', _('Descriptive Itinerary'), domain=[('is_description', '=', True)])

    @api.multi
    def action_create_quotation(self):
        order_values = self.env['sale.order'].onchange_partner_id(self.partner_id.id)['value']
        order_values['partner_id'] = self.partner_id.id

        line_values = self.env['sale.order.line'].product_id_change(
            order_values['pricelist_id'],
            self.template_id.product_id.id,
            qty=1,
            partner_id=self.partner_id.id,
        )['value']

        line_values['product_id'] = self.template_id.product_id.id
        line_values['itinerary_id'] = self.descriptive_itinerary_id and self.descriptive_itinerary_id.id

        sorted_lines = sorted(self.quotation_line_ids, key=lambda x: x.transfer_date)

        line_values['price_unit'] = self.env['transfer.template.price'].get_price(
            self.template_id,
            self.partner_id,
            price_date=datetime.strptime(sorted_lines[0].transfer_date, DEFAULT_SERVER_DATETIME_FORMAT).date().strftime(DEFAULT_SERVER_DATE_FORMAT)
        ) or self.template_id.product_price

        if line_values.get('tax_id'):
            line_values['tax_id'] = [[6, 0, line_values['tax_id']]]
        else:
            raise exceptions.Warning(_("Please set taxes for product '{product}'").format(product=self.template_id.product_id.name))

        order_values['order_line'] = [(0, 0, line_values)]

        if self.order_id:
            order = self.order_id
            line_values['order_id'] = order.id
            order_line = self.env['sale.order.line'].create(line_values)
        else:
            order = self.env['sale.order'].create(order_values)
            order_line = order.order_line[0]

        if len(self.quotation_line_ids) > 1:
            # Create MRP:
            for line in self.quotation_line_ids:
                # price_quantity = self.env['transfer.price'].get_price_and_quantity(line.product_id, self.partner_id, itinerary=line.itinerary_id)

                template_line_values = self.env['sale.order.line'].product_id_change(
                    order_values['pricelist_id'],
                    line.product_id.id,
                    qty=1,
                    partner_id=self.partner_id.id
                )['value']

                # if price_quantity['price_unit']:
                #     template_line_values['price_unit'] = price_quantity['price_unit']
                template_line_values.update({
                    'product_id': line.product_id.id,
                    'itinerary_id': line.itinerary_id and line.itinerary_id.id or False,
                    'transfer_date': line.transfer_date,
                    'service_supplier_id': line.service_supplier_id and line.service_supplier_id.id or False,
                    'driver_id': line.driver_id and line.driver_id.id or False,
                    'tax_id': [[6, 0, template_line_values['tax_id']]],
                    'order_line_id': order_line.id,
                    'transfer_template_line_id': line.template_line_id.id,
                    'product_uom_qty': line.itinerary_id and line.itinerary_id.distance or 1.0
                })

                self.env['sale.order.template.line'].create(template_line_values)

        return {
            'domain': str([('id', '=', order.id)]),
            'view_type': 'form',
            'view_mode': 'form,tree',
            'res_model': 'sale.order',
            'view_id': False,
            'type': 'ir.actions.act_window',
            'name': _('Quotation'),
            'res_id': order.id
        }

    @api.one
    @api.onchange('transfer_date')
    def on_change_transfer_date(self):
        for line in self.quotation_line_ids:
            line.transfer_date = self.transfer_date


class WizardQuotationLine(models.TransientModel):
    _name = 'wizard.quotation.line'

    name = fields.Char(_('Name'), compute='_compute_name')
    transfer_date = fields.Datetime(_('Travel date and time'))
    product_id = fields.Many2one('product.product', _('Service'), required=True)
    itinerary_id = fields.Many2one('transfer.itinerary', _('Itinerary'), required=False, readonly=True)
    template_line_id = fields.Many2one('transfer.template.line', _('Template Line'), required=True)
    create_quotation_id = fields.Many2one('wizard.create.quotation', _('Create Quotation'))
    service_supplier_id = fields.Many2one('res.partner', _('Service Supplier'), domain="[('id', 'in', service_supplier_ids[0][2])]")
    service_supplier_ids = fields.Many2many('res.partner', compute='compute_supplier_ids', string=_('Service Suppliers'))
    driver_id = fields.Many2one('res.partner', _('Driver'), domain="[('id', 'in', driver_ids[0][2])]")
    driver_ids = fields.Many2many('res.partner', compute='compute_driver_ids', string=_('Drivers'))

    @api.one
    @api.depends('product_id')
    def compute_supplier_ids(self):
        self.service_supplier_ids = [seller.name.id for seller in self.product_id.seller_ids]

    @api.one
    @api.depends('service_supplier_id')
    def compute_driver_ids(self):
        self.driver_ids = [driver.id for driver in self.service_supplier_id.child_ids]

    @api.one
    @api.depends('product_id', 'itinerary_id')
    def _compute_name(self):
        self.name = '{name}: {itinerary}'.format(name=self.product_id.name, itinerary=self.itinerary_id.name)
