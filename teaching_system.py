"""
智能教学系统核心模块
基于LangChain和Qwen3实现智能出题、阅卷、分析功能
"""
import os
import json
import re
from typing import List, Dict, Tuple, Optional, Any
from langchain.schema import HumanMessage, SystemMessage
from database import DatabaseManager
from llm_config import LLMProvider, LLMConfig, get_llm_by_name

class IntelligentTutoringSystem:
    def __init__(self, llm_provider: str = "qwen3", api_key: str = None):
        """初始化智能教学系统
        
        Args:
            llm_provider: LLM提供商 ('qwen3' 或 'gemini')
            api_key: API密钥（可选，如果未设置环境变量）
        """
        self.llm_provider = llm_provider
        
        # 设置API密钥（如果提供）
        if api_key:
            if llm_provider == "qwen3":
                os.environ["DASHSCOPE_API_KEY"] = api_key
            elif llm_provider == "gemini":
                os.environ["GOOGLE_API_KEY"] = api_key
        
        # 初始化LLM模型
        try:
            self.llm = get_llm_by_name(llm_provider)
            print(f"✅ 已初始化 {LLMConfig.MODELS[LLMProvider(llm_provider)]['display_name']} 模型")
        except Exception as e:
            print(f"❌ 初始化LLM模型失败: {e}")
            raise
        
        # 初始化数据库
        self.db = DatabaseManager()
        
        # 辅助函数：处理LLM返回的可能包含Markdown代码块的JSON字符串
        def parse_llm_json_response(response_content: str) -> Optional[Any]:
            """解析LLM返回的可能包含Markdown代码块的JSON字符串"""
            response_content = response_content.strip()
            
            # 处理可能带有Markdown代码块标记的JSON
            if response_content.startswith('```json'):
                # 移除```json和```标记
                response_content = response_content.replace('```json', '', 1)
                if response_content.endswith('```'):
                    response_content = response_content[:-3]
                response_content = response_content.strip()
            # 处理只有```而没有json标识符的情况
            elif response_content.startswith('```') and response_content.endswith('```'):
                response_content = response_content[3:-3].strip()
            
            try:
                return json.loads(response_content)
            except json.JSONDecodeError:
                return None
        
        # 将辅助函数添加为实例方法
        self.parse_llm_json_response = parse_llm_json_response
        
        # 系统提示词模板
        self.system_prompts = {
            'question_generator': """你是一位专业的教师，负责根据给定的知识点和难度生成高质量的考试题目。
要求：
1. 题目应该准确测试学生对知识点的掌握程度
2. 题目表述清晰，无歧义
3. 难度适中，符合指定的难度等级
4. 题目类型可以是选择题、填空题、简答题或计算题
5. 每道题都要有明确的标准答案

请严格按照JSON格式输出：
{
    "question": "题目内容",
    "question_type": "题目类型",
    "difficulty": "难度等级",
    "knowledge_points": ["知识点1", "知识点2"],
    "standard_answer": "标准答案",
    "explanation": "答案解释"
}""",
            
            'grader': """你是一位经验丰富的阅卷老师，负责评判学生答案并给出详细分析。
评分标准：
1. 满分10分
2. 根据答案的准确性、完整性、逻辑性进行评分
3. 给出具体的扣分原因
4. 识别学生的薄弱知识点
5. 提供改进建议

请严格按照JSON格式输出：
{
    "score": 分数(0-10),
    "analysis": "详细的答案分析",
    "weak_points": ["薄弱知识点1", "薄弱知识点2"],
    "suggestions": "改进建议",
    "correct_answer": "正确答案要点"
}""",
            
            'tutor': """你是一位个性化辅导专家，根据学生的答题情况提供专业的学习建议。
分析要点：
1. 识别学生的学习模式和特点
2. 找出知识盲区和薄弱环节
3. 提供针对性的学习方法和资源
4. 制定个性化的学习计划
5. 给出鼓励性的建议

请提供详细的辅导报告，包括：
- 学习现状分析
- 薄弱项目总结
- 个性化学习建议
- 推荐学习资源
- 后续学习计划"""
        }
    
    def generate_question(self, subject: str, difficulty: str, knowledge_points: List[str]) -> Dict:
        """LLM生成题目"""
        prompt = f"""
科目：{subject}
难度：{difficulty}
知识点：{', '.join(knowledge_points)}

请根据以上信息生成一道高质量的考试题目。
"""
        
        messages = [
            SystemMessage(content=self.system_prompts['question_generator']),
            HumanMessage(content=prompt)
        ]
        
        try:
            response = self.llm.invoke(messages)
            # 解析JSON响应
            question_data = self.parse_llm_json_response(response.content)
            if question_data is None:
                print("生成题目时出错: 返回内容不是有效的JSON格式")
                return None
            return question_data
        except Exception as e:
            print(f"生成题目时出错: {e}")
            return None
    
    def grade_answer(self, question: str, standard_answer: str, student_answer: str, 
                    knowledge_points: List[str]) -> Dict:
        """LLM阅卷评分"""
        prompt = f"""
题目：{question}
标准答案：{standard_answer}
学生答案：{student_answer}
涉及知识点：{', '.join(knowledge_points)}

请对学生答案进行评分和分析。
"""
        
        messages = [
            SystemMessage(content=self.system_prompts['grader']),
            HumanMessage(content=prompt)
        ]
        
        try:
            response = self.llm.invoke(messages)
            grading_result = self.parse_llm_json_response(response.content)
            
            # 检查是否成功解析为JSON
            if grading_result is None:
                print(f"阅卷返回的内容不是有效的JSON格式")
                return {
                    "score": 0,
                    "analysis": "评分系统出错：返回内容格式不正确",
                    "weak_points": [],
                    "suggestions": "请重新提交答案",
                    "correct_answer": standard_answer
                }
            return grading_result
        except Exception as e:
            print(f"阅卷时出错: {e}")
            return {
                "score": 0,
                "analysis": "评分系统出错",
                "weak_points": [],
                "suggestions": "请重新提交答案",
                "correct_answer": standard_answer
            }
    
    def generate_tutoring_report(self, student_name: str, exam_results: Dict) -> str:
        """生成个性化辅导报告"""
        # 整理学生答题数据
        total_score = exam_results['total_score']
        answers = exam_results['answers']
        subject = exam_results['subject']
        
        # 收集所有薄弱点
        all_weak_points = []
        detailed_analysis = []
        
        for answer in answers:
            all_weak_points.extend(answer['weak_points'])
            questionStr = answer['question'][:50]
            if len(questionStr) >= 50:
                questionStr += '...'
            detailed_analysis.append({
                'question': questionStr,
                'score': answer['score'],
                'analysis': answer['analysis']
            })
        
        # 统计薄弱点频次
        from collections import Counter
        weak_point_counts = Counter(all_weak_points)
        top_weak_points = [point for point, count in weak_point_counts.most_common(5)]

        prompt = f"""
学生姓名：{student_name}
考试科目：{subject}
总分：{total_score}/50分
答题详情：{json.dumps(detailed_analysis, ensure_ascii=False, indent=2)}
主要薄弱知识点：{', '.join(top_weak_points)}

请为该学生生成详细的个性化辅导报告。
"""
        
        messages = [
            SystemMessage(content=self.system_prompts['tutor']),
            HumanMessage(content=prompt)
        ]
        
        try:
            response = self.llm.invoke(messages)
            return response.content
        except Exception as e:
            print(f"生成辅导报告时出错: {e}")
            return f"为{student_name}生成辅导报告时出现错误，请稍后重试。"
    
    def conduct_exam(self, student_name: str, subject: str, grade: str = None) -> int:
        """进行考试流程"""
        print(f"\n=== 欢迎 {student_name} 参加 {subject} 测试 ===")
        
        # 创建学生记录
        student_id = self.db.create_student(student_name, grade)
        
        # 创建考试记录
        exam_id = self.db.create_exam(student_id, subject)
        
        # 获取题目（从数据库随机选择5道题）
        questions = self.db.get_questions_by_subject(subject, limit=5)
        
        if len(questions) < 5:
            print(f"题库中{subject}科目题目不足，当前只有{len(questions)}道题")
            if len(questions) == 0:
                print("请先添加题目到题库中")
                return None
        
        total_score = 0
        
        # 逐题答题
        for i, question_data in enumerate(questions, 1):
            print(f"\n--- 第 {i} 题 ---")
            print(f"题目：{question_data['question']}")
            
            # 学生答题
            student_answer = input("请输入你的答案：").strip()
            
            if not student_answer:
                student_answer = "未作答"
            
            # LLM阅卷
            print("正在评分中...")
            grading_result = self.grade_answer(
                question_data['question'],
                question_data['standard_answer'],
                student_answer,
                question_data['knowledge_points']
            )
            
            # 确保grading_result包含所有必要的键
            if grading_result and isinstance(grading_result, dict):
                score = grading_result.get('score', 0)
                analysis = grading_result.get('analysis', '无分析')
                weak_points = grading_result.get('weak_points', [])
                
                total_score += score
                
                # 保存答案记录
                self.db.save_answer(
                    exam_id,
                    question_data['id'],
                    student_answer,
                    score,
                    analysis,
                    weak_points
                )
                
                # 显示即时反馈
                print(f"得分：{score}/10")
                print(f"分析：{analysis}")
                
                if weak_points:
                    print(f"薄弱点：{', '.join(weak_points)}")
            else:
                print("评分系统返回了无效的结果")
                # 使用默认值
                self.db.save_answer(
                    exam_id,
                    question_data['id'],
                    student_answer,
                    0,
                    "评分系统出错",
                    []
                )
                print("得分：0/10")
                print("分析：评分系统出错")
            
            print("-" * 50)
        
        # 完成考试
        self.db.complete_exam(exam_id, total_score)
        
        print(f"\n=== 考试完成 ===")
        print(f"总分：{total_score}/50")
        
        return exam_id
    
    def generate_final_report(self, exam_id: int) -> str:
        """生成最终的学习报告"""
        exam_results = self.db.get_exam_results(exam_id)
        if not exam_results:
            return "未找到考试记录"
        
        print("\n=== 正在生成个性化辅导报告 ===")
        tutoring_report = self.generate_tutoring_report(
            exam_results['student_name'],
            exam_results
        )
        
        return tutoring_report

