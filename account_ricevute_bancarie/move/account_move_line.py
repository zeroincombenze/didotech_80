# -*- coding: utf-8 -*-
##############################################################################
#    
#    Copyright (C) 2012 Andrea Cometa.
#    Email: info@andreacometa.it
#    Web site: http://www.andreacometa.it
#    Copyright (C) 2012 Agile Business Group sagl (<http://www.agilebg.com>)
#    Copyright (C) 2012 Domsense srl (<http://www.domsense.com>)
#    Copyright (C) 2012 Associazione OpenERP Italia
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
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp.osv import fields, orm


# se distinta_line_ids == None allora non è stata emessa
class account_move_line(orm.Model):
    _inherit = "account.move.line"

    _columns = {
        'distinta_line_ids': fields.one2many('riba.distinta.move.line', 'move_line_id', "Dettaglio riba"),
        'unsolved_invoice_ids': fields.many2many('account.invoice', 'invoice_unsolved_line_rel', 'line_id', 'invoice_id', 'Unsolved Invoices'),
        'iban': fields.related('partner_id', 'bank_ids', 'iban', type='char', string='IBAN', store=False),
        'unsolved_move_originator_id': fields.many2one('account.move',
                                        'Unsolved Move Originator'),
    }
    _defaults = {
        'distinta_line_ids' : None,
    }

    def fields_view_get(
        self, cr, uid, view_id=None, view_type='form',
        context={}, toolbar=False, submenu=False
    ):
        # Special view for account.move.line object
        # (for ex. tree view contains user defined fields)
        result = super(account_move_line, self).fields_view_get(
            cr, uid, view_id, view_type, context, toolbar=toolbar,
            submenu=submenu)
        try:
            view_payments_tree_id = self.pool.get(
                'ir.model.data').get_object_reference(
                cr, uid, 'account_ricevute_bancarie',
                'view_riba_da_emettere_tree')
        except ValueError:
            return result
        if view_id == view_payments_tree_id[1]:
            # Use RiBa list - grazie a eLBati @ account_due_list
            return super(orm.Model, self).fields_view_get(
                cr, uid, view_id, view_type, context, toolbar=toolbar,
                submenu=submenu)
        else:
            return result
