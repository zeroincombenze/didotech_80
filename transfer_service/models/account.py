# -*- coding: utf-8 -*-
# #############################################################################
#
#    Copyright (C) 2015-2016 Didotech srl (<http://www.didotech.com>)
#
#                       All Rights Reserved
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

from openerp import models, api, fields, _
from openerp import addons


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    force_delete = fields.Boolean(_('Force'), default=False)
    sale_order_ids = fields.Many2many('sale.order', 'sale_order_invoice_rel', 'invoice_id', 'order_id', 'Sale Order')
    sorted_order_ids = fields.Many2many('sale.order', compute='_compute_sorted_orders')

    @api.one
    @api.depends('sale_order_ids')
    def _compute_sorted_orders(self):
        sale_order_ids = []
        for line in self.invoice_line:
            if line.origin_line and line.origin_line.order_id.id not in self.sale_order_ids.ids:
                # update table sale_order_invoice_rel
                line.origin_line.order_id.connect_invoice(line.invoice_id)

            if line.origin_line:
                sale_order_ids.append(line.origin_line.order_id)

        if sale_order_ids:
            self.sorted_order_ids = [order.id for order in sorted(sale_order_ids, key=lambda x: x.client_order_ref)]

        # This is OK, if sale_order_ids are correct
        # if self.sale_order_ids:
        #     self.sorted_order_ids = [order.id for order in sorted(self.sale_order_ids, key=lambda x: x.client_order_ref)]



    @api.multi
    def unlink(self):
        doomed_orders = set()
        doomed_tasks = []
        doomed_template_lines = []
        for invoice in self:
            if invoice.force_delete:
                for invoice_line in invoice.invoice_line:
                    if invoice_line.origin_line and invoice_line.origin_line._name == 'sale.order.line':
                        doomed_orders.add(invoice_line.origin_line.order_id)
                        doomed_tasks += self.env['project.task'].search([('sale_line_id', '=', invoice_line.origin_line.id)])
                        doomed_template_lines += self.env['sale.order.template.line'].search([('order_line_id', '=', invoice_line.origin_line.id)])

        deleted_invoice = super(AccountInvoice, self).unlink()

        if doomed_tasks:
            for task in doomed_tasks:
                if task.purchase_order_id:
                    task.purchase_order_id.action_cancel()
                    task.purchase_order_id.unlink()
                task.unlink()

        if doomed_template_lines:
            for template_line in doomed_template_lines:
                template_line.unlink()

        if doomed_orders:
            for order in doomed_orders:
                order.action_cancel()
                order.unlink()

        return deleted_invoice

    @api.multi
    def confirm_paid(self):
        if self.sale_order_ids:
            map(lambda order: order.set_invoiced(), self.sale_order_ids)
        return super(AccountInvoice, self).confirm_paid()

    @api.multi
    def name_get(self):
        new_result = []
        result = super(AccountInvoice, self).name_get()
        for invoice in result:
            if len(invoice[1]) > 100:
                new_result.append((invoice[0], invoice[1][:100] + ' ...'))
            else:
                new_result.append(invoice)

        return new_result


class AccountInvoiceLine(models.Model):
    _inherit = 'account.invoice.line'

    @api.multi
    def get_referenceable_models(self):
        return addons.base.res.res_request.referencable_models(self, self._cr, self._uid, self._context)

    origin_line = fields.Reference(get_referenceable_models, _('Origin'))
