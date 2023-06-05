# -*- coding: utf-8 -*-
# © 2015-2017 Didotech srl (http://www.didotech.com).
# © Andrei Levin <andrei.levin@didotech.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields, api, _


class ProductCategory(models.Model):
    _inherit = 'product.category'

    name = fields.Char(translate=False)
    spareparts = fields.Boolean(_('Spare parts classification'))

    @api.onchange(
        'parent_id'
    )
    def onchange_parent_id(self):
        if self.parent_id:
            self.spareparts = self.parent_id.spareparts

    @api.model
    def children_search(self, parent_ids, offset=0, limit=0, order=None, count=False):
        children = super(ProductCategory, self).search([('parent_id', 'in', parent_ids)])
        if children:
            return children + self.children_search(children.ids, offset=offset, limit=limit, order=order, count=count)
        else:
            return children

    def search(self, cr, uid, args, offset=0, limit=None, order=None, context=None, count=False, strict=False):
        new_args = []
        context = context or {}

        if args and not strict and not context.get('strict'):
            for arg in args:
                if isinstance(arg, (list, tuple)) and len(arg) == 3 and arg[0] == 'name' and arg[1] == 'ilike' and len(arg[2]) > 1:
                    categories = set()
                    for sub_arg in arg[2].split(' '):
                        if sub_arg and not sub_arg == '/':
                            sub_categories = super(ProductCategory, self).search(
                                cr, uid, [[arg[0], arg[1], sub_arg]], offset=offset, limit=None, order=order, count=count, context=context
                            )
                            if not isinstance(sub_categories, (tuple, list)):
                                sub_categories = [sub_categories]

                            children = self.children_search(cr, uid, sub_categories, offset=offset, limit=None, order=order, count=count, context=context)
                            if children:
                                family = set(sub_categories + children.ids)
                            else:
                                family = set(sub_categories)

                            if categories:
                                categories = categories.intersection(family)
                            else:
                                categories = family

                    if categories:
                        arg = ('id', 'in', list(categories))

                new_args.append(arg)
        else:
            new_args = args

        return super(ProductCategory, self).search(cr, uid, new_args, offset=offset, limit=limit, order=order, count=count, context=context)


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    # source = fields.Many2one(
    #     'product.category', _('Source'), domain="[('child_id', '=', False), ('spareparts', '=', True)]"
    # )

    # Disabled in UI:
    part_number_id = fields.Many2one('spare.part.number', _('Part number'))
    categ_id = fields.Many2one(domain="[('spareparts', '=', False)]")
    compatibility = fields.Many2many('product.category', string=_('Compatible Models'), select="1")
    oe_code = fields.Char('OE Code 4 ruote')

    # This is the right implementation of search function with new API. Unfortunately it doesn't work
    # @api.model
    # def search(self, args, offset=0, limit=0, order=None, count=False, context=None):
    #     for i, arg in enumerate(args):
    #         if len(arg) > 2 and (arg[1] == 'like' or arg[1] == 'ilike') and arg[0] == 'part_number':
    #             part_numbers = self.env['spare.part.number'].search([('name', 'ilike', arg[2])])
    #             if part_numbers:
    #                 args[i] = ['part_number_id', 'in', part_numbers.ids]
    #             else:
    #                 args[i] = ['part_number_id', 'in', []]
    #     return super(ProductTemplate, self).search(
    #         args, offset=offset, limit=limit, order=order, count=count, context=context)

    def search(self, cr, uid, args, offset=0, limit=0, order=None, count=False, context=None):
        for i, arg in enumerate(args):
            if len(arg) > 2 and (arg[1] == 'like' or arg[1] == 'ilike') and arg[0] == 'part_number':
                part_number_ids = self.pool['spare.part.number'].search(cr, uid, [('name', 'ilike', arg[2])])
                if part_number_ids:
                    args[i] = ['part_number_id', 'in', part_number_ids]
                else:
                    args[i] = ['part_number_id', 'in', []]
            elif len(arg) > 2 and (arg[1] == 'like' or arg[1] == 'ilike') and arg[0] == 'serial_number':
                lot_ids = self.pool['stock.production.lot'].search(cr, uid, [('name', 'ilike', arg[2])])
                lots = self.pool['stock.production.lot'].browse(cr, uid, lot_ids, context)
                template_product_ids = []
                for lot in lots:
                    for quant in lot.quant_ids:
                        if quant.location_id.usage == 'internal':
                            template_product_ids.append(lot.product_id.product_tmpl_id.id)
                            break

                if template_product_ids:
                    args[i] = ['id', 'in', template_product_ids]
                else:
                    args[i] = ['id', 'in', []]
            elif len(arg) > 2 and (arg[1] == 'like' or arg[1] == 'ilike') and arg[0] == 'note':
                arg_2 = arg[2].replace(' ', '')
                pattern = '%'
                for letter in arg_2:
                    pattern += ' ?' + letter
                pattern += '%'
                product_tmpl_ids = []

                cr.execute("SELECT id from stock_quant WHERE note SIMILAR TO '{}'".format(pattern))
                records = cr.fetchall()

                if records:
                    quant_ids = [record[0] for record in records]

                    for quant in self.pool['stock.quant'].browse(cr, uid, quant_ids):
                        if quant.location_id.usage == 'internal':
                            product_tmpl_ids.append(quant.lot_id.product_id.product_tmpl_id.id)
                if product_tmpl_ids:
                    args[i] = ['id', 'in', product_tmpl_ids]
                else:
                    args[i] = ['id', 'in', []]

        return super(ProductTemplate, self).search(
            cr, uid, args, offset=offset, limit=limit, order=order, count=count, context=context
        )


