{
    'name': 'eCommerce - Show Cart/Qty on Product List',
    'category': 'Website',
    'summary': 'Allow Qty selection for add to cart from List view',
    'website': 'https://www.deneroteam.com',
    'version': '1.0',
    'description': """
Allows adding the quantity selection to the cart directly from the List view'

        """,
    'author': 'Deneroteam & Matmoz',
    'depends': ['website_sale'],
    'data': [
        'views/templates.xml',
    ],
    'demo': [
    ],
    'qweb': ['static/src/xml/*.xml'],
    'installable': True,
    'application': True,
}
