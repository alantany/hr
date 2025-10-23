# AI模型切换功能说明

## 功能概述

本系统现在支持在 DeepSeek 和 Google Gemini 两种 AI 模型之间切换，您可以根据需要选择不同的模型进行简历分析和筛选。

## 配置说明

### 1. API密钥配置

在 `.env` 文件中配置两个模型的 API 密钥：

```env
# DeepSeek API 配置
OPENAI_API_KEY=your_deepseek_api_key_here
OPENAI_BASE_URL=https://openrouter.ai/api/v1
OPENAI_MODEL=deepseek/deepseek-chat-v3.1:free

# Google Gemini API 配置
GOOGLE_API_KEY=***REMOVED***
GOOGLE_MODEL=gemini-2.0-flash-exp

# 默认使用的AI模型 (deepseek 或 gemini)
DEFAULT_AI_MODEL=gemini
```

### 2. 支持的 Gemini 模型

当前配置使用 `gemini-2.0-flash-exp`，这是一个实验版本，通常有更高的免费配额。

您也可以选择其他模型，例如：
- `gemini-2.5-flash` - 最新的快速版本
- `gemini-2.0-flash` - 稳定版本
- `gemini-pro-latest` - 最新的 Pro 版本

## 使用方法

### 在用户界面中切换模型

1. 打开系统页面（首页或任何功能页面）
2. 在页面顶部找到"AI模型"下拉选择器
3. 选择您想使用的模型：
   - **DeepSeek** - 使用 DeepSeek AI 模型
   - **Google Gemini** - 使用 Google Gemini AI 模型

### 功能支持

模型切换功能在以下模块中可用：

1. **简历上传与分析** - 上传简历时使用选定的模型进行智能分析
2. **简历筛选** - 根据需求筛选简历时使用选定的模型
3. **批量简历筛选** - 批量上传简历后使用选定的模型进行查询
4. **员工福利政策问答** - 查询福利政策时使用选定的模型

## 模型对比

| 特性 | DeepSeek | Google Gemini |
|------|----------|---------------|
| 响应速度 | 快 | 非常快 |
| 中文支持 | 优秀 | 优秀 |
| 免费配额 | 较高 | 中等（实验版本较高） |
| 准确性 | 高 | 高 |
| 最大上下文 | 较大 | 非常大（1M tokens） |

## 注意事项

1. **API配额限制**
   - 每个模型都有不同的免费配额限制
   - 如果遇到配额超限错误，可以切换到另一个模型
   - Gemini 实验版本（`gemini-2.0-flash-exp`）通常有更高的配额

2. **模型选择建议**
   - 日常使用：推荐使用 Gemini（更快，配额充足）
   - 需要深度分析：可以尝试两个模型并对比结果
   - 配额不足时：切换到另一个模型

3. **数据隔离**
   - 简历池和福利政策库是跨模型共享的
   - 切换模型不会丢失已上传的数据
   - 只是分析时使用的AI引擎不同

## 技术实现

### 后端支持

系统已经改造以下模块支持模型切换：
- `ai_resume_analyzer.py` - AI简历分析器
- `batch_screener.py` - 批量简历筛选器
- `benefit_screener.py` - 福利政策筛选器
- `app.py` - Flask应用主程序

### API接口

所有相关的API接口都支持 `model_type` 参数：
- `/upload` - 简历上传
- `/screen` - 简历筛选
- `/api/batch_query` - 批量查询
- `/api/benefit_query` - 福利政策查询

## 故障排除

### 问题：Gemini API 返回 429 错误

**原因**：免费配额已用完

**解决方法**：
1. 等待配额重置（通常每分钟/每天重置）
2. 切换到 DeepSeek 模型
3. 尝试使用实验版本模型（如 `gemini-2.0-flash-exp`）

### 问题：DeepSeek 连接失败

**原因**：API密钥未配置或网络问题

**解决方法**：
1. 检查 `.env` 文件中的 `OPENAI_API_KEY` 是否正确
2. 确认 `OPENAI_BASE_URL` 配置正确
3. 切换到 Gemini 模型

## 更新历史

- 2025-10-22: 初始版本，支持 DeepSeek 和 Gemini 双模型切换

