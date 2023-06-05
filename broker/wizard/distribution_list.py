# -*- encoding: utf-8 -*-
# =============================================================================
# For copyright and license notices, see __openerp__.py file in root directory
# =============================================================================

from openerp import models, fields, api, _
from openerp.exceptions import Warning
from StringIO import StringIO
import json
import sys

from .partners.main import DistributionList
from .partners.bierreti import Bierreti
from .partners.agromey import Agromey
from .partners.excel import Excel, ExcelPurchaseOrder
from .partners.koffeman import Koffeman


class WizardDistributionList(models.TransientModel):
    _name = 'wizard.distribution.list'
    _description = "Create distribution list"

    name = fields.Char()
    data = fields.Binary('File', readonly=True)
    state = fields.Selection((
        ('export', 'export'),
        ('end', 'end')
    ), 'state', required=True, translate=False, readonly=True, default='export')
    truck_info_id = fields.Many2one('broker.truck.info', 'Truck info', required=False,
                                    domain="[('id', 'in', order_truck_info_ids[0][2])]")
    truck_info_ids = fields.Many2many('broker.truck.info', string='Truck info', domain="[('id', 'in', order_truck_info_ids[0][2])]")
    order_truck_info_ids = fields.Many2many('broker.truck.info')
    ignore_truck_info = fields.Boolean('Ignore Truck Info', default=False)
    file_format = fields.Selection(
        '_get_formats', _('File format'), required=True, default='Excel'
    )
    info = fields.Text(_('Info'), readonly=True)
    dvce_required = fields.Boolean('Require DVCE')
    dvce = fields.Char('DVCE')
    show_prices = fields.Boolean()
    dry_run = fields.Boolean(default=False)

    def _get_formats(self):
        formats = [
            ('Excel', 'Excel'),
            ('Koffeman', 'Koffeman')
        ]

        if self._context.get('show_prices', False):
            formats.append(('Agromey', 'Agromey XML'))
            formats.append(('ExcelPurchaseOrder', 'Export Purchase Order'))
        else:
            formats.append(('Bierreti', 'Bierreti XML'))

        return formats

    @api.model
    def default_get(self, fields):
        purchase_order = self.env['broker.purchase.order'].browse(self._context['active_id'])
        values = super(WizardDistributionList, self).default_get(fields)
        # Create list of truck for this Broker Order
        values['order_truck_info_ids'] = purchase_order.get_trucks_info()
        values['show_prices'] = self._context.get('show_prices', False)
        values['ignore_truck_info'] = self._context.get('show_prices', False)
        values['dvce_required'] = purchase_order.supplier_id.dvce_required
        if self._context.get('show_prices'):
            transmission = purchase_order.supplier_id.transmission and json.loads(purchase_order.supplier_id.transmission) or {}
            if transmission.get('default_transmission'):
                values['file_format'] = transmission['default_transmission']
        else:
            transmission = purchase_order.carrier_id and purchase_order.carrier_id.partner_id.transmission and json.loads(purchase_order.carrier_id.partner_id.transmission) or {}
            if transmission.get('default_transmission'):
                values['file_format'] = transmission['default_transmission']

        return values

    def sale_order_has_trucks(self, sale_order):
        return self.env['sale.order.line'].search([('order_id', '=', sale_order.id), ('truck_info_id', '=', self.truck_info_id.id)])

    @api.multi
    def action_start_export(self):
        broker_order = self.env['broker.purchase.order'].browse(self._context['active_id'])

        if not self.ignore_truck_info:
            delivery_info = self.env['broker.delivery.info'].search([
                ('purchase_order_id', '=', self._context['active_id']),
                ('truck_id', '=', self.truck_info_id.id)
            ])
            if delivery_info and not self.dvce == delivery_info.name:
                delivery_info.name = self.dvce
            elif not delivery_info:
                self.env['broker.delivery.info'].create({
                    'purchase_order_id': self._context['active_id'],
                    'truck_id': self.truck_info_id.id,
                    'name': self.dvce
                })

        file_data = StringIO()

        if self._context.get('show_prices'):
            if self.file_format in ('Agromey', ):
                self.name = '{}.{}'.format(broker_order.name, 'xml')
            elif self.file_format in ('Koffeman', ):
                self.name = '{}.{}'.format(broker_order.name, 'txt')
            else:
                self.name = 'Purchase_order_{}.{}'.format(broker_order.name, 'xls')
        else:
            if self.file_format == 'Bierreti':
                self.name = 'Distribution_list_{}.{}'.format(broker_order.name, 'xml')
            else:
                self.name = 'Distribution_list_{}.{}'.format(broker_order.name, 'xls')

        # Take the class according to selected format
        template = getattr(sys.modules[__name__], self.file_format)

        if self.ignore_truck_info:
            truck_info = self.truck_info_ids
        else:
            truck_info = self.truck_info_id

        document = template(
            self._context.get('show_prices'),
            truck_info,
            self.env['res.users'].browse(self._uid).company_id.currency_id.symbol,
            self.ignore_truck_info,
            self.dvce
        )
        document.supplier_header(broker_order)
        document.main(broker_order.order_ids)
        document.save(file_data)
        out = file_data.getvalue()

        wizard_values = {
            'state': 'end'
        }

        if self.dry_run or document.download_only or \
                not broker_order.supplier_id.transmission and self._context.get('show_prices') or \
                not self._context.get('show_prices') and document.delivery_carrier and not document.delivery_carrier.transmission:
            wizard_values['data'] = out.encode("base64")
        elif broker_order.supplier_id.transmission and self._context.get('show_prices'):
            if broker_order.transmitted_to_supplier:
                raise Warning("Order already transmitted")
            else:
                broker_order.transmitted_to_supplier = document.transmit(out)
                if broker_order.transmitted_to_supplier:
                    broker_order.state = 'sent'
                    broker_order.message_post(u'Purchase Order transmitted to Supplier')
        elif not self._context.get('show_prices') and document.delivery_carrier and document.delivery_carrier.transmission:
            broker_order.transmitted_to_carrier = document.transmit(out)
            if broker_order.transmitted_to_carrier:
                broker_order.message_post(u'Distribution list transmitted to Carrier')

        info = document.info
        wizard_values['info'] = info and u'\n'.join(info) or 'Document ready for download'

        self.write(wizard_values)

        view_rec = self.env['ir.model.data'].get_object_reference('broker', 'distribution_list_export_form')
        if view_rec:
            view_id = view_rec and view_rec[1] or False

        return {
            'view_type': 'form',
            'name': "Export Distribution List",
            'view_id': [view_id],
            'res_id': self.id,
            'view_mode': 'form',
            'res_model': 'wizard.distribution.list',
            'type': 'ir.actions.act_window',
            'target': 'new'
        }

    @api.onchange('truck_info_id')
    def onchange_truck_info(self):
        delivery_info = self.env['broker.delivery.info'].search([
            ('purchase_order_id', '=', self._context['active_id']),
            ('truck_id', '=', self.truck_info_id.id)
        ])
        if delivery_info:
            self.dvce = delivery_info.name
        else:
            self.dvce = ''
