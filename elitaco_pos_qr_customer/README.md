# Elitaco POS QR Customer Selection

Odoo 18 模块 - 通过扫描二维码自动选择 POS 客户

## 功能

- **二维码客户识别**: 扫描会员二维码自动选中客户
- **过期验证**: 检查二维码过期时间
- **可选 Token 验证**: 支持在线/离线模式
- **错误提示**: 清晰的错误信息（过期/未同步/无效）
- **完整兼容**: 不影响现有条码流程（商品/会员卡/优惠券）

## QR 码格式

```json
{
  "token": "5ab5d21b-e8ee-4fc9-9608-235ed6377a10",
  "partnerId": 52,
  "name": "Kin Sin",
  "tier": "steel",
  "expiresAt": "2026-05-21T03:19:34.947Z"
}
```

## 安装

1. 将 `elitaco_pos_qr_customer` 目录复制到 Odoo addons 目录
2. 更新应用列表
3. 安装 "Elitaco POS QR Customer" 模块

## 配置

1. 进入 **POS > Configuration > Point of Sales**
2. 编辑 POS 配置
3. 启用 "Enable QR Customer Selection"
4. 选择验证模式:
   - **Offline Only**: 仅本地验证过期时间
   - **Online (API)**: 调用后端 API 验证 token
   - **Hybrid**: 优先在线验证，失败则离线

## 验证模式

### Offline Mode (离线)
- 验证 `expiresAt` 字段
- 在 POS 缓存中查找 partnerId
- 无需网络连接

### Online Mode (在线)
- 调用 `/pos/qr/validate` API
- 验证 token 与 partnerId 匹配
- 记录审计日志

### Hybrid Mode (混合)
- 优先尝试在线验证
- 网络错误时降级到离线验证

## 错误处理

| 场景 | 处理 |
|------|------|
| 非 JSON 格式 | 保持原有条码处理 |
| 缺少 partnerId | 保持原有条码处理 |
| QR 已过期 | 提示"二维码已过期" |
| 客户未同步到 POS | 提示"客户未同步到POS" |
| Token 验证失败 | 提示"Token 验证失败" |
| 网络错误(在线模式) | 提示"网络错误" |

## 调试

### 浏览器调试
1. 打开 POS 界面
2. 按 F12 打开开发者工具
3. Console 中查看日志

### 模拟扫码输入
在浏览器 Console 中:
```javascript
// 模拟扫码枪输入
var barcode = '{"token":"test","partnerId":52,"name":"Test","expiresAt":"2027-01-01T00:00:00.000Z"}';

// 触发 barcode parser
var parser = this.pos.barcode_parser;
parser.parse_barcode(barcode);
```

### 查看扫描日志
```bash
# 查看 QR 扫描日志
odoo shell -d odoo -c "
from elitaco_pos_qr_customer.models.qr_scan_log import QRScanLog
logs = env['elitaco.qr.scan.log'].search([], limit=20)
for log in logs:
    print(log.scan_time, log.partner_name, log.status)
"
```

## 文件结构

```
elitaco_pos_qr_customer/
├── __init__.py
├── __manifest__.py
├── SPEC.md
├── README.md
├── controllers/
│   ├── __init__.py
│   └── qr_validate.py        # 在线验证 API
├── models/
│   ├── __init__.py
│   ├── pos_config.py         # POS 配置
│   └── qr_scan_log.py       # 扫描日志
├── security/
│   └── ir.model.access.csv
├── static/
│   └── src/
│       ├── js/
│       │   └── overrides/
│       │       └── barcode_parser.js  # 扫码拦截
│       └── xml/
│           └── pos_qr.xml
└── views/
    └── pos_config_views.xml
```

## API 端点

### POST /pos/qr/validate

验证 QR token

**请求:**
```json
{
  "token": "...",
  "partnerId": 123
}
```

**响应:**
```json
{
  "valid": true,
  "message": "Valid",
  "partner_name": "John Doe",
  "tier": "gold"
}
```

## 已知限制

- POS 启动时必须已加载客户列表（partner cache）
- Token 验证需要网络连接
- 仅支持 JSON 格式 QR 码

## 更新日志

### v1.0.0 (2026-02-20)
- 初始版本
- 支持离线/在线/混合验证模式
- 扫描日志记录
- 错误提示

## License

LGPL-3
