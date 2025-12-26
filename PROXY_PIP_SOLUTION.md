# 代理环境下Pip/Poetry下载失败问题解决方案

## 问题描述

### 症状表现
在开启Clash等代理工具时，使用Poetry或Pip安装Python包时出现SSL证书验证失败：

```bash
poetry install
# 或
pip install email-validator

# 错误信息：
# SSL: CERTIFICATE_VERIFY_FAILED
# Could not fetch URL https://pypi.org/simple/...
```

### 问题影响
- Poetry无法正常安装依赖包
- Pip无法从PyPI下载包
- 开发环境依赖安装受阻
- 每次都需要手动关闭代理才能安装，影响开发效率

### 根本原因
Clash等代理工具通过MITM（中间人）方式代理HTTPS流量时，会替换原始的SSL证书为代理工具自己的证书。而Python的pip/poetry工具在验证PyPI服务器证书时，发现证书不匹配，导致SSL验证失败。

**为什么会发生：**
1. Clash代理默认对所有HTTPS流量进行拦截和解密
2. 替换为Clash自己的根证书
3. Pip/Poetry严格验证服务器证书，发现不是PyPI官方证书
4. 拒绝连接，安装失败

---

## 解决方案

### 方案一：配置Clash代理规则（推荐）

在Clash配置文件中添加规则，让PyPI相关域名直接连接，不走代理。

#### 1. 找到Clash配置文件
通常位于：
- Windows: `C:\Users\<用户名>\.config\clash\config.yaml`
- 或Clash的配置文件目录

#### 2. 编辑配置文件
在 `rules:` 部分**最前面**添加以下规则：

```yaml
rules:
  # ==================== Python PyPI 直连规则 ====================
  # PyPI官方源
  - 'DOMAIN-SUFFIX,pypi.org,DIRECT'
  - 'DOMAIN-SUFFIX,pypi.python.org,DIRECT'
  - 'DOMAIN-SUFFIX,pythonhosted.org,DIRECT'
  - 'DOMAIN-SUFFIX,files.pythonhosted.org,DIRECT'

  # 国内镜像源（加速下载）
  - 'DOMAIN-SUFFIX,pypi.tuna.tsinghua.edu.cn,DIRECT'
  - 'DOMAIN-SUFFIX,mirrors.aliyun.com,DIRECT'
  - 'DOMAIN-SUFFIX,mirrors.cloud.tencent.com,DIRECT'
  - 'DOMAIN-SUFFIX,pypi.douban.com,DIRECT'
  # ============================================================

  # ... 其他原有规则 ...
  - GEOIP,CN,DIRECT
  - MATCH,PROXY
```

#### 3. 重载Clash配置
- 打开Clash客户端
- 点击"配置" → "重载配置"
- 或重启Clash

#### 4. 验证配置
```bash
# 测试pip下载
cd backend
poetry run pip install requests --upgrade

# 测试PyPI官方源
poetry run pip install --index-url https://pypi.org/simple httpx --upgrade
```

**预期结果：**
```
✅ 成功下载并安装
✅ 无SSL证书错误
✅ 下载速度正常
```

---

### 方案二：临时禁用SSL验证（不推荐）

**⚠️ 警告：仅用于应急，存在安全风险**

```bash
# Poetry
poetry config http-basic.pypi <username> <password>
poetry install --cert /path/to/cert.pem

# Pip
pip install package_name --trusted-host pypi.org --trusted-host files.pythonhosted.org
```

**缺点：**
- 不安全，容易受到中间人攻击
- 需要每次都手动添加参数
- 治标不治本

---

### 方案三：临时关闭代理（不推荐）

**缺点：**
- 影响其他需要代理的服务
- 操作繁琐，每次都要开关代理
- 效率低下

---

## 配置说明

### 规则优先级
Clash的规则是**从上到下**匹配的，匹配到第一条规则后就会停止。因此：

```yaml
rules:
  # ✅ 正确：PyPI规则在最前面
  - 'DOMAIN-SUFFIX,pypi.org,DIRECT'
  - 'MATCH,PROXY'

  # ❌ 错误：MATCH在前，PyPI规则永远不会生效
  - 'MATCH,PROXY'
  - 'DOMAIN-SUFFIX,pypi.org,DIRECT'  # 这条规则不会被执行
```

### 规则类型说明

| 规则类型 | 说明 | 示例 |
|---------|------|------|
| `DOMAIN-SUFFIX` | 匹配域名后缀 | `pypi.org` 会匹配 `files.pythonhosted.org` |
| `DOMAIN` | 精确匹配域名 | 只匹配完全相同的域名 |
| `DIRECT` | 直接连接，不走代理 | 绕过代理 |
| `PROXY` | 走代理连接 | 使用代理 |

### 为什么要添加国内镜像源？

即使配置了PyPI直连，Poetry/Pip可能会使用国内镜像源加速下载。如果不添加镜像源规则，访问镜像时仍会走代理，可能出现问题。

