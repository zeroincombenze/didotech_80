# -*- coding: utf-8 -*-
# #############################################################################
#
#    Copyright (C) 2015 Didotech srl (<http://www.didotech.com>)
#
#                       All Rights Reserved
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

from openerp import models, fields, api, _
from openerp import exceptions
import openerp.addons.decimal_precision as dp
from openerp.addons.google_maps_distance_duration.google_maps import GoogleMapsDistance
from datetime import datetime
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT
import logging
_logger = logging.getLogger(__name__)
_logger.setLevel(logging.DEBUG)


class Transfer(models.AbstractModel):
    _name = 'transfer.transfer'
    _description = 'Base Transfer Fields'

    taking = fields.Float(_('Taking'), widget="monetary")
    itinerary_id = fields.Many2one('transfer.itinerary', _('Itinerary'), domain=[('is_description', '=', False)])
    start_address = fields.Text(_('Departure Address'))
    finish_address = fields.Text(_('Destination Address'))

    connection = fields.Text(_('Flight / Train / Ship'))
    service_supplier_id = fields.Many2one('res.partner', _('Service Supplier'), domain="[('id', 'in', service_supplier_ids[0][2])]")
    service_supplier_ids = fields.Many2many('res.partner', compute='compute_supplier_ids', string=_('Service Suppliers'))
    driver_id = fields.Many2one('res.partner', _('Driver'), domain="[('id', 'in', driver_ids[0][2])]")
    driver_ids = fields.Many2many('res.partner', compute='compute_driver_ids', string=_('Drivers'))

    note = fields.Text(_('Note'))

    # show_details = fields.Boolean(_('Show details'))
    transfer_date = fields.Datetime(_('Travel date and time'))
    passenger_qty = fields.Integer(_('Pax'))
    bag_qty = fields.Integer(_('Bag'))
    passengers = fields.Text(_('Passengers'))

    passenger_name = fields.Char(_('Contact Name'))
    passenger_phone = fields.Char(_('Phone'))
    passenger_email = fields.Char(_('Email'))

    @api.one
    def compute_supplier_ids(self):
        # self.service_supplier_ids = [seller.name.id for seller in self.product_id.seller_ids]
        self.service_supplier_ids = []

    @api.one
    @api.depends('service_supplier_id')
    def compute_driver_ids(self):
        self.driver_ids = [driver.id for driver in self.service_supplier_id.child_ids]
        self.driver_id = False


