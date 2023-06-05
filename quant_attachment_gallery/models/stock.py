# -*- encoding: utf-8 -*-
# =============================================================================
# For copyright and license notices, see __openerp__.py file in root directory
# =============================================================================

from openerp import models, fields, api


class StockQuant(models.Model):
    _inherit = 'stock.quant'

    image_ids = fields.One2many('ir.attachment', compute='_get_images', string="Images")
    has_image = fields.Boolean(compute='_has_image')
    image = fields.Binary('Image', related='product_id.image')

    @api.multi
    def _get_images(self):
        attachment_obj = self.env["ir.attachment"]
        for quant in self:
            attachment_ids = attachment_obj.search([
                ('res_model', '=', 'stock.quant'),
                ('res_id', '=', quant.id), ('file_type', 'ilike', 'image')
            ], order='name')
            quant.image_ids = attachment_ids.ids

    @api.one
    def _has_image(self):
        if self.image_ids:
            self.has_image = True
        else:
            self.has_image = False

    @api.multi
    def action_dummy(self):
        pass
