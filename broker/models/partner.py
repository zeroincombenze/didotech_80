# -*- encoding: utf-8 -*-
# =============================================================================
# For copyright and license notices, see __openerp__.py file in root directory
# =============================================================================

from openerp import models, fields, api
from openerp.tools.translate import _
import json
from openerp.exceptions import Warning

# from pprint import pprint


class ResPartner(models.Model):
    _inherit = 'res.partner'

    delivery_address = fields.Boolean(_('Delivery address'), default=False)
    delivery_addresses = fields.One2many('res.partner', compute='compute_delivery_addresses')
    product_variant_ids = fields.One2many('product.supplierinfo', 'name', _('Products'))
    supplier_ids = fields.One2many('customer.supplier.info', 'customer_id', _('Supplier Info'))
    customer_ids = fields.One2many('customer.supplier.info', 'supplier_id', _('Customer Info'))
    require_customer_ref = fields.Boolean(_('Require Customer Reference'))
    require_supplier_ref = fields.Boolean(_('Require Supplier Reference'), compute='_compute_require_supplier_ref')
    auth_number = fields.Char(_('Auth Number'), help=_("Authorization number"))
    dvce_required = fields.Boolean(_('Require DVCE'))
    transmission = fields.Text(_("Transmission Parameters"), help=_("Transmission parameters in JSON format"))

    @api.one
    def _compute_require_supplier_ref(self):
        self.require_supplier_ref = self.env['delivery.carrier'].search([('partner_id', '=', self.id)]) and True or False

    @api.one
    @api.onchange('delivery_address')
    def onchange_delivery_address(self):
        if self.delivery_address:
            self.type = 'delivery'

    @api.one
    @api.onchange('type')
    def onchange_contact_type(self):
        if self.type == 'delivery':
            self.delivery_address = True
        else:
            self.delivery_address = False

    @api.one
    def compute_delivery_addresses(self):
        if not self.parent_id:
            if self.child_ids:
                self.delivery_addresses = self.search([('id', 'in', self.child_ids.ids), ('type', '=', 'delivery')]).ids or [self.id]
            else:
                self.delivery_addresses = [self.id]

    @api.multi
    def get_customer_ref(self, customer_id):
        return self.env['customer.supplier.info'].search([('supplier_id', '=', self.id), ('customer_id', '=', customer_id)])

    @api.multi
    def verify_reference(self):
        for partner in self:
            config = json.loads(partner.transmission)
            if config and config.get('communication'):
                mod = __import__('openerp.addons.broker.wizard.partners.{partner}'.format(
                    partner=config['communication']
                ), fromlist=['Communication'])
                communication = getattr(mod, 'Communication')(config)
                # pprint(communication.get_record('customers'))
                # pprint(communication.get_record('products'))

                for customer in self.customer_ids:
                    # customer_ref = self.get_customer_ref(customer.id)
                    # if customer_ref and not communication.get_record('customers', customer_ref):
                    if customer.customer_ref and not communication.get_record('customers/code', customer.customer_ref):
                        raise Warning(u"Customer reference {} for '{}' is not present in suppliers database".format(
                            customer.customer_ref,
                            customer.customer_id.name)
                        )


class CustomerSupplierInfo(models.Model):
    _name = 'customer.supplier.info'

    supplier_id = fields.Many2one('res.partner', string=_('Suppliers'), domain=[('supplier', '=', True)], required=True)
    customer_id = fields.Many2one(
        'res.partner',
        string=_('Customers'),
        domain=['|', ('customer', '=', True), ('parent_id.customer', '=', True)],
        required=True
    )
    payment_term_id = fields.Many2one('account.payment.term', _('Payment Term'))
    customer_ref = fields.Char(_('Customer reference'))
    invoice_ref = fields.Char(_('Invoice reference'))
    delivery_ref = fields.Char(_('Delivery reference'))
    credit_limit = fields.Float(_('Credit Limit'))

    _sql_constraints = [
        ('customer_supplier_unique_together', 'unique(supplier_id, customer_id)', 'Customer should be unique!')
    ]
