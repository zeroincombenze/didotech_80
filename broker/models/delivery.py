# -*- encoding: utf-8 -*-
# =============================================================================
# For copyright and license notices, see __openerp__.py file in root directory
# =============================================================================

from openerp import models, fields, api


class DeliveryCarrier(models.Model):
    _inherit = 'delivery.carrier'

    sequence = fields.Integer('Sequence')

    _order = 'sequence'
