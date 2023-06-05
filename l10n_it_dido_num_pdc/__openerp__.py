# -*- encoding: utf-8 -*-
##############################################################################
#    
#    Copyright (C) 2015 Didotech SRL
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
{
    'name': 'Italia - Didotech SRL',
    'version': '8.0.3.0.1',
    'category': 'Localization/Account Charts',
    'description': """
        Profilatura Didotech SRL, 
    """,
    'author': 'Didotech SRL',
    'website': 'http://www.didotech.com',
    'license': 'AGPL-3',
    "depends": [
        'account_accountant',
        'l10n_configurable',
        'sale',
        #'profile_base',
        #'account_tax_simplified',
        #'account_withholding_tax',
        #'hr_agent',
        #'res_user_signature',
        #'sale_order_dates',
        #'sale_order_attachment',
        #'multi_payment',
    ],
    "data": [
        'l10n_it/data/account.account.type.csv',
        'l10n_it/data/account.account.template.csv',
        'l10n_it/data/account.tax.code.template.csv',
        'l10n_it/account_chart.xml',
        'l10n_it/data/account.tax.template.csv',
        'l10n_it/data/account.fiscal.position.template.csv',
        'l10n_it/data/account.fiscal.position.tax.template.csv',
        'l10n_it/l10n_chart_it_generic.xml',
        #'sale_order/reports.xml',
        #'purchase_order/reports.xml',
        #'stock_picking/reports.xml',
        #'account_invoice/report.xml',
    ],
    "demo": [],
    "active": False,
    "installable": True,
}
