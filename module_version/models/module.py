# -*- encoding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2013-2016 Didotech srl (info at didotech.com)
#
#                          All Rights Reserved.
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsability of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# garantees and support are strongly adviced to contract a Free Software
# Service Company
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
##############################################################################

from openerp import models, fields, api, _
from openerp import exceptions


class module(models.Model):
    _inherit = "ir.module.module"

    @api.multi
    def _check_upgrade(self):
        installed_modules = self.search([('state', 'in', ['installed', 'to upgrade', 'to remove'])])
        for module in installed_modules:
            # if module.name == 'module_version':
            #     print module.name
            #     pdb.set_trace()
            if not module.latest_version == self.get_module_info(module.name).get('version', '') and not module.need_upgrade:
                # module.need_upgrade = True
                module.write({'need_upgrade': True})
            elif module.latest_version == self.get_module_info(module.name).get('version', '') and module.need_upgrade:
                module.need_upgrade = False

    @api.one
    @api.depends('installed_version', 'latest_version')
    def _need_upgrade(self):
        if self.state in ['installed', 'to upgrade', 'to remove'] and not self.latest_version == self.get_module_info(self.name).get('version', ''):
            self.need_upgrade = True
        else:
            self.need_upgrade = False

    need_upgrade = fields.Boolean(compute='_need_upgrade', string=_('Need Upgrade'), store=True)
    check_upgrade = fields.Boolean(compute='_check_upgrade', string=_('Need Upgrade (hidden)'), store=False)

    _order = 'name'

    @api.model
    def set_modules_to_upgrade(self, view=False):
        modules = self.env['ir.module.module']

        installed_modules = self.search([('state', 'in', ['installed', 'to upgrade', 'to remove'])])
        for module in installed_modules:
            if not module.latest_version == self.get_module_info(module.name).get('version', '') or module.state in ('to upgrade', 'to remove'):
                modules += module

        if modules:
            modules.button_upgrade()
            if view:
                return modules
            else:
                return True
        else:
            return False

    @api.multi
    def verify_modules(self):
        modules = self.set_modules_to_upgrade(view=True)
        if modules:
            return {
                'type': 'ir.actions.act_window',
                'name': _('Modules to upgrade'),
                'res_model': 'ir.module.module',
                'view_type': 'form',
                'view_mode': 'tree,form',
                'view_id': False,
                'target': 'current',
                'res_id': False,
                "domain": [('id', 'in', modules.ids)]
            }
        else:
            raise exceptions.Warning(_('There are no modules that should be updated'))
