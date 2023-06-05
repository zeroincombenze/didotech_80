# -*- encoding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import models, fields, _


class ProductProduct(models.Model):
    _inherit = "product.product"

    description = fields.Text(_('Description'), translate=True,
                              help=_("A precise description of the Product, used only for internal information purposes."))
