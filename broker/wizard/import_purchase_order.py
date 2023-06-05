# -*- encoding: utf-8 -*-
# =============================================================================
# For copyright and license notices, see __openerp__.py file in root directory
# =============================================================================
from openerp import models, fields, api, _
from openerp.addons.core_extended.file_manipulation import import_sheet
import base64


class WizardImportPurchaseOrder(models.TransientModel):
    _name = 'wizard.import.purchase.order'
    _description = "Import Purchase Order"

    name = fields.Char()
    data = fields.Binary('File', required=True)
    state = fields.Selection((
        ('import', 'import'),
        ('end', 'end')
    ), 'state', required=True, translate=False, readonly=True, default='import')
    info = fields.Text(_('Info'), readonly=True)

    @api.multi
    def action_start_import(self):
        table, number_of_lines = import_sheet(self.name, base64.decodestring(self.data))

        for row in table:
            if isinstance(row[0], float):
                # print row
                order_line = self.env['sale.order.line'].browse(int(row[0]))
                if order_line.product_uom_qty != row[3]:
                    order_line.product_uom_qty = row[3]

                if order_line.total_weight != row[4]:
                    order_line.total_weight = row[4]

                if order_line.price_unit != row[5]:
                    order_line.price_unit = row[5]

        wizard_values = {
            'state': 'end',
            'info': 'Import finished successfully'
        }
        self.write(wizard_values)

        view_rec = self.env['ir.model.data'].get_object_reference('broker', 'import_purchase_order_form')
        if view_rec:
            view_id = view_rec and view_rec[1] or False

        return {
            'view_type': 'form',
            'name': "Import Purchase Order",
            'view_id': [view_id],
            'res_id': self.id,
            'view_mode': 'form',
            'res_model': 'wizard.import.purchase.order',
            'type': 'ir.actions.act_window',
            'target': 'new'
        }
