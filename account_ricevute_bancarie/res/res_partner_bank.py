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


class res_partner_bank_add(orm.Model):
    _inherit = 'res.partner.bank'

    def _get_iban(self, cr, uid, ids, field_names, args,
                           context=None):
        result = {}
        for data in self.browse(cr, uid, ids, context=context):
            t_acc_number = data.acc_number
            if t_acc_number:
                result[data.id] = t_acc_number.replace(' ', '')
            else:
                result[data.id] = ''
        return result

    _columns = {
        'codice_sia' : fields.char('Codice SIA', size=5, help="Identification Code of the Company in the System Interbank"),
        # iban field is Deprecated in v7
        # We use acc_number instead of IBAN since v6.1, but we keep this field
        # to not break community modules.
        'iban': fields.function(_get_iban,
                                string='IBAN',
                                method=True,
                                store=False,
                                help="International Bank Account Number",
                                type="char"),
    }
