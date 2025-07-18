"""
数据库管理模块
负责题库管理、学生答题记录、成绩分析等数据存储
"""
import sqlite3
import json
from datetime import datetime
from typing import List, Dict, Optional, Tuple

class DatabaseManager:
    def __init__(self, db_path: str = "teaching_system.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """初始化数据库表结构"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 题库表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS questions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                subject TEXT NOT NULL,
                difficulty TEXT NOT NULL,
                question TEXT NOT NULL,
                standard_answer TEXT NOT NULL,
                knowledge_points TEXT,  -- JSON格式存储知识点列表
                created_by TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 学生表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS students (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                grade TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 考试记录表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS exams (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id INTEGER,
                subject TEXT NOT NULL,
                total_questions INTEGER DEFAULT 5,
                total_score REAL DEFAULT 0,
                start_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                end_time TIMESTAMP,
                status TEXT DEFAULT 'in_progress',  -- in_progress, completed
                FOREIGN KEY (student_id) REFERENCES students (id)
            )
        ''')
        
        # 答题记录表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS answers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                exam_id INTEGER,
                question_id INTEGER,
                student_answer TEXT NOT NULL,
                score REAL DEFAULT 0,
                analysis TEXT,  -- LLM分析结果
                weak_points TEXT,  -- JSON格式存储薄弱知识点
                answered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (exam_id) REFERENCES exams (id),
                FOREIGN KEY (question_id) REFERENCES questions (id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def add_question(self, subject: str, difficulty: str, question: str, 
                    standard_answer: str, knowledge_points: List[str], 
                    created_by: str) -> int:
        """管理员添加题目"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO questions (subject, difficulty, question, standard_answer, 
                                 knowledge_points, created_by)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (subject, difficulty, question, standard_answer, 
              json.dumps(knowledge_points, ensure_ascii=False), created_by))
        
        question_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return question_id
    
    def get_questions_by_subject(self, subject: str, difficulty: str = None, 
                               limit: int = 5) -> List[Dict]:
        """根据科目获取题目"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if difficulty:
            cursor.execute('''
                SELECT id, subject, difficulty, question, standard_answer, knowledge_points
                FROM questions 
                WHERE subject = ? AND difficulty = ?
                ORDER BY RANDOM()
                LIMIT ?
            ''', (subject, difficulty, limit))
        else:
            cursor.execute('''
                SELECT id, subject, difficulty, question, standard_answer, knowledge_points
                FROM questions 
                WHERE subject = ?
                ORDER BY RANDOM()
                LIMIT ?
            ''', (subject, limit))
        
        questions = []
        for row in cursor.fetchall():
            questions.append({
                'id': row[0],
                'subject': row[1],
                'difficulty': row[2],
                'question': row[3],
                'standard_answer': row[4],
                'knowledge_points': json.loads(row[5]) if row[5] else []
            })
        
        conn.close()
        return questions
    
    def create_student(self, name: str, grade: str = None) -> int:
        """创建学生记录"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO students (name, grade)
            VALUES (?, ?)
        ''', (name, grade))
        
        student_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return student_id
    
    def create_exam(self, student_id: int, subject: str) -> int:
        """创建考试记录"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO exams (student_id, subject)
            VALUES (?, ?)
        ''', (student_id, subject))
        
        exam_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return exam_id
    
    def save_answer(self, exam_id: int, question_id: int, student_answer: str, 
                   score: float, analysis: str, weak_points: List[str]) -> int:
        """保存学生答案和分析结果"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO answers (exam_id, question_id, student_answer, score, 
                               analysis, weak_points)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (exam_id, question_id, student_answer, score, analysis,
              json.dumps(weak_points, ensure_ascii=False)))
        
        answer_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return answer_id
    
    def complete_exam(self, exam_id: int, total_score: float):
        """完成考试，更新总分"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE exams 
            SET total_score = ?, end_time = CURRENT_TIMESTAMP, status = 'completed'
            WHERE id = ?
        ''', (total_score, exam_id))
        
        conn.commit()
        conn.close()
    
    def get_exam_results(self, exam_id: int) -> Dict:
        """获取考试结果详情"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 获取考试基本信息
        cursor.execute('''
            SELECT e.id, s.name, e.subject, e.total_score, e.start_time, e.end_time
            FROM exams e
            JOIN students s ON e.student_id = s.id
            WHERE e.id = ?
        ''', (exam_id,))
        
        exam_info = cursor.fetchone()
        if not exam_info:
            conn.close()
            return None
        
        # 获取答题详情
        cursor.execute('''
            SELECT a.question_id, q.question, q.standard_answer, a.student_answer,
                   a.score, a.analysis, a.weak_points
            FROM answers a
            JOIN questions q ON a.question_id = q.id
            WHERE a.exam_id = ?
            ORDER BY a.id
        ''', (exam_id,))
        
        answers = []
        for row in cursor.fetchall():
            answers.append({
                'question_id': row[0],
                'question': row[1],
                'standard_answer': row[2],
                'student_answer': row[3],
                'score': row[4],
                'analysis': row[5],
                'weak_points': json.loads(row[6]) if row[6] else []
            })
        
        conn.close()
        
        return {
            'exam_id': exam_info[0],
            'student_name': exam_info[1],
            'subject': exam_info[2],
            'total_score': exam_info[3],
            'start_time': exam_info[4],
            'end_time': exam_info[5],
            'answers': answers
        }
    
    def get_student_weak_points(self, student_id: int, subject: str = None) -> List[str]:
        """分析学生薄弱知识点"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if subject:
            cursor.execute('''
                SELECT a.weak_points
                FROM answers a
                JOIN exams e ON a.exam_id = e.id
                WHERE e.student_id = ? AND e.subject = ?
            ''', (student_id, subject))
        else:
            cursor.execute('''
                SELECT a.weak_points
                FROM answers a
                JOIN exams e ON a.exam_id = e.id
                WHERE e.student_id = ?
            ''', (student_id,))
        
        all_weak_points = []
        for row in cursor.fetchall():
            if row[0]:
                weak_points = json.loads(row[0])
                all_weak_points.extend(weak_points)
        
        conn.close()
        
        # 统计频次，返回最常见的薄弱点
        from collections import Counter
        weak_point_counts = Counter(all_weak_points)
        return [point for point, count in weak_point_counts.most_common()]