class TransferItinerary(models.Model):
    _name = 'transfer.itinerary'
    _description = _('Transfer Itineraries')

    @api.one
    @api.depends('start_city_id', 'end_city_id')
    def compute_name(self):
        self.name = u'From: {start} to: {finish}'.format(start=self.start_city_id.name, finish=self.end_city_id.name)

    name = fields.Char(_('Name'), compute="compute_name", store=True)

    start_city_id = fields.Many2one('res.city', _('Departure city'), required=True)
    end_city_id = fields.Many2one('res.city', _('Arrival city'), required=True)
    distance = fields.Float(_("Distance (km)"))
    duration = fields.Integer(_('Transfer duration'), readonly=True)  # in minutes
    duration_time = fields.Char(_('Transfer duration (hh:mm)'), compute='_compute_duration')
    mirror = fields.Boolean(_('With Mirror Itinerary'), default=True)
    # price_ids = fields.One2many('transfer.price', 'itinerary_id', _('Mixed Prices for Service'))
    supplier_price_ids = fields.One2many('transfer.price', 'itinerary_id', _('Supplier Price for Service'), domain=[('partner_id.supplier', '=', True)])
    customer_price_ids = fields.One2many('transfer.price', 'itinerary_id', _('Customer Price for Service'), domain=[('partner_id.customer', '=', True)])
    is_description = fields.Boolean(_('Itinerary as Description'), default=False, readonly=True)

    _order = 'name'

    @api.one
    @api.constrains('start_city_id', 'end_city_id')
    def _check_itinerary_unique(self):
        if self.start_city_id and self.end_city_id:
            if self.start_city_id.id == self.end_city_id.id:
                raise exceptions.ValidationError(_("The beginning and the end of itinerary can't be the same"))

            itinerary_ids = self.search([('start_city_id', '=', self.start_city_id.id),
                                         ('end_city_id', '=', self.end_city_id.id),
                                         ('is_description', '=', self.is_description)])
            if len(itinerary_ids) > 1:
                raise exceptions.ValidationError(_("Itinerary {start} - {finish} is already exists").format(
                    start=self.start_city_id.name,
                    finish=self.end_city_id.name
                ))
        else:
            raise exceptions.ValidationError(_("You can't insert itinerary with just one end"))

    @api.one
    @api.depends('duration')
    def _compute_duration(self):
        self.duration_time = '{hours}:{minutes:>02}'.format(
            hours=self.duration / 60,
            minutes=self.duration - self.duration / 60 * 60
        )

    @api.one
    def get_distance(self):
        if self.start_city_id and self.end_city_id:
            origin = u'{city} {country}'.format(city=self.start_city_id.name, country=self.start_city_id.province_id.region.country_id.name or '')
            destination = u'{city} {country}'.format(city=self.end_city_id.name, country=self.end_city_id.province_id.region.country_id.name or '')

            if self.env.user.company_id.google_key:
                key = self.env.user.company_id.google_key
            else:
                key = ''

            maps = GoogleMapsDistance(key)
            distance = maps.distance(origin, destination)
            if distance.get('error'):
                _logger.warning(_('Google Maps Error: {error}'.format(error=distance['error'])))
            else:
                if distance.get('distance'):
                    distance_meters = distance['distance']['value']
                    self.distance = distance_meters and distance_meters / 1000.00 or 0.0
                    self.duration = distance['duration']['value'] / 60
                elif distance.get('status'):
                    raise exceptions.Warning(_('Distance: {status}').format(status=distance['status']))

    @api.model
    def create(self, values):
        if not values.get('start_city_id'):
            values['start_city_id'] = False
        if not values.get('end_city_id'):
            values['end_city_id'] = False

        return super(TransferItinerary, self).create(values)

    @api.multi
    def write(self, values):
        # Exclude city change or update of itinerary name
        # Permit change if city is False (impossible condition. because cities are required)

        if not self._context.get('mirror'):
            if values.get('start_city_id') and self.start_city_id and not self.start_city_id.id == values['start_city_id'] \
                    or values.get('end_city_id') and self.end_city_id and not self.end_city_id.id == values['end_city_id']:
                raise exceptions.Warning("Please don't change the city, create new itinerary instead")

            if self.mirror or values.get('mirror'):
                mirror = self.search([
                    ('start_city_id', '=', self.end_city_id.id),
                    ('end_city_id', '=', self.start_city_id.id),
                    ('is_description', '=', False)
                ])
                mirror_values = values.copy()
                mirror_values['start_city_id'] = self.end_city_id.id
                mirror_values['end_city_id'] = self.start_city_id.id
                if values.get('supplier_price_ids'):
                    values['supplier_price_ids'] = self.env['transfer.price'].mirror_price_values(
                        values['supplier_price_ids'], mirror)
                if values.get('customer_price_ids'):
                    values['customer_price_ids'] = self.env['transfer.price'].mirror_price_values(
                        values['customer_price_ids'], mirror)
                if mirror:
                    mirror.with_context(mirror=True).write(mirror_values)
                else:
                    mirror_values['distance'] = self.distance or values.get('distance') or 0
                    mirror_values['duration'] = self.duration or values.get('duration') or 0
                    mirror_values['mirror'] = True
                    self.create(mirror_values)

        return super(TransferItinerary, self).write(values)


