# -*- coding: utf-8 -*-
# #############################################################################
#
#    Copyright (C) 2015 Didotech srl (<http://www.didotech.com>)
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
# #############################################################################

from openerp import models, fields, api, _


class ProductProduct(models.Model):
    _inherit = "product.product"

    attachment_ids = fields.One2many(compute='get_attachments', string=_('Attachments'), comodel_name='ir.attachment',
                                     store=True, inverse_name='res_id')

    @api.one
    @api.depends('attachment_ids.sequence')
    def get_attachments(self):
        # product_ids = self.env['product.product'].search([('product_tmpl_id', '=', self.id)])
        self.attachment_ids = self.env['ir.attachment'].search(
            [('res_model', '=', 'product.product'), ('res_id', '=', self.id)]
        )

    @api.one
    def write(self, values):
        if values.get('attachment_ids'):
            # This is not a standard way. It is a workaround needed to be able to write to attachment_ids
            for attachment_values in values['attachment_ids']:
                attachment = self.env['ir.attachment'].browse(attachment_values[1])
                if attachment_values[0] == 0 and attachment_values[2]:
                    # Add new attachment
                    # Attention! This is just a draft! Create is not (yet) enabled in view
                    attachment_values[2].update({
                        'res_model': 'product.product',
                        'res_id': self.id
                    })
                    self.env['ir.attachment'].create(attachment_values[2])
                elif attachment_values[0] == 2:
                    attachment.unlink()
                else:
                    attachment.sequence = attachment_values[2] and attachment_values[2].get('sequence', 1) or 1

            del values['attachment_ids']

        return super(ProductProduct, self).write(values)
