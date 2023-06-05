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


class vat_registries(orm.Model):
    _name = "vat.registries.isa"
    _description = "Vat Registries Type"
    _columns = {
        'name': fields.char('Nome', size=64, required=True),
        'layout_type': fields.selection([
            ('customer', 'Vendite'),
            ('supplier', 'Acquisti'),
            ('corrispettivi', 'Corrispettivi'),
            ], 'Layout Stampa'),
        'sequence_iva_registry_id': fields.many2one('ir.sequence',
                                                    'Entry Sequence',
                                                    required=True),
        'period_id': fields.many2one('account.period',
                                     'Period',
                                     required=False,
                                     readonly=True),
        'page': fields.integer('Page Position',
                               required=False,
                               readonly=True),
    }

    _defaults = {
        'page': 0,
    }

    def onchange_sequence_iva_registry_id(self, cr, uid, ids,
                                          sequence_iva_registry_id,
                                          context=None):
        warning = {}
        if sequence_iva_registry_id:
            seq_registry_obj = self.pool.get('ir.sequence')
            seq_registry_ids = seq_registry_obj.search(cr, uid,
                                        [('id', '=', sequence_iva_registry_id)])
            for seq_registry_data in seq_registry_obj.browse(cr, uid,
                                                          seq_registry_ids):

                if seq_registry_data.prefix:
                    warning = {
                               'title': _('Warning!'),
                               'message': _('This sequence is not allowed because it contains a prefix')
                               }

                if seq_registry_data.suffix:
                    warning = {
                               'title': _('Warning!'),
                               'message': _('This sequence is not allowed because it contains a suffix')
                               }
        
        return {'value': {},
                'warning': warning,
                 }