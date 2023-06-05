# -*- encoding: utf-8 -*-
# =============================================================================
# For copyright and license notices, see __openerp__.py file in root directory
# =============================================================================

from openerp import api, models, fields, _


class ResCompany(models.Model):
    _inherit = 'res.company'

    custom_header = fields.Boolean(_('Custom Header'))
    qweb_header = fields.Text(_('Header (QWeb)'))
    cf_in_header = fields.Boolean(_('Codice Fiscale in Header'))
