# 📚 ABSESpy 文档版本管理指南

## ✅ Mike版本管理已配置

### 工作流程

**GitHub Actions自动处理**:

```yaml
# dev分支推送
→ mike deploy dev (预览版)

# master分支推送
→ mike deploy 0.8 latest (当前版本)

# 版本tag推送 (v0.8.0)
→ mike deploy 0.8 latest (自动从tag提取版本号)
```

### URL结构

```
主站点（最新版本，latest别名）:
https://absespy.github.io/ABSESpy/

开发预览版（dev分支）:
https://absespy.github.io/ABSESpy/dev/

特定版本（0.8）:
https://absespy.github.io/ABSESpy/0.8/

旧版本（0.7）:
https://absespy.github.io/ABSESpy/0.7/
```

### 双语支持

**每个版本都包含双语**:

```
英文:
https://absespy.github.io/ABSESpy/0.8/
https://absespy.github.io/ABSESpy/0.8/home/Installation/

中文:
https://absespy.github.io/ABSESpy/0.8/zh/
https://absespy.github.io/ABSESpy/0.8/zh/home/Installation/
```

---

## 🔧 本地使用Mike

### 部署版本

```bash
# 部署dev预览版
mike deploy dev

# 部署0.8版本并设为latest
mike deploy 0.8 latest --update-aliases

# 设置默认版本
mike set-default latest
```

### 查看版本

```bash
# 列出所有版本
mike list

# 输出示例:
# dev [dev]
# 0.8 [latest]
# 0.7
```

### 删除版本

```bash
# 删除dev版本
mike delete dev
```

### 服务特定版本

```bash
# 本地预览latest版本
mike serve

# 本地预览特定版本
mike serve --dev-addr 127.0.0.1:8000 0.8
```

---

## 📋 版本发布流程

### 场景1: 开发预览（dev分支）

```bash
# 1. 在dev分支上修改文档
git checkout dev
# ... 修改文档 ...

# 2. 提交并推送
git add .
git commit -m "docs: update something"
git push origin dev

# 3. GitHub Actions自动部署
# 结果: https://absespy.github.io/ABSESpy/dev/
```

### 场景2: 正式发布（master分支）

```bash
# 1. 合并dev到master
git checkout master
git merge dev

# 2. 推送master
git push origin master

# 3. GitHub Actions自动部署
# 结果: https://absespy.github.io/ABSESpy/ (0.8版本，latest)
```

### 场景3: 版本tag发布

```bash
# 1. 创建版本tag（通常由release-please自动完成）
git tag v0.8.0
git push origin v0.8.0

# 2. GitHub Actions自动部署
# 结果:
#   - https://absespy.github.io/ABSESpy/0.8/
#   - https://absespy.github.io/ABSESpy/ (latest更新)
```

---

## 🎨 版本选择器

### 用户体验

访问文档时，页面顶部会显示两个选择器：

```
[📚 0.8 (latest) ▼]  [🌐 English ▼]
```

**版本选择器** (📚):
- latest (0.8)
- dev
- 0.7 (如果存在)

**语言选择器** (🌐):
- English
- 中文

用户可以：
1. 选择版本（0.8, 0.7, dev）
2. 选择语言（English, 中文）
3. 两个选择独立工作

---

## 📊 版本管理策略

### 版本别名

| 别名 | 指向 | 用途 |
|------|------|------|
| `latest` | 最新stable版本 | 默认文档 |
| `dev` | 开发分支 | 预览新功能 |
| `0.8` | v0.8.x系列 | 特定版本 |
| `0.7` | v0.7.x系列 | 历史版本 |

### 更新策略

**Minor版本更新** (0.8.0 → 0.8.1):
```bash
# 不创建新版本，更新0.8
mike deploy 0.8 latest --update-aliases --push
```

**Major/Minor版本更新** (0.8.x → 0.9.0):
```bash
# 创建新版本，保留旧版本
mike deploy 0.9 latest --update-aliases --push

# 0.8仍然可访问
# https://absespy.github.io/ABSESpy/0.8/
```

---

## 🔄 GitHub Actions配置详解

### 触发条件

```yaml
on:
  push:
    branches: [master, main, dev]  # 分支推送
```

### 部署逻辑

1. **dev分支**:
   ```bash
   mike deploy --push dev
   # 部署到 /dev/ 路径
   ```

2. **master分支**:
   ```bash
   mike deploy --push --update-aliases 0.8 latest
   # 部署到 /0.8/ 和根路径
   ```

3. **版本tag** (v0.8.0, v0.9.0等):
   ```bash
   VERSION=0.8.0
   mike deploy --push --update-aliases 0.8 latest
   # 自动从tag提取版本号
   ```

---

## ✅ 当前状态

```
✓ Mike已安装并配置
✓ GitHub Actions workflow已更新
✓ 版本管理策略已定义
✓ 双语支持已集成
✓ 准备推送代码
```

---

## 🚀 立即执行

```bash
# 推送dev分支（包含最新的文档更新）
git push origin dev

# GitHub Actions将自动：
# 1. 构建双语文档
# 2. 部署到 https://absespy.github.io/ABSESpy/dev/
# 3. 双语切换器正常工作
```

### 预期结果

访问：https://absespy.github.io/ABSESpy/dev/

您会看到：
- 🌐 语言切换器（English / 中文）
- 📚 版本选择器（dev）
- 所有16个中文页面
- 所有API文档
- 4个内置示例

---

**状态**: ✅ 所有配置完成
**下一步**: `git push origin dev`
**效果**: 专业级双语多版本文档系统！

