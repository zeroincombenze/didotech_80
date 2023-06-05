# -*- coding: utf-8 -*-
##############################################################################
#    
#    Copyright (C) 2010 Associazione OpenERP Italia
#    (<http://www.openerp-italia.org>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp import models, fields, api, _
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT
from openerp import exceptions

import time


class WizardAssignDdt(models.TransientModel):
    _name = "wizard.assign.ddt"

    @api.multi
    def assign_ddt(self):
        picking_obj = self.env['stock.picking']
        for picking in picking_obj.browse(self._context.get('active_ids', [])):
            if picking.ddt_number:
                raise exceptions.Error(_('DDT number already assigned'))

            # Assign ddt from journal's sequence
            if picking.picking_type_id.ddt_sequence:
                picking.write({
                    'ddt_number': self.env['ir.sequence'].get(picking.picking_type_id.ddt_sequence.code),
                    'ddt_date': time.strftime(DEFAULT_SERVER_DATE_FORMAT),
                })
            else:
                picking.write({
                    'ddt_number': self.env['ir.sequence'].get('stock.ddt'),
                    'ddt_date': time.strftime(DEFAULT_SERVER_DATE_FORMAT),
                })
        return {
            'type': 'ir.actions.act_window_close'
        }
