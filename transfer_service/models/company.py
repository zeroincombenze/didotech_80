# -*- encoding: utf-8 -*-
# =============================================================================
# For copyright and license notices, see __openerp__.py file in root directory
# =============================================================================

from openerp import models, fields, api
from openerp.tools.translate import _


class ResCompany(models.Model):
    _inherit = 'res.company'

    closing_delay = fields.Integer(_('Closing Delay'),
                                   help=_("After how many days the task should be closed. '1' day means the day after the task date."),
                                   default=4)
