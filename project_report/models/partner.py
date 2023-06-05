# -*- coding: utf-8 -*-
# © 2017 Didotech srl (http://www.didotech.com).
# © Andrei Levin <andrei.levin@didotech.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, api, fields, _


class ResPartner(models.Model):
    _inherit = 'res.partner'

    @api.multi
    def get_projects(self):
        for partner in self:
            projects = self.env['project.project'].search([
                ('partner_id', '=', self.id),
                ('state', 'in', ('draft', 'open', 'pending'))
            ])
            return projects
