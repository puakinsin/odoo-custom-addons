# -*- coding: utf-8 -*-
import json
from odoo import http
from odoo.http import request, JsonRequest
import logging

_logger = logging.getLogger(__name__)


class ElitacoIntegrationAPI(http.Controller):
    
    # ========== Partner API ==========
    
    @http.route('/api/partner/<email>', type='json', auth='public', methods=['GET'], csrf=False)
    def get_partner_by_email(self, email):
        """Get partner information by email"""
        partner = request.env['res.partner'].sudo().search([('email', '=', email)], limit=1)
        if not partner:
            return {'error': 'Partner not found'}, 404
        
        return {
            'id': partner.id,
            'name': partner.name,
            'email': partner.email,
            'phone': partner.phone,
            'points': partner.points,
            'tier': partner.tier,
            'tier_expiry': partner.tier_expiry,
            'tier_upgrade_reward': partner.tier_upgrade_reward,
            'birth_date': partner.birth_date,
        }
    
    @http.route('/api/partner/<int:partner_id>', type='json', auth='public', methods=['GET'], csrf=False)
    def get_partner_by_id(self, partner_id):
        """Get partner information by ID"""
        partner = request.env['res.partner'].sudo().browse(partner_id)
        if not partner.exists():
            return {'error': 'Partner not found'}, 404
        
        return {
            'id': partner.id,
            'name': partner.name,
            'email': partner.email,
            'phone': partner.phone,
            'points': partner.points,
            'tier': partner.tier,
            'tier_expiry': partner.tier_expiry,
            'tier_upgrade_reward': partner.tier_upgrade_reward,
            'birth_date': partner.birth_date,
        }
    
    # ========== Points API ==========
    
    @http.route('/api/points/add', type='json', auth='public', methods=['POST'], csrf=False)
    def add_points(self):
        """Add points to partner account"""
        data = request.jsonrequest
        
        partner_id = data.get('partner_id')
        points = data.get('points')
        reason = data.get('reason', 'Points addition')
        
        if not partner_id or not points:
            return {'error': 'Missing required fields'}, 400
        
        try:
            partner = request.env['res.partner'].sudo().browse(partner_id)
            if not partner.exists():
                return {'error': 'Partner not found'}, 404
            
            partner.action_add_points(points, reason)
            
            return {
                'success': True,
                'new_points': partner.points,
            }
        except Exception as e:
            _logger.error(f'Error adding points: {e}')
            return {'error': str(e)}, 500
    
    @http.route('/api/points/deduct', type='json', auth='public', methods=['POST'], csrf=False)
    def deduct_points(self):
        """Deduct points from partner account"""
        data = request.jsonrequest
        
        partner_id = data.get('partner_id')
        points = data.get('points')
        reason = data.get('reason', 'Points deduction')
        
        if not partner_id or not points:
            return {'error': 'Missing required fields'}, 400
        
        try:
            partner = request.env['res.partner'].sudo().browse(partner_id)
            if not partner.exists():
                return {'error': 'Partner not found'}, 404
            
            partner.action_deduct_points(points, reason)
            
            return {
                'success': True,
                'new_points': partner.points,
            }
        except Exception as e:
            _logger.error(f'Error deducting points: {e}')
            return {'error': str(e)}, 500
    
    # ========== Order API ==========
    
    @http.route('/api/order/create', type='json', auth='public', methods=['POST'], csrf=False)
    def create_order(self):
        """Create sale order from WooCommerce"""
        data = request.jsonrequest
        
        partner_email = data.get('partner_email')
        partner_id = data.get('partner_id')
        lines = data.get('lines', [])
        woo_order_id = data.get('woo_order_id')
        
        # Find partner
        if partner_id:
            partner = request.env['res.partner'].sudo().browse(partner_id)
        elif partner_email:
            partner = request.env['res.partner'].sudo().search([('email', '=', partner_email)], limit=1)
        else:
            return {'error': 'No partner specified'}, 400
        
        if not partner.exists():
            return {'error': 'Partner not found'}, 404
        
        # Create order
        order_vals = {
            'partner_id': partner.id,
            'partner_invoice_id': partner.id,
            'partner_shipping_id': partner.id,
            'origin': f'WOO:{woo_order_id}' if woo_order_id else False,
        }
        
        order = request.env['sale.order'].sudo().create(order_vals)
        
        # Add order lines
        for line in lines:
            product = request.env['product.product'].sudo().browse(line.get('product_id'))
            if not product.exists():
                continue
            
            request.env['sale.order.line'].sudo().create({
                'order_id': order.id,
                'product_id': product.id,
                'name': product.name,
                'product_uom_qty': line.get('qty', 1),
                'price_unit': line.get('price', 0),
            })
        
        # Confirm order if needed
        if data.get('auto_confirm', False):
            order.action_confirm()
        
        return {
            'success': True,
            'order_id': order.id,
            'order_name': order.name,
        }
    
    # ========== Voucher API ==========
    
    @http.route('/api/voucher/create', type='json', auth='public', methods=['POST'], csrf=False)
    def create_voucher(self):
        """Create a new voucher"""
        data = request.jsonrequest
        
        partner_id = data.get('partner_id')
        product_id = data.get('product_id')
        points_spent = data.get('points_spent', 0)
        
        if not partner_id:
            return {'error': 'Missing partner_id'}, 400
        
        # Generate voucher code
        import random
        import string
        code = 'V-' + ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
        
        voucher = request.env['loyalty.voucher'].sudo().create({
            'code': code,
            'partner_id': partner_id,
            'product_id': product_id,
            'points_spent': points_spent,
            'status': 'new',
        })
        
        # Deduct points
        if points_spent > 0:
            partner = request.env['res.partner'].sudo().browse(partner_id)
            partner.action_deduct_points(points_spent, f'Voucher: {code}')
        
        return {
            'success': True,
            'voucher_code': code,
            'voucher_id': voucher.id,
        }
    
    @http.route('/api/voucher/<code>', type='json', auth='public', methods=['GET'], csrf=False)
    def get_voucher(self, code):
        """Get voucher by code"""
        voucher = request.env['loyalty.voucher'].sudo().search([('code', '=', code)], limit=1)
        if not voucher.exists():
            return {'error': 'Voucher not found'}, 404
        
        return {
            'id': voucher.id,
            'code': voucher.code,
            'partner_id': voucher.partner_id.id,
            'points_spent': voucher.points_spent,
            'status': voucher.status,
            'expiry_date': voucher.expiry_date,
        }
    
    @http.route('/api/voucher/redeem', type='json', auth='public', methods=['POST'], csrf=False)
    def redeem_voucher(self):
        """Redeem a voucher"""
        data = request.jsonrequest
        
        code = data.get('code')
        if not code:
            return {'error': 'Missing voucher code'}, 400
        
        voucher = request.env['loyalty.voucher'].sudo().search([('code', '=', code)], limit=1)
        if not voucher.exists():
            return {'error': 'Voucher not found'}, 404
        
        if voucher.status != 'new':
            return {'error': 'Voucher already redeemed or expired'}, 400
        
        voucher.status = 'redeemed'
        voucher.redeemed_at = fields.Datetime.now()
        
        return {
            'success': True,
            'voucher_id': voucher.id,
        }
    
    # ========== Health Check ==========
    
    @http.route('/api/health', type='json', auth='public', methods=['GET'], csrf=False)
    def health_check(self):
        """Health check endpoint"""
        return {
            'status': 'ok',
            'service': 'elitaco_integration_api',
        }
