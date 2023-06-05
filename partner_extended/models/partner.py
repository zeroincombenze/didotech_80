# -*- encoding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2014-2016 Didotech srl (info at didotech.com)
#
#                          All Rights Reserved.
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsability of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# garantees and support are strongly adviced to contract a Free Software
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

from openerp import models, api, _, fields
from openerp import exceptions
from urlparse import urlparse

# import pdb


class ResPartner(models.Model):
    _inherit = 'res.partner'

    # not_qualified = fields.Binary(_('Not qualified'), help=_("Partner which is not a Customer o Supplier"))
    hostname = fields.Char(_('Hostname'), compute='get_url', default='')
    domain = fields.Char(_('Domain'), compute='get_url', default='')

    @api.one
    @api.constrains('vat')
    def _check_vat_unique(self):
        if self.vat:
            partners = self.search([('vat', 'ilike', self.vat), ('parent_id', '=', False)])
            if len(partners) > 1:
                raise exceptions.Warning(_("Partner with VAT '{vat}' is already present in database").format(vat=self.vat))
        return True

    # @api.one
    # @api.onchange('not_qualified')
    # def onchange_not_qualified(self):
    #     pdb.set_trace()
    #     if self.not_qualified:
    #         self.customer = False
    #         self.supplier = False

    @api.one
    @api.depends('website')
    def get_url(self):
        if self.website:
            parsed_url = urlparse(self.website)
            self.hostname = parsed_url and parsed_url.hostname or ''
            if self.hostname[:4] == 'www.':
                self.domain = self.hostname[4:]
