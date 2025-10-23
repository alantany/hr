# 🚨 API 密钥泄露应急处理指南

## ⚠️ 当前状况

已发现以下 API 密钥在 Git 历史记录中泄露：
1. **Google Gemini API Key**: `AIzaSyC0VL9qmxzQ8oMVFfbLnWyE0FY6x8NGyDc`
2. **硅基流动 API Key**: `sk-hiqxnuveyuckekjqbtdgbetspfjhxahdesakehbldzpuitzq`

## 🔴 立即行动（优先级最高）

### 1. 撤销 Google API 密钥

**步骤：**
1. 访问 [Google Cloud Console](https://console.cloud.google.com/)
2. 进入 "APIs & Services" → "Credentials"
3. 找到泄露的 API Key
4. 点击删除或禁用
5. 创建新的 API Key
6. 更新本地 `.env` 文件

### 2. 重置硅基流动 API 密钥

**步骤：**
1. 访问 [硅基流动控制台](https://siliconflow.cn/account)
2. 进入 API 密钥管理
3. 删除或重置泄露的密钥
4. 生成新的 API Key
5. 更新本地 `.env` 文件

## 🛠️ 清理 Git 历史记录

### 方案 A：使用 BFG Repo-Cleaner（推荐，简单快速）

```bash
# 1. 安装 BFG
brew install bfg

# 2. 创建要替换的密钥列表
cat > passwords.txt << 'EOF'
AIzaSyC0VL9qmxzQ8oMVFfbLnWyE0FY6x8NGyDc
sk-hiqxnuveyuckekjqbtdgbetspfjhxahdesakehbldzpuitzq
EOF

# 3. 清理 Git 历史
bfg --replace-text passwords.txt

# 4. 清理和压缩仓库
git reflog expire --expire=now --all
git gc --prune=now --aggressive

# 5. 强制推送（⚠️ 危险操作）
git push --force
```

### 方案 B：使用 git filter-repo（更彻底）

```bash
# 1. 安装 git-filter-repo
pip install git-filter-repo

# 2. 创建替换配置
cat > replacements.txt << 'EOF'
AIzaSyC0VL9qmxzQ8oMVFfbLnWyE0FY6x8NGyDc==>your_google_api_key_here
sk-hiqxnuveyuckekjqbtdgbetspfjhxahdesakehbldzpuitzq==>your_siliconflow_api_key_here
EOF

# 3. 执行清理
git filter-repo --replace-text replacements.txt

# 4. 重新添加远程仓库
git remote add origin https://github.com/alantany/hr.git

# 5. 强制推送
git push --force --all
git push --force --tags
```

### 方案 C：删除仓库重新创建（最彻底，最简单）

**适用场景：** 如果这是个人项目，没有其他协作者

```bash
# 1. 在 GitHub 上删除仓库
#    访问: https://github.com/alantany/hr/settings
#    滚动到底部，删除仓库

# 2. 清理本地 Git 历史
rm -rf .git
git init
git add .
git commit -m "Initial commit (cleaned)"

# 3. 创建新的 GitHub 仓库
#    访问: https://github.com/new

# 4. 推送到新仓库
git remote add origin https://github.com/alantany/hr.git
git branch -M main
git push -u origin main
```

## 📋 推荐执行顺序

### 第一步：立即撤销密钥（5分钟内完成）
1. ✅ 撤销 Google API Key
2. ✅ 重置硅基流动 API Key
3. ✅ 更新本地 `.env` 文件
4. ✅ 测试新密钥是否工作

### 第二步：清理 Git 历史（可选）
根据您的情况选择：
- **个人项目** → 推荐方案 C（删除重建）
- **需要保留历史** → 推荐方案 A（BFG）
- **需要彻底清理** → 推荐方案 B（filter-repo）

## ⚠️ 重要警告

### 使用 force push 的风险
- ⚠️ 会重写 Git 历史
- ⚠️ 其他协作者需要重新克隆仓库
- ⚠️ 可能影响依赖此仓库的其他项目

### 如果有协作者
通知他们：
```bash
# 其他协作者需要执行
git fetch origin
git reset --hard origin/main
```

## 🔒 预防措施（未来）

### 1. 使用 git-secrets
```bash
# 安装
brew install git-secrets

# 配置
cd /path/to/your/repo
git secrets --install
git secrets --register-aws
git secrets --add 'AIza[0-9A-Za-z_-]{35}'
git secrets --add 'sk-[a-zA-Z0-9]{48,}'
```

### 2. 添加 pre-commit hook
创建 `.git/hooks/pre-commit`:
```bash
#!/bin/bash
# 检查是否包含 API 密钥模式
if git diff --cached | grep -E 'AIza[0-9A-Za-z_-]{35}|sk-[a-zA-Z0-9]{48,}'; then
    echo "错误: 检测到可能的 API 密钥！"
    echo "请移除后再提交。"
    exit 1
fi
```

### 3. 使用 GitHub Secret Scanning
- GitHub 会自动扫描公开仓库
- 发现密钥会发送警告邮件
- 及时响应警告

## 📞 需要帮助？

如果您不确定如何操作，我可以帮您：
1. 执行 BFG 清理命令
2. 重建仓库
3. 验证清理结果

**重要提示：** 无论选择哪种方案，第一步必须是撤销泄露的 API 密钥！

