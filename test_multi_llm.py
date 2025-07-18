"""
测试多LLM模型支持功能
验证Qwen3和Gemini模型的配置和切换功能
"""
import os
from llm_config import LLMConfig, LLMProvider, list_available_models

def test_llm_config():
    """测试LLM配置功能"""
    print("🧪 测试多LLM模型支持功能")
    print("="*50)
    
    # 1. 测试模型列表
    print("1. 支持的模型列表:")
    models = LLMConfig.get_available_models()
    for provider_id, display_name in models.items():
        print(f"   - {provider_id}: {display_name}")
    
    # 2. 测试API密钥验证
    print("\n2. API密钥状态检查:")
    api_status = LLMConfig.validate_api_keys()
    for provider_id, has_key in api_status.items():
        status = "✅ 已设置" if has_key else "❌ 未设置"
        display_name = LLMConfig.MODELS[LLMProvider(provider_id)]['display_name']
        print(f"   - {display_name}: {status}")
    
    # 3. 测试可用模型
    print("\n3. 当前可用的模型:")
    available_models = [
        provider_id for provider_id, has_key in api_status.items() 
        if has_key
    ]
    
    if available_models:
        for model in available_models:
            display_name = LLMConfig.MODELS[LLMProvider(model)]['display_name']
            print(f"   ✅ {display_name} ({model})")
    else:
        print("   ❌ 没有可用的模型，需要设置API密钥")
    
    # 4. 测试模型创建（仅对有API密钥的模型）
    print("\n4. 模型创建测试:")
    for model in available_models:
        try:
            from llm_config import get_llm_by_name
            llm = get_llm_by_name(model)
            display_name = LLMConfig.MODELS[LLMProvider(model)]['display_name']
            print(f"   ✅ {display_name} 模型创建成功")
        except Exception as e:
            print(f"   ❌ {model} 模型创建失败: {e}")
    
    return available_models

def demo_llm_usage(available_models):
    """演示LLM使用"""
    if not available_models:
        print("\n❌ 没有可用的模型进行演示")
        return
    
    print(f"\n🎯 LLM功能演示 (使用 {available_models[0]})")
    print("="*50)
    
    try:
        from teaching_system import IntelligentTutoringSystem
        
        # 使用第一个可用模型创建系统
        system = IntelligentTutoringSystem(llm_provider=available_models[0])
        
        # 测试简单的问答
        test_question = "什么是2+3？"
        test_answer = "5"
        knowledge_points = ["基础加法"]
        
        print(f"测试问题: {test_question}")
        print(f"学生答案: {test_answer}")
        print("AI评分中...")
        
        result = system.grade_answer(test_question, "5", test_answer, knowledge_points)
        
        print(f"评分结果: {result['score']}/10")
        print(f"分析: {result['analysis']}")
        
        print("\n✅ LLM功能测试成功！")
        
    except Exception as e:
        print(f"❌ LLM功能测试失败: {e}")

if __name__ == "__main__":
    # 运行测试
    available_models = test_llm_config()
    demo_llm_usage(available_models)
    
    print("\n" + "="*50)
    print("🎉 多LLM支持功能测试完成！")
    print("\n💡 使用说明:")
    print("1. 运行 python main_system.py 启动完整系统")
    print("2. 系统会自动检测可用的LLM模型")
    print("3. 如果有多个模型可用，系统会让你选择")
    print("4. 支持在Qwen3和Gemini之间切换")
