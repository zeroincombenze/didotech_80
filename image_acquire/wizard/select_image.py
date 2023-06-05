# -*- encoding: utf-8 -*-
# =============================================================================
# For copyright and license notices, see __openerp__.py file in root directory
# =============================================================================

from openerp import models, fields, api


class WizardSelectImage(models.TransientModel):
    _name = 'wizard.select.image'

    image_ids = fields.Many2many('image.acquisition', string="Images")
    active_id = fields.Integer()
    active_model = fields.Char()

    @api.model
    def default_get(self, fields):
        values = super(WizardSelectImage, self).default_get(fields)
        image_ids = self.env['image.acquisition'].search([])
        if image_ids:
            values['image_ids'] = image_ids.ids

        return values

    @api.multi
    def action_move_images(self):
        image_ids = self.ids
        wizard = self.browse(self._context['active_id'])

        destination = self.env[wizard.active_model].browse(wizard.active_id)

        for image in self.env['image.acquisition'].browse(image_ids):
            if hasattr(destination, 'set_main_image'):
                destination.set_main_image(image)
            image.attach(wizard.active_model, wizard.active_id)

        return {'type': 'ir.actions.act_window_close'}
