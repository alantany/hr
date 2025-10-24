#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
动态配置功能测试脚本
测试从 .env 文件动态加载和配置多个 AI 模型
"""

import os
import sys
from dotenv import load_dotenv
from config_manager import get_ai_config_manager

def print_separator(title):
    """打印分隔线"""
    print(f"\n{'='*60}")
    print(f"🧪 {title}")
    print('='*60)

def test_config_loading():
    """测试配置加载"""
    print_separator("测试配置加载")
    
    # 加载环境变量
    load_dotenv()
    
    # 获取配置管理器
    config_manager = get_ai_config_manager()
    
    # 验证配置
    is_valid, errors = config_manager.validate_config()
    
    print(f"📋 配置验证结果: {'✅ 通过' if is_valid else '❌ 失败'}")
    
    if errors:
        print("❌ 配置错误:")
        for error in errors:
            print(f"   - {error}")
    else:
        print("✅ 配置完整")
    
    return is_valid, config_manager

def test_available_models(config_manager):
    """测试可用模型"""
    print_separator("测试可用模型")
    
    models = config_manager.get_available_models()
    print(f"📊 可用模型数量: {len(models)}")
    
    for i, model in enumerate(models, 1):
        print(f"   {i}. {model['display_name']} ({model['value']})")
        print(f"      模型名称: {model['model_name']}")
    
    return models

def test_model_configs(config_manager):
    """测试模型配置"""
    print_separator("测试模型配置")
    
    for model in config_manager.get_available_models():
        model_name = model['value']
        config = config_manager.get_model_config(model_name)
        
        print(f"🔧 {model['display_name']} 配置:")
        print(f"   API Key: {config['api_key'][:20]}...{config['api_key'][-10:] if config['api_key'] else 'None'}")
        print(f"   Base URL: {config['base_url']}")
        print(f"   Model: {config['model']}")
        print(f"   Display Name: {config['display_name']}")
        print()

def test_model_availability(config_manager):
    """测试模型可用性"""
    print_separator("测试模型可用性")
    
    # 测试已配置的模型
    for model in config_manager.get_available_models():
        model_name = model['value']
        is_available = config_manager.is_model_available(model_name)
        print(f"✅ {model['display_name']}: {'可用' if is_available else '不可用'}")
    
    # 测试不存在的模型
    test_models = ['nonexistent', 'invalid', 'test']
    for model in test_models:
        is_available = config_manager.is_model_available(model)
        print(f"❌ {model}: {'可用' if is_available else '不可用'}")

def test_default_model(config_manager):
    """测试默认模型"""
    print_separator("测试默认模型")
    
    default_model = config_manager.get_default_model()
    print(f"🎯 默认模型: {default_model}")
    
    is_available = config_manager.is_model_available(default_model)
    print(f"📊 默认模型可用性: {'✅ 可用' if is_available else '❌ 不可用'}")

def test_config_summary(config_manager):
    """测试配置摘要"""
    print_separator("配置摘要")
    
    summary = config_manager.get_config_summary()
    
    print(f"📊 配置摘要:")
    print(f"   可用模型列表: {summary['available_models']}")
    print(f"   已配置模型: {summary['configured_models']}")
    print(f"   默认模型: {summary['default_model']}")
    print(f"   模型数量: {summary['model_count']}")
    
    print(f"\n📋 模型详情:")
    for model in summary['models']:
        print(f"   - {model['display_name']} ({model['value']})")

def create_sample_env():
    """创建示例 .env 文件"""
    print_separator("创建示例配置")
    
    sample_env_content = """# ===========================================
# 动态 AI 模型配置示例
# ===========================================

# 启用的 AI 模型列表（用逗号分隔）
AI_MODELS=deepseek,gemini

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
# 默认设置
# ===========================================
DEFAULT_AI_MODEL=deepseek
"""
    
    with open('.env.sample', 'w', encoding='utf-8') as f:
        f.write(sample_env_content)
    
    print("✅ 已创建 .env.sample 示例文件")
    print("💡 您可以复制此文件为 .env 并填入真实的 API 密钥")

def main():
    """主测试函数"""
    print("🚀 动态配置功能测试")
    print("=" * 60)
    
    try:
        # 1. 测试配置加载
        is_valid, config_manager = test_config_loading()
        
        if not is_valid:
            print("\n❌ 配置验证失败，请检查 .env 文件")
            create_sample_env()
            return
        
        # 2. 测试可用模型
        models = test_available_models(config_manager)
        
        if not models:
            print("\n❌ 没有可用的模型，请检查配置")
            create_sample_env()
            return
        
        # 3. 测试模型配置
        test_model_configs(config_manager)
        
        # 4. 测试模型可用性
        test_model_availability(config_manager)
        
        # 5. 测试默认模型
        test_default_model(config_manager)
        
        # 6. 测试配置摘要
        test_config_summary(config_manager)
        
        print_separator("测试完成")
        print("✅ 动态配置功能测试通过！")
        print("🎉 系统已支持从 .env 文件动态加载多个 AI 模型")
        
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()
