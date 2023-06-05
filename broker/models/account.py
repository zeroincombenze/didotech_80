# -*- encoding: utf-8 -*-
# =============================================================================
# For copyright and license notices, see __openerp__.py file in root directory
# =============================================================================

from openerp import models, fields, api
from openerp.tools.translate import _
from datetime import datetime
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    supplier_id = fields.Many2one('res.partner', _('Supplier'), domain=[('supplier', '=', True)])
    credit_limit = fields.Float(compute='_get_credit_limit')
    expired = fields.Boolean(compute='_compute_expired', default=False)
    delivery_date = fields.Datetime('Delivery Date', compute='compute_delivery_date', readonly=True)
    sale_order_ids = fields.Many2many(comodel_name='sale.order', relation='sale_order_invoice_rel', column2='order_id', column1='invoice_id', string='Sale Orders', readonly=True)

    @api.one
    def _get_credit_limit(self):
        if self.supplier_id:
            customer_supplier_info = self.supplier_id.get_customer_ref(self.partner_id.id)
            if customer_supplier_info:
                self.credit_limit = customer_supplier_info.credit_limit

    @api.one
    def _compute_expired(self):
        if self.state == 'open' and datetime.now() > datetime.strptime(self.date_due, DEFAULT_SERVER_DATE_FORMAT):
            self.expired = True

    @api.one
    def compute_delivery_date(self):
        for sale_order in self.sale_order_ids:
            self.delivery_date = sale_order.delivery_date or sale_order.broker_order_id.delivery_date
