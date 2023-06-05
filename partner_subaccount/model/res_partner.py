# -*- encoding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2014-2015 Didotech SRL (info at didotech.com)
#                          All Rights Reserved.
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsibility of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# guarantees and support are strongly advised to contract a Free Software
# Service Company
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
##############################################################################

from openerp import models, fields, api, _
from openerp import exceptions


class ResPartner(models.Model):
    _inherit = 'res.partner'

    block_ref_customer = fields.Boolean(_('Block Reference'))
    block_ref_supplier = fields.Boolean(_('Block Reference'))
    property_supplier_ref = fields.Char(_('Supplier Ref.'), size=16, help=_("The reference attributed by the partner to the current company as a supplier of theirs."))
    property_customer_ref = fields.Char(_('Customer Ref.'), size=16, help=_("The reference attributed by the partner to the current company as a customer of theirs."))

    @api.one
    @api.constrains('property_customer_ref')
    def _check_supplier_ref_unique(self):
        if self.property_customer_ref and len(self.search([('property_customer_ref', '=', self.property_customer_ref)])) > 1:
            raise exceptions.ValidationError(_("Codice Cliente deve essere Univoco"))

    @api.one
    @api.constrains('property_supplier_ref')
    def _check_supplier_ref_unique(self):
        if self.property_supplier_ref and len(self.search([('property_supplier_ref', '=', self.property_supplier_ref)])) > 1:
            raise exceptions.ValidationError(_("Codice Fornitore deve essere Univoco"))

    @api.model
    def _get_chart_template_property(self, property_chart=None):
        chart_obj = self.env['account.chart.template']
        # We need Administrator rights to read account.chart.template properties
        chart_templates = chart_obj.sudo().search([])
        if len(chart_templates) > 0 and property_chart:
            # We need Administrator rights to read account.chart.template properties
            for chart_template in chart_templates:
                # if it's not a view type code, it's another branch without partner_subaccount
                account_template = getattr(chart_template, property_chart)
                if account_template.type == 'view':
                    account_accounts = self.env['account.account'].search([('code', '=', account_template.code)])
                    if account_accounts:
                        return account_accounts[0]
                    else:
                        continue
                else:
                    continue
            else:
                raise exceptions.Warning("Parent Account Type is not of type 'view'")
        else:
            return []

    @api.multi
    def get_create_partner_account(self, partner_type):
        account_obj = self.env['account.account']

        if partner_type == 'customer':
            property_account = self.property_account_receivable
            type_account = 'receivable'
            property_ref_name = 'property_customer_ref'
            property_ref = self.property_customer_ref
        elif partner_type == 'supplier':
            property_account = self.property_account_payable
            type_account = 'payable'
            property_ref_name = 'property_supplier_ref'
            property_ref = self.property_supplier_ref
        else:
            # Unknown partner type
            return False

        if not property_ref:
            if partner_type == 'customer':
                property_ref = self.env['ir.sequence'].get('SEQ_CUSTOMER_REF')
            else:
                property_ref = self.env['ir.sequence'].get('SEQ_SUPPLIER_REF')

            setattr(self, property_ref_name, property_ref)
            # raise exceptions.Warning(_("Please set '{property_ref}' for {partner_type} '{partner}'").format(
            #     property_ref=property_ref_name, partner_type=partner_type, partner=self.name)
            # )

        if not property_account:
            property_account = self._get_chart_template_property('property_account_{}'.format(type_account))

        if property_account:
            code = '{code}{property_ref}'.format(code=property_account.code, property_ref=property_ref)
            accounts = account_obj.search([('code', '=', code)])
            if accounts:
                return accounts
            else:
                account_type_id = self.env['account.account.type'].search([('code', '=', type_account)])[0]
                return account_obj.create({
                    'name': self.name,
                    'code': code,
                    'user_type': account_type_id.id,
                    'type': type_account,
                    'parent_id': property_account.id,
                    'active': True,
                    'reconcile': True,
                    'currency_mode': property_account.currency_mode
                })
        else:
            return False

    @api.model
    def create(self, vals):
        #1 se marcato come cliente - inserire se non esiste
        if vals.get('customer'):
            vals['block_ref_customer'] = True
            if not vals.get('property_customer_ref', False):
                vals['property_customer_ref'] = self.env['ir.sequence'].get('SEQ_CUSTOMER_REF') or ''

        #2 se marcato come fornitore - inserire se non esiste
        if vals.get('supplier'):
            vals['block_ref_supplier'] = True
            if not vals.get('property_supplier_ref', False):
                vals['property_supplier_ref'] = self.env['ir.sequence'].get('SEQ_SUPPLIER_REF') or ''

        return super(ResPartner, self).create(vals)

    # Disabled: we should not unlink an account if it was already used (it is created at the moment of first usage)
    # TODO: Evaluate how to port to v8
    # def unlink(self, cr, uid, ids, context=None):
    #     if not context:
    #         context = {}
    #     ids_account_payable = []
    #     ids_account_receivable = []
    #     for partner in self.pool['res.partner'].browse(cr, uid, ids, context):
    #         if partner.property_account_payable and partner.property_account_payable.type != 'view':
    #             if partner.property_account_payable.balance == 0.0:
    #                 ids_account_payable.append(partner.property_account_payable.id)
    #             else:
    #                 ids.remove(partner.id)
    #         if partner.property_account_receivable and partner.property_account_receivable.type != 'view':
    #             if partner.property_account_receivable.balance == 0.0:
    #                 ids_account_receivable.append(partner.property_account_receivable.id)
    #             else:
    #                 ids.remove(partner.id)
    #
    #     res = super(ResPartner, self).unlink(cr, uid, ids, context)
    #     ids_account = list(set(ids_account_payable + ids_account_receivable))
    #
    #     if res and ids_account:
    #         self.pool['account.account'].unlink(cr, SUPERUSER_ID, ids_account, context)  # for unlink force superuser
    #     return res

    @api.multi
    def write(self, vals):
        if len(self) == 1:
            if not self.block_ref_customer and (vals.get('customer') or self.customer):
                # already a customer or flagged as a customer
                vals['block_ref_customer'] = True
                if not vals.get('property_customer_ref'):
                    # there isn't the partner code, so create it
                    vals['property_customer_ref'] = self.env['ir.sequence'].get('SEQ_CUSTOMER_REF') or ''

            if not self.block_ref_supplier and vals.get('supplier') or self.supplier:
                # already a customer or flagged as a customer
                vals['block_ref_supplier'] = True
                if not vals.get('property_supplier_ref'):
                    # there isn't the partner code, so create it
                    vals['property_supplier_ref'] = self.env['ir.sequence'].get('SEQ_SUPPLIER_REF') or ''
        return super(ResPartner, self).write(vals)

    @api.one
    def copy(self, defaults, context=None):
        raise exceptions.Warning(_('Duplication of a partner is not allowed'))
