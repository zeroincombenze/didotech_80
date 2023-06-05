# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2016 Didotech srl (info at didotech.com)
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
#

{
    'name': 'Italian Localisation - Report with Fiscal Code',
    'version': '4.0.0.0',
    'category': 'Localisation/Italy',
    "author": "Didotech srl",
    'website': 'http://www.didotech.com',
    'depends': [
        'base',
        'l10n_it_fiscalcode'
    ],
    'data': [
        'reports/report_invoice.xml'
    ],
    'test': [],
    'installable': True,
    'auto_install': False,
}
