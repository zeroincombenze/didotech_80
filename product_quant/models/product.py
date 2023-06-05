# -*- encoding: utf-8 -*-
# =============================================================================
# For copyright and license notices, see __openerp__.py file in root directory
# =============================================================================

from openerp import models, fields, api
from openerp.tools.translate import _


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    quant_ids = fields.One2many('stock.quant', compute='compute_quant_ids', string=_('Quant'))

    @api.one
    def compute_quant_ids(self):
        quant_ids = self.env['stock.quant'].search([
            ('location_id.usage', '=', 'internal'),
            ('product_id', 'in', self.product_variant_ids.ids)
        ])
        self.quant_ids = quant_ids.ids


class ProductProduct(models.Model):
    _inherit = 'product.product'

    quant_ids = fields.One2many('stock.quant', 'product_id', string=_('Quant'),
                                # Without this domain we will see all quants
                                # that pass through our warehouse:
                                domain=[('location_id.usage', '=', 'internal')])
