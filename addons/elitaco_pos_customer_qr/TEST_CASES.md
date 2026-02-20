# Elitaco POS Customer QR - 测试用例

## 测试环境准备

1. 安装模块
2. 在 POS 配置中启用 "Enable QR Customer Selection"
3. 确保有测试客户数据已同步到 POS

## 测试用例

### TC001: 正常短码选客

**目标**: 验证短码格式可以正常选客

**前置条件**:
- 模块已安装并启用
- 客户 ID=123 已同步到 POS

**输入**:
```
PMCUST:123:20251231T235959Z:550e8400e29b41d4a716446655440000
```

**预期结果**:
- [ ] 条码解析成功 (type = 'qr_customer', format = 'short')
- [ ] partnerId = 123
- [ ] expiresAt = '20251231T235959Z'
- [ ] token = '550e8400e29b41d4a716446655440000'
- [ ] 客户123被自动设置到当前订单
- [ ] 扫码日志记录 status = 'success'

---

### TC002: 过期短码

**目标**: 验证过期二维码被正确拒绝

**前置条件**:
- 模块已安装并启用

**输入**:
```
PMCUST:123:20200101T000000Z:550e8400e29b41d4a716446655440000
```

**预期结果**:
- [ ] 条码解析成功
- [ ] 显示错误提示 "二维码已过期"
- [ ] 不设置客户到订单
- [ ] 扫码日志记录 status = 'expired'

---

### TC003: 客户不在 POS 缓存

**目标**: 验证不存在的客户被正确处理

**前置条件**:
- 模块已安装并启用
- 客户 ID=999999 不存在或未同步

**输入**:
```
PMCUST:999999:20251231T235959Z:550e8400e29b41d4a716446655440000
```

**预期结果**:
- [ ] 条码解析成功
- [ ] 显示错误提示 "客户未同步到POS"
- [ ] 不设置客户到订单
- [ ] 扫码日志记录 status = 'partner_not_found'

---

### TC004: 商品条码不受影响

**目标**: 验证商品条码功能正常

**前置条件**:
- 模块已安装并启用

**输入**:
```
5901234123457
```

**预期结果**:
- [ ] 条码解析为商品条码 (type = 'product')
- [ ] 正常添加到订单
- [ ] 不触发 QR 客户选择逻辑

---

### TC005: 旧 JSON 码仍可用

**目标**: 验证向后兼容 JSON 格式

**前置条件**:
- 模块已安装并启用
- 客户 ID=123 已同步到 POS

**输入**:
```json
{"partnerId": 123, "expiresAt": "20251231T235959Z", "token": "550e8400e29b41d4a716446655440000", "name": "张三"}
```

**预期结果**:
- [ ] JSON 解析成功
- [ ] 客户被设置到当前订单
- [ ] 扫码日志记录 status = 'success'

---

### TC006: 在线验证模式 - 验证成功

**目标**: 验证在线验证功能

**前置条件**:
- 模块已安装并启用
- 已配置 "QR Validation Mode" = "Online"
- 已配置 "Require Token Validation" = True

**输入**:
```
PMCUST:123:20251231T235959Z:550e8400e29b41d4a716446655440000
```

**预期结果**:
- [ ] 调用验证 API 成功
- [ ] 验证返回 valid = true
- [ ] 客户被设置到订单

---

### TC007: 在线验证模式 - 验证失败

**目标**: 验证在线验证失败时正确处理

**前置条件**:
- 模块已安装并启用
- 已配置 "QR Validation Mode" = "Online"
- 已配置 "Require Token Validation" = True

**输入**:
```
PMCUST:123:20251231T235959Z:INVALIDTOKEN123456789012345678
```

**预期结果**:
- [ ] 调用验证 API 成功
- [ ] 验证返回 valid = false
- [ ] 显示错误提示
- [ ] 不设置客户到订单
- [ ] 扫码日志记录 status = 'token_failed'

---

### TC008: 错误格式 - 非 PMCUST 前缀

**目标**: 验证非识别前缀 fallback 到原逻辑

**前置条件**:
- 模块已安装并启用

**输入**:
```
INVALID:123:20251231T235959Z:550e8400e29b41d4a716446655440000
```

**预期结果**:
- [ ] 解析失败
- [ ] fallback 到原条码处理逻辑

---

### TC009: 错误格式 - 缺少字段

**目标**: 验证缺少字段时正确处理

**前置条件**:
- 模块已安装并启用

**输入**:
```
PMCUST:123
```

**预期结果**:
- [ ] 解析失败
- [ ] fallback 到原条码处理逻辑

---

### TC010: 错误格式 - token 格式错误

**目标**: 验证 token 格式校验

**前置条件**:
- 模块已安装并启用

**输入**:
```
PMCUST:123:20251231T235959Z:not-valid-token
```

**预期结果**:
- [ ] 解析失败 (token 不是 32 位 16 进制)
- [ ] fallback 到原条码处理逻辑

---

## 自动化测试

### JavaScript 单元测试

在 Odoo 18 中，可以使用 QUnit 进行 JS 测试:

```javascript
QUnit.module('Elitaco POS Customer QR', {
    beforeEach: function() {
        this.parser = this.env.barcodeParser;
    }
});

QUnit.test('Parse short code format', function(assert) {
    const result = this.parser.parse_barcode('PMCUST:123:20251231T235959Z:550e8400e29b41d4a716446655440000');
    assert.strictEqual(result.type, 'qr_customer');
    assert.strictEqual(result.partnerId, 123);
    assert.strictEqual(result.format, 'short');
});

QUnit.test('Parse JSON format', function(assert) {
    const result = this.parser.parse_barcode('{"partnerId": 123}');
    assert.strictEqual(result.type, 'qr_customer');
    assert.strictEqual(result.partnerId, 123);
});

QUnit.test('Fallback for product barcode', function(assert) {
    const result = this.parser.parse_barcode('5901234123457');
    assert.strictEqual(result.type, 'product');
});
```

## 测试检查清单

- [ ] 所有测试用例通过
- [ ] 商品条码不受影响
- [ ] 旧 JSON 格式兼容
- [ ] 过期码正确处理
- [ ] 不存在的客户正确处理
- [ ] 在线验证模式正常工作
- [ ] 扫码日志正确记录
