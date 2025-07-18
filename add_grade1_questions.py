"""
批量添加小学一年级20以内加减法题目
"""
import random
from database import DatabaseManager

def generate_grade1_math_questions():
    """生成小学一年级20以内加减法题目"""
    questions = []
    
    # 生成25个加法题
    for i in range(25):
        # 确保两个数相加不超过20
        a = random.randint(1, 19)
        b = random.randint(1, 20 - a)
        answer = a + b
        
        question = {
            'subject': '数学',
            'difficulty': '简单',
            'question': f'{a} + {b} = ?',
            'standard_answer': str(answer),
            'knowledge_points': ['20以内加法', '基础运算'],
            'created_by': '系统管理员'
        }
        questions.append(question)
    
    # 生成25个减法题
    for i in range(25):
        # 确保被减数在1-20之间，减数不大于被减数
        a = random.randint(1, 20)
        b = random.randint(1, a)
        answer = a - b
        
        question = {
            'subject': '数学',
            'difficulty': '简单',
            'question': f'{a} - {b} = ?',
            'standard_answer': str(answer),
            'knowledge_points': ['20以内减法', '基础运算'],
            'created_by': '系统管理员'
        }
        questions.append(question)
    
    return questions

def generate_special_questions():
    """生成一些特殊的题目（应用题等）"""
    special_questions = [
        {
            'subject': '数学',
            'difficulty': '简单',
            'question': '小明有5个苹果，妈妈又给了他3个苹果，小明现在一共有多少个苹果？',
            'standard_answer': '8个苹果',
            'knowledge_points': ['20以内加法', '应用题', '实际问题'],
            'created_by': '系统管理员'
        },
        {
            'subject': '数学',
            'difficulty': '简单',
            'question': '树上有12只小鸟，飞走了4只，树上还剩多少只小鸟？',
            'standard_answer': '8只小鸟',
            'knowledge_points': ['20以内减法', '应用题', '实际问题'],
            'created_by': '系统管理员'
        },
        {
            'subject': '数学',
            'difficulty': '简单',
            'question': '一个班有9个男同学和7个女同学，这个班一共有多少个同学？',
            'standard_answer': '16个同学',
            'knowledge_points': ['20以内加法', '应用题', '实际问题'],
            'created_by': '系统管理员'
        },
        {
            'subject': '数学',
            'difficulty': '简单',
            'question': '妈妈买了15个橘子，吃掉了6个，还剩多少个橘子？',
            'standard_answer': '9个橘子',
            'knowledge_points': ['20以内减法', '应用题', '实际问题'],
            'created_by': '系统管理员'
        },
        {
            'subject': '数学',
            'difficulty': '简单',
            'question': '小红有8支铅笔，小明给了她5支铅笔，小红现在有多少支铅笔？',
            'standard_answer': '13支铅笔',
            'knowledge_points': ['20以内加法', '应用题', '实际问题'],
            'created_by': '系统管理员'
        }
    ]
    return special_questions

def main():
    """主函数"""
    print("正在生成小学一年级20以内加减法题目...")
    
    # 初始化数据库
    db = DatabaseManager()
    
    # 生成基础计算题目（45个）
    basic_questions = generate_grade1_math_questions()
    
    # 生成应用题（5个）
    special_questions = generate_special_questions()
    
    # 合并所有题目
    all_questions = basic_questions + special_questions
    
    print(f"共生成 {len(all_questions)} 道题目")
    print("题目类型分布：")
    print(f"- 加法题：25道")
    print(f"- 减法题：25道") 
    print(f"- 应用题：5道")
    
    # 批量添加到数据库
    success_count = 0
    for i, question in enumerate(all_questions, 1):
        try:
            question_id = db.add_question(
                question['subject'],
                question['difficulty'],
                question['question'],
                question['standard_answer'],
                question['knowledge_points'],
                question['created_by']
            )
            success_count += 1
            print(f"[{i:2d}/50] 已添加: {question['question']}")
        except Exception as e:
            print(f"[{i:2d}/50] 添加失败: {question['question']} - 错误: {e}")
    
    print(f"\n✅ 成功添加 {success_count} 道小学一年级数学题目到题库！")
    print("现在可以让小学一年级的学生参加数学测试了。")
    
    # 显示一些示例题目
    print("\n📝 题目示例：")
    sample_questions = random.sample(all_questions, 5)
    for i, q in enumerate(sample_questions, 1):
        print(f"{i}. {q['question']} (答案: {q['standard_answer']})")

if __name__ == "__main__":
    main()
