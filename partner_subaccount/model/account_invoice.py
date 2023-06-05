# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2015 Didotech SRL
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp import models, fields, api, _
from openerp.exceptions import except_orm, Warning, RedirectWarning


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    @api.multi
    def action_create_subaccount(self):
        for invoice in self:
            if invoice.account_id.type == 'view':  # if i have an account of type view on invoice
                if invoice.partner_id:
                    rec_account = invoice.partner_id.property_account_receivable
                    pay_account = invoice.partner_id.property_account_payable
                    if invoice.company_id:
                        if invoice.partner_id.property_account_receivable.company_id and \
                                rec_account.company_id.id != invoice.company_id.id and \
                                pay_account.property_account_payable.company_id and \
                                pay_account.property_account_payable.company_id.id != invoice.company_id.id:
                            property_obj = self.env['ir.property']
                            rec_dom = [('name', '=', 'property_account_receivable'), ('company_id', '=', invoice.company_id.id)]
                            pay_dom = [('name', '=', 'property_account_payable'), ('company_id', '=', invoice.company_id.id)]
                            res_dom = [('res_id', '=', 'res.partner,%s' % invoice.partner_id.id)]
                            rec_prop = property_obj.search(rec_dom + res_dom) or property_obj.search(rec_dom)
                            pay_prop = property_obj.search(pay_dom + res_dom) or property_obj.search(pay_dom)
                            rec_account = rec_prop.get_by_record(rec_prop)
                            pay_account = pay_prop.get_by_record(pay_prop)
                            if not rec_account and not pay_account:
                                account_action = self.env.ref('account.action_account_config')
                                msg = _('Cannot find a chart of accounts for this company, You should configure it. \nPlease go to Account Configuration.')
                                raise RedirectWarning(msg, account_action.id, _('Go to the configuration panel'))

                    # recupero il sottoconto, poi và salvato sia su partner che su invoice
                    if invoice.type in ('out_invoice', 'out_refund'):
                        if invoice.account_id.id == rec_account.id:
                            invoice.account_id = invoice.partner_id.get_create_partner_account('customer').id
                        else:
                            invoice.account_id = rec_account.id
                    else:
                        if invoice.account_id.id == pay_account.id:
                            invoice.account_id = invoice.partner_id.get_create_partner_account('supplier').id
                        else:
                            invoice.account_id = pay_account.id

        return True
