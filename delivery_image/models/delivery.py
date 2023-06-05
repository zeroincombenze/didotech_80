# -*- coding: utf-8 -*-
# #############################################################################
#
#    Copyright (C) 2016 Didotech srl (<http://www.didotech.com>)
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

from openerp import models, api, fields, tools


class DeliveryCarrier(models.Model):
    _inherit = 'delivery.carrier'

    image = fields.Binary("Image",
        help="This field holds the image used as image for the product, limited to 1024x1024px.")

    image_medium = fields.Binary("Image Medium",
        help="This field holds the image used as image for the product, limited to 128x128px.")

    image_small = fields.Binary("Image Small",
        help="This field holds the image used as image for the product, limited to 64x64px.")

    @api.onchange('image')
    def _set_image(self):
        self.image = tools.image_resize_image_big(self.image)
        self.image_small = tools.image_resize_image_small(self.image)
        self.image_medium = tools.image_resize_image_medium(self.image)
