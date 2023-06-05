# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2013 ISA s.r.l. (<http://www.isa.it>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
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
from openerp.tools.translate import _
from datetime import datetime
from openerp import tools
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT as DF
from fiscalcode import fiscalcode
import re


class res_partner_fiscalcode(orm.Model):
    _inherit = 'res.partner'

    def check_fiscalcode(self, cr, uid, ids, context={}):

        for partner in self.browse(cr, uid, ids):
            t_fiscalcode = partner.fiscalcode
            if not t_fiscalcode:
                return True
            elif ((len(t_fiscalcode) != 16
                       and  len(t_fiscalcode) != 11)
                   and partner.individual):
                return False
            else:
                regCf = '^[A-Z]{6}\d{2}[A-Z]\d{2}[A-Z]\d{3}[A-Z]$'
                regSTP = '^STP\d{13}$'
                regCRA = '^CRA\d{13}$'
                regENI = '^ENI\d{13}$'
                regTEMP = '^\d{11}$'
                if not (re.match(regCf, partner.fiscalcode)
                        or re.match(regSTP, partner.fiscalcode)
                        or re.match(regCRA, partner.fiscalcode)
                        or re.match(regENI, partner.fiscalcode)
                        or re.match(regTEMP, partner.fiscalcode)):
                    return False
            return True

    _columns = {
        'fiscalcode': fields.char('Fiscal Code', size=16,
                                help="Italian Fiscal Code"),
        'individual': fields.boolean('Individual',
                                help="If checked the C.F. is referred to a Individual Person"),
        'person_name': fields.char('Name',
                                size=40),
        'person_surname': fields.char('Surname',
                                size=40),
        'birth_date': fields.date('Birth Date'),
        'birth_city_id': fields.many2one('res.city',
                                'City of birth'),
        'sex': fields.selection([('M', 'Male'),
                                 ('F', 'Female'),
                                ],
                                "Sex"),
    }

    _defaults = {
        'individual': False,
        'sex': 'M',
    }

    _constraints = [(check_fiscalcode,
                     "The fiscal code doesn't seem to be correct.",
                     ["fiscalcode"])]

    def compute_fc(self, cr, uid, ids, context):
        active_id = ids[0]
        partner = self.pool.get('res.partner').browse(cr,
                                                      uid,
                                                      active_id,
                                                      context)
        form_obj = self.browse(cr, uid, ids, context)
        for t_fields in form_obj:
            if (not t_fields.person_surname
                    or not t_fields.person_name
                    or not t_fields.birth_date
                    or not t_fields.birth_city_id
                    or not t_fields.sex):
                raise orm.except_orm(_('Error'),
                                     _('One or more fields are missing'))
            if not t_fields.birth_city_id.cadaster_code:
                raise orm.except_orm(_('Error'),
                                     _('Cataster code is missing'))
            birth_date = datetime.strptime(t_fields.birth_date, DF)
            fc_obj = fiscalcode()
            CF = fc_obj.codicefiscale(t_fields.person_surname,
                            t_fields.person_name,
                            str(birth_date.day),
                            str(birth_date.month),
                            str(birth_date.year),
                            t_fields.sex,
                            t_fields.birth_city_id.cadaster_code)
            if (partner.fiscalcode
                    and partner.fiscalcode != CF):
                raise orm.except_orm(_('Error'),
                      _('Existing fiscal code %s is different from the computed one (%s). If you want to use the computed one, remove the existing one') % (partner.fiscalcode, CF))
            self.pool.get('res.partner').write(cr, uid,
                                               active_id,
                                               {'fiscalcode': CF},
                                               context)
        return {}

    def onchange_fiscalcode(self, cr, uid, ids, fiscal_code, context=None):
        warning = {}
        t_partner_ids = []
        if fiscalcode:
            t_partner_ids = self.search(cr,
                                        uid,
                                        [('fiscalcode', '=', fiscal_code)])
            if t_partner_ids:
                warning = {
                           'title': _('Warning!'),
                           'message': _('There is another partner with the same fiscalcode.')
                           }
        return {'value': {},
                'warning': warning
                }

    def compute_fc_inv(self, cr, uid, ids, context):
        # Partendo dal codice fiscale ricavo sesso, data di nascita
        # e comune di nascita
        active_id = ids[0]
        t_fiscalcode = context.get('fiscalcode', None)

        if (t_fiscalcode):
            birth_year  = t_fiscalcode[6:8]
            t_elem = "ABCDEHLMPRST"
            t_month = t_fiscalcode[8:9]
            t_find = t_elem.find(t_month)
            birth_month = ("%02d" % int(t_find + 1))
            birth_day   = t_fiscalcode[9:11]
            gender = "M"
            city_code = t_fiscalcode[11:15]

            if int(birth_day) > 31:
                birth_day_num = int(birth_day) - 40
                birth_day = "%02d" % birth_day_num
                gender = "F"
            
            today = fields.date.context_today(self, cr, uid, context=context)
            datetime_today = datetime.strptime(today, DF)
            t_year = datetime_today.strftime("%y")

            if (int(birth_year) > int(t_year)):
                birth_year = "19" + birth_year
            else:
                birth_year = "20" + birth_year

            city_obj = self.pool.get('res.city')
            city_ids = city_obj.search(cr, uid,
                                       [('cadaster_code','=',city_code)],
                                       offset=0, limit=1)
            city_id = city_ids[0]
            city_data = self.pool.get('res.city').browse(cr,
                                                         uid,
                                                         city_id,
                                                         context)
            province_id = city_data.province_id.id
            city_id = city_data.id

            ret_values = {'birth_date': birth_year + "-" + birth_month + "-" + birth_day,
                         'birth_city_id': city_id,
                         'sex': gender,
                         }

            self.pool.get('res.partner').write(cr, uid,
                                               active_id,
                                               ret_values,
                                               context)
        return {}
