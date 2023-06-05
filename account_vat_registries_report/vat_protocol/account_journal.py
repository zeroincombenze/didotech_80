# -*- coding: utf-8 -*-
##############################################################################
#    
#    Copyright (C) 2013 ISA srl (<http://www.isa.it>)
#    All Rights Reserved
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

from openerp.osv import fields, orm
from openerp.tools.translate import _


class account_journal(orm.Model):
    _inherit = 'account.journal'

    _columns = {
        'iva_registry_id' : fields.many2one('vat.registries.isa',
                                            'VAT Registry'),
    }

    def onchange_iva_registry_id(self, cr, uid, ids,
                                 iva_registry_id,
                                 context=None):
        warning = {}
        if iva_registry_id:
            vat_registry_obj = self.pool.get('vat.registries.isa')
            vat_registry_ids = vat_registry_obj.search(cr, uid,
                                        [('id', '=', iva_registry_id)])
            for vat_registry_data in vat_registry_obj.browse(cr, uid,
                                                          vat_registry_ids):
                t_seq = vat_registry_data.sequence_iva_registry_id
                if t_seq and t_seq.prefix:
                    warning = {
                               'title': _('Warning!'),
                               'message': _('This sequence is not allowed because it contains a prefix')
                               }

                if t_seq and t_seq.suffix:
                    warning = {
                               'title': _('Warning!'),
                               'message': _('This sequence is not allowed because it contains a suffix')
                               }

        return {'value': {},
                'warning': warning,
                 }
