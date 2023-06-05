# -*- encoding: utf-8 -*-
# =============================================================================
# For copyright and license notices, see __openerp__.py file in root directory
# =============================================================================

from openerp import models, fields, api, _


class ProjectProject(models.Model):
    _inherit = 'project.project'

    @api.one
    def set_main_image(self, image):
        if not self.image:
            self.image = image.image

    @api.multi
    def action_select_images(self):
        wizard_add_images = self.env['wizard.select.image'].create({
            'active_id': self._context.get('active_id'),
            'active_model': self._context.get('active_model')
        })

        view = self.env['ir.model.data'].get_object_reference('image_acquire', 'wizard_select_image')
        view_id = view and view[1] or False

        return {
            'type': 'ir.actions.act_window',
            'name': _('Image Selection'),
            'res_model': 'wizard.select.image',
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': [view_id],
            'target': 'new',
            'res_id': wizard_add_images.id
        }
