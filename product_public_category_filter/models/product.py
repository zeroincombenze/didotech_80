# -*- encoding: utf-8 -*-
# =============================================================================
# For copyright and license notices, see __openerp__.py file in root directory
# =============================================================================

from openerp import models, fields, api
from openerp.tools.translate import _


class ProductPublicCategory(models.Model):
    _inherit = 'product.public.category'

    childless = fields.Boolean(_('Childless'), compute='is_childless')

    @api.one
    def is_childless(self):
        if self.search([('parent_id', '=', self.id)]):
            self.childless = False
        else:
            if self.env['product.template'].search([('public_categ_ids', '=', self.id)]):
                self.childless = False
            else:
                self.childless = True
