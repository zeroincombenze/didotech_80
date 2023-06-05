# -*- encoding: utf-8 -*-
# =============================================================================
# For copyright and license notices, see __openerp__.py file in root directory
# =============================================================================

from openerp import models, api, fields, _
from openerp.http import request

import json
import logging
_logger = logging.getLogger(__name__)
_logger.setLevel(logging.DEBUG)


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    class Meta:
        context = {
            'model': 'account.invoice',
            'fields': (
                'number', 'partner_id', 'date_invoice', 'invoice_line',
                'state', 'amount_untaxed', 'amount_tax', 'amount_total'
            ),
            'fields_map': {
                'invoice_line': (
                    'name', 'product_id', 'quantity', 'price_unit', 'price_subtotal'
                ),
                'partner_id': ('name',),
                'product_id': ('name', 'image_medium', 'lst_price')
            }
        }

    @api.model
    def json_list(self, partner_remote_id=False):
        if partner_remote_id:
            partner = self.env['res.partner'].search([('ext_partner_id', '=', partner_remote_id)])
            if partner:
                invoices = self.search([('partner_id', '=', partner.id), ('type', '=', 'out_invoice'), ('state', 'in', ('paid', 'open'))])
                if invoices:
                    return json.loads(self.env['rest.ful'].with_context(self.Meta.context).get(invoices.ids))
                else:
                    return {'results': [], 'status': 200, 'count': 0}
            else:
                return {'error': "Partner with this ID does not exists in Odoo database", 'status': 404}
        else:
            return {'error': "Partner is required", 'status': 400}

    @api.multi
    def json_pdf(self):
        request.website_multilang = False

        pdf = self.env['report'].get_pdf(self, 'account.report_invoice')
        if pdf:
            return {'data': pdf.encode('base64'), 'name': self.number}
        else:
            return {'error': 'Attachment not found', 'name': self.number}
