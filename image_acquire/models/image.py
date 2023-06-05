# -*- encoding: utf-8 -*-
# =============================================================================
# For copyright and license notices, see __openerp__.py file in root directory
# =============================================================================

from openerp import models, fields, api, _
from openerp import tools
from openerp.addons.base.res.res_request import referencable_models

import string
import random
import os


class ImageAcquisition(models.Model):
    _name = 'image.acquisition'

    @api.model
    def _links_get(self):
        links = referencable_models(self, self._cr, self._uid, self._context)
        if 'stock.quant' not in dict(links):
            links.append(
                (u'stock.quant', u'Quants')
            )
        # return sorted(links, key=lambda link: link[0])
        return sorted(links, key=lambda link: link[1])

    name = fields.Char(_('Name'), required=True)
    image = fields.Binary("Image", compute='_compute_image', inverse='_write_image', required=True)
    destination = fields.Reference(_links_get, 'Destination', size=None)
    model = fields.Char('Model')

    @api.one
    def _compute_image(self):
        base_path = self.get_base_path()
        image_path = os.path.join(base_path, self.name)

        if os.path.isfile(image_path):
            image = open(image_path, 'rb').read()
        else:
            image = b''

        self.image = image.encode('base64')

    @staticmethod
    def id_generator(size=6, chars=string.ascii_uppercase + string.digits):
        return ''.join(random.choice(chars) for _ in range(size))

    @api.one
    def _write_image(self):
        base_dir = self.get_base_path()

        for record in self:
            if record.image:
                if record.name:
                    name = record.name.lower()
                else:
                    name = self.id_generator()

                n = 1
                image_name = name
                while os.path.isfile(os.path.join(base_dir, image_name + '.jpeg')):
                    n += 1
                    image_name = "{}_{}".format(name, n)

                with open(os.path.join(base_dir, image_name + '.jpeg'), 'wb') as new_image:
                    record.name = image_name + '.jpeg'
                    new_image.write(record.image.decode('base64'))

    @api.model
    def get_base_path(self):
        base_path = tools.config.filestore(self._cr.dbname)
        base_dir = os.path.join(base_path, 'acquisition')
        if not os.path.isdir(base_dir):
            os.mkdir(base_dir)
        return base_dir

    @api.multi
    def unlink(self):
        for record in self:
            # Ugly but pythonic:
            try:
                os.remove(os.path.join(self.get_base_path(), record.name))
            except OSError:
                pass

        return super(ImageAcquisition, self).unlink()

    def attach(self, destination_model, destination_id):
        attachment = self.env['ir.attachment'].create({
            'description': self.name,
            'res_model': destination_model,
            'res_id': destination_id,
            'name': self.name,
            'type': 'binary',
            'datas': self.image
        })

        if attachment and attachment.datas:
            self.unlink()

    @api.model
    def create(self, values):
        lookup = [
            {'model': 'project.project', 'field': 'plate'},
            {'model': 'project.project', 'field': 'name'},
            {'model': 'stock.quant', 'field': 'lot_id.name'}
        ]

        if '_' in values['name']:
            name, progress = values['name'].rsplit('_', 1)
        else:
            name = values['name']

        for search in lookup:
            results = self.env[search['model']].search([
                (search['field'], '=ilike', name)
            ])
            if len(results) == 1:
                values.update({
                    'destination': '{model}, {serial_id}'.format(
                        model=results._name, serial_id=results.id),
                    'model': results._name
                })
                break

        return super(ImageAcquisition, self).create(values)

    @api.model
    def move_image(self):
        for image in self.browse(self._context['active_ids']):
            if image.destination:
                if hasattr(image.destination, 'set_main_image'):
                    image.destination.set_main_image(image)
                image.attach(str(image.destination._model), image.destination.id)

        return True