class TransferPrice(models.Model):
    _name = 'transfer.price'

    itinerary_id = fields.Many2one('transfer.itinerary', _('Itinerary'))
    product_id = fields.Many2one('product.product', _('Service'), domain=[('type', '=', 'service')], required=True)
    price = fields.Float(_('Fixed Price'), widget='monetary', required=True)
    partner_id = fields.Many2one('res.partner', _('Partner'), required=True)
    start_date = fields.Date(_('Start Date'))
    end_date = fields.Date(_('End Date'))
    price_mirror_id = fields.Many2one('transfer.price')

    # @api.one
    # @api.constrains(
    #     'product_id',
    #     'itinerary_id',
    #     'partner_id'
    # )
    # def _check_product_itinerary_unique(self):
    #     service_price = self.search([
    #         ('product_id', '=', self.product_id.id),
    #         ('itinerary_id', '=', self.itinerary_id.id),
    #         ('partner_id', '=', self.partner_id.id)
    #     ])
    #
    #     # Check duplicate rows
    #     if len(service_price) > 1:
    #         raise exceptions.ValidationError(_('Price for "{0}" is already set').format(self.product_id.name))

    # TODO: show only suppliers of selected service


    # @api.model
    # def create(self, values):
    #     if values.get('product_id') and values.get('partner_id'):
    #         partner = self.env['res.partner'].browse(values['partner_id'])
    #         product = self.env['product.product'].browse(values['product_id'])
    #         if partner.supplier:
    #             product_suppliers = [info.name.id for info in product.seller_ids]
    #             if partner.id not in product_suppliers:
    #                 self.env['product.supplierinfo'].create({
    #                     'name': partner.id,
    #                     'product_tmpl_id': product.product_tmpl_id.id
    #                 })
    #
    #     return super(TransferPrice, self).create(values)
    #
    # @api.multi
    # def write(self, values):
    #     if values.get('product_id') and values.get('partner_id'):
    #         partner = self.env['res.partner'].browse(values['partner_id'])
    #         product = self.env['product.product'].browse(values['product_id'])
    #         if partner.supplier:
    #             product_suppliers = [info.name.id for info in product.seller_ids]
    #             if partner.id not in product_suppliers:
    #
    #                 self.env['product.supplierinfo'].create({
    #                     'name': partner.id,
    #                     'product_tmpl_id': product.product_tmpl_id.id
    #                 })
    #     return super(TransferPrice, self).write(values)

    @api.model
    def mirror_price_values(self, prices, mirror):
        """
        Create mirrored price lines for mirrored itinerary
        :param prices: prices list received from view:
            [0, False, {'price': 100, 'product_id': 1}] - create
            [1, 16, {'price': 80}] - update
            [2, 9, False] - delete
            [4, 4, False] - do nothing
        :param mirror: mirrored itinerary record
        """

        for row in prices:
            if not row[0]:
                # Create -> just copy
                price = self.create(row[2])
                row[0] = 4
                row[1] = price.id
                row[2] = False
            elif row[0] in (1, 2, 4):
                # 1: Update -> compose new or update
                # 2: Delete
                # 4: Do nothing
                price = self.browse(row[1])

            if price.price_mirror_id:
                if row[0] == 2:
                    price.price_mirror_id.unlink()
                elif row[0] == 1:
                    if row[2].get('itinerary_id'):
                        # this should never happen
                        _logger.error('For some reason itinerary_id is changed')
                        del row[2]['itinerary_id']
                    price.price_mirror_id.write(row[2])
            elif row[0] in (1, 4):
                mirror_price = self.create({
                    'price': price.price,
                    'product_id': price.product_id.id,
                    'partner_id': price.partner_id.id,
                    'itinerary_id': mirror.id,
                    'start_date': price.start_date,
                    'end_date': price.end_date,
                    'price_mirror_id': price.id
                })
                price.price_mirror_id = mirror_price.id
        return prices

    @api.model
    def get_price_and_quantity(self, product, partner, itinerary=False, price_date=False):
        """
        Create mirror lines for mirrored itinerary
        :param product: record
        :param partner: record
        :param itinerary: record
        :param price_date: date
        """

        price_date = price_date and price_date.strftime(DEFAULT_SERVER_DATE_FORMAT) or datetime.now().date().strftime(DEFAULT_SERVER_DATE_FORMAT)

        prices = self.search([
            ('product_id', '=', product.id),
            ('partner_id', '=', partner.id),
            ('itinerary_id', '=', itinerary and itinerary.id),
            ('start_date', '<=', price_date),
            ('end_date', '>=', price_date)
        ])

        if not prices:
            prices = self.search([
                ('product_id', '=', product.id),
                ('partner_id', '=', partner.id),
                ('itinerary_id', '=', itinerary and itinerary.id),
                ('start_date', '<=', price_date),
                ('end_date', '=', False)
            ])

        if not prices:
            prices = self.search([
                ('product_id', '=', product.id),
                ('partner_id', '=', partner.id),
                ('itinerary_id', '=', itinerary and itinerary.id),
                ('start_date', '=', False),
                ('end_date', '>=', price_date)
            ])

        if not prices:
            prices = self.search([
                ('product_id', '=', product.id),
                ('partner_id', '=', partner.id),
                ('itinerary_id', '=', itinerary and itinerary.id),
                ('start_date', '=', False),
                ('end_date', '=', False)
            ])

        if not prices and partner.parent_id:
            return self.get_price_and_quantity(product, partner.parent_id, itinerary, price_date)

        if prices:
            price_unit = prices[0].price
            product_uom_qty = 1.0
        else:
            price_unit = False
            product_uom_qty = itinerary and float(itinerary.distance) or 1.0
        return {'price_unit': price_unit, 'product_uom_qty': product_uom_qty}


