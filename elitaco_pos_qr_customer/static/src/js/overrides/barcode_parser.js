/**
 * Elitaco POS QR Customer Selection
 * 
 * This file overrides the POS barcode handler to intercept
 * QR codes containing customer information.
 */

odoo.define('elitaco_pos_qr_customer.BarcodeParser', function (require) {
    'use strict';

    var BarcodeParser = require('point_of_sale.BarcodeParser');
    var Mutex = require('web.Mutex');
    var rpc = require('web.rpc');
    
    var ElitacoBarcodeParser = BarcodeParser.extend({
        init: function (pos) {
            this._super(pos);
            this.pos = pos;
            this.mutex = new Mutex();
        },

        /**
         * Override parse_barcode to intercept QR codes
         */
        parse_barcode: function (barcode) {
            var self = this;
            
            // Try to parse as QR JSON first
            var qrResult = this._tryParseQRCode(barcode);
            
            if (qrResult.shouldHandle) {
                // Handle QR code asynchronously
                this.mutex.exec(function () {
                    return self._handleQRCustomer(barcode, qrResult.data);
                }).then(function (handled) {
                    if (handled) {
                        // QR was handled successfully, don't process as regular barcode
                        return { handled: true };
                    }
                }).catch(function (error) {
                    console.error('QR Code handling error:', error);
                });
                
                // Return early to indicate we're handling this
                // The actual result will be handled asynchronously
                return { handled: true, type: 'qr_customer' };
            }
            
            // Fallback to original handler
            return this._super(barcode);
        },

        /**
         * Try to parse barcode as QR JSON
         * @param {string} barcode - The scanned string
         * @returns {Object} - { shouldHandle: boolean, data: Object|null }
         */
        _tryParseQRCode: function (barcode) {
            var result = {
                shouldHandle: false,
                data: null
            };

            // Only attempt JSON parsing if it starts with '{'
            if (!barcode || typeof barcode !== 'string' || !barcode.trim().startsWith('{')) {
                return result;
            }

            try {
                var data = JSON.parse(barcode);
                
                // Check for required fields (partnerId is required)
                if (data && typeof data === 'object' && data.partnerId) {
                    result.shouldHandle = true;
                    result.data = data;
                }
            } catch (e) {
                // Not valid JSON, let original handler deal with it
                result.shouldHandle = false;
                result.data = null;
            }

            return result;
        },

        /**
         * Handle QR code customer selection
         * @param {string} rawBarcode - Raw barcode string
         * @param {Object} qrData - Parsed QR data
         * @returns {Promise<boolean>} - True if handled successfully
         */
        _handleQRCustomer: async function (rawBarcode, qrData) {
            var self = this;
            var pos = this.pos;
            var order = pos.get_order();
            
            if (!order) {
                this._showError('No active order');
                return false;
            }

            var partnerId = qrData.partnerId;
            var token = qrData.token;
            var expiresAt = qrData.expiresAt;
            var name = qrData.name;

            // 1. Check expiration
            if (expiresAt) {
                var expDate = new Date(expiresAt);
                if (expDate < new Date()) {
                    this._showError('QR Code Expired');
                    this._logScan(partnerId, name, token, expiresAt, 'expired');
                    return false;
                }
            }

            // 2. Get POS configuration
            var config = pos.config;
            var validationMode = config.qr_validation_mode || 'offline';
            var tokenRequired = config.qr_token_required || false;

            // 3. Online validation if enabled
            if ((validationMode === 'online' || validationMode === 'hybrid') && token) {
                try {
                    var validation = await rpc.query({
                        model: 'pos.config',
                        method: 'validate_qr_token',
                        args: [[config.id], token, partnerId],
                    });
                    
                    if (!validation.valid) {
                        this._showError(validation.message || 'Token Validation Failed');
                        this._logScan(partnerId, name, token, expiresAt, 'token_failed');
                        return false;
                    }
                } catch (error) {
                    console.error('Online validation error:', error);
                    if (validationMode === 'online') {
                        this._showError('Network Error - Cannot Validate');
                        return false;
                    }
                    // Hybrid mode: continue with offline validation
                }
            }

            // 4. Find partner in POS cache
            var partner = this._findPartnerInCache(partnerId);
            
            if (!partner) {
                this._showError('Customer Not Synced to POS\n\nPlease sync customers in POS settings or refresh.');
                this._logScan(partnerId, name, token, expiresAt, 'partner_not_found');
                return false;
            }

            // 5. Set customer on order
            order.set_customer(partner);
            
            // 6. Show success message
            this._showSuccess('Customer: ' + partner.name);
            
            // 7. Log successful scan
            this._logScan(partnerId, name, token, expiresAt, 'success');
            
            return true;
        },

        /**
         * Find partner in POS cached partners
         */
        _findPartnerInCache: function (partnerId) {
            var partners = this.pos.partners;
            return partners.find(function (p) {
                return p.id === partnerId;
            });
        },

        /**
         * Show error popup
         */
        _showError: function (message) {
            var pos = this.pos;
            if (pos && pos.gui && pos.gui.show_popup) {
                pos.gui.show_popup('error', {
                    title: 'QR Customer',
                    body: message,
                });
            } else if (pos && pos.gui && pos.gui.show_screen) {
                // Fallback for older Odoo versions
                pos.gui.show_popup('alert', {
                    title: 'QR Customer',
                    text: message,
                });
            }
        },

        /**
         * Show success notification
         */
        _showSuccess: function (message) {
            var pos = this.pos;
            if (pos && pos.gui && pos.gui.show_popup) {
                // Show a brief success message
                pos.gui.show_popup('confirm', {
                    title: 'QR Customer',
                    body: message,
                });
            }
        },

        /**
         * Log scan to backend
         */
        _logScan: function (partnerId, partnerName, token, expiresAt, status) {
            var pos = this.pos;
            var sessionId = pos && pos.session ? pos.session.id : null;
            
            rpc.query({
                model: 'elitaco.qr.scan.log',
                method: 'log_scan',
                args: [[], partnerId, partnerName, token, expiresAt, status, null, sessionId, JSON.stringify({partnerId: partnerId})],
            }).catch(function (error) {
                console.error('Failed to log QR scan:', error);
            });
        },
    });

    return ElitacoBarcodeParser;
});
