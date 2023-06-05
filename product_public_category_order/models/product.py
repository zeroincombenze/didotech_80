# -*- encoding: utf-8 -*-
# =============================================================================
# For copyright and license notices, see __openerp__.py file in root directory
# =============================================================================

from openerp import models, fields, api, _
from openerp import exceptions


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    product_attribute_sequence_ids = fields.One2many('product.attribute.sequence', 'product_id', string=_('Product Attribute Sequence'))
    # auto_product_attribute_sequence_ids = fields.One2many('product.attribute.sequence', 'product_id',
    #                                                       string=_('Product Attribute Sequence'),
    #                                                       compute='get_create_product_attribute_sequence')
    auto_product_attribute_sequence_ids = fields.One2many('product.attribute.sequence',
                                                          string=_('Product Attribute Sequence'),
                                                          compute='get_create_product_attribute_sequence')

    @api.one
    def get_create_product_attribute_sequence(self):
        if self.public_categ_ids:
            # create missing attributes
            public_categ_ids = [sequence.public_category_id for sequence in self.product_attribute_sequence_ids]
            missing_attributes = set(self.public_categ_ids).difference(public_categ_ids)
            for attribute in missing_attributes:
                # print 'Missing', attribute.id, attribute.name
                self.env['product.attribute.sequence'].create({
                    'product_id': self.id,
                    'public_category_id': attribute.id
                })

            dead_attributes = set(public_categ_ids).difference(self.public_categ_ids)
            for sequence in self.product_attribute_sequence_ids:
                if sequence.public_category_id in dead_attributes:
                    sequence.unlink()

            if missing_attributes or dead_attributes:
                attribute_sequence_ids = self.env['product.attribute.sequence'].search([('product_id', '=', self.id)])
                if attribute_sequence_ids:
                    self.auto_product_attribute_sequence_ids = attribute_sequence_ids.ids
                else:
                    self.auto_product_attribute_sequence_ids = []
            else:
                self.auto_product_attribute_sequence_ids = self.product_attribute_sequence_ids.ids
        else:
            self.auto_product_attribute_sequence_ids = []

    @api.multi
    def write(self, values):
        if values.get('public_categ_ids'):
            self.get_create_product_attribute_sequence()
        return super(ProductTemplate, self).write(values)

    # TODO: write create() function to autopopulate product_attribute_sequence_ids field

    @api.multi
    def ordered_public_categ_ids(self):
        rest_public_category = self.env['rest.ful'].with_context({
            'model': 'product.public.category'
        })

        categories = [rest_public_category.serialize(record, ['name', 'name_tree']) for record in self.public_categ_ids]
        for category in categories:
            category_sequence = self.env['product.attribute.sequence'].search([
                ('product_id', '=', self.id),
                ('public_category_id', '=', category['pk'])
            ])
            if category_sequence:
                category['sequence'] = category_sequence.sequence
            else:
                category['sequence'] = 0

        return sorted(categories, key=lambda c: c['sequence'])


class ProductAttributeSequence(models.Model):
    _name = 'product.attribute.sequence'

    name = fields.Char(related='public_category_id.name')
    product_id = fields.Many2one('product.template', string=_('Product'))
    public_category_id = fields.Many2one('product.public.category', string=_('Public Category'))
    sequence = fields.Integer(_('Sequence'))

    @api.one
    @api.constrains('product_id', 'public_category_id')
    def _check_sequence_exists(self):
        if len(self.search([('product_id', '=', self.product_id.id), ('public_category_id', '=', self.public_category_id.id)])) > 1:
            raise exceptions.ValidationError("Sequence already exists")

    _order = 'sequence'
