# -*- coding: utf-8 -*-
# #############################################################################
#
#    Copyright (C) 2015 Didotech srl (<http://www.didotech.com>)
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

from openerp import models, api, fields, _


class ResPartner(models.Model):
    _inherit = 'res.partner'

    ext_partner_id = fields.Integer(_('External partner'), default=None, oldname='vg_partner_id')
    data_hash = fields.Char(_('Fingerprint'), size=32)

    _sql_constraints = [('ext_partner_uniq', 'unique(ext_partner_id)', 'Partner must be unique!')]

    @api.multi
    def get_hash(self, values=False):
        if values:
            partner_data = u"{street}{street2}{zip}{city}{email}{mobile}".format(
                street='street' in values and values['street'] or '',
                street2='street2' in values and values['street2'] or '',
                zip='zip' in values and values['zip'] or '',
                city='city' in values and values['city'] or '',
                # state='state_id' in values and values['state_id'] or '',
                # country='country_id' in values and values['country_id'] or '',
                email='email' in values and values['email'] or '',
                phone='phone' in values and values['phone'] or '',
                mobile='mobile' in values and values['mobile'] or ''
            )
        else:
            partner_data = u"{street}{street2}{zip}{city}{email}{mobile}".format(
                street=self.street or '',
                street2=self.street2 or '',
                zip=self.zip or '',
                city=self.city or '',
                # state=self.state_id and self.state_id.name or '',
                # country=self.country_id and self.country_id.name or '',
                email=self.email or '',
                phone=self.phone or '',
                mobile=self.mobile or ''
            )

        partner_data = partner_data.lower()
        partner_data = partner_data.replace(' ', '')

        return partner_data and str(hash(partner_data)) or ''

    @api.model
    def create(self, values):
        values['data_hash'] = self.get_hash(values)

        if values.get('country'):
            country = self.env['res.country'].with_context(lang='en_EN').search([('name', 'ilike', values['country'])]) or self.env['res.country'].with_context(lang='it_IT').search([('name', 'ilike', values['country'])])
            if country:
                values['country_id'] = country.id
            del values['country']

        return super(ResPartner, self).create(values)

    @api.multi
    def write(self, values):
        values['data_hash'] = self.get_hash(values) or self.get_hash()

        if values.get('country'):
            country = self.env['res.country'].with_context(lang='en_EN').search([('name', 'ilike', values['country'])]) or self.env['res.country'].with_context(lang='it_IT').search([('name', 'ilike', values['country'])])
            if country:
                values['country_id'] = country.id
            del values['country']

        return super(ResPartner, self).write(values)

    # @api.model
    # def _display_address(self, address, without_company=False):
    def _display_address(self, cr, uid, address, without_company=False, context=None):
        """
        The purpose of this function is to build and return an address formatted accordingly to the
        standards of the country where it belongs.

        :param address: browse record of the res.partner to format
        :returns: the address formatted in a display that fit its country habits (or the default ones
            if not country is specified)
        :rtype: string
        """

        # get the information that will be injected into the display format
        # get the address format
        address_format = address.country_id.address_format or \
            "%(street)s\n%(street2)s\n%(zip)s %(city)s (%(state_code)s)\n%(country_name)s"
        args = {
            'state_code': address.state_id.code or '',
            'state_name': address.state_id.name or '',
            'country_code': address.country_id.code or '',
            'country_name': address.country_id.name or '',
            'company_name': address.parent_name or '',
        }
        for field in self._address_fields(cr, uid, context=context):
            args[field] = getattr(address, field) or ''
        if without_company:
            args['company_name'] = ''
        elif address.parent_id:
            address_format = '%(company_name)s\n' + address_format
        return address_format % args
