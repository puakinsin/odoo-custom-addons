# Test Cases - QR Customer Selection

## 测试清单

### 1. 有效 QR 码测试
- [ ] 扫描有效的 QR 码（未过期，partnerId 存在）
- [ ] 验证客户自动选中
- [ ] 验证订单客户信息更新

### 2. 过期 QR 码测试
- [ ] 扫描过期的 QR 码（expiresAt < 当前时间）
- [ ] 验证显示"二维码已过期"错误
- [ ] 验证客户未选中

### 3. 客户不存在测试
- [ ] 扫描 QR 码（partnerId 不在 POS 缓存）
- [ ] 验证显示"客户未同步到POS"错误
- [ ] 验证提供同步建议

### 4. 无效 JSON 测试
- [ ] 扫描普通商品条码（EAN13）
- [ ] 验证走原有处理流程
- [ ] 验证商品正常识别

### 5. 部分字段缺失测试
- [ ] 扫描只有 partnerId 的 JSON
- [ ] 验证按客户选择处理
- [ ] 扫描无 partnerId 的 JSON
- [ ] 验证走原有处理流程

### 6. Token 验证测试（在线模式）
- [ ] 配置为 Online 模式
- [ ] 扫描有效 token
- [ ] 验证在线验证成功
- [ ] 扫描无效 token
- [ ] 验证 Token 验证失败提示

### 7. 扫码枪输入测试
- [ ] 使用扫码枪扫描 QR
- [ ] 验证正确识别和处理

### 8. 相机扫码测试（如支持）
- [ ] 使用相机扫描 QR
- [ ] 验证正确识别和处理

### 9. 并发处理测试
- [ ] 快速连续扫描多个 QR
- [ ] 验证每个都正确处理

### 10. 日志记录测试
- [ ] 执行各种扫描
- [ ] 验证日志正确记录

## 手工测试脚本

```javascript
// 在 POS 浏览器 Console 中测试

// Test 1: Valid QR
var validQR = '{"token":"test-token","partnerId":52,"name":"Kin Sin","tier":"steel","expiresAt":"2027-12-31T23:59:59.000Z"}';

// Test 2: Expired QR
var expiredQR = '{"token":"test-token","partnerId":52,"name":"Test","expiresAt":"2020-01-01T00:00:00.000Z"}';

// Test 3: Missing partnerId
var noPartnerQR = '{"token":"test-token","name":"Test"}';

// 模拟扫码
function testQR(qr) {
    var parser = odoo.pos_widgets.some(function(w) { return w.barcode_parser; });
    if (parser) {
        parser.parse_barcode(qr);
    }
}
```

## 测试数据

| partnerId | Name | Tier |
|-----------|------|------|
| 52 | Kin Sin | Steel |
| 53 | John Doe | Gold |
| 54 | Jane Smith | Platinum |

## 回归测试

确保以下功能不受影响：
- [ ] 商品条码扫描
- [ ] 会员卡积分
- [ ] 优惠券/礼品券
- [ ] 重量秤条码
- [ ] 序列号扫描
