# -*- encoding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2015 Didotech SRL (info at didotech.com)
#                          All Rights Reserved.
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsibility of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# guarantees and support are strongly advised to contract a Free Software
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

from openerp import models, api
from collections import OrderedDict
from datetime import datetime
import json
import types


class RestFul(models.AbstractModel):
    _name = 'rest.ful'

    @api.model
    def set_init(self):
        self.fields = self._context.get('fields')
        if self._context.get('fields_map'):
            self.fields_map = self._context['fields_map']

        self.model_obj = self.env[self._context['model']]

    @api.model
    def serialize(self, record, odoo_fields):
        data = OrderedDict([
            ('pk', record.id),
            ('_name', record._name)
        ])

        for k, field in enumerate(odoo_fields):
            # Exceptions:
            if field == 'list_price' and record._name == 'sale.order.line':
                odoo_product = record.product_id.product_tmpl_id
                if odoo_product:
                    data['list_price'] = odoo_product.get_price(partner_id=record.order_id.partner_id.id, quantity=record.product_uom_qty)[0]
            elif not field == 'url':
                try:
                    attribute = getattr(record, field)

                    if isinstance(attribute, list):
                        data[field] = []
                    elif isinstance(attribute, (datetime,)):
                        data[field] = str(attribute)
                    elif isinstance(attribute, models.Model):
                        data[field] = []
                        for line in attribute:
                            data[field].append(self.serialize(line, self.fields_map[field]))
                    elif isinstance(attribute, types.MethodType):
                        data[field] = attribute()
                    else:
                        data[field] = attribute
                except:
                    continue
            elif field == 'url':
                if k == 0:
                    data = OrderedDict([('url', '')] + data.items())
                else:
                    data['url'] = ''
        return data

    @api.model
    def rbrowse(self, odoo_record_ids):
        if odoo_record_ids and not isinstance(odoo_record_ids, (list, tuple)):
            odoo_record_ids = [odoo_record_ids]

        if odoo_record_ids:
            odoo_records = self.model_obj.search([('id', 'in', odoo_record_ids)])
        else:
            odoo_records = self.model_obj.search([])

        if odoo_records:
            return odoo_records
        else:
            return False

    @api.model
    def get(self, odoo_record_ids, queryset=False):
        self.set_init()

        if queryset:
            if odoo_record_ids:
                queryset.append(('id', 'in', odoo_record_ids))
            recordset = self.model_obj.search(queryset)
        else:
            recordset = self.rbrowse(odoo_record_ids)

        if recordset:
            recordset.count = len(recordset)
            if isinstance(recordset.ids, (tuple, list)):
                data = OrderedDict([
                    ('count',  len(recordset)),
                    ('results', [self.serialize(order, self.fields) for order in recordset]),
                ])
                return json.dumps(data)
            else:
                return json.dumps(self.serialize(recordset, self.fields))
        else:
            return json.dumps({'error': 'Empty recodset'})
