# 🔧 登录和API问题修复指南

## 📋 问题说明

如果您遇到以下问题：
1. ❌ 打开系统直接跳转到仪表板，跳过登录页面
2. ❌ 生产排程页面显示"请求的资源不存在"错误
3. ❌ API调用失败（404错误）

这是因为浏览器缓存了旧版本的token和配置。

---

## ✅ 完整解决方案

### 方法1：使用自动重启脚本（推荐⭐）

**步骤如下：**

#### 1. 停止当前服务
在两个运行中的命令行窗口中按 `Ctrl+C` 或直接关闭窗口

#### 2. 双击运行重启脚本
```
双击 restart-clean.bat
```

这个脚本会自动：
- ✅ 停止所有后端和前端服务
- ✅ 清除前端Vite构建缓存
- ✅ 重新启动后端服务（等待5秒）
- ✅ 重新启动前端服务（等待8秒）
- ✅ 自动打开清除缓存页面

#### 3. 清除浏览器缓存
脚本会自动打开 `clear-cache.html` 页面：
- 点击 **"清除缓存数据"** 按钮
- 等待提示"缓存已清除"
- 页面会自动跳转到登录页

#### 4. 重新登录
使用默认账号登录：
- 用户名：`admin`
- 密码：`admin123`

---

### 方法2：手动操作

如果自动脚本有问题，可以手动操作：

#### 第1步：停止所有服务
```bash
stop.bat
```

#### 第2步：清除前端缓存
```bash
cd frontend
rd /s /q node_modules\.vite
rd /s /q dist
cd ..
```

#### 第3步：清除浏览器缓存

**选项A：使用清除工具**
```
双击打开 clear-cache.html
点击"清除缓存数据"按钮
```

**选项B：浏览器开发者工具**
1. 按 `F12` 打开开发者工具
2. 进入 **Application** (Chrome) 或 **存储** (Firefox) 标签
3. 找到 **Local Storage** → `http://localhost:5173`
4. 删除 `access_token` 和 `user_info`
5. 关闭开发者工具

**选项C：浏览器控制台**
1. 按 `F12` 打开开发者工具
2. 进入 **Console** 标签
3. 执行：
   ```javascript
   localStorage.clear()
   location.reload()
   ```

#### 第4步：重启服务
```bash
start.bat
```

#### 第5步：强制刷新浏览器
打开浏览器后按 `Ctrl+Shift+R` (Windows) 或 `Cmd+Shift+R` (Mac)

---

## 🎯 验证修复结果

### ✅ 正常表现

1. **首次访问**
   - 自动跳转到 `http://localhost:5173/login`
   - 显示登录页面

2. **登录后**
   - 成功跳转到仪表板
   - 控制台显示：`[路由守卫] Token有效，允许访问`

3. **生产排程页面**
   - 正常显示统计卡片（5个）
   - 正常加载工单列表
   - 无红色错误提示

4. **浏览器控制台（F12）**
   - Network面板：API请求返回 `200 OK`
   - Console面板：无错误信息

### ❌ 异常表现（需要重新操作）

- 直接进入仪表板而非登录页
- 生产排程显示"请求的资源不存在"
- 控制台显示401/404错误
- Network面板显示API请求失败

---

## 🔍 技术细节

### 修复内容

#### 1. API路径配置修复
**文件**: `frontend/src/api/request.js`
```javascript
// 修改前（错误）
baseURL: 'http://localhost:8000'

// 修改后（正确）
baseURL: 'http://localhost:8000/api/v1'
```

#### 2. 路由守卫增强
**文件**: `frontend/src/router/index.js`

新增功能：
- ✅ 真正验证token有效性（调用API测试）
- ✅ 无效token自动清除并跳转登录
- ✅ 避免重复验证（使用tokenValidated标记）
- ✅ 详细的控制台日志

#### 3. Token验证机制
**文件**: `frontend/src/stores/user.js`

新增方法：
- `validateToken()` - 验证token是否有效
- `tokenValidated` - 标记token已验证，避免重复请求

验证逻辑：
```javascript
// 调用materials API测试token
GET http://localhost:8000/api/v1/materials/?page=1&page_size=1
Authorization: Bearer <token>

// 401 → Token无效，清除并跳转登录
// 200 → Token有效，标记已验证
```

---

## 🚀 启动流程（修复后）

```
1. 用户打开浏览器 → http://localhost:5173
                    ↓
2. 路由守卫检查
   - 检查localStorage.token
   - 存在 → 调用API验证
   - 不存在 → 跳转登录
                    ↓
3a. Token有效                3b. Token无效
    - 恢复用户信息                - 清除localStorage
    - 允许访问仪表板              - 跳转登录页
    - 显示统计数据                - 要求重新登录
                    ↓
4. 用户登录
   - 输入 admin/admin123
   - 获取新token
   - 标记tokenValidated=true
   - 进入系统
```

---

## 📝 常见问题

### Q1: 为什么要清除浏览器缓存？
**A**: 旧的token可能已过期，但浏览器仍在使用它，导致认证失败。

### Q2: 为什么要清除Vite缓存？
**A**: Vite会缓存编译后的代码，清除后可以确保使用最新的代码。

### Q3: 每次启动都需要清除缓存吗？
**A**: 不需要！只有在遇到问题时才需要清除。正常使用时，token会自动续期。

### Q4: Token有效期是多久？
**A**: 默认30分钟（在 `backend/app/core/config.py` 中配置）

### Q5: 如果重启脚本失败怎么办？
**A**: 使用手动操作方法，按步骤逐一执行。

---

## 📞 仍然有问题？

如果按照以上步骤仍然无法解决，请检查：

1. **后端服务是否正常运行**
   ```bash
   访问 http://localhost:8000/docs
   应该能看到API文档页面
   ```

2. **数据库是否连接**
   ```bash
   后端命令行窗口不应该有数据库连接错误
   ```

3. **端口是否被占用**
   ```bash
   netstat -ano | findstr "8000"
   netstat -ano | findstr "5173"
   ```

4. **浏览器控制台日志**
   ```
   按F12查看Console和Network面板
   截图错误信息
   ```

---

## ✨ 修复完成标志

当您看到以下情况时，说明修复成功：

- ✅ 打开系统自动跳转到登录页
- ✅ 登录后进入仪表板
- ✅ 生产排程页面正常显示统计数据
- ✅ 控制台显示 `[路由守卫] Token有效，允许访问`
- ✅ Network面板所有API请求返回200

**恭喜！系统已恢复正常！** 🎉
