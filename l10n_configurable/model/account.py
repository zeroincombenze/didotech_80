# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2014-2016 Didotech srl
#    (<http://www.didotech.com>).
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
##############################################################################

from openerp import fields, models, api


PAYMENT_TERM_TYPE_SELECTION = [
    ('BB', 'Bonifico Bancario'),
    ('BP', 'Bonifico Postale'),
    ('RD', 'Rimessa Diretta'),
    ('RB', 'Ricevuta Bancaria'),
    ('F4', 'F24'),
    ('PP', 'Paypal'),
    ('CC', 'Carta di Credito'),
    ('CO', 'Contrassegno'),
    ('CN', 'Contanti'),
]


class account_payment_term(models.Model):
    _inherit = 'account.payment.term'

    type = fields.Selection(
        PAYMENT_TERM_TYPE_SELECTION, "Type of payment"
    )


class account_tax_code_template(models.Model):
    _inherit = "account.tax.code.template"

    is_base = fields.Boolean(
        'Is base',
        help="This tax code is used for base amounts (field used by VAT registries)")
    vat_statement_type = fields.Selection(
        [('credit', 'Credit'), ('debit', 'Debit')],
        'Type',
        help="This establish whether amount will be loaded as debit or credit")
    vat_statement_sign = fields.Integer(
        'Sign used in statement',
        help="If tax code period sum is usually negative, set '-1' here")
    vat_statement_account_id = fields.Many2one(
        'account.account.template',
        "Account used for VAT statement")
    exclude_from_registries = fields.Boolean('Exclude from VAT registries')
    withholding_type = fields.Boolean("Ritenuta d'acconto")
    withholding_payment_term_id = fields.Many2one(
        'account.payment.term', "Termine di pagamento ritenuta d'acconto")


class account_tax_code(models.Model):
    _inherit = "account.tax.code"

    is_base = fields.Boolean(
        'Is base',
        help="This tax code is used for base amounts (field used by VAT registries)"
    )
    vat_statement_type = fields.Selection(
        [('credit', 'Credit'),
         ('debit', 'Debit')],
        'Type',
        help="This establish whether amount will be loaded as debit or credit"
    )
    vat_statement_sign = fields.Integer(
        'Sign used in statement',
        help="If tax code period sum is usually negative, set '-1' here"
    )
    vat_statement_account_id = fields.Many2one(
        'account.account',
        "Account used for VAT statement"
    )
    exclude_from_registries = fields.Boolean(
        'Exclude from VAT registries')
    withholding_type = fields.Boolean(
        "Ritenuta d'acconto")
    withholding_payment_term_id = fields.Many2one(
        'account.payment.term',
        "Termine di pagamento ritenuta d'acconto")


class account_tax_template(models.Model):
    _inherit = 'account.tax.template'

    auto_invoice_tax_id = fields.Many2one(
        'account.tax.template',
        string='Tax code for reverse charge invoice'
    )


class account_tax(models.Model):
    _inherit = 'account.tax'

    auto_invoice_tax_id = fields.Many2one(
        'account.tax',
        string='Tax code for reverse charge invoice'
    )

    # This lines creates problems in account.invoice.line:
    #   any value that is touched in a line eliminates taxes.
    # Disabled 27.04.2016
    # ref_base_code_id = fields.Many2one(
    #     'account.tax.code',
    #     string='Refund Base Code',
    #     related='base_code_id',
    #     copy=False, store=True, readonly=True
    # )
    # ref_tax_code_id = fields.Many2one(
    #     'account.tax.code',
    #     string='Refund Tax Code',
    #     related='tax_code_id',
    #     copy=False, store=True, readonly=True
    # )


# update tax codes with tax codes templates is_base values
class wizard_multi_charts_accounts(models.TransientModel):
    _inherit = 'wizard.multi.charts.accounts'

    @api.multi
    def execute(self):
        super(wizard_multi_charts_accounts, self).execute()

        wizard = self.search([])[0]
        if wizard.chart_template_id.name[:5] == "Italy" or \
                wizard.chart_template_id.name[:5] == "Itali":
            obj_multi = self.search([])[0]
            obj_tax_code = self.env['account.tax.code']
            tax_code_root_id = obj_multi.chart_template_id.tax_code_root_id.id
            company_id = obj_multi.company_id.id
            children_tax_code_template = self.env[
                'account.tax.code.template'].search(
                [('parent_id', 'child_of', [tax_code_root_id])])
            #sorted(children_tax_code_template, key=lambda x: x.id)
            for tax_code_template in children_tax_code_template:
                tax_code_id = obj_tax_code.search([
                    ('code', '=', tax_code_template.code),
                    ('company_id', '=', company_id)]
                )
                if tax_code_id:
                    obj_tax_code.write({
                            'is_base': tax_code_template.is_base,
                            'vat_statement_type':
                            tax_code_template.vat_statement_type,
                            'vat_statement_sign':
                            tax_code_template.vat_statement_sign,
                            'vat_statement_account_id':
                            tax_code_template.vat_statement_account_id.id,
                            'exclude_from_registries':
                            tax_code_template.exclude_from_registries,
                            'withholding_type': tax_code_template.withholding_type,
                            'withholding_payment_term_id':
                            tax_code_template.withholding_payment_term_id.id, })

            obj_tax = self.env['account.tax']
            tax_template_ids = self.env['account.tax.template'].search([])
            #sorted(tax_template_ids, key=lambda x: x.id)
            for tax_template in tax_template_ids:

                tax_id = obj_tax.search([
                    ('description', '=', tax_template.description),
                    ('company_id', '=', company_id)])
                if tax_id:
                    obj_tax.write({
                        'auto_invoice_tax_id': tax_template.auto_invoice_tax_id.id,
                    })
        return True
