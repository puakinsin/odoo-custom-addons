# Odoo POS QR Customer Selection - Architecture Specification

## Overview
This module extends Odoo 18 POS to recognize QR codes containing member information and automatically select the corresponding customer.

## QR Code Format (Existing)
```json
{"token":"5ab5d21b-e8ee-4fc9-9608-235ed6377a10","partnerId":52,"name":"Kin Sin","tier":"steel","expiresAt":"2026-05-21T03:19:34.947Z"}
```

## Architecture

### 1. Scanning Interception
- **Entry Point**: `point_of_sale/models/pos_session.py` - loads POS assets
- **Frontend Handler**: POS barcode scanner service in `pos_fronted/src/screen/...`
- **Hook Method**: Override `BarcodeParser` or use Odoo's `BarcodeWidget` events

### 2. Processing Flow
```
Scanner Input → BarcodeHandler → Parse as JSON? 
  → YES: Validate structure (partnerId, token?, expiresAt?)
    → YES: Check expiresAt
      → Valid: Find partner in POS cache
        → Found: Set customer on order
        → Not found: Show "customer not synced" popup
      → Expired: Show "QR expired" popup
    → NO (missing fields): Fallback to original handler
  → NO: Fallback to original barcode handler (product barcode, loyalty card, etc.)
```

### 3. Components

#### Backend (Python)
- `models/pos_config.py` - Configuration settings (enable/disable, validation mode)
- `models/res_partner.py` - Add POS display fields
- `controllers/qr_validate.py` - Optional online token validation API

#### Frontend (JS/OWL)
- `static/src/overrides/models/pos_order.js` - Extend order to handle customer
- `static/src/overrides/components/barcode_parser.js` - Intercept barcode
- `static/src/overrides/popups/qr_error_popup.js` - Error notifications
- `static/src/xml/pos_qr.xml` - UI templates

### 4. Security Strategy
- **Offline Mode**: Validate `expiresAt` locally only
- **Online Mode**: Call `/pos/qr/validate` endpoint (configurable)
- **Fallback**: Any parsing failure returns to original Odoo handler
- **Audit Log**: Log all QR scans (partnerId, timestamp, status)

### 5. Compatibility
- Does NOT modify core POS files
- Uses Odoo module extension mechanism
- Compatible with existing barcode types:
  - Product barcodes (EAN13, UPC)
  - Loyalty cards
  - Gift vouchers
  - Weight scales

### 6. Configuration
- `qr_customer_enabled`: Enable/disable feature
- `qr_validation_mode`: 'offline' | 'online' | 'hybrid'
- `qr_token_required`: Require token validation (default: false)

### 7. Error Handling
| Scenario | Action |
|----------|--------|
| Invalid JSON | Fallback to original handler |
| Missing partnerId | Fallback to original handler |
| Expired QR | Show "QR Code Expired" popup |
| Partner not in POS cache | Show "Customer Not Synced" popup |
| Network error (online mode) | Fall back to offline validation |
| Token mismatch | Show "Invalid Token" popup |