class TransferTemplatePrice(models.Model):
    _name = 'transfer.template.price'

    template_id = fields.Many2one('transfer.template', _('Template'))
    # product_id = fields.Many2one('product.product', _('Service'), domain=[('type', '=', 'service')], required=True)
    price = fields.Float(_('Fixed Price'), widget='monetary', required=True)
    partner_id = fields.Many2one('res.partner', _('Partner'))
    start_date = fields.Date(_('Start Date'))
    end_date = fields.Date(_('End Date'))

    # @api.one
    # @api.constrains(
    #     'product_id',
    #     'itinerary_id',
    #     'partner_id'
    # )
    # def _check_product_itinerary_unique(self):
    #     service_price = self.search([
    #         ('product_id', '=', self.product_id.id),
    #         ('itinerary_id', '=', self.itinerary_id.id),
    #         ('partner_id', '=', self.partner_id.id)
    #     ])
    #
    #     # Check duplicate rows
    #     if len(service_price) > 1:
    #         raise exceptions.ValidationError(_('Price for "{0}" is already set').format(self.product_id.name))

    # TODO: show only suppliers of selected service

    @api.model
    def get_price(self, template, partner, price_date=False):
        """
        Create mirror lines for mirrored itinerary
        :param template: record
        :param partner: record
        :param price_date: string representing date
        """
        if not price_date:
            price_date = datetime.now().date().strftime(DEFAULT_SERVER_DATE_FORMAT)

        prices = self.search([
            ('template_id', '=', template.id),
            ('partner_id', '=', partner.id),
            ('start_date', '<=', price_date),
            ('end_date', '>=', price_date)
        ])

        if not prices:
            prices = self.search([
                ('template_id', '=', template.id),
                ('partner_id', '=', partner.id),
                ('start_date', '<=', price_date),
                ('end_date', '=', False)
            ])

        if not prices:
            prices = self.search([
                ('template_id', '=', template.id),
                ('partner_id', '=', partner.id),
                ('start_date', '=', False),
                ('end_date', '>=', price_date)
            ])

        if not prices:
            prices = self.search([
                ('template_id', '=', template.id),
                ('partner_id', '=', partner.id),
                ('start_date', '=', False),
                ('end_date', '=', False)
            ])

        if not prices and partner.parent_id:
            return self.get_price(template, partner.parent_id, price_date)

        return prices and prices[0].price or False


