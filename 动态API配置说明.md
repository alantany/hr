# 🚀 动态 API 配置功能说明

## 📋 功能概述

系统现在支持从 `.env` 文件动态配置多个 AI 模型，页面会根据配置自动显示可用的模型选项，无需修改代码！

## ✨ 主要特性

### 1. 动态配置
- ✅ 从 `.env` 文件读取模型配置
- ✅ 页面自动显示配置的模型选项
- ✅ 支持任意数量的 AI 模型
- ✅ 无需修改代码即可添加新模型

### 2. 灵活扩展
- ✅ 支持 DeepSeek、Gemini、OpenAI 等
- ✅ 每个模型独立配置
- ✅ 自定义显示名称
- ✅ 动态验证配置完整性

## 🔧 配置方法

### 1. 基本配置格式

在 `.env` 文件中添加以下配置：

```env
# ===========================================
# 动态 AI 模型配置
# ===========================================

# 启用的 AI 模型列表（用逗号分隔）
AI_MODELS=deepseek,gemini,openai

# ===========================================
# DeepSeek 配置（硅基流动）
# ===========================================
DEEPSEEK_API_KEY=your_siliconflow_api_key_here
DEEPSEEK_BASE_URL=https://api.siliconflow.cn/v1
DEEPSEEK_MODEL=deepseek-ai/DeepSeek-V3.2-Exp
DEEPSEEK_DISPLAY_NAME=DeepSeek V3.2

# ===========================================
# Google Gemini 配置
# ===========================================
GEMINI_API_KEY=your_google_api_key_here
GEMINI_BASE_URL=https://generativelanguage.googleapis.com/v1beta
GEMINI_MODEL=gemini-2.0-flash-exp
GEMINI_DISPLAY_NAME=Google Gemini

# ===========================================
# OpenAI 配置（可选）
# ===========================================
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_BASE_URL=https://api.openai.com/v1
OPENAI_MODEL=gpt-4o-mini
OPENAI_DISPLAY_NAME=OpenAI GPT-4

# ===========================================
# 默认设置
# ===========================================
DEFAULT_AI_MODEL=deepseek
```

### 2. 配置规则

#### 必需配置项
每个模型都需要以下配置：
- `{MODEL_NAME}_API_KEY`: API 密钥
- `{MODEL_NAME}_MODEL`: 模型名称

#### 可选配置项
- `{MODEL_NAME}_BASE_URL`: API 基础 URL
- `{MODEL_NAME}_DISPLAY_NAME`: 显示名称（默认为模型名）

#### 命名规则
- 模型名必须小写
- 配置项使用大写 + 下划线格式
- 例如：`deepseek` → `DEEPSEEK_API_KEY`

## 🎯 使用示例

### 示例 1：只配置 DeepSeek
```env
AI_MODELS=deepseek
DEEPSEEK_API_KEY=sk-xxx
DEEPSEEK_MODEL=deepseek-ai/DeepSeek-V3.2-Exp
DEFAULT_AI_MODEL=deepseek
```

### 示例 2：配置多个模型
```env
AI_MODELS=deepseek,gemini,claude
DEEPSEEK_API_KEY=sk-xxx
DEEPSEEK_MODEL=deepseek-ai/DeepSeek-V3.2-Exp
GEMINI_API_KEY=AIza-xxx
GEMINI_MODEL=gemini-2.0-flash-exp
CLAUDE_API_KEY=sk-ant-xxx
CLAUDE_MODEL=claude-3-5-sonnet-20241022
DEFAULT_AI_MODEL=deepseek
```

### 示例 3：自定义显示名称
```env
AI_MODELS=deepseek,gemini
DEEPSEEK_API_KEY=sk-xxx
DEEPSEEK_MODEL=deepseek-ai/DeepSeek-V3.2-Exp
DEEPSEEK_DISPLAY_NAME=深度思考 V3.2
GEMINI_API_KEY=AIza-xxx
GEMINI_MODEL=gemini-2.0-flash-exp
GEMINI_DISPLAY_NAME=谷歌双子星
```

## 🔍 配置验证

### 自动验证
系统启动时会自动验证配置：
- ✅ 检查必需配置项是否存在
- ✅ 验证模型是否可用
- ✅ 显示配置错误信息

### 手动验证
运行测试脚本：
```bash
python test_dynamic_config.py
```

### 验证结果示例
```
🚀 动态配置功能测试
============================================================

🧪 测试配置加载
📋 配置验证结果: ✅ 通过
✅ 配置完整

🧪 测试可用模型
📊 可用模型数量: 2
   1. DeepSeek V3.2 (deepseek)
   2. Google Gemini (gemini)

🧪 测试模型配置
🔧 DeepSeek V3.2 配置:
   API Key: sk-hiqxnuveyuckekjqb...bldzpuitzq
   Base URL: https://api.siliconflow.cn/v1
   Model: deepseek-ai/DeepSeek-V3.2-Exp
   Display Name: DeepSeek V3.2
```

## 🌐 前端显示

### 自动加载
页面加载时会自动：
1. 调用 `/api/available_models` 获取模型列表
2. 动态生成下拉选项
3. 设置默认选中项

### 显示效果
```html
<select id="modelSelect">
    <option value="deepseek">DeepSeek V3.2</option>
    <option value="gemini">Google Gemini</option>
    <option value="openai">OpenAI GPT-4</option>
</select>
```

## 🛠️ 技术实现

### 后端架构
```
config_manager.py          # 配置管理器
├── AIConfigManager         # 主配置类
├── _load_available_models # 加载模型列表
├── _load_model_configs     # 加载模型配置
└── validate_config        # 验证配置

app.py                     # Flask 应用
├── /api/available_models  # 获取模型列表 API
└── 动态模型选择           # 根据用户选择创建分析器
```

### 前端实现
```javascript
// 页面加载时自动获取模型列表
async function loadAvailableModels() {
    const response = await fetch('/api/available_models');
    const data = await response.json();
    
    // 动态生成选项
    data.models.forEach(model => {
        const option = document.createElement('option');
        option.value = model.value;
        option.textContent = model.display_name;
        modelSelect.appendChild(option);
    });
}
```

## 📊 支持的模型类型

### 当前支持
- ✅ **DeepSeek** (硅基流动)
- ✅ **Google Gemini**
- ✅ **OpenAI** (GPT 系列)

### 扩展支持
可以轻松添加：
- 🔄 **Claude** (Anthropic)
- 🔄 **通义千问** (阿里云)
- 🔄 **文心一言** (百度)
- 🔄 **ChatGLM** (智谱AI)

## 🚨 注意事项

### 安全提醒
1. **API 密钥安全**
   - 不要将 `.env` 文件提交到 Git
   - 使用 `.env.example` 作为模板
   - 定期轮换 API 密钥

2. **配置验证**
   - 启动前检查配置完整性
   - 测试 API 连接性
   - 监控 API 使用量

### 性能考虑
1. **延迟初始化**
   - 配置管理器采用延迟初始化
   - 避免启动时的性能影响

2. **错误处理**
   - 配置错误时提供回退选项
   - 详细的错误信息提示

## 🎉 总结

动态 API 配置功能让系统更加灵活和可扩展：

- 🚀 **零代码添加新模型**：只需修改 `.env` 文件
- 🎯 **自动前端适配**：页面自动显示可用选项
- 🔧 **配置验证**：启动时自动检查配置完整性
- 📊 **灵活扩展**：支持任意数量的 AI 模型

现在您可以轻松地在 `.env` 文件中配置任意数量的 AI 模型，系统会自动识别并在页面上显示相应的选项！
