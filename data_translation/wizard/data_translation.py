# -*- encoding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2016 Didotech srl (http://www.didotech.com)
#
#                          All Rights Reserved.
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
###############################################################################

from openerp import models, fields, api, _
from xlwt import *
from cStringIO import StringIO
from openerp.addons.core_extended.file_manipulation import import_sheet
import base64


class DataTranslation(models.TransientModel):
    _name = 'data.translation'
    _description = "Export data for translation"

    MODELS = (
        ('product.public.category', 'Product Public Category'),
        ('product.template', 'Product')
    )

    name = fields.Char()
    data = fields.Binary('File', readonly=True)
    model = fields.Selection(MODELS, 'model', required=True, translate=False)
    language = fields.Selection('_get_language', required=False)
    state = fields.Selection((
        ('import', 'import'),
        ('export', 'export'),
        ('end', 'end')
    ), 'state', required=True, translate=False, readonly=True, default='export')

    bold = easyxf('font: bold on')

    @api.model
    def _get_language(self):
        languages = self.env['res.lang'].search([])
        return [(language.code, language.name) for language in languages]

    @api.multi
    def action_start_export(self):
        self.state = 'end'

        name = dict(self.MODELS)[self.model].title()
        self.name = 'l10n_{}.xls'.format(name)

        book = Workbook(encoding='utf-8')
        # ws = book.add_sheet(name, cell_overwrite_ok=True)
        ws = book.add_sheet(name)

        ws.write(0, 0, 'Id', self.bold)
        ws.write(0, 1, _('Name'), self.bold)
        ws.write(0, 2, _('Translation'), self.bold)

        for row, line in enumerate(self.env[self.model].search([], order='id'), start=1):
            translated = self.env[self.model].with_context(lang=self.language).browse(line.id)
            ws.write(row, 0, line.id)
            ws.write(row, 1, line.name)
            ws.write(row, 2, translated.name)

            if hasattr(line, 'description'):
                if row == 1:
                    ws.write(0, 3, _('Description'), self.bold)
                    ws.write(0, 4, _('Translation'), self.bold)
                ws.write(row, 3, line.description)
                ws.write(row, 4, translated.description)

        # PARSING DATA AS STRING
        file_data = StringIO()
        book.save(file_data)
        # STRING ENCODE OF DATA IN WKSHEET
        out = file_data.getvalue()
        self.data = out.encode("base64")
        # self.data = base64.encodestring(output)

        view_rec = self.env['ir.model.data'].get_object_reference('data_translation', 'view_data_translation_export_form')
        if view_rec:
            view_id = view_rec and view_rec[1] or False

        return {
            'view_type': 'form',
            'name': "Export Translations",
            'view_id': [view_id],
            'res_id': self.id,
            'view_mode': 'form',
            'res_model': 'data.translation',
            'type': 'ir.actions.act_window',
            'target': 'new'
        }

    @api.multi
    def action_start_import(self):
        self.state = 'end'

        table, number_of_lines = import_sheet(self.name, base64.decodestring(self.data))

        for row in table:
            if isinstance(row[0], (int, float)):
                values = {}
                if row[2]:
                    values['name'] = row[2]

                if len(row) > 4 and row[4]:
                    values['description'] = row[4]

                if values:
                    translatable_row = self.env[self.model].with_context(lang=self.language).browse(int(row[0]))
                    translatable_row.write(values)

        view_rec = self.env['ir.model.data'].get_object_reference('data_translation', 'view_data_translation_import_form')
        if view_rec:
            view_id = view_rec and view_rec[1] or False

        return {
            'view_type': 'form',
            'name': "Import Done",
            'view_id': [view_id],
            'res_id': self.id,
            'view_mode': 'form',
            'res_model': 'data.translation',
            'type': 'ir.actions.act_window',
            'target': 'new'
        }
