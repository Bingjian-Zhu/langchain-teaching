"""
智能教学系统主程序
整合题库管理、智能出题、自动阅卷、个性化辅导等功能
"""
import os
import getpass
from teaching_system import IntelligentTutoringSystem, AdminTools
from llm_config import LLMConfig, LLMProvider, list_available_models

def setup_api_keys_and_model():
    """设置API密钥并选择LLM模型"""
    print("🔧 配置LLM模型")
    
    # 检查已有的API密钥
    api_status = LLMConfig.validate_api_keys()
    available_models = []
    
    # 检查Qwen3
    if not api_status.get('qwen3', False):
        if not os.environ.get("DASHSCOPE_API_KEY"):
            choice = input("是否设置 Qwen3 (通义千问) API密钥? (y/n): ").strip().lower()
            if choice == 'y':
                api_key = getpass.getpass("请输入DashScope API密钥: ")
                if api_key.strip():
                    os.environ["DASHSCOPE_API_KEY"] = api_key.strip()
                    available_models.append('qwen3')
    else:
        available_models.append('qwen3')
    
    # 检查国内Gemini
    if not api_status.get('gemini_openai', False):
        if not os.environ.get("GOOGLE_API_KEY"):
            choice = input("是否设置 Gemini API密钥? (y/n): ").strip().lower()
            if choice == 'y':
                api_key = getpass.getpass("请输入Google API密钥: ")
                if api_key.strip():
                    os.environ["GOOGLE_API_KEY"] = api_key.strip()
                    available_models.append('gemini_openai')
    else:
        available_models.append('gemini_openai')

    # 检查海外Gemini
    if not api_status.get('gemini', False):
        if not os.environ.get("GOOGLE_API_KEY"):
            choice = input("是否设置 Gemini API密钥? (y/n): ").strip().lower()
            if choice == 'y':
                api_key = getpass.getpass("请输入Google API密钥: ")
                if api_key.strip():
                    os.environ["GOOGLE_API_KEY"] = api_key.strip()
                    available_models.append('gemini')
    else:
        available_models.append('gemini')
    
    # 选择模型
    if len(available_models) == 0:
        print("❌ 没有可用的模型，请至少设置一个API密钥")
        return None
    elif len(available_models) == 1:
        selected_model = available_models[0]
        print(f"✅ 自动选择唯一可用模型: {LLMConfig.MODELS[LLMProvider(selected_model)]['display_name']}")
    else:
        print("\n可用的模型:")
        for i, model in enumerate(available_models, 1):
            display_name = LLMConfig.MODELS[LLMProvider(model)]['display_name']
            print(f"  {i}. {display_name} ({model})")
        
        while True:
            try:
                choice = int(input("请选择模型 (输入数字): ").strip())
                if 1 <= choice <= len(available_models):
                    selected_model = available_models[choice - 1]
                    break
                else:
                    print("❌ 无效选择，请重新输入")
            except ValueError:
                print("❌ 请输入有效数字")
    
    return selected_model

def init_sample_data(admin_tools: AdminTools):
    """初始化示例题目数据"""
    sample_questions = [
        {
            'subject': '数学',
            'difficulty': '中等',
            'question': '求解方程 2x + 5 = 13 中 x 的值',
            'standard_answer': 'x = 4',
            'knowledge_points': ['一元一次方程', '代数运算'],
            'created_by': '系统管理员'
        },
        {
            'subject': '数学',
            'difficulty': '中等',
            'question': '计算 (3 + 4) × 2 - 5 的结果',
            'standard_answer': '9',
            'knowledge_points': ['四则运算', '运算顺序'],
            'created_by': '系统管理员'
        },
        {
            'subject': '数学',
            'difficulty': '简单',
            'question': '一个正方形的边长是5cm，求它的面积',
            'standard_answer': '25平方厘米',
            'knowledge_points': ['几何图形', '面积计算'],
            'created_by': '系统管理员'
        },
        {
            'subject': '数学',
            'difficulty': '困难',
            'question': '已知函数 f(x) = x² - 4x + 3，求 f(x) 的最小值',
            'standard_answer': '最小值为 -1，当 x = 2 时取得',
            'knowledge_points': ['二次函数', '函数最值'],
            'created_by': '系统管理员'
        },
        {
            'subject': '数学',
            'difficulty': '中等',
            'question': '在直角三角形中，如果一个锐角为30°，斜边长为10，求对边的长度',
            'standard_answer': '5',
            'knowledge_points': ['三角函数', '直角三角形'],
            'created_by': '系统管理员'
        },
        {
            'subject': '语文',
            'difficulty': '中等',
            'question': '请解释"春风得意马蹄疾，一日看尽长安花"这句诗的含义',
            'standard_answer': '这句诗出自孟郊的《登科后》，表达了诗人考中进士后的喜悦心情，形容心情愉快时做事顺利迅速的样子',
            'knowledge_points': ['古诗词理解', '文学鉴赏'],
            'created_by': '系统管理员'
        },
        {
            'subject': '语文',
            'difficulty': '简单',
            'question': '请写出"静夜思"这首诗的作者',
            'standard_answer': '李白',
            'knowledge_points': ['古诗词', '文学常识'],
            'created_by': '系统管理员'
        }
    ]
    
    print("正在初始化示例题目...")
    admin_tools.batch_add_questions(sample_questions)
    print(f"已添加 {len(sample_questions)} 道示例题目")

def admin_menu(admin_tools: AdminTools):
    """管理员菜单"""
    while True:
        print("\n=== 管理员功能菜单 ===")
        print("1. 添加题目")
        print("2. 查看题库")
        print("3. 初始化示例数据")
        print("4. 返回主菜单")
        
        choice = input("请选择功能 (1-4): ").strip()
        
        if choice == '1':
            admin_tools.add_question_interactive()
        elif choice == '2':
            subject = input("查看指定科目 (留空查看全部): ").strip()
            admin_tools.view_questions(subject if subject else None)
        elif choice == '3':
            init_sample_data(admin_tools)
        elif choice == '4':
            break
        else:
            print("无效选择，请重新输入")

def student_menu(system: IntelligentTutoringSystem):
    """学生菜单"""
    while True:
        print("\n=== 学生功能菜单 ===")
        print("1. 开始考试")
        print("2. 返回主菜单")
        
        choice = input("请选择功能 (1-2): ").strip()
        
        if choice == '1':
            student_name = input("请输入你的姓名: ").strip()
            if not student_name:
                print("姓名不能为空")
                continue
                
            print("\n可选科目：数学、语文、英语、物理、化学")
            subject = input("请选择考试科目: ").strip()
            if not subject:
                print("科目不能为空")
                continue
                
            grade = input("请输入年级 (可选): ").strip()
            
            # 开始考试
            exam_id = system.conduct_exam(student_name, subject, grade)
            
            if exam_id:
                # 生成个性化辅导报告
                print("\n" + "="*60)
                report = system.generate_final_report(exam_id)
                print(report)
                print("="*60)
                
                # 询问是否保存报告
                save_report = input("\n是否将报告保存到文件? (y/n): ").strip().lower()
                if save_report == 'y':
                    filename = f"tutoring_report_{exam_id}_{student_name}.txt"
                    with open(filename, 'w', encoding='utf-8') as f:
                        f.write(f"学生: {student_name}\n")
                        f.write(f"科目: {subject}\n")
                        f.write(f"考试ID: {exam_id}\n")
                        f.write("="*60 + "\n")
                        f.write(report)
                    print(f"报告已保存到: {filename}")
        
        elif choice == '2':
            break
        else:
            print("无效选择，请重新输入")

def main():
    """主程序"""
    print("欢迎使用智能教学系统！")
    print("基于 LangChain + 多种LLM模型 的个性化学习辅导平台")
    
    # 设置API密钥并选择模型
    selected_model = setup_api_keys_and_model()
    
    if not selected_model:
        print("❌ 未选择模型，程序退出")
        return
    
    try:
        # 初始化系统
        print(f"\n正在初始化系统 (使用 {LLMConfig.MODELS[LLMProvider(selected_model)]['display_name']})...")
        system = IntelligentTutoringSystem(llm_provider=selected_model)
        admin_tools = AdminTools(system)
        print("系统初始化完成！")
        
        while True:
            print("\n" + "="*50)
            print("智能教学系统 - 主菜单")
            print("="*50)
            print("1. 管理员功能 (题库管理)")
            print("2. 学生功能 (参加考试)")
            print("3. 系统说明")
            print("4. 退出系统")
            
            choice = input("\n请选择功能 (1-4): ").strip()
            
            if choice == '1':
                admin_menu(admin_tools)
            elif choice == '2':
                student_menu(system)
            elif choice == '3':
                show_system_info()
            elif choice == '4':
                print("感谢使用智能教学系统，再见！")
                break
            else:
                print("无效选择，请重新输入")
                
    except Exception as e:
        print(f"系统运行出错: {e}")
        print("请检查API密钥是否正确，网络连接是否正常")

def show_system_info():
    """显示系统说明"""
    info = """
=== 智能教学系统功能说明 ===

🎯 系统特色：
• 基于阿里云通义千问(Qwen3)大语言模型
• 智能出题、自动阅卷、个性化辅导
• 完整的学习数据分析和薄弱项识别

📚 主要功能：

1. 题库管理 (管理员)
   • 添加题目和标准答案
   • 设置知识点标签
   • 管理题目难度等级

2. 智能考试 (学生)
   • 自动从题库选择5道题
   • 实时答题和即时反馈
   • AI智能评分和分析

3. 自动阅卷
   • AI理解学生答案
   • 智能评分 (0-10分)
   • 详细的答案分析

4. 薄弱项分析
   • 识别知识盲区
   • 统计错误模式
   • 生成学习建议

5. 个性化辅导
   • 根据答题情况定制学习计划
   • 提供针对性学习资源
   • 给出专业学习建议

💡 使用建议：
• 管理员先添加题目到题库
• 学生可以多次参加不同科目考试
• 系统会记录所有学习数据用于分析
• 建议定期查看辅导报告调整学习策略

🔧 技术架构：
• 前端：Python命令行界面
• 后端：LangChain + Qwen3
• 数据库：SQLite
• AI模型：阿里云通义千问
"""
    print(info)

if __name__ == "__main__":
    main()
