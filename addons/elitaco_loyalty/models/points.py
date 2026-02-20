# -*- coding: utf-8 -*-
from odoo import models, fields, api


class LoyaltyPointsTransaction(models.Model):
    _name = 'loyalty.points.transaction'
    _description = 'Loyalty Points Transaction'
    _order = 'create_date desc'
    
    partner_id = fields.Many2one('res.partner', string='Partner', required=True, ondelete='cascade')
    points = fields.Integer('Points', required=True)
    transaction_type = fields.Selection([
        ('add', 'Added'),
        ('deduct', 'Deducted'),
        ('expired', 'Expired'),
        ('upgrade_reward', 'Tier Upgrade Reward'),
        ('voucher_redeem', 'Voucher Redeemed'),
        ('order_reward', 'Order Reward'),
    ], string='Type', required=True)
    reason = fields.Char('Reason')
    order_id = fields.Many2one('sale.order', string='Related Order')
    voucher_id = fields.Many2one('loyalty.voucher', string='Related Voucher')
    create_date = fields.Datetime('Date', default=fields.Datetime.now)
