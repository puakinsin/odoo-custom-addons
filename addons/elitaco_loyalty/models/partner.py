# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.addons.base.models.res_partner import PARTICIPANT_STATES


class ResPartner(models.Model):
    _inherit = 'res.partner'
    
    # Points fields
    points = fields.Integer('Points', default=0, tracking=True)
    tier = fields.Selection([
        ('steel', 'Steel'),
        ('bronze', 'Bronze'),
        ('stainless', 'Stainless'),
        ('titanium', 'Titanium'),
        ('diamond', 'Diamond'),
    ], string='Tier', default='steel', tracking=True)
    tier_expiry = fields.Date('Tier Expiry Date', tracking=True)
    tier_upgrade_reward = fields.Integer('Upgrade Reward Points', default=0)
    birth_date = fields.Date('Birth Date', tracking=True)
    custom_age = fields.Integer('Age', compute='_compute_age', store=True)
    
    # Points transaction history
    points_transaction_ids = fields.One2many(
        'loyalty.points.transaction',
        'partner_id',
        string='Points Transactions'
    )
    
    @api.depends('birth_date')
    def _compute_age(self):
        for partner in self:
            if partner.birth_date:
                today = fields.Date.today()
                partner.custom_age = (today - partner.birth_date).days // 365
            else:
                partner.custom_age = 0
    
    def action_add_points(self, points, reason=''):
        """Add points to partner account"""
        self.ensure_one()
        
        # Create transaction record
        self.env['loyalty.points.transaction'].create({
            'partner_id': self.id,
            'points': points,
            'transaction_type': 'add',
            'reason': reason,
        })
        
        # Update points
        self.points += points
        
        # Check for tier upgrade
        self._check_tier_upgrade()
        
        return True
    
    def action_deduct_points(self, points, reason=''):
        """Deduct points from partner account"""
        self.ensure_one()
        
        if self.points < points:
            raise models.ValidationError('Insufficient points')
        
        # Create transaction record
        self.env['loyalty.points.transaction'].create({
            'partner_id': self.id,
            'points': -points,
            'transaction_type': 'deduct',
            'reason': reason,
        })
        
        # Update points
        self.points -= points
        
        return True
    
    def _check_tier_upgrade(self):
        """Check and upgrade tier based on points"""
        tier_thresholds = {
            'bronze': 500,
            'stainless': 5000,
            'titanium': 10000,
            'diamond': 20000,
        }
        
        tier_rewards = {
            'bronze': 50,
            'stainless': 100,
            'titanium': 200,
            'diamond': 500,
        }
        
        tier_days = {
            'bronze': 30,
            'stainless': 45,
            'titanium': 60,
            'diamond': 75,
        }
        
        current_tier_index = ['steel', 'bronze', 'stainless', 'titanium', 'diamond'].index(self.tier)
        
        for tier in ['diamond', 'titanium', 'stainless', 'bronze']:
            tier_index = ['steel', 'bronze', 'stainless', 'titanium', 'diamond'].index(tier)
            if tier_index > current_tier_index:
                if self.points >= tier_thresholds[tier]:
                    # Upgrade tier
                    self.tier = tier
                    self.tier_upgrade_reward = tier_rewards[tier]
                    self.points += tier_rewards[tier]
                    
                    # Set expiry
                    from datetime import timedelta
                    self.tier_expiry = fields.Date.today() + timedelta(days=tier_days[tier])
                    
                    # Create upgrade transaction
                    self.env['loyalty.points.transaction'].create({
                        'partner_id': self.id,
                        'points': tier_rewards[tier],
                        'transaction_type': 'upgrade_reward',
                        'reason': f'Tier upgrade to {tier}',
                    })
                    break
        
        return True
