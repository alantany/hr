#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
API 测试脚本
测试 DeepSeek 和 Gemini API 的可用性
"""

import os
from dotenv import load_dotenv
from openai import OpenAI
import google.generativeai as genai

# 加载环境变量
load_dotenv()

def print_separator(title=""):
    """打印分隔线"""
    if title:
        print(f"\n{'='*60}")
        print(f"  {title}")
        print('='*60)
    else:
        print('-'*60)

def test_deepseek_openrouter():
    """测试 DeepSeek (通过 OpenRouter)"""
    print_separator("🧪 测试 1: DeepSeek (OpenRouter)")
    
    api_key = os.getenv('OPENAI_API_KEY')
    base_url = os.getenv('OPENAI_BASE_URL')
    model = os.getenv('OPENAI_MODEL')
    
    print(f"📋 配置信息:")
    print(f"   API Key: {api_key[:20]}...{api_key[-10:] if api_key else 'None'}")
    print(f"   Base URL: {base_url}")
    print(f"   Model: {model}")
    
    if not api_key:
        print("❌ 错误: OPENAI_API_KEY 未配置")
        return False
    
    try:
        print("\n🔄 发送测试请求...")
        client = OpenAI(
            api_key=api_key,
            base_url=base_url
        )
        
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "user", "content": "你好，请用一句话介绍你自己"}
            ],
            max_tokens=100,
            temperature=0.7
        )
        
        result = response.choices[0].message.content
        print("✅ DeepSeek API 测试成功！")
        print(f"📝 响应: {result[:150]}...")
        return True
        
    except Exception as e:
        error_msg = str(e)
        print(f"❌ DeepSeek API 测试失败!")
        print(f"📛 错误信息: {error_msg[:200]}")
        
        # 分析错误类型
        if "429" in error_msg:
            print("\n💡 诊断:")
            print("   - 错误类型: 速率限制 (Rate Limit)")
            print("   - 原因: OpenRouter 的免费 DeepSeek 模型被限流")
            print("   - 建议: ")
            print("     1. 等待几分钟后重试")
            print("     2. 注册 OpenRouter 账号并添加自己的 API Key")
            print("     3. 切换到 Gemini 模型")
            print("     4. 使用其他免费模型（如 Llama）")
        elif "401" in error_msg:
            print("\n💡 诊断:")
            print("   - 错误类型: 认证失败")
            print("   - 原因: API Key 无效或已过期")
            print("   - 建议: 获取新的 OpenRouter API Key")
        
        return False

def test_gemini():
    """测试 Google Gemini"""
    print_separator("🧪 测试 2: Google Gemini")
    
    api_key = os.getenv('GOOGLE_API_KEY')
    base_url = os.getenv('GOOGLE_BASE_URL')
    model_name = os.getenv('GOOGLE_MODEL')
    
    print(f"📋 配置信息:")
    print(f"   API Key: {api_key[:20]}...{api_key[-10:] if api_key else 'None'}")
    print(f"   Base URL: {base_url}")
    print(f"   Model: {model_name}")
    
    if not api_key:
        print("❌ 错误: GOOGLE_API_KEY 未配置")
        return False
    
    try:
        print("\n🔄 发送测试请求...")
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel(model_name)
        
        response = model.generate_content(
            "你好，请用一句话介绍你自己",
            generation_config=genai.types.GenerationConfig(
                max_output_tokens=100,
                temperature=0.7,
            )
        )
        
        result = response.text
        print("✅ Gemini API 测试成功！")
        print(f"📝 响应: {result[:150]}...")
        return True
        
    except Exception as e:
        error_msg = str(e)
        print(f"❌ Gemini API 测试失败!")
        print(f"📛 错误信息: {error_msg[:200]}")
        
        # 分析错误类型
        if "429" in error_msg or "quota" in error_msg.lower():
            print("\n💡 诊断:")
            print("   - 错误类型: 配额超限")
            print("   - 原因: Gemini 免费配额已用完")
            print("   - 建议: 等待配额重置或升级到付费版")
        elif "503" in error_msg or "timeout" in error_msg.lower():
            print("\n💡 诊断:")
            print("   - 错误类型: 网络连接问题")
            print("   - 原因: 无法连接到 Google API 服务")
            print("   - 建议: ")
            print("     1. 检查网络连接")
            print("     2. 使用 VPN（如果在国内）")
            print("     3. 稍后重试")
        
        return False

def list_available_openrouter_models():
    """列出 OpenRouter 可用的免费模型"""
    print_separator("📋 OpenRouter 推荐的免费模型")
    
    free_models = [
        ("meta-llama/llama-3.1-8b-instruct:free", "Llama 3.1 8B (推荐)"),
        ("meta-llama/llama-3.2-3b-instruct:free", "Llama 3.2 3B"),
        ("google/gemma-2-9b-it:free", "Gemma 2 9B"),
        ("mistralai/mistral-7b-instruct:free", "Mistral 7B"),
        ("deepseek/deepseek-chat-v3.1:free", "DeepSeek Chat (当前被限流)"),
    ]
    
    print("\n可选的免费模型列表:")
    for model_id, description in free_models:
        print(f"  • {model_id}")
        print(f"    {description}\n")
    
    print("💡 如何切换模型:")
    print("   1. 编辑 .env 文件")
    print("   2. 修改 OPENAI_MODEL=模型ID")
    print("   3. 重启服务或等待热重载")

def test_alternative_model():
    """测试替代模型 (Llama 3.1)"""
    print_separator("🧪 测试 3: 替代方案 - Llama 3.1")
    
    api_key = os.getenv('OPENAI_API_KEY')
    base_url = os.getenv('OPENAI_BASE_URL')
    alternative_model = "meta-llama/llama-3.1-8b-instruct:free"
    
    print(f"📋 测试模型: {alternative_model}")
    
    if not api_key:
        print("❌ 错误: API Key 未配置")
        return False
    
    try:
        print("\n🔄 发送测试请求...")
        client = OpenAI(
            api_key=api_key,
            base_url=base_url
        )
        
        response = client.chat.completions.create(
            model=alternative_model,
            messages=[
                {"role": "user", "content": "你好，请用中文简单介绍你自己"}
            ],
            max_tokens=100,
            temperature=0.7
        )
        
        result = response.choices[0].message.content
        print("✅ Llama 3.1 模型测试成功！")
        print(f"📝 响应: {result[:150]}...")
        
        print("\n💡 建议:")
        print("   这个模型可用！可以在 .env 中将 OPENAI_MODEL 改为:")
        print(f"   OPENAI_MODEL={alternative_model}")
        
        return True
        
    except Exception as e:
        print(f"❌ 测试失败: {str(e)[:200]}")
        return False

def main():
    """主函数"""
    print("\n" + "="*60)
    print("  🚀 AI 模型 API 测试工具")
    print("="*60)
    print("\n正在读取 .env 配置...")
    
    # 检查 .env 文件
    if not os.path.exists('.env'):
        print("❌ 错误: .env 文件不存在！")
        return
    
    print("✅ .env 文件找到\n")
    
    # 测试统计
    results = {
        'deepseek': False,
        'gemini': False,
        'llama': False
    }
    
    # 执行测试
    results['deepseek'] = test_deepseek_openrouter()
    print("\n")
    
    results['gemini'] = test_gemini()
    print("\n")
    
    results['llama'] = test_alternative_model()
    print("\n")
    
    list_available_openrouter_models()
    
    # 总结
    print_separator("📊 测试总结")
    print(f"\n测试结果:")
    print(f"  DeepSeek (OpenRouter): {'✅ 可用' if results['deepseek'] else '❌ 不可用'}")
    print(f"  Gemini (Google):       {'✅ 可用' if results['gemini'] else '❌ 不可用'}")
    print(f"  Llama 3.1 (替代):      {'✅ 可用' if results['llama'] else '❌ 不可用'}")
    
    print("\n🎯 推荐方案:")
    if results['gemini']:
        print("  ✨ 使用 Gemini 模型（在界面选择 Gemini）")
    elif results['llama']:
        print("  ✨ 使用 Llama 3.1 模型")
        print("     1. 编辑 .env 文件")
        print("     2. 修改: OPENAI_MODEL=meta-llama/llama-3.1-8b-instruct:free")
        print("     3. 服务会自动重载")
    elif results['deepseek']:
        print("  ✨ DeepSeek 可用（在界面选择 DeepSeek）")
    else:
        print("  ⚠️  所有模型都不可用，需要:")
        print("     1. 检查网络连接")
        print("     2. 获取有效的 API Key")
        print("     3. 等待限流恢复")
    
    print("\n" + "="*60)
    print("  测试完成！")
    print("="*60 + "\n")

if __name__ == "__main__":
    main()

