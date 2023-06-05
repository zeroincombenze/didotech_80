# -*- encoding: utf-8 -*-
# =============================================================================
# For copyright and license notices, see __openerp__.py file in root directory
# =============================================================================

from openerp import models, api, _, fields


class ResPartner(models.Model):
    _inherit = 'res.partner'

    journal_id = fields.Many2one('account.journal', string=_('Payment Method'))
