# -*- encoding: utf-8 -*-
# =============================================================================
# For copyright and license notices, see __openerp__.py file in root directory
# =============================================================================

from openerp import models, fields, api
from openerp.tools.translate import _


class ProductProduct(models.Model):
    _inherit = 'product.product'

    product_uib = fields.Float(_('Units in a Box (kg)'), help=_('Units in one box'))

    @api.multi
    def get_partner_code_name(self, partner_id):
        for supinfo in self.seller_ids:
            if supinfo.name.id == partner_id:
                return {'code': supinfo.product_code or '', 'name': supinfo.product_name or ''}
        return {'code': '', 'name': ''}
