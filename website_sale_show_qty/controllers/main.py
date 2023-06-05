# -*- coding: utf-8 -*-
import werkzeug
#
from openerp import SUPERUSER_ID
from openerp import http
from openerp.http import request
from openerp.tools.translate import _
import openerp.addons.website_sale.controllers.main as main
from openerp.addons.website.models.website import slug


class website_sale(main.website_sale):
    def get_products(self):
        cr, uid, context, pool = request.cr, request.uid, request.context, request.registry
        products = {}
        sale_order = request.website.sale_get_order(context=context)
        if sale_order:
            for line in sale_order.order_line:
                if line.product_id:
                    #if not products.has_key(line.product_id.id):
                    if not 'line.product_id.id' in products:
                        products[line.product_id.id] = {
                            'id': line.product_id.id,
                            'line_id': line.id,
                            'qty': line.product_uom_qty or 0,
                        }
                    else:
                        products[line.product_id.id]['qty'] += line.product_uom_qty
        return products

    @http.route([
        '/shop',
        '/shop/page/<int:page>',
        '/shop/category/<model("product.public.category"):category>',
        '/shop/category/<model("product.public.category"):category>/page/<int:page>'
    ], type='http', auth="public", website=True)
    def shop(self, page=0, category=None, search='', **post):
        cr, uid, context, pool = request.cr, request.uid, request.context, request.registry

        domain = request.website.sale_product_domain()
        if search:
            domain += [
                '|', '|', '|', ('name', 'ilike', search), ('description', 'ilike', search),
                ('description_sale', 'ilike', search), ('product_variant_ids.default_code', 'ilike', search)
            ]
        if category:
            domain += [('product_variant_ids.public_categ_ids', 'child_of', int(category))]

        attrib_list = request.httprequest.args.getlist('attrib')
        attrib_values = [map(int, v.split("-")) for v in attrib_list if v]
        attrib_set = set([v[1] for v in attrib_values])

        if attrib_values:
            attrib = None
            ids = []
            for value in attrib_values:
                if not attrib:
                    attrib = value[0]
                    ids.append(value[1])
                elif value[0] == attrib:
                    ids.append(value[1])
                else:
                    domain += [('attribute_line_ids.value_ids', 'in', ids)]
                    attrib = value[0]
                    ids = [value[1]]
            if attrib:
                domain += [('attribute_line_ids.value_ids', 'in', ids)]

        keep = main.QueryURL('/shop', category=category and int(category), search=search, attrib=attrib_list)

        if not context.get('pricelist'):
            pricelist = self.get_pricelist()
            context['pricelist'] = int(pricelist)
        else:
            pricelist = pool.get('product.pricelist').browse(cr, uid, context['pricelist'], context)

        product_obj = pool.get('product.template')

        url = "/shop"
        product_count = product_obj.search_count(cr, uid, domain, context=context)
        if search:
            post["search"] = search
        if category:
            url = "/shop/category/%s" % slug(category)
        pager = request.website.pager(url=url, total=product_count, page=page, step=main.PPG, scope=7, url_args=post)
        product_ids = product_obj.search(
            cr, uid, domain, limit=main.PPG+10, offset=pager['offset'],
            order='website_published desc, website_sequence desc', context=context
        )
        products = product_obj.browse(cr, uid, product_ids, context=context)

        style_obj = pool['product.style']
        style_ids = style_obj.search(cr, uid, [], context=context)
        styles = style_obj.browse(cr, uid, style_ids, context=context)

        category_obj = pool['product.public.category']
        category_ids = category_obj.search(cr, uid, [], context=context)
        categories = category_obj.browse(cr, uid, category_ids, context=context)
        categs = filter(lambda x: not x.parent_id, categories)

        attributes_obj = request.registry['product.attribute']
        attributes_ids = attributes_obj.search(cr, uid, [], context=context)
        attributes = attributes_obj.browse(cr, uid, attributes_ids, context=context)

        from_currency = pool.get('product.price.type')._get_field_currency(cr, uid, 'list_price', context)
        to_currency = pricelist.currency_id
        compute_currency = lambda price: pool['res.currency']._compute(
            cr, uid, from_currency, to_currency, price, context=context
        )

        order_products = self.get_products()

        values = {
            'search': search,
            'category': category,
            'attrib_values': attrib_values,
            'attrib_set': attrib_set,
            'pager': pager,
            'pricelist': pricelist,
            'products': products,
            'bins': main.table_compute().process(products),
            'rows': main.PPR,
            'styles': styles,
            'categories': categs,
            'attributes': attributes,
            'compute_currency': compute_currency,
            'keep': keep,
            'style_in_product': lambda style, product: style.id in [s.id for s in product.website_style_ids],
            'attrib_encode': lambda attribs: werkzeug.url_encode([('attrib', i) for i in attribs]),
            'order_products': order_products,
        }
        return request.website.render("website_sale.products", values)

    @http.route(['/shop/product/<model("product.template"):product>'], type='http', auth="public", website=True)
    def product(self, product, category='', search='', **kwargs):
        cr, uid, context, pool = request.cr, request.uid, request.context, request.registry
        category_obj = pool['product.public.category']
        template_obj = pool['product.template']

        context.update(active_id=product.id)

        if category:
            category = category_obj.browse(cr, uid, int(category), context=context)

        attrib_list = request.httprequest.args.getlist('attrib')
        attrib_values = [map(int, v.split("-")) for v in attrib_list if v]
        attrib_set = set([v[1] for v in attrib_values])

        keep = main.QueryURL('/shop', category=category and category.id, search=search, attrib=attrib_list)

        category_ids = category_obj.search(cr, uid, [], context=context)
        category_list = category_obj.name_get(cr, uid, category_ids, context=context)
        category_list = sorted(category_list, key=lambda category: category[1])

        pricelist = self.get_pricelist()
        from_currency = pool.get('product.price.type')._get_field_currency(cr, uid, 'list_price', context)
        to_currency = pricelist.currency_id
        compute_currency = lambda price: pool['res.currency']._compute(
            cr, uid, from_currency, to_currency, price, context=context
        )
        order_products = self.get_products()
        product_id = int(product)
        if not context.get('pricelist'):
            context['pricelist'] = int(self.get_pricelist())
            product = template_obj.browse(cr, uid, int(product), context=context)
        order_products = self.get_products()
        values = {
            'search': search,
            'category': category,
            'pricelist': pricelist,
            'attrib_values': attrib_values,
            'compute_currency': compute_currency,
            'attrib_set': attrib_set,
            'keep': keep,
            'category_list': category_list,
            'main_object': product,
            'product': product,
            'line_id': False,
            'qty': 1,
            'get_attribute_value_ids': self.get_attribute_value_ids,
            'order_products': order_products,
        }
        #if order_products.has_key(product_id):
        if 'product_id' in order_products:
            values.update({
                'line_id': order_products[product_id].get('line_id', False),
                'qty': order_products[product_id].get('qty', 1),
            })
        return request.website.render("website_sale.product", values)
## vim:expandtab:tabstop=4:softtabstop=4:shiftwidth=4:
