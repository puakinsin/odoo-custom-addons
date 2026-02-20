# -*- coding: utf-8 -*-
from odoo import models, fields

class PosConfig(models.Model):
    _inherit = 'pos.config'
    
    qr_customer_enabled = fields.Boolean(
        string='Enable QR Customer Selection',
        default=True,
        help='When enabled, QR codes containing customer info will be parsed'
    )
    
    qr_validation_mode = fields.Selection(
        string='QR Validation Mode',
        selection=[
            ('offline', 'Offline Only'),
            ('online', 'Online (API)'),
            ('hybrid', 'Hybrid (prefer online, fallback offline)')
        ],
        default='offline',
        help='How to validate QR codes'
    )
    
    qr_token_required = fields.Boolean(
        string='Require Token Validation',
        default=False,
        help='When enabled, token must be validated online'
    )
