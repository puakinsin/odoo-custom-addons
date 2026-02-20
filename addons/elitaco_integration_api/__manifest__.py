# -*- coding: utf-8 -*-
{
    'name': 'Elitaco Integration API',
    'version': '1.0.0',
    'category': 'Integration',
    'summary': 'REST API for external integrations',
    'description': '''
        External API for integration with WooCommerce and PWA Portal.
        
        Endpoints:
        - Partner info (GET /api/partner/<email>)
        - Create order (POST /api/order)
        - Update points (POST /api/points)
        - Voucher operations (POST/GET /api/voucher)
    ''',
    'author': 'Elitaco',
    'website': 'https://elitaco.my',
    'depends': ['base', 'sale', 'elitaco_loyalty'],
    'data': [
        'security/ir.model.access.csv',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',
}
