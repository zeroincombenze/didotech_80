# -*- encoding: utf-8 -*-
# =============================================================================
# For copyright and license notices, see __openerp__.py file in root directory
# =============================================================================

from openerp import models, fields, api, _


class AccountInvoiceLine(models.Model):
    _inherit = 'account.invoice.line'

    description = fields.Text(_('Description'))
