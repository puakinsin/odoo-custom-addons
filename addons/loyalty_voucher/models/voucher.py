# -*- coding: utf-8 -*-
from odoo import models, fields, api


class LoyaltyVoucher(models.Model):
    _name = 'loyalty.voucher'
    _description = 'Loyalty Voucher'
    _order = 'create_date desc'
    
    code = fields.Char('Code', required=True, index=True)
    partner_id = fields.Many2one('res.partner', string='Partner')
    product_id = fields.Many2one('product.product', string='Reward Product')
    points_spent = fields.Integer('Points Spent')
    status = fields.Selection([
        ('new', 'New'),
        ('redeemed', 'Redeemed'),
        ('expired', 'Expired'),
    ], string='Status', default='new')
    redeemed_at = fields.Datetime('Redeemed At')
    expiry_date = fields.Date('Expiry Date')
    create_date = fields.Datetime('Created At', default=fields.Datetime.now)