**常用国内镜像：**
- 清华大学：`pypi.tuna.tsinghua.edu.cn`
- 阿里云：`mirrors.aliyun.com`
- 腾讯云：`mirrors.cloud.tencent.com`
- 豆瓣：`pypi.douban.com`

---

## 验证方法

### 1. 测试清华镜像源
```bash
cd backend
poetry run pip install requests --upgrade
```

**预期输出：**
```
Looking in indexes: https://pypi.tuna.tsinghua.edu.cn/simple
Collecting requests
  Downloading https://pypi.tuna.tsinghua.edu.cn/packages/.../requests-2.32.5-py3-none-any.whl
Successfully installed requests-2.32.5
```

### 2. 测试PyPI官方源
```bash
poetry run pip install --index-url https://pypi.org/simple httpx --upgrade
```

**预期输出：**
```
Downloading httpx-0.28.1-py3-none-any.whl
Successfully installed httpx-0.28.1
```

### 3. 测试Poetry安装
```bash
poetry install
```

**预期输出：**
```
Installing dependencies from lock file
...
Installing the current project: print-erp-backend
```

---

## 常见问题

### Q1: 为什么添加规则后还是失败？

**可能原因：**
1. ❌ 规则位置错误 - 确保PyPI规则在 `MATCH,PROXY` 之前
2. ❌ 未重载配置 - 需要重启Clash或重载配置
3. ❌ 配置文件语法错误 - 检查YAML缩进和格式
4. ❌ Clash版本太旧 - 更新到最新版本

**解决办法：**
```bash
# 1. 检查Clash配置是否生效
# 在Clash日志中查看是否有DIRECT规则匹配

# 2. 验证YAML语法
# 使用在线YAML验证器检查配置文件

# 3. 清除pip缓存
poetry cache clear pypi --all
```

### Q2: 还需要配置Poetry的PyPI源吗？

**不需要，但建议配置国内镜像加速：**

```bash
# 配置清华镜像源（可选，加速下载）
poetry source add --priority=primary tsinghua https://pypi.tuna.tsinghua.edu.cn/simple/

# 查看已配置的源
poetry source show
```

### Q3: 能否只添加PyPI官方源，不添加镜像源？

**可以，但不推荐：**
- Poetry可能会自动使用pip配置的镜像源
- 如果镜像源没有直连规则，仍会走代理
- 建议**全部添加**，确保万无一失

### Q4: 这个配置会影响其他软件吗？

**不会：**
- 只影响访问PyPI相关域名的流量
- 其他网站仍然正常走代理
- 不影响浏览器、游戏、其他软件

---

## 完整配置示例

```yaml
# Clash配置文件示例
proxies:
  - name: "Proxy-1"
    type: ss
    server: example.com
    port: 443
    cipher: aes-256-gcm
    password: password

proxy-groups:
  - name: PROXY
    type: select
    proxies:
      - Proxy-1
      - DIRECT

rules:
  # ==================== Python PyPI 直连规则 ====================
  - 'DOMAIN-SUFFIX,pypi.org,DIRECT'
  - 'DOMAIN-SUFFIX,pypi.python.org,DIRECT'
  - 'DOMAIN-SUFFIX,pythonhosted.org,DIRECT'
  - 'DOMAIN-SUFFIX,files.pythonhosted.org,DIRECT'
  - 'DOMAIN-SUFFIX,pypi.tuna.tsinghua.edu.cn,DIRECT'
  - 'DOMAIN-SUFFIX,mirrors.aliyun.com,DIRECT'
  - 'DOMAIN-SUFFIX,mirrors.cloud.tencent.com,DIRECT'
  - 'DOMAIN-SUFFIX,pypi.douban.com,DIRECT'
  # ============================================================

  # 国内直连
  - GEOIP,CN,DIRECT

  # 其他流量走代理
  - MATCH,PROXY
```

---

## 总结

### 问题核心
开启Clash代理后，PyPI的HTTPS流量被代理拦截，SSL证书被替换，导致pip/poetry验证失败。

### 最佳实践
✅ **在Clash配置中添加PyPI直连规则（推荐）**
- 一次配置，永久生效
- 安全可靠，不降低安全性
- 不影响开发效率

### 配置要点
1. ✅ 规则添加在 `rules:` 部分最前面
2. ✅ 包含PyPI官方源和国内镜像源
3. ✅ 使用 `DOMAIN-SUFFIX` 匹配子域名
4. ✅ 配置后重载Clash
5. ✅ 测试验证是否生效

### 效果
- 🚀 开着代理也能正常使用pip/poetry
- 🚀 无需每次关闭代理
- 🚀 无SSL证书错误
- 🚀 提升开发效率

---

**文档版本：** 1.0
**更新日期：** 2025-12-23
**适用场景：** Clash/ClashX/Clash for Windows + Poetry/Pip
**测试环境：** Windows 11 + Python 3.11 + Poetry 1.8+
