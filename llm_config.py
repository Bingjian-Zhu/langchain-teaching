"""
LLM模型配置管理
支持 Qwen3 和 Gemini 模型的配置和切换
"""
import os
from enum import Enum
from typing import Dict, Any
from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI

class LLMProvider(Enum):
    """支持的LLM提供商"""
    QWEN3 = "qwen3"
    GEMINI = "gemini"

class LLMConfig:
    """LLM配置类"""
    
    # 模型配置
    MODELS = {
        LLMProvider.QWEN3: {
            "class": ChatOpenAI,
            "api_key_env": "DASHSCOPE_API_KEY",
            "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1",
            "model_name": "qwen-turbo",
            "temperature": 0.7,
            "display_name": "通义千问 Qwen3"
        },
        LLMProvider.GEMINI: {
            "class": ChatGoogleGenerativeAI,
            "api_key_env": "GOOGLE_API_KEY",
            "model_name": "gemini-pro",
            "temperature": 0.7,
            "display_name": "Google Gemini"
        }
    }
    
    @classmethod
    def get_available_models(cls) -> Dict[str, str]:
        """获取可用的模型列表"""
        return {
            provider.value: config["display_name"] 
            for provider, config in cls.MODELS.items()
        }
    
    @classmethod
    def create_llm(cls, provider: LLMProvider, **kwargs) -> Any:
        """创建指定的LLM实例"""
        if provider not in cls.MODELS:
            raise ValueError(f"不支持的LLM提供商: {provider}")
        
        config = cls.MODELS[provider].copy()
        llm_class = config.pop("class")
        api_key_env = config.pop("api_key_env")
        
        # 检查API密钥
        api_key = os.getenv(api_key_env)
        if not api_key:
            raise ValueError(f"未设置API密钥环境变量: {api_key_env}")
        
        # 合并用户自定义参数
        config.update(kwargs)
        
        # 根据不同的LLM类型创建实例
        if provider == LLMProvider.QWEN3:
            return llm_class(
                api_key=api_key,
                base_url=config["base_url"],
                model=config["model_name"],
                temperature=config["temperature"]
            )
        elif provider == LLMProvider.GEMINI:
            return llm_class(
                google_api_key=api_key,
                model=config["model_name"],
                temperature=config["temperature"]
            )
    
    @classmethod
    def validate_api_keys(cls) -> Dict[str, bool]:
        """验证所有模型的API密钥是否已设置"""
        results = {}
        for provider, config in cls.MODELS.items():
            api_key_env = config["api_key_env"]
            results[provider.value] = bool(os.getenv(api_key_env))
        return results

def get_llm_by_name(provider_name: str, **kwargs) -> Any:
    """根据提供商名称获取LLM实例"""
    try:
        provider = LLMProvider(provider_name)
        return LLMConfig.create_llm(provider, **kwargs)
    except ValueError as e:
        raise ValueError(f"无法创建LLM实例: {e}")

def list_available_models() -> None:
    """列出所有可用的模型"""
    print("支持的LLM模型:")
    models = LLMConfig.get_available_models()
    api_status = LLMConfig.validate_api_keys()
    
    for provider_id, display_name in models.items():
        status = "✅" if api_status[provider_id] else "❌ (需要API密钥)"
        print(f"  {provider_id}: {display_name} {status}")

if __name__ == "__main__":
    # 测试配置
    print("LLM配置测试")
    list_available_models()
