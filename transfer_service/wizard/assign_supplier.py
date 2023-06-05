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


class AssignSupplier(models.TransientModel):
    _name = 'assign.supplier'

    task_id = fields.Many2one('project.task', 'Task', ondelete='set null')
    service_supplier_id = fields.Selection(selection='_get_suppliers', string=_('Service Suppliers'))
    driver_id = fields.Many2one('res.partner', _('Driver'), domain="[('id', 'in', driver_ids[0][2])]")
    driver_ids = fields.Many2many('res.partner', compute='compute_driver_ids', string=_('Drivers'))

    @api.one
    @api.depends('service_supplier_id')
    def compute_driver_ids(self):
        if self.service_supplier_id:
            supplier = self.env['res.partner'].browse(int(self.service_supplier_id))
            self.driver_ids = [driver.id for driver in supplier.child_ids]
        else:
            self.driver_ids = map(lambda x: x.id, self.task_id.sale_line_id.driver_ids)

    @api.multi
    def _get_suppliers(self):
        product = self.env['product.product'].browse(self._context.get('product_id'))
        return [(str(seller.name.id), seller.name.name) for seller in product.seller_ids]

    @api.multi
    def set_supplier(self):
        assert len(self) == 1, 'This option should only be used for a single id at a time.'

        if self.service_supplier_id and not int(self.service_supplier_id) == self.task_id.service_supplier_id.id:
            # Cancel existing order
            if self.task_id.purchase_order_id:
                self.task_id.purchase_order_id.action_cancel()

                # Duplicate task, set new supplier
                task = self.task_id.copy()

                # Cancella old task
                self.task_id.set_cancelled()
            else:
                task = self.task_id

            task.service_supplier_id = int(self.service_supplier_id)
            task.driver_id = self.driver_id

            #new_task.action_assign()
            task.set_draft()
        elif not self.driver_id.id == self.task_id.driver_id.id:
            self.task_id.driver_id = self.driver_id.id
            task = self.task_id
        else:
            task = self.task_id

        return {
            'name': _('Project Task'),
            'view_type': 'form',
            'view_mode': 'form,tree',
            'res_model': 'project.task',
            'view_id': False,
            # 'target': 'new',
            'type': 'ir.actions.act_window',
            'res_id': task.id,
            'target': 'current',
            'domain': str([('id', '=', task.id)])
        }
