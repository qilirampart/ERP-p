# Git 工作流指南

本文档提供Print-ERP项目的Git日常操作指南。

---

## 📚 目录

- [基础工作流](#基础工作流)
- [使用代理推送](#使用代理推送)
- [分支管理](#分支管理)
- [常用场景](#常用场景)
- [最佳实践](#最佳实践)
- [故障排查](#故障排查)

---

## 🔄 基础工作流

### 日常开发流程

```bash
# 1. 进入项目目录
cd C:\Project\ERP-p

# 2. 查看当前状态
git status

# 3. 查看修改内容
git diff

# 4. 添加修改到暂存区
git add .                    # 添加所有修改
git add backend/app/main.py  # 添加特定文件

# 5. 提交修改
git commit -m "描述你的修改内容"

# 6. 推送到远程仓库
git push
```

### 提交信息规范

**推荐格式**:
```
<type>: <subject>

<body>
```

**类型 (type)**:
- `feat`: 新功能
- `fix`: 修复bug
- `docs`: 文档修改
- `style`: 代码格式调整
- `refactor`: 重构代码
- `test`: 添加测试
- `chore`: 构建工具或依赖更新

**示例**:
```bash
git commit -m "feat: 添加订单导出功能

- 支持导出为Excel格式
- 支持自定义导出字段
- 添加导出按钮到订单列表页"
```

```bash
git commit -m "fix: 修复物料库存扣减错误"
```

```bash
git commit -m "docs: 更新README安装说明"
```

---

## 🔐 使用代理推送

### 方法1: 临时设置代理（推荐）

**每次推送前**:
```bash
cd C:\Project\ERP-p

# 设置代理（Clash端口7890）
git config http.proxy http://127.0.0.1:7890
git config https.proxy http://127.0.0.1:7890

# 推送代码
git push

# 推送完成后立即取消代理
git config --unset http.proxy
git config --unset https.proxy
```

### 方法2: 创建别名脚本

**Windows PowerShell**:

在项目根目录创建 `git-push.ps1`:
```powershell
# git-push.ps1
git config http.proxy http://127.0.0.1:7890
git config https.proxy http://127.0.0.1:7890
git push
git config --unset http.proxy
git config --unset https.proxy
Write-Host "推送完成，代理已清除" -ForegroundColor Green
```

使用:
```bash
.\git-push.ps1
```

**Git Bash**:

在项目根目录创建 `git-push.sh`:
```bash
#!/bin/bash
git config http.proxy http://127.0.0.1:7890
git config https.proxy http://127.0.0.1:7890
git push "$@"
git config --unset http.proxy
git config --unset https.proxy
echo "✅ 推送完成，代理已清除"
```

使用:
```bash
bash git-push.sh
```

### 方法3: 全局代理（不推荐）

```bash
# 设置全局代理
git config --global http.proxy http://127.0.0.1:7890
git config --global https.proxy http://127.0.0.1:7890

# 查看配置
git config --global --list

# 取消全局代理（记得用完取消！）
git config --global --unset http.proxy
git config --global --unset https.proxy
```

⚠️ **注意**: 全局代理会影响所有Git仓库，用完务必取消。

---

## 🌿 分支管理

### 创建新分支

```bash
# 创建并切换到新分支
git checkout -b feature/订单导出

# 或分两步
git branch feature/订单导出
git checkout feature/订单导出
```

### 分支命名规范

- `feature/功能名` - 新功能开发
- `fix/bug描述` - Bug修复
- `hotfix/紧急修复` - 紧急线上修复
- `refactor/重构内容` - 代码重构
- `docs/文档更新` - 文档修改

**示例**:
```bash
git checkout -b feature/物料批量导入
git checkout -b fix/库存扣减错误
git checkout -b docs/更新API文档
```

### 分支操作

```bash
# 查看所有分支
git branch -a

# 查看当前分支
git branch

# 切换分支
git checkout main
git checkout develop

# 删除本地分支
git branch -d feature/订单导出

# 删除远程分支
git push origin --delete feature/订单导出

# 重命名当前分支
git branch -m 新分支名
```

### 合并分支

```bash
# 切换到目标分支（如main）
git checkout main

# 拉取最新代码
git pull

# 合并功能分支
git merge feature/订单导出

# 推送合并结果
git push
```

---

## 🎯 常用场景

### 场景1: 每天开始工作

```bash
cd C:\Project\ERP-p

# 拉取最新代码
git pull

# 查看当前分支
git branch

# 如果需要，切换到开发分支
git checkout develop
```

### 场景2: 开发新功能

```bash
# 1. 确保在最新的代码基础上
git checkout main
git pull

# 2. 创建功能分支
git checkout -b feature/新功能名

# 3. 开发代码...

# 4. 提交修改
git add .
git commit -m "feat: 添加新功能"

# 5. 推送到远程（首次推送需要-u）
git config http.proxy http://127.0.0.1:7890
git push -u origin feature/新功能名
git config --unset http.proxy

# 6. 在GitHub上创建Pull Request
```

### 场景3: 修复Bug

```bash
# 1. 创建修复分支
git checkout -b fix/修复内容

# 2. 修复代码...

# 3. 提交
git add .
git commit -m "fix: 修复XX问题"

# 4. 推送
git config http.proxy http://127.0.0.1:7890
git push -u origin fix/修复内容
git config --unset http.proxy
```

### 场景4: 暂存当前工作

```bash
# 保存当前未提交的修改
git stash save "暂存描述"

# 查看暂存列表
git stash list

# 切换分支处理其他事情
git checkout other-branch

# 回到原分支
git checkout feature/原分支

# 恢复暂存的修改
git stash pop
```

### 场景5: 撤销修改

```bash
# 撤销工作区的修改（未add）
git checkout -- <文件名>
git checkout -- .  # 撤销所有修改

# 撤销已add的文件（回到工作区）
git reset HEAD <文件名>

# 撤销最后一次commit（保留修改）
git reset --soft HEAD^

# 撤销最后一次commit（丢弃修改）⚠️危险
git reset --hard HEAD^

# 修改最后一次commit信息
git commit --amend -m "新的提交信息"
```

### 场景6: 查看历史

```bash
# 查看提交历史
git log

# 简洁格式查看
git log --oneline

# 查看最近3次提交
git log -3

# 查看某个文件的修改历史
git log -- backend/app/main.py

# 查看某次提交的详细内容
git show <commit-hash>
```

### 场景7: 同步远程分支

```bash
# 查看远程分支
git branch -r

# 拉取所有远程分支信息
git fetch

# 拉取并合并
git pull origin main

# 查看本地分支与远程分支的关系
git branch -vv
```

---

## 📋 最佳实践

### ✅ 提交频率

- **频繁提交**: 完成一个小功能就提交
- **避免**: 一天结束才提交一次大改动
- **原则**: 每次提交应该是一个逻辑完整的单元

### ✅ 提交内容

```bash
# ✅ 好的做法 - 单一职责
git commit -m "feat: 添加物料导出按钮"
git commit -m "feat: 实现物料导出API"
git commit -m "feat: 添加导出格式选择"

# ❌ 不好的做法 - 混合多个功能
git commit -m "添加导出功能、修复bug、更新文档"
```

### ✅ 分支策略

**推荐工作流**:

```
main (production)     ← 稳定版本，随时可部署
  ↑
develop              ← 开发主分支
  ↑
feature/xxx          ← 功能分支（从develop创建）
fix/xxx              ← 修复分支（从develop创建）
hotfix/xxx           ← 紧急修复（从main创建）
```

**操作流程**:
```bash
# 开发新功能
git checkout develop
git pull
git checkout -b feature/新功能
# ... 开发 ...
git push origin feature/新功能
# 在GitHub创建PR，合并到develop

# 发布版本
git checkout main
git merge develop
git tag -a v1.0.0 -m "Release version 1.0.0"
git push origin main --tags
```

### ✅ 忽略文件

确保 `.gitignore` 包含:
```gitignore
# 环境变量
.env
.env.local

# 依赖
node_modules/
__pycache__/

# 构建产物
dist/
build/

# IDE
.vscode/
.idea/

# 日志
*.log

# 系统文件
.DS_Store
Thumbs.db
```

### ✅ 代码审查

使用Pull Request进行代码审查:

1. **创建PR**: 功能开发完成后，在GitHub创建PR
2. **描述清楚**: PR描述应包含改动内容、测试情况
3. **等待审查**: 团队成员审查代码
4. **修改反馈**: 根据反馈修改代码
5. **合并代码**: 审查通过后合并到目标分支

---

## 🔧 故障排查

### 问题1: Push失败 - 网络错误

```bash
fatal: unable to access 'https://github.com/...': Failed to connect
```

**解决**:
```bash
# 设置代理
git config http.proxy http://127.0.0.1:7890
git config https.proxy http://127.0.0.1:7890

# 重试push
git push
```

### 问题2: Push被拒绝 - 远程有更新

```bash
! [rejected] main -> main (fetch first)
error: failed to push some refs
```

**解决**:
```bash
# 先拉取远程更新
git pull

# 如果有冲突，解决冲突后
git add .
git commit -m "Merge remote changes"

# 再推送
git push
```

### 问题3: 冲突解决

```bash
# 拉取时出现冲突
Auto-merging file.py
CONFLICT (content): Merge conflict in file.py
```

**解决步骤**:

1. 打开冲突文件，找到冲突标记:
```python
<<<<<<< HEAD
# 你的修改
print("Hello")
=======
# 远程的修改
print("Hi")
>>>>>>> origin/main
```

2. 手动编辑，保留需要的内容:
```python
# 解决后的代码
print("Hello")
```

3. 标记为已解决:
```bash
git add file.py
git commit -m "Resolve merge conflict"
git push
```

### 问题4: 误提交敏感文件

```bash
# 从Git历史中完全删除（⚠️谨慎使用）
git filter-branch --force --index-filter \
  "git rm --cached --ignore-unmatch 文件路径" \
  --prune-empty --tag-name-filter cat -- --all

# 强制推送（会改写历史）
git push origin --force --all
```

更安全的方法:
```bash
# 只从当前版本删除，历史保留
git rm --cached .env
git commit -m "Remove .env from tracking"
git push

# 确保.gitignore包含该文件
echo ".env" >> .gitignore
```

### 问题5: 忘记切换分支就开发了

```bash
# 已修改但未提交
git stash
git checkout 正确的分支
git stash pop

# 已提交但在错误分支
git log  # 记录commit hash
git checkout 正确的分支
git cherry-pick <commit-hash>
```

---

## 📝 快速参考

### 常用命令速查

| 命令 | 说明 |
|------|------|
| `git status` | 查看状态 |
| `git add .` | 添加所有修改 |
| `git commit -m "msg"` | 提交 |
| `git push` | 推送 |
| `git pull` | 拉取 |
| `git log` | 查看历史 |
| `git branch` | 查看分支 |
| `git checkout -b xxx` | 创建并切换分支 |
| `git merge xxx` | 合并分支 |
| `git stash` | 暂存修改 |

### 代理快速设置

```bash
# 设置代理
git config http.proxy http://127.0.0.1:7890 && git config https.proxy http://127.0.0.1:7890

# 取消代理
git config --unset http.proxy && git config --unset https.proxy
```

### 一键推送脚本（含代理）

**PowerShell** (`push.ps1`):
```powershell
git config http.proxy http://127.0.0.1:7890
git config https.proxy http://127.0.0.1:7890
git push
$exitCode = $LASTEXITCODE
git config --unset http.proxy
git config --unset https.proxy
if ($exitCode -eq 0) {
    Write-Host "✅ 推送成功" -ForegroundColor Green
} else {
    Write-Host "❌ 推送失败" -ForegroundColor Red
}
exit $exitCode
```

**Bash** (`push.sh`):
```bash
#!/bin/bash
git config http.proxy http://127.0.0.1:7890
git config https.proxy http://127.0.0.1:7890
git push "$@"
exit_code=$?
git config --unset http.proxy
git config --unset https.proxy
if [ $exit_code -eq 0 ]; then
    echo "✅ 推送成功"
else
    echo "❌ 推送失败"
fi
exit $exit_code
```

---

## 🔗 相关资源

- **GitHub仓库**: https://github.com/qilirampart/ERP-p
- **Git官方文档**: https://git-scm.com/doc
- **GitHub帮助**: https://docs.github.com

---

## 📌 小贴士

1. ✅ **提交前先Pull**: 避免冲突
2. ✅ **频繁提交**: 小步快跑，便于回滚
3. ✅ **清晰的提交信息**: 方便查找历史
4. ✅ **使用分支**: 保持main分支稳定
5. ✅ **代理用完就关**: 不影响其他项目
6. ✅ **定期备份**: Push到远程就是最好的备份

---

**最后更新**: 2025-12-07
