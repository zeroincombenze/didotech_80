# -*- encoding: utf-8 -*-
# =============================================================================
# For copyright and license notices, see __openerp__.py file in root directory
# =============================================================================

from openerp import models, fields, api, _


class WizardSelectDestination(models.TransientModel):
    _name = 'wizard.select.image.destination'

    @api.multi
    def _get_destinations(self):
        return [
            ('stock.quant', 'Quant'),
            ('project.project', 'Project')
        ]

    destination = fields.Reference(_get_destinations, 'Destination')

    @api.multi
    def action_move_images(self):
        if 'active_ids' in self._context:
            for image in self.env['image.acquisition'].browse(self._context['active_ids']):
                if hasattr(self.destination, 'set_main_image'):
                    self.destination.set_main_image(image)

                # attachment = self.env['ir.attachment'].create({
                #     'description': image.name,
                #     'res_model': str(self.destination._model),
                #     'res_id': self.destination.id,
                #     'name': image.name,
                #     'type': 'binary',
                #     'datas': image.image
                # })
                #
                # if attachment and attachment.datas:
                #     image.unlink()

                image.attach(str(self.destination._model), self.destination.id)

        return {'type': 'ir.actions.act_window_close'}
