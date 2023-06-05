# -*- encoding: utf-8 -*-
# =============================================================================
# For copyright and license notices, see __openerp__.py file in root directory
# =============================================================================

from openerp import models, api


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.model
    def create(self, values):
        if values.get('warehouse_id'):
            warehouse = self.env['stock.warehouse'].browse(values['warehouse_id'])
            values['company_id'] = warehouse.company_id.id
        return super(SaleOrder, self).create(values)

    @api.multi
    def write(self, values):
        if values.get('warehouse_id'):
            warehouse = self.env['stock.warehouse'].browse(values['warehouse_id'])
            values['company_id'] = warehouse.company_id.id
        return super(SaleOrder, self).write(values)
