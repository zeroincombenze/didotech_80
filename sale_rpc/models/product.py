# -*- encoding: utf-8 -*-
# =============================================================================
# For copyright and license notices, see __openerp__.py file in root directory
# =============================================================================

from openerp import models, fields, api, _
from datetime import datetime
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT


class Product(models.Model):
    _inherit = 'product.product'

    ext_product_id = fields.Integer(_('External product'), default=None)

    @api.model
    def external_get_or_create(self, values):
        product = self.search([('ext_product_id', '=', values['ext_product_id'])])
        if product:
            return product[0]
        else:
            default_values = {
                'cost_method': 'standard',
                'sale_ok': True,
                'type': 'consu'
            }

            new_values = self.default_get(['uom_id', 'uom_po_id'])
            new_values.update(default_values)
            new_values.update({
                'name': values['name'],
                'lst_price': values.get('price_unit', 0),
                'ext_product_id': values['ext_product_id']
            })
            return self.create(new_values)

class ProductPricelist(models.Model):
    _inherit = 'product.pricelist'

    black_partner_ids = fields.Many2many('res.partner', string=_("Promo Users"),
                                         help=_("Users that already used their promo codes"))
    otc = fields.Boolean('One Time Code', help=_("Promo code can be used only once"))

    @api.model
    def get_pricelist(self, code=None, partner_id=None):
        if partner_id:
            partner = self.env['res.partner'].browse(partner_id)
        else:
            partner = False

        if code and partner:
            pricelists = self.sudo().search([('code', '=', code)])
            if pricelists:
                date = datetime.now().date().strftime(DEFAULT_SERVER_DATE_FORMAT)
                version = False
                pricelist = pricelists[0]

                if partner_id in pricelist.black_partner_ids.ids and pricelist.otc:
                    return {'info': _('Code already used'), 'pricelist': partner.property_product_pricelist}

                for v in pricelist.version_id:
                    if ((v.date_start is False) or (v.date_start <= date)) and (
                                (v.date_end is False) or (v.date_end >= date)):
                        version = v
                        break

                if version:
                    return {'pricelist': pricelist}
                else:
                    return {'info': _('Code is not valid'), 'pricelist': partner.property_product_pricelist}
            else:
                return {'info': _('Unknown code'), 'pricelist': partner.property_product_pricelist}
        elif partner:
            return {'pricelist': partner.property_product_pricelist}
        else:
            return {}

    @api.multi
    def update_blacklist(self, partner_id):
        if self.otc:
            self.black_partner_ids = self.black_partner_ids.ids + [partner_id]
