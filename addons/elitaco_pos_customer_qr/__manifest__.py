# -*- coding: utf-8 -*-
{
    'name': 'Elitaco POS Customer QR',
    'version': '1.0.0',
    'category': 'Point of Sale',
    'summary': 'POS 扫会员码自动选客 - 短码格式',
    'description': """
POS Customer QR Selection Module
================================
支持短码格式: PMCUST:{partnerId}:{expiresAt}:{token}

功能:
- 扫描会员二维码自动选择客户
- 支持短码格式 PMCUST:{partnerId}:{expiresAt}:{token}
- 向后兼容旧版 JSON 二维码
- 可选在线 token 验证
- 完整的扫码日志

二维码格式 (方案2短码):
- PMCUST:{partnerId}:{expiresAt}:{token}
- partnerId: 客户ID (整数)
- expiresAt: UTC时间 "YYYYMMDDTHHMMSSZ"
- token: UUID去横线, 32位十六进制

兼容旧格式 (JSON):
- {"partnerId": 123, "expiresAt": "20251231T235959Z", "token": "xxx"}
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
            'elitaco_pos_customer_qr/static/src/js/overrides/*.js',
            'elitaco_pos_customer_qr/static/src/xml/*.xml',
        ],
    },
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}
