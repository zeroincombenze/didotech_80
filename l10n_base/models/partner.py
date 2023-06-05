# -*- encoding: utf-8 -*-
# ==================================================================================
# For copyright and license notices, see __openerp__.py file in the root directory
# ==================================================================================

from openerp import models


class res_partner(models.Model):
    _name = 'res.partner'
    _inherit = ['res.partner', 'base.address']
