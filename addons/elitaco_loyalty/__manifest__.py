# -*- coding: utf-8 -*-
{
    'name': 'Elitaco Loyalty Points',
    'version': '1.0.0',
    'category': 'Social',
    'summary': 'Member loyalty points and tier system',
    'description': '''
        Member loyalty points system with tier management.
        
        Features:
        - Points accumulation
        - Tier levels (Steel, Bronze, Stainless, Titanium, Diamond)
        - Auto tier upgrade based on points threshold
        - Points transaction history
    ''',
    'author': 'Elitaco',
    'website': 'https://elitaco.my',
    'depends': ['base', 'contacts'],
    'data': [
        'views/res_partner_views.xml',
        'views/loyalty_points_views.xml',
        'security/ir.model.access.csv',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',
}
