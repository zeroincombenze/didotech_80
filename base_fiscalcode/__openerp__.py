# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2010-2012 Associazione OpenERP Italia
#    (<http://www.openerp-italia.org>).
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
{
    'name': 'Fiscal Code for Partners - ISA',
    'version': '0.1',
    'category': 'Localisation/Italy',
    'description': """
This module customizes OpenERP in order to fit italian laws and mores - Account version

Functionalities:

- Fiscal code computation for partner


Questo modulo customizza OpenERP per permettere di essere allineati con le leggi italiane ed altro.


""",
    'author': 'ISA srl',
    'website': 'http://www.openerp-italia.org',
    'license': 'AGPL-3',
    "depends" : [
                 'base',
                 'l10n_it_base'
                 ],
    "data" : [
                  'res_partner_view.xml',
                  ],
    "demo" : [],
    'test': [],
    "active": False,
    "installable": True
}
