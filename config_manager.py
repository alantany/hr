"""
动态 AI 模型配置管理器
支持从 .env 文件动态读取和配置多个 AI 模型
"""

import os
from typing import Dict, List, Optional, Tuple


class AIConfigManager:
    """AI 模型配置管理器"""
    
    def __init__(self):
        self.available_models = self._load_available_models()
        self.model_configs = self._load_model_configs()
        self.default_model = os.getenv('DEFAULT_AI_MODEL', 'deepseek')
    
    def _load_available_models(self) -> List[str]:
        """从环境变量加载可用的模型列表"""
        models_str = os.getenv('AI_MODELS', 'deepseek,gemini')
        return [model.strip().lower() for model in models_str.split(',') if model.strip()]
    
    def _load_model_configs(self) -> Dict[str, Dict[str, str]]:
        """加载所有模型的配置"""
        configs = {}
        
        for model in self.available_models:
            config = {
                'api_key': os.getenv(f'{model.upper()}_API_KEY'),
                'base_url': os.getenv(f'{model.upper()}_BASE_URL'),
                'model': os.getenv(f'{model.upper()}_MODEL'),
                'display_name': os.getenv(f'{model.upper()}_DISPLAY_NAME', model.title())
            }
            
            # 检查必要配置是否存在
            if config['api_key'] and config['model']:
                configs[model] = config
            else:
                missing = []
                if not config['api_key']:
                    missing.append('API_KEY')
                if not config['model']:
                    missing.append('MODEL')
                print(f"⚠️  警告: {model} 模型配置不完整，缺少: {', '.join(missing)}")
        
        return configs
    
    def get_available_models(self) -> List[Dict[str, str]]:
        """获取可用的模型列表，用于前端显示"""
        models = []
        for model, config in self.model_configs.items():
            models.append({
                'value': model,
                'display_name': config['display_name'],
                'model_name': config['model']
            })
        return models
    
    def get_model_config(self, model_name: str) -> Optional[Dict[str, str]]:
        """获取指定模型的配置"""
        return self.model_configs.get(model_name.lower())
    
    def is_model_available(self, model_name: str) -> bool:
        """检查模型是否可用"""
        return model_name.lower() in self.model_configs
    
    def get_default_model(self) -> str:
        """获取默认模型"""
        if self.is_model_available(self.default_model):
            return self.default_model
        elif self.model_configs:
            return list(self.model_configs.keys())[0]
        else:
            return 'deepseek'
    
    def validate_config(self) -> Tuple[bool, List[str]]:
        """验证配置完整性"""
        errors = []
        
        if not self.available_models:
            errors.append("未配置任何 AI 模型 (AI_MODELS)")
        
        if not self.model_configs:
            errors.append("没有可用的模型配置")
        
        for model, config in self.model_configs.items():
            if not config['api_key']:
                errors.append(f"{model} 缺少 API_KEY")
            if not config['model']:
                errors.append(f"{model} 缺少 MODEL")
        
        return len(errors) == 0, errors
    
    def get_config_summary(self) -> Dict:
        """获取配置摘要"""
        return {
            'available_models': self.available_models,
            'configured_models': list(self.model_configs.keys()),
            'default_model': self.get_default_model(),
            'model_count': len(self.model_configs),
            'models': self.get_available_models()
        }


# 全局配置管理器实例（延迟初始化）
_config_manager = None


def get_ai_config_manager() -> AIConfigManager:
    """获取全局配置管理器实例"""
    global _config_manager
    if _config_manager is None:
        _config_manager = AIConfigManager()
    return _config_manager


def reload_config():
    """重新加载配置（用于开发环境）"""
    global _config_manager
    _config_manager = None
    
    # 重新加载环境变量
    from dotenv import load_dotenv
    load_dotenv(override=True)
    
    return get_ai_config_manager()


def get_available_models() -> List[Dict[str, str]]:
    """获取可用模型列表（便捷函数）"""
    return get_ai_config_manager().get_available_models()


def get_model_config(model_name: str) -> Optional[Dict[str, str]]:
    """获取模型配置（便捷函数）"""
    return get_ai_config_manager().get_model_config(model_name)


def is_model_available(model_name: str) -> bool:
    """检查模型是否可用（便捷函数）"""
    return get_ai_config_manager().is_model_available(model_name)
