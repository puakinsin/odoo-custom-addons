# -*- coding: utf-8 -*-
{
    'name': 'Elitaco POS QR Customer',
    'version': '1.0.0',
    'category': 'Point of Sale',
    'summary': 'Scan QR codes to select customers in POS',
    'description': """
        POS QR Customer Selection Module
        =================================
        Allows scanning member QR codes in POS to automatically
        select the corresponding customer.
        
        Features:
        - Parse QR codes containing partner information
        - Validate expiration and optionally token
        - Auto-select customer in current order
        - Fallback to original barcode handling
    """,
    'author': 'Elitaco',
    'website': 'https://elitaco.my',
    'depends': ['point_of_sale'],
    'data': [
        'security/ir.model.access.csv',
        'views/pos_config_views.xml',
    ],
    'assets': {
        'point_of_sale._assets_pos': [
            'elitaco_pos_qr_customer/static/src/js/overrides/*.js',
            'elitaco_pos_qr_customer/static/src/xml/*.xml',
        ],
    },
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}
