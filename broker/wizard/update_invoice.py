# -*- encoding: utf-8 -*-
# =============================================================================
# For copyright and license notices, see __openerp__.py file in root directory
# =============================================================================
from openerp import models, fields, api, _
from openerp.exceptions import Warning


class wizard_update_invoice(models.TransientModel):
    _name = 'wizard.update.invoice'

    date_invoice = fields.Date(string='Invoice Date', required=True)

    @api.multi
    def action_update_invoices(self):
        for invoice in self.env['account.invoice'].browse(self._context['active_ids']):
            if invoice.state == 'draft':
                invoice.date_invoice = self.date_invoice
            else:
                raise Warning("You can't change the date of the invoice '{}' because it is not in a Draft state".format(invoice.name))
        view_tree = self.env['ir.model.data'].get_object_reference('account', 'invoice_tree')
        view_form = self.env['ir.model.data'].get_object_reference('account', 'invoice_form')
        if view_tree and view_form:
            views = [[view_tree[1], 'tree'], [view_form[1], 'form']]
        else:
            views = False

        return {
            'name': _('Invoices'),
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'account.invoice',
            'views': views,
            'type': 'ir.actions.act_window',
            'target': 'current',
            'domain': str([('id', 'in', self._context['active_ids'])]),
            'context': "{'type': 'out_invoice'}"
        }