class ProductProduct(models.Model):
    _inherit = 'product.product'

    def search(self, cr, uid, args, offset=0, limit=0, order=None, count=False, context=None):
        context = context or {}

        for i, arg in enumerate(args):
            if len(arg) > 2 and arg[0] == 'categ_id' and arg[1] == 'child_of' and context.get('compatibility'):
                category_ids = self.pool['product.category'].search(cr, uid, [('name', 'ilike', arg[2])])
                if category_ids:
                    args[i] = ['compatibility', 'in', category_ids]
                    del context['search_default_categ_id']

            elif len(arg) > 2 and (arg[1] == 'like' or arg[1] == 'ilike') and arg[0] == 'part_number':
                part_number_ids = self.pool['spare.part.number'].search(cr, uid, [('name', 'ilike', arg[2])])
                if part_number_ids:
                    args[i] = ['part_number_id', 'in', part_number_ids]
                else:
                    args[i] = ['part_number_id', 'in', []]
            elif len(arg) > 2 and (arg[1] == 'like' or arg[1] == 'ilike') and arg[0] == 'serial_number':
                lot_ids = self.pool['stock.production.lot'].search(cr, uid, [('name', 'ilike', arg[2])])
                lots = self.pool['stock.production.lot'].browse(cr, uid, lot_ids, context)
                product_ids = []
                for lot in lots:
                    for quant in lot.quant_ids:
                        if quant.location_id.usage == 'internal':
                            product_ids.append(lot.product_id.id)
                            break

                if product_ids:
                    args[i] = ['id', 'in', product_ids]
                else:
                    args[i] = ['id', 'in', []]
            elif len(arg) > 2 and (arg[1] == 'like' or arg[1] == 'ilike') and arg[0] == 'note':
                arg_2 = arg[2].replace(' ', '')
                pattern = '%'
                for letter in arg_2:
                    pattern += ' ?' + letter
                pattern += '%'
                product_ids = []

                cr.execute("SELECT id from stock_quant WHERE note SIMILAR TO '{}'".format(pattern))
                records = cr.fetchall()

                if records:
                    quant_ids = [record[0] for record in records]
                    for quant in self.pool['stock.quant'].browse(cr, uid, quant_ids):
                        if quant.location_id.usage == 'internal':
                            product_ids.append(quant.lot_id.product_id.id)
                if product_ids:
                    args[i] = ['id', 'in', product_ids]
                else:
                    args[i] = ['id', 'in', []]

        return super(ProductProduct, self).search(
            cr, uid, args, offset=offset, limit=limit, order=order, count=count, context=context
        )
