# Elitaco POS Customer QR

POS 扫会员码自动选客模块 - 支持短码格式

## 功能概述

在 POS 中扫描会员二维码自动选择客户到当前订单。

### 支持的二维码格式

#### 方案2: 短码格式 (推荐)

```
PMCUST:{partnerId}:{expiresAt}:{token}
```

参数说明:
- `partnerId`: 客户ID (整数)
- `expiresAt`: UTC时间，格式 `YYYYMMDDTHHMMSSZ` (例如: `20251231T235959Z`)
- `token`: UUID去横线，32位十六进制 (例如: `550e8400e29b41d4a716446655440000`)

**示例:**
```
PMCUST:123:20251231T235959Z:550e8400e29b41d4a716446655440000
```

#### 旧版 JSON 格式 (向后兼容)

```json
{
    "partnerId": 123,
    "expiresAt": "20251231T235959Z",
    "token": "550e8400e29b41d4a716446655440000",
    "name": "张三"
}
```

## 安装与启用

1. 将模块复制到 Odoo 的 addons 目录
2. 在 Odoo 界面更新应用列表
3. 安装 `Elitaco POS Customer QR` 模块
4. 进入 `POS > Configuration > Point of Sales`
5. 编辑需要启用的 POS 配置
6. 勾选 `Enable QR Customer Selection`
7. (可选) 设置 `QR Validation Mode` 为 `Online` 启用在线验证
8. (可选) 勾选 `Require Token Validation` 要求 token 验证

## 验证模式

### 离线模式 (默认)

- 仅校验过期时间
- 仅检查客户是否已同步到 POS
- 不需要网络请求

### 在线模式

- 校验过期时间
- 调用后端 API 验证 token
- 需要网络连接
- 更安全

## 配置说明

| 配置项 | 说明 | 默认值 |
|--------|------|--------|
| Enable QR Customer Selection | 启用二维码选客 | 关闭 |
| QR Validation Mode | 验证模式 | 离线 |
| Require Token Validation | 要求 token 验证 | 关闭 |

## 扫码行为

1. **解析二维码** - 识别 `PMCUST:` 前缀或 JSON 格式
2. **校验过期** - 检查 `expiresAt` 是否过期
   - 过期: 显示错误 "二维码已过期"，不再继续处理
3. **查找客户** - 在 POS 缓存的客户列表中查找
   - 不存在: 显示错误 "客户未同步到POS"
   - 存在: 自动设置客户到当前订单
4. **在线验证** (可选)
   - 调用后端 API 验证 token
   - 验证失败: 显示错误并拒绝选客

## 故障排查

### 扫码无反应

1. 检查模块是否已安装并启用
2. 检查该 POS 是否勾选了 "Enable QR Customer Selection"
3. 检查浏览器控制台是否有 JS 错误

### 提示 "客户未同步到POS"

1. 确保客户已同步到 POS (在 POS 配置中加载客户)
2. 检查客户 ID 是否正确

### 提示 "二维码已过期"

1. 检查手机时间是否正确
2. 检查二维码生成时的有效期设置

### 在线验证失败

1. 检查网络连接
2. 检查 API URL 配置是否正确
3. 检查后端日志

## 技术细节

### 文件结构

```
elitaco_pos_customer_qr/
├── __init__.py
├── __manifest__.py
├── models/
│   ├── __init__.py
│   ├── pos_config.py          # POS 配置字段
│   └── qr_scan_log.py         # 扫码日志模型
├── controllers/
│   ├── __init__.py
│   └── qr_validate.py         # Token 验证 API
├── security/
│   └── ir.model.access.csv    # 访问权限
├── views/
│   └── pos_config_views.xml   # POS 配置视图
└── static/
    └── src/
        ├── js/overrides/
        │   └── barcode_handler.js  # Odoo 18 POS 条码处理
        └── xml/
            └── pos_customer_qr.xml   # 资源定义
```

### 兼容性

- Odoo 18.0+
- 使用 Odoo 18 的 Owl 框架和新的 POS API
- 向后兼容旧版 JSON 格式

## 测试用例

### 测试1: 正常短码选客

**输入:**
```
PMCUST:123:20251231T235959Z:550e8400e29b41d4a716446655440000
```

**预期:**
- 解析成功
- 客户123被设置到当前订单
- 状态: success

### 测试2: 过期短码

**输入:**
```
PMCUST:123:20200101T000000Z:550e8400e29b41d4a716446655440000
```

**预期:**
- 解析成功
- 显示错误 "二维码已过期"
- 不设置客户

### 测试3: 客户不在 POS 缓存

**输入:**
```
PMCUST:999999:20251231T235959Z:550e8400e29b41d4a716446655440000
```

**预期:**
- 解析成功
- 显示错误 "客户未同步到POS"
- 不设置客户

### 测试4: 商品条码不受影响

**输入:**
```
5901234123457
```

**预期:**
- 正常解析为商品条码
- 添加商品到订单

### 测试5: 旧 JSON 码仍可用

**输入:**
```json
{"partnerId": 123, "expiresAt": "20251231T235959Z", "token": "xxx"}
```

**预期:**
- 解析成功
- 客户被设置到当前订单
- 状态: success

## 许可证

LGPL-3
