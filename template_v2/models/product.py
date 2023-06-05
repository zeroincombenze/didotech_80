# -*- encoding: utf-8 -*-
# =============================================================================
# For copyright and license notices, see __openerp__.py file in root directory
# =============================================================================

from openerp import models, fields, api
from openerp.tools.translate import _


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    description_in_invoice = fields.Boolean(_('Description visible in invoice'))
