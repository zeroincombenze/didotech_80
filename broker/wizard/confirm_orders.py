# -*- encoding: utf-8 -*-
# =============================================================================
# For copyright and license notices, see __openerp__.py file in root directory
# =============================================================================

from openerp import models, fields, api, _


class WizardConfirmOrders(models.TransientModel):
    _name = 'wizard.confirm.orders'
    _description = "Create distribution list"

    info = fields.Html('Info', readonly=True)
    state = fields.Selection((
        ('export', 'export'),
        ('end', 'end')
    ), 'state', required=True, translate=False, readonly=True, default='export')

    @api.model
    def default_get(self, fields):
        values = super(WizardConfirmOrders, self).default_get(fields)
        values['info'] = "<strong>Attention!<br/>Double check everything. This operation is <dev style='color: red;'>irreversible!</dev></strong>"
        return values

    @api.multi
    def action_confirm(self):
        order = self.env[self._context['active_model']].browse(self._context['active_id'])
        if self._context['active_model'] == 'broker.purchase.order':
            for sale_order in order.order_ids:
                sale_order.action_button_confirm()
                sale_order.action_invoice_create()

            order.state = 'confirmed'
        elif self._context['active_model'] == 'sale.order':
            order.action_button_confirm()
            order.action_invoice_create()

            # Set purchase order 'confirmed' if all orders are confirmed
            all_orders_count = self.env['sale.order'].search(
                [('state', '!=', 'draft'), ('broker_order_id', '=', order.broker_order_id.id)], count=True).id
            if len(order.broker_order_id.order_ids) == all_orders_count:
                order.broker_order_id.state = 'confirmed'
