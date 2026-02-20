/**
 * Elitaco POS Customer QR - Odoo 18
 * 
 * Short code format: PMCUST:{partnerId}:{expiresAt}:{token}
 * - partnerId: int
 * - expiresAt: UTC "YYYYMMDDTHHMMSSZ"
 * - token: UUID without dashes, 32 hex chars
 * 
 * Also supports legacy JSON format for backward compatibility.
 * 
 * This module registers a high-priority barcode handler that intercepts
 * QR codes starting with "PMCUST:" or "{".
 */

import { patch } from "@web/core/utils/patch";
import { _t } from "@web/core/l10n/translation";
import { BarcodeParser } from "@point_of_sale/app/utils/barcode_parser";

patch(BarcodeParser.prototype, {
    setup() {
        super.setup();
    },

    /**
     * Override barcode parsing to intercept QR customer codes
     * @param {string} barcode - Raw barcode/scanned text
     * @returns {Object} Parsed barcode result
     */
    parse_barcode(barcode) {
        if (!barcode || typeof barcode !== 'string') {
            return super.parse_barcode(barcode);
        }

        const trimmed = barcode.trim();

        // Try to parse as our short code format: PMCUST:...
        if (trimmed.startsWith('PMCUST:')) {
            const result = this._parseShortCode(trimmed);
            if (result) {
                return result;
            }
            // If parse fails, fall through to try JSON, then original handler
        }

        // Try to parse as legacy JSON format: {"partnerId": ...}
        if (trimmed.startsWith('{')) {
            const result = this._parseJsonCode(trimmed);
            if (result) {
                return result;
            }
        }

        // Fallback to original handler for regular barcodes
        return super.parse_barcode(barcode);
    },

    /**
     * Parse short code format: PMCUST:{partnerId}:{expiresAt}:{token}
     * @param {string} code - The scanned code
     * @returns {Object|null} Parsed result or null if invalid
     */
    _parseShortCode(code) {
        try {
            const parts = code.split(':');
            
            // Format: PMCUST:{partnerId}:{expiresAt}:{token}
            if (parts.length !== 4) {
                console.warn('[Elitaco QR] Invalid short code format, expected 4 parts');
                return null;
            }

            const [prefix, partnerIdStr, expiresAt, token] = parts;

            if (prefix !== 'PMCUST') {
                return null;
            }

            const partnerId = parseInt(partnerIdStr, 10);
            if (isNaN(partnerId)) {
                console.warn('[Elitaco QR] Invalid partnerId in short code');
                return null;
            }

            // Validate token format (32 hex chars)
            if (!/^[a-fA-F0-9]{32}$/.test(token)) {
                console.warn('[Elitaco QR] Invalid token format (expected 32 hex chars)');
                return null;
            }

            return {
                type: 'qr_customer',
                format: 'short',
                partnerId: partnerId,
                expiresAt: expiresAt,
                token: token,
                raw: code,
                isValid: true,
            };
        } catch (e) {
            console.error('[Elitaco QR] Error parsing short code:', e);
            return null;
        }
    },

    /**
     * Parse legacy JSON format: {"partnerId": ..., "expiresAt": ..., "token": ...}
     * @param {string} code - The scanned code
     * @returns {Object|null} Parsed result or null if invalid
     */
    _parseJsonCode(code) {
        try {
            const data = JSON.parse(code);
            
            // Check for required field
            if (!data.partnerId) {
                return null;
            }

            const partnerId = parseInt(data.partnerId, 10);
            if (isNaN(partnerId)) {
                return null;
            }

            return {
                type: 'qr_customer',
                format: 'json',
                partnerId: partnerId,
                expiresAt: data.expiresAt || null,
                token: data.token || null,
                name: data.name || null,
                raw: code,
                isValid: true,
            };
        } catch (e) {
            // Not valid JSON, return null to fall through
            return null;
        }
    },
});

// Import for POS Order management
import { Orderline } from "@point_of_sale/app/models/order_line";

patch(Orderline.prototype, {
    setup() {
        super.setup();
    },
});

// Export for use in POS
export {};
