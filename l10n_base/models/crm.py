# -*- encoding: utf-8 -*-
# ==================================================================================
# For copyright and license notices, see __openerp__.py file in the root directory
# ==================================================================================

from openerp import models


class CrmLead(models.Model):
    _name = 'crm.lead'
    _inherit = ['crm.lead', 'base.address']