class TransferTemplate(models.Model):
    _name = 'transfer.template'

    name = fields.Char(_('Name'))
    descriptive_itinerary_id = fields.Many2one('transfer.itinerary', _('Descriptive Itinerary'), domain=[('is_description', '=', True)])
    template_line_ids = fields.One2many('transfer.template.line', 'template_id', string=_('Template Lines'))
    product_id = fields.Many2one('product.product', _('Product'), domain=[('type', '=', 'service')], ondelete='cascade')
    price = fields.Float(string=_('Price'), digits_compute=dp.get_precision('Product Price'), default=0.0, required=True)
    product_price = fields.Float(related='product_id.list_price', string=_('Price'), digits_compute=dp.get_precision('Product Price'))
    customer_price_ids = fields.One2many('transfer.template.price', 'template_id', _('Customer Price for Service'), domain=[('partner_id.customer', '=', True)])

    @api.model
    def create(self, values):
        uom_obj = self.env['product.uom']
        uoms = uom_obj.search([('name', '=', 'Transfer(s)')])
        if uoms:
            uom_id = uoms[0].id
        else:
            new_uom = uom_obj.name_create('Transfer(s)')
            uom_id = new_uom[0]
            uom = uom_obj.browse(uom_id)
            uom.rounding = 1.0

        category = self.env['product.category'].get_or_create('Transfer')

        product = self.env['product.product'].create({
            'name': values['name'],
            'type': 'service',
            'auto_create_task': True,
            'categ_id': category.id,
            'uom_id':  uom_id,
            'uom_po_id': uom_id,
            'list_price': values['price'],
            'active': True,
            'sale_ok': True
        })

        values['product_id'] = product.id
        del values['product_price']
        return super(TransferTemplate, self).create(values)

    @api.multi
    def create_quotation(self):
        assert len(self) == 1, 'This option should only be used for a single id at a time.'

        quotation_lines = map(lambda line: (0, 0, {
            'product_id': line.product_id.id,
            'itinerary_id': line.itinerary_id and line.itinerary_id.id or False,
            'template_line_id': line.id
        }), self.template_line_ids)
        quotation = self.env['wizard.create.quotation'].create({
            'template_id': self.id,
            'descriptive_itinerary_id': self.descriptive_itinerary_id and self.descriptive_itinerary_id.id,
            'quotation_line_ids': quotation_lines
        })
        return {
            'name': _('Create Quotation'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'wizard.create.quotation',
            'view_id': False,
            'target': 'new',
            'res_id': quotation.id
        }


class TransferTemplateLines(models.Model):
    _name = 'transfer.template.line'

    name = fields.Char(_('Name'), compute='_compute_name')
    product_id = fields.Many2one('product.product', _('Service'), required=True, domain=[('type', '=', 'service'), ('auto_create_task', '=', True)])
    itinerary_id = fields.Many2one('transfer.itinerary', _('Itinerary'), required=False)
    template_id = fields.Many2one('transfer.template', _('Template'))

    @api.one
    @api.depends('product_id', 'itinerary_id')
    def _compute_name(self):
        self.name = u'{name}{itinerary}'.format(
            name=self.product_id.name,
            itinerary=self.itinerary_id and ': ' + self.itinerary_id.name or ''
        )


class ResCity(models.Model):
    _inherit = 'res.city'

    @api.model
    def create(self, values):
        values['name'] = values.get('name').title() or ''
        return super(ResCity, self).create(values)

    @api.multi
    def write(self, values):
        if values.get('name'):
            values['name'] = values['name'].title()

        return super(ResCity, self).write(values)

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        operator = '=ilike'
        name += '%'
        return super(ResCity, self).name_search(name, args, operator, limit)
