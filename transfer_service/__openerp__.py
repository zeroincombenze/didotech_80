# -*- coding: utf-8 -*-
# #############################################################################
#
#    Copyright (C) 2015-2016 Didotech srl (<http://www.didotech.com>)
#    All Rights Reserved
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
# #############################################################################

{
    'name': 'Transfer Service',
    'version': '4.2.38.30',
    'category': 'Generic Modules/Service',
    'summary': 'Chauffeur Transfer Service',
    'author': 'Didotech Srl',
    'website': 'http://www.didotech.com',
    'depends': [
        'base',
        'sale',
        'project',
        'l10n_base_data_it',
        'google_maps_distance_duration',
        'web_m2x_options',
        # 'web_relativedelta',
        'core_extended',
        'purchase',
        'document',
        'template_transfer'
    ],
    'data': [
        'views/sale_view.xml',
        'views/transfer_view.xml',
        'views/project_view.xml',
        'views/project_menu.xml',
        'views/product_view.xml',
        'wizard/assign_supplier_view.xml',
        'wizard/create_quotation_order_view.xml',
        'wizard/select_template.xml',
        # 'cron.xml',
        'report/sale_order_template_line_report.xml',
        'report/invoice_detail_report.xml',
        'report/task_report.xml',
        'views/account_view.xml',
        'views/company_view.xml',
        'security/ir.model.access.csv'
    ],
    'test': [],
    'installable': True,
    'active': False,
}
