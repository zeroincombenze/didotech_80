# -*- encoding: utf-8 -*-
# =============================================================================
# For copyright and license notices, see __openerp__.py file in root directory
# =============================================================================

from openerp import models, fields, api
from openerp.tools.translate import _


class StockQuant(models.Model):
    _inherit = 'stock.quant'

    @api.one
    def _get_variant(self):
        self.product_variant = ", ".join([v.name for v in self.product_id.attribute_value_ids])

    product_code = fields.Char(related='product_id.default_code', string='Code')
    product_name = fields.Char(related='product_id.name', string='Name')
    product_variant = fields.Char(compute=_get_variant, string='Variant')
    origin = fields.Many2one('project.project', _('Telaio'))
    source = fields.Many2one('product.category', _('Versione (Marca/Modello)'))
    note = fields.Text(_('Note'))
    compatibility = fields.Many2many(compute=lambda *a, **k: {}, method=True, string="Compatibility")

    # def search(self, cr, uid, args, offset=0, limit=0, order=None, count=False, context=None):
    #     context = context or {}
    #
    #     for index, arg in enumerate(args):
    #         if len(arg) > 2 and arg[0] == 'compatibility':
    #             # TODO: find categories
    #
    #             # TODO: find all products
    #
    #             # TODO: args[index] = ['product_id', 'in', product_ids]
    #             # TODO: Try to create Quant by compatibility with group_by product_id,
    #             # TODO: because normal search will be very CPU intensive
    #             pass
    #
    #     return super(StockQuant, self).search(
    #         cr, uid, args, offset=offset, limit=limit, order=order, count=count, context=context
    #     )

    def search(self, cr, uid, args, offset=0, limit=0, order=None, count=False, context=None):
        context = context or {}

        if 'categ_id' in context:
            categories = self.pool['product.category'].children_search(cr, uid, [context['categ_id']])
            category_ids = categories.ids
            category_ids.append(context['categ_id'])
            project_ids = self.pool['project.project'].search(cr, uid, [('car_type_id', 'in', category_ids)])
            args += [
                '|',
                ('product_id.compatibility', 'in', category_ids),
                ('origin', 'in', project_ids),
                ('location_id.usage', '=', 'internal')
            ]

        result = super(StockQuant, self).search(
            cr, uid, args, offset=offset, limit=limit, order=order, count=count, context=context
        )

        if isinstance(result, (list, tuple)):
            return list(set(result))
        else:
            return result


class StockProductionLot(models.Model):
    _inherit = 'stock.production.lot'

    name_old = fields.Char(_('Matricola Old'))
