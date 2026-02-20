# -*- coding: utf-8 -*-
from odoo import models, fields, api
from datetime import datetime

class QRScanLog(models.Model):
    _name = 'elitaco.qr.scan.log'
    _description = 'QR Code Scan Log'
    _order = 'scan_time DESC'
    
    scan_time = fields.Datetime(
        string='Scan Time',
        default=fields.Datetime.now,
        required=True
    )
    
    partner_id = fields.Many2one(
        'res.partner',
        string='Customer',
        help='Partner ID from QR code'
    )
    
    partner_name = fields.Char(
        string='Customer Name',
        help='Name from QR code'
    )
    
    token = fields.Char(
        string='Token',
        help='Token from QR code'
    )
    
    expires_at = fields.Datetime(
        string='Expires At',
        help='Expiration from QR code'
    )
    
    status = fields.Selection(
        string='Status',
        selection=[
            ('success', 'Success'),
            ('expired', 'Expired'),
            ('partner_not_found', 'Partner Not Found'),
            ('invalid_json', 'Invalid JSON'),
            ('invalid_format', 'Invalid Format'),
            ('token_failed', 'Token Validation Failed'),
            ('error', 'Error')
        ],
        required=True
    )
    
    error_message = fields.Text(
        string='Error Message'
    )
    
    pos_session_id = fields.Many2one(
        'pos.session',
        string='POS Session'
    )
    
    user_id = fields.Many2one(
        'res.users',
        string='Scanned By',
        default=lambda self: self.env.user
    )
    
    raw_qr_content = fields.Text(
        string='Raw QR Content'
    )
    
    @api.model
    def log_scan(self, partner_id, partner_name, token, expires_at, status, 
                  error_message=None, pos_session_id=None, raw_qr_content=None):
        """Log a QR code scan event"""
        return self.create({
            'partner_id': partner_id,
            'partner_name': partner_name,
            'token': token,
            'expires_at': expires_at,
            'status': status,
            'error_message': error_message,
            'pos_session_id': pos_session_id,
            'raw_qr_content': raw_qr_content,
        })
