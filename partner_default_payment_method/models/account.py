# -*- encoding: utf-8 -*-
# =============================================================================
# For copyright and license notices, see __openerp__.py file in root directory
# =============================================================================

from openerp import models, api, _, fields


class AccountVoucher(models.Model):
    _inherit = 'account.voucher'

    @api.model
    def default_get(self, fields):
        values = super(AccountVoucher, self).default_get(fields)
        if 'partner_id' in values:
            partner = self.env['res.partner'].browse(values['partner_id'])
            values['journal_id'] = partner.journal_id.id
        return values
