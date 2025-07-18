"""
学生考试功能演示脚本
模拟一个小学生参加数学考试的完整流程
"""
import os
import getpass
from teaching_system import IntelligentTutoringSystem

def setup_api_key():
    """设置API密钥"""
    if not os.environ.get("DASHSCOPE_API_KEY"):
        # 使用已知的API密钥
        os.environ["DASHSCOPE_API_KEY"] = "sk-ebdfebf21dad458fae87fcf4485be415"

def simulate_student_answers():
    """模拟学生答案 - 有对有错，展示AI评分能力"""
    return [
        "9",      # 第1题答案
        "15",     # 第2题答案  
        "8",      # 第3题答案
        "12",     # 第4题答案
        "6个苹果"  # 第5题答案（如果是应用题）
    ]

def demo_exam():
    """演示考试流程"""
    print("🎓 智能教学系统 - 学生考试功能演示")
    print("="*60)
    
    # 设置API密钥
    setup_api_key()
    
    # 初始化系统
    print("正在初始化智能教学系统...")
    system = IntelligentTutoringSystem()
    print("✅ 系统初始化完成！")
    
    # 模拟学生信息
    student_name = "小明"
    subject = "数学"
    grade = "一年级"
    
    print(f"\n👦 学生信息：{student_name} ({grade})")
    print(f"📚 考试科目：{subject}")
    print(f"📝 题目数量：5道题")
    print("-" * 60)
    
    # 创建学生记录
    student_id = system.db.create_student(student_name, grade)
    
    # 创建考试记录
    exam_id = system.db.create_exam(student_id, subject)
    
    # 获取题目（从数据库随机选择5道题）
    questions = system.db.get_questions_by_subject(subject, limit=5)
    
    if len(questions) < 5:
        print(f"❌ 题库中{subject}科目题目不足，当前只有{len(questions)}道题")
        return
    
    print(f"✅ 已从题库中选择了5道{subject}题目")
    
    # 模拟学生答案
    student_answers = [
        "9",           # 可能正确
        "错误答案",      # 故意错误
        "8",           # 可能正确
        "不知道",       # 不会做
        "13支铅笔"      # 应用题答案
    ]
    
    total_score = 0
    
    print("\n🎯 开始考试...")
    print("=" * 60)
    
    # 逐题答题和评分
    for i, question_data in enumerate(questions, 1):
        print(f"\n📋 第 {i} 题")
        print(f"题目：{question_data['question']}")
        print(f"标准答案：{question_data['standard_answer']}")
        
        # 使用预设的学生答案
        if i <= len(student_answers):
            student_answer = student_answers[i-1]
        else:
            student_answer = "不知道"
            
        print(f"学生答案：{student_answer}")
        
        # AI阅卷
        print("🤖 AI正在评分中...")
        grading_result = system.grade_answer(
            question_data['question'],
            question_data['standard_answer'],
            student_answer,
            question_data['knowledge_points']
        )
        
        score = grading_result['score']
        total_score += score
        
        # 保存答案记录
        system.db.save_answer(
            exam_id,
            question_data['id'],
            student_answer,
            score,
            grading_result['analysis'],
            grading_result['weak_points']
        )
        
        # 显示评分结果
        print(f"📊 得分：{score}/10")
        print(f"📝 AI分析：{grading_result['analysis']}")
        
        if grading_result['weak_points']:
            print(f"⚠️  薄弱点：{', '.join(grading_result['weak_points'])}")
        
        if grading_result['suggestions']:
            print(f"💡 建议：{grading_result['suggestions']}")
        
        print("-" * 50)
    
    # 完成考试
    system.db.complete_exam(exam_id, total_score)
    
    print(f"\n🎉 考试完成！")
    print(f"📊 总分：{total_score}/50")
    print(f"📈 正确率：{(total_score/50)*100:.1f}%")
    
    # 生成个性化辅导报告
    print("\n🎓 正在生成个性化辅导报告...")
    print("=" * 60)
    
    exam_results = system.db.get_exam_results(exam_id)
    tutoring_report = system.generate_tutoring_report(
        exam_results['student_name'],
        exam_results
    )
    
    print("📋 个性化辅导报告：")
    print(tutoring_report)
    
    # 保存报告
    filename = f"demo_report_{student_name}_{exam_id}.txt"
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(f"学生: {student_name}\n")
        f.write(f"年级: {grade}\n")
        f.write(f"科目: {subject}\n")
        f.write(f"总分: {total_score}/50\n")
        f.write(f"考试ID: {exam_id}\n")
        f.write("="*60 + "\n")
        f.write(tutoring_report)
    
    print(f"\n💾 辅导报告已保存到: {filename}")
    
    print("\n" + "="*60)
    print("🎯 演示完成！")
    print("这就是完整的智能教学系统学生考试流程：")
    print("1. 📝 从题库随机选题")
    print("2. 🤖 AI智能阅卷评分") 
    print("3. 📊 实时分析和反馈")
    print("4. 🎓 生成个性化辅导报告")
    print("5. 💡 提供学习建议和改进方案")

if __name__ == "__main__":
    demo_exam()
