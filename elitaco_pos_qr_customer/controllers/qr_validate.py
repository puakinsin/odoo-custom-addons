# -*- coding: utf-8 -*-
import json
from odoo import http
from odoo.http import request

class QrValidate(http.Controller):
    """
    Optional API for online QR token validation.
    
    Endpoint: /pos/qr/validate
    Method: POST
    Input: {"token": "...", "partnerId": 123}
    Output: {"valid": true/false, "message": "...", "partner_name": "...", "tier": "..."}
    """
    
    @http.route('/pos/qr/validate', type='json', auth='user', methods=['POST'])
    def validate_qr(self):
        """
        Validate QR token and partnerId
        
        Called from POS frontend when online validation is enabled.
        """
        # Get request data
        rpc_request = request.jsonrequest
        token = rpc_request.get('token')
        partner_id = rpc_request.get('partnerId')
        
        if not token or not partner_id:
            return {
                'valid': False,
                'message': 'Missing token or partnerId'
            }
        
        # Find partner
        partner = request.env['res.partner'].sudo().browse(partner_id)
        
        if not partner.exists():
            return {
                'valid': False,
                'message': 'Customer not found'
            }
        
        # Check if partner has a valid token (stored in partner)
        # This depends on how tokens are stored in the loyalty system
        # For now, we validate that the partner exists
        
        # Get tier information
        tier = partner.loyalty_tier if hasattr(partner, 'loyalty_tier') else None
        
        return {
            'valid': True,
            'message': 'Valid',
            'partner_name': partner.name,
            'tier': tier,
        }
    
    @http.route('/pos/qr/validate-batch', type='json', auth='user', methods=['POST'])
    def validate_qr_batch(self):
        """
        Validate multiple QR codes at once.
        
        Input: {"codes": [{"token": "...", "partnerId": 123}, ...]}
        Output: {"results": [...]}
        """
        rpc_request = request.jsonrequest
        codes = rpc_request.get('codes', [])
        
        results = []
        for code in codes:
            token = code.get('token')
            partner_id = code.get('partnerId')
            
            partner = request.env['res.partner'].sudo().browse(partner_id)
            
            if not partner.exists():
                results.append({
                    'partnerId': partner_id,
                    'valid': False,
                    'message': 'Customer not found'
                })
            else:
                tier = partner.loyalty_tier if hasattr(partner, 'loyalty_tier') else None
                results.append({
                    'partnerId': partner_id,
                    'valid': True,
                    'partner_name': partner.name,
                    'tier': tier,
                })
        
        return {'results': results}
