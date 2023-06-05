# -*- encoding: utf-8 -*-
# =============================================================================
# For copyright and license notices, see __openerp__.py file in root directory
# =============================================================================

from openerp import models, fields, api, _


class ResCompany(models.Model):
    _inherit = 'res.company'

    auto_delivery_cost = fields.Boolean(help=_("Automatically add delivery costs to every Sale Order"))
