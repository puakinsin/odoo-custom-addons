# -*- coding: utf-8 -*-
from odoo import models, fields, api
from datetime import datetime


class QRScanLog(models.Model):
    _name = 'elitaco.qr.scan.log'
    _description = 'QR Code Scan Log'
    _order = 'create_date desc'

    partner_id = fields.Many2one(
        'res.partner',
        string='Customer',
        ondelete='set null'
    )
    partner_name = fields.Char(string='Customer Name')
    partner_external_id = fields.Integer(string='Partner External ID')
    token = fields.Char(string='Token')
    expires_at = fields.Datetime(string='Expires At')
    status = fields.Selection([
        ('success', 'Success'),
        ('expired', 'Expired'),
        ('token_failed', 'Token Validation Failed'),
        ('partner_not_found', 'Customer Not Found'),
        ('parse_error', 'Parse Error'),
        ('api_error', 'API Error'),
    ], string='Status')
    message = fields.Text(string='Message')
    pos_session_id = fields.Many2one(
        'pos.session',
        string='POS Session',
        ondelete='set null'
    )
    pos_config_id = fields.Many2one(
        'pos.config',
        string='POS Config',
        ondelete='set null'
    )
    raw_qr = fields.Text(string='Raw QR Data')

    @api.model
    def log_scan(self, partner_id, partner_name, token, expires_at, status, message=None, session_id=None, config_id=None, raw_qr=None):
        """Log a QR code scan event"""
        partner_external_id = partner_id
        partner = False
        
        if partner_id:
            try:
                partner = self.env['res.partner'].browse(partner_id)
                if partner.exists():
                    partner_external_id = partner.id
                    partner_name = partner.name
            except:
                pass

        expires_dt = False
        if expires_at:
            try:
                if isinstance(expires_at, str):
                    expires_dt = fields.Datetime.from_string(expires_at)
                else:
                    expires_dt = expires_at
            except:
                pass

        session = False
        config = False
        if session_id:
            try:
                session = self.env['pos.session'].browse(session_id)
                if session.exists():
                    config = session.config_id
            except:
                pass
        elif config_id:
            try:
                config = self.env['pos.config'].browse(config_id)
            except:
                pass

        vals = {
            'partner_id': partner.id if partner else False,
            'partner_name': partner_name,
            'partner_external_id': partner_external_id,
            'token': token,
            'expires_at': expires_dt,
            'status': status,
            'message': message,
            'pos_session_id': session.id if session else False,
            'pos_config_id': config.id if config else False,
            'raw_qr': raw_qr,
        }
        
        return self.create(vals).id

    def validate_token(self, token, partner_id, config_id):
        """
        Override this method to implement custom token validation.
        Default implementation returns True (always valid).
        """
        # Default: always valid in offline mode
        # Override in custom modules for custom validation
        return {'valid': True, 'message': 'OK'}