# 管理员工具类
class AdminTools:
    def __init__(self, teaching_system: IntelligentTutoringSystem):
        self.system = teaching_system
        self.db = teaching_system.db
    
    def add_question_interactive(self):
        """交互式添加题目"""
        print("\n=== 添加新题目 ===")
        
        subject = input("科目：").strip()
        difficulty = input("难度 (简单/中等/困难)：").strip()
        question = input("题目内容：").strip()
        standard_answer = input("标准答案：").strip()
        
        knowledge_points_str = input("知识点 (用逗号分隔)：").strip()
        knowledge_points = [kp.strip() for kp in knowledge_points_str.split(',') if kp.strip()]
        
        created_by = input("出题人：").strip()
        
        if all([subject, difficulty, question, standard_answer, created_by]):
            question_id = self.db.add_question(
                subject, difficulty, question, standard_answer, 
                knowledge_points, created_by
            )
            print(f"题目添加成功！ID: {question_id}")
        else:
            print("信息不完整，添加失败")
    
    def batch_add_questions(self, questions_data: List[Dict]):
        """批量添加题目"""
        for q_data in questions_data:
            try:
                self.db.add_question(
                    q_data['subject'],
                    q_data['difficulty'],
                    q_data['question'],
                    q_data['standard_answer'],
                    q_data.get('knowledge_points', []),
                    q_data.get('created_by', 'System')
                )
                print(f"已添加题目: {q_data['question'][:30]}...")
            except Exception as e:
                print(f"添加题目失败: {e}")
    
    def view_questions(self, subject: str = None):
        """查看题库"""
        if subject:
            questions = self.db.get_questions_by_subject(subject, limit=100)
        else:
            # 获取所有题目的简化版本
            import sqlite3
            conn = sqlite3.connect(self.db.db_path)
            cursor = conn.cursor()
            cursor.execute('SELECT id, subject, difficulty, question FROM questions')
            rows = cursor.fetchall()
            questions = [{'id': r[0], 'subject': r[1], 'difficulty': r[2], 'question': r[3]} for r in rows]
            conn.close()
        
        if questions:
            print(f"\n=== 题库内容 ({'所有科目' if not subject else subject}) ===")
            for q in questions:
                print(f"ID: {q['id']} | {q['subject']} | {q['difficulty']} | {q['question'][:50]}...")
        else:
            print("题库为空")
