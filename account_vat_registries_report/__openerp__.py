# -*- coding: utf-8 -*-
##############################################################################
#    
#    Copyright (C) 2011-2013 Associazione OpenERP Italia
#    (<http://www.openerp-italia.org>). 
#    Copyright (C) 2012 Agile Business Group sagl (<http://www.agilebg.com>)
#    Copyright (C) 2012 Domsense srl (<http://www.domsense.com>)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
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
{
    'name': 'Registri IVA - VAT Registries',
    'version': '0.2',
    'category': 'Localisation/Italy',
    'description': """
Registri IVA
============

Si tratta di una procedura contabile per conformità con le disposizioni
fiscali italiane non prevista nello standard OperErp, DPR 633/62 art. 23 c.1.

I documenti soggetti ad Iva emessi o ricevuti sono contrassegnati con un
numero di protocollo, il registro iva è ordinato in base a questa numerazione.

            
            """,
    'author': 'ISA srl',
    'website': 'http://www.isa.it',
    'license': 'AGPL-3',
    "depends" : ['account',
                 'l10n_it_base',
                ],
    "data" : [
              'security/ir.model.access.csv',
              'data/registry_sequence.xml',
              'vat_protocol/vat_registries_view.xml',
              'vat_protocol/account_journal_view.xml',
             ],
    "demo" : [],
    "active": False,
    "installable": True
}
