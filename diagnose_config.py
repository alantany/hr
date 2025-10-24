#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
配置诊断工具
用于诊断配置管理器的问题
"""

import os
from dotenv import load_dotenv, find_dotenv
from config_manager import get_ai_config_manager, reload_config, is_model_available, get_model_config

print("🔍 配置诊断工具")
print("=" * 60)

# 1. 检查 .env 文件
print("\n📄 检查 .env 文件:")
env_path = find_dotenv()
print(f"   .env 文件路径: {env_path}")
print(f"   .env 文件存在: {os.path.exists(env_path)}")

# 2. 加载环境变量
load_dotenv(env_path, override=True)

# 3. 检查环境变量
print("\n🔐 检查环境变量:")
env_vars = ['AI_MODELS', 'DEFAULT_AI_MODEL']
for var in env_vars:
    value = os.getenv(var)
    print(f"   {var}: {value}")

# 4. 检查各个模型的配置
print("\n📊 检查模型配置:")
models = os.getenv('AI_MODELS', '').split(',')
for model in models:
    model = model.strip()
    if not model:
        continue
    print(f"\n   {model.upper()}:")
    print(f"      API_KEY: {os.getenv(f'{model.upper()}_API_KEY', 'NOT_FOUND')[:20]}...")
    print(f"      BASE_URL: {os.getenv(f'{model.upper()}_BASE_URL', 'NOT_FOUND')}")
    print(f"      MODEL: {os.getenv(f'{model.upper()}_MODEL', 'NOT_FOUND')}")
    print(f"      DISPLAY_NAME: {os.getenv(f'{model.upper()}_DISPLAY_NAME', 'NOT_FOUND')}")

# 5. 检查配置管理器
print("\n🔧 检查配置管理器:")
config_manager = reload_config()
print(f"   可用模型列表: {config_manager.available_models}")
print(f"   已配置模型: {list(config_manager.model_configs.keys())}")
print(f"   默认模型: {config_manager.get_default_model()}")

# 6. 检查各个模型的可用性
print("\n✅ 检查模型可用性:")
for model in models:
    model = model.strip()
    if not model:
        continue
    available = is_model_available(model)
    config = get_model_config(model)
    print(f"   {model}: {'✅ 可用' if available else '❌ 不可用'}")
    if config:
        print(f"      配置完整: ✅")
    else:
        print(f"      配置完整: ❌")

print("\n" + "=" * 60)
print("✅ 诊断完成")

