# -*- coding: utf-8 -*-
from odoo import models, fields


class PosConfig(models.Model):
    _inherit = 'pos.config'

    qr_customer_enabled = fields.Boolean(
        string='Enable QR Customer Selection',
        default=False,
        help='Enable scanning QR codes to select customers in POS'
    )

    qr_validation_mode = fields.Selection(
        selection=[
            ('offline', 'Offline (Local Only)'),
            ('online', 'Online (API Validation)'),
        ],
        string='QR Validation Mode',
        default='offline',
        help='How to validate QR codes: offline (local only) or online (API)'
    )

    qr_token_required = fields.Boolean(
        string='Require Token Validation',
        default=False,
        help='Require token validation when using online mode'
    )

    qr_validation_url = fields.Char(
        string='Validation API URL',
        help='URL for online token validation API',
        default='/elitaco_pos_customer_qr/validate_token'
    )
