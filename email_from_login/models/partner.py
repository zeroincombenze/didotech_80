# -*- encoding: utf-8 -*-
# =============================================================================
# For copyright and license notices, see __openerp__.py file in root directory
# =============================================================================

from openerp import models, fields, api


class ResPartner(models.Model):
    _inherit = 'res.partner'

    @api.multi
    def set_email(self):
        for partner in self.browse(self._context['active_ids']):
            if not partner.email and not partner.parent_id and partner.user_ids:
                user = partner.user_ids[0]
                if '@' in user.login:
                    partner.email = user.login
