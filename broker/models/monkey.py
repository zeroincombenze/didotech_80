# -*- encoding: utf-8 -*-
# =============================================================================
# For copyright and license notices, see __openerp__.py file in root directory
# =============================================================================

from openerp.addons.sale.sale import sale_order


def _amount_line_tax(self, cr, uid, line, context=None):
    val = 0.0

    for c in self.pool['account.tax'].compute_all(cr, uid, line.tax_id,
                                                  line.price_unit * (1 - (line.discount or 0.0) / 100.0),
                                                  line.product_uom_qty * line.product_uib,
                                                  line.product_id, line.order_id.partner_id)['taxes']:
        val += c.get('amount', 0.0)
    return val


sale_order._amount_line_tax = _amount_line_tax
