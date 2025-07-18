"""
LLM模型设置和选择工具
帮助用户配置和选择合适的LLM模型
"""
import os
import getpass
from llm_config import LLMConfig, LLMProvider, list_available_models

def setup_api_keys():
    """交互式设置API密钥"""
    print("🔧 LLM模型配置向导")
    print("="*50)
    
    # 检查当前API密钥状态
    api_status = LLMConfig.validate_api_keys()
    
    print("当前API密钥状态:")
    for provider_id, has_key in api_status.items():
        status = "✅ 已设置" if has_key else "❌ 未设置"
        display_name = LLMConfig.MODELS[LLMProvider(provider_id)]['display_name']
        print(f"  {display_name}: {status}")
    
    print("\n" + "="*50)
    
    # 为未设置的API密钥提供设置选项
    for provider_id, has_key in api_status.items():
        if not has_key:
            provider = LLMProvider(provider_id)
            config = LLMConfig.MODELS[provider]
            display_name = config['display_name']
            api_key_env = config['api_key_env']
            
            choice = input(f"\n是否设置 {display_name} 的API密钥? (y/n): ").strip().lower()
            if choice == 'y':
                api_key = getpass.getpass(f"请输入 {display_name} 的API密钥: ")
                if api_key.strip():
                    os.environ[api_key_env] = api_key.strip()
                    print(f"✅ {display_name} API密钥已设置")
                else:
                    print(f"❌ 未设置 {display_name} API密钥")

def choose_llm_model():
    """选择LLM模型"""
    print("\n🤖 选择LLM模型")
    print("="*30)
    
    # 显示可用模型
    list_available_models()
    
    # 获取可用的模型（有API密钥的）
    api_status = LLMConfig.validate_api_keys()
    available_models = [
        provider_id for provider_id, has_key in api_status.items() 
        if has_key
    ]
    
    if not available_models:
        print("\n❌ 没有可用的模型，请先设置API密钥")
        return None
    
    print(f"\n可选择的模型: {', '.join(available_models)}")
    
    while True:
        choice = input("请选择模型 (输入模型ID): ").strip().lower()
        if choice in available_models:
            return choice
        else:
            print(f"❌ 无效选择，请选择: {', '.join(available_models)}")

def main():
    """主函数"""
    print("🎓 智能教学系统 - LLM配置工具")
    print("="*60)
    
    # 设置API密钥
    setup_api_keys()
    
    # 选择模型
    selected_model = choose_llm_model()
    
    if selected_model:
        print(f"\n✅ 已选择模型: {LLMConfig.MODELS[LLMProvider(selected_model)]['display_name']}")
        print(f"模型ID: {selected_model}")
        
        # 保存选择到环境变量
        os.environ["SELECTED_LLM"] = selected_model
        print("💾 模型选择已保存到环境变量")
        
        return selected_model
    else:
        print("\n❌ 未选择任何模型")
        return None

if __name__ == "__main__":
    main()
