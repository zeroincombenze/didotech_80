# -*- encoding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2013-2014 Didotech SRL (info at didotech.com)
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

from openerp.osv import orm, fields

COLOR_SELECTION = [
    ('aqua', u"Aqua"),
    ('black', u"Black"),
    ('blue', u"Blue"),
    ('brown', u"Brown"),
    ('cadetblue', u"Cadet Blue"),
    ('darkblue', u"Dark Blue"),
    ('fuchsia', u"Fuchsia"),
    ('forestgreen', u"Forest Green"),
    ('green', u"Green"),
    ('grey', u"Grey"),
    ('red', u"Red"),
    ('orange', u"Orange")
]


class crm_lead(orm.Model):
    _inherit = 'crm.lead'

    def get_color(self, cr, uid, ids, field_name, arg, context):
        value = {}
        for lead in self.browse(cr, uid, ids, context):
            if lead.categ_ids:
                # TODO is not correct way, i take only first element of list
                value[lead.id] = lead.categ_ids[0].color
            else:
                value[lead.id] = 'black'
        return value
   
    def _get_sale_order(self, cr, uid, ids, field_name, model_name, context=None):
        return {
            crm_lead.id: self.pool['sale.order'].search(cr, uid, [('partner_id', '=', crm_lead.partner_id.id)])
            for crm_lead in self.pool['crm.lead'].browse(cr, uid, ids, context)
        }
    
    def _get_crm_lead(self, cr, uid, ids, field_name, model_name, context=None):
        crm_lead_obj = self.pool['crm.lead']
        return {
            crm_lead.id: crm_lead_obj.search(cr, uid, [('partner_id', '=', crm_lead.partner_id.id), ('name', '!=', crm_lead.name)])
            for crm_lead in crm_lead_obj.browse(cr, uid, ids, context)
        }

    _columns = {
        'province': fields.many2one('res.province', string='Province', ondelete='restrict'),
        'region': fields.many2one('res.region', string='Region', ondelete='restrict'),
        'find_city': fields.boolean('Find City'),
        'website': fields.char('Website', size=64, help="Website of Partner."),
        'function_id': fields.many2one('res.contact.function', 'Function'),
        'partner_category_id': fields.many2one('res.partner.category', 'Partner Category'),
        'row_color': fields.function(get_color, 'Row color', type='char', readonly=True, method=True),
        'sale_order_ids': fields.function(_get_sale_order, 'Sale Order', type='one2many', relation="sale.order", readonly=True, method=True),
        'crm_lead_ids': fields.function(_get_crm_lead, 'Opportunity', type='one2many', relation="crm.lead", readonly=True, method=True)
    }

    _defaults = {
        'name': '/',
    }

    _order = "create_date desc"

    def on_change_city(self, cr, uid, ids, city, zip_code=None):
        return self.pool['res.partner'].on_change_city(cr, uid, ids, city, zip_code)

    def on_change_zip(self, cr, uid, ids, zip_code):
        return self.pool['res.partner'].on_change_zip(cr, uid, ids, zip_code)

    def on_change_province(self, cr, uid, ids, province):
        return self.pool['res.partner'].on_change_province(cr, uid, ids, province)

    def on_change_region(self, cr, uid, ids, region):
        return self.pool['res.partner'].on_change_region(cr, uid, ids, region)

    def on_change_function_id(self, cr, uid, ids, function_id):
        res = {'value': {}}
        if function_id:
            function = self.pool['res.contact.function'].browse(cr, uid, function_id, context=None)
            res = {'value': {
                'function': function.name
            }}
        return res

    def create(self, cr, uid, vals, context=None):
        vals = self.pool['res.partner']._set_vals_city_data(cr, uid, vals)

        if vals.get('name', '/') == '/':
            sequence_data_id = self.pool['ir.model.data'].get_object_reference(
                cr, uid, 'crm_lead_extended', 'seq_lead_item')
            if sequence_data_id:
                new_name = self.pool['ir.sequence'].next_by_id(cr, uid, sequence_data_id[1], context=context)
                vals.update({'name': new_name})

        result = super(crm_lead, self).create(cr, uid, vals, context=context)
        return result

    def write(self, cr, uid, ids, vals, context=None):
        vals = self.pool['res.partner']._set_vals_city_data(cr, uid, vals)
        return super(crm_lead, self).write(cr, uid, ids, vals, context=context)

    def copy(self, cr, uid, ids, defaults, context=None):
        defaults['name'] = '/'
        return super(crm_lead, self).copy(cr, uid, ids, defaults, context)
