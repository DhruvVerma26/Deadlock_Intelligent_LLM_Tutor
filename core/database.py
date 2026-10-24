"""
SQLite Database Layer for Deadlock Tutor
Stores student profiles, topic-wise mastery scores, quiz attempts, and misconception logs.
"""
import sqlite3
import os
import json
from typing import Dict, List, Optional
from datetime import datetime


class TutorDatabase:
    def __init__(self, db_path: Optional[str] = None):
        if db_path is None:
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            db_path = os.path.join(base_dir, "deadlock_tutor.db")
        self.db_path = db_path
        self._init_tables()

    def _get_connection(self):
        return sqlite3.connect(self.db_path)

    def _init_tables(self):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS students (
                    student_id TEXT PRIMARY KEY,
                    student_name TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS topic_mastery (
                    student_id TEXT,
                    topic TEXT,
                    mastery_score REAL,
                    attempts_count INTEGER,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    PRIMARY KEY (student_id, topic)
                )
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS quiz_attempts (
                    attempt_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    student_id TEXT,
                    question_id TEXT,
                    question_type TEXT,
                    topic TEXT,
                    user_response TEXT,
                    is_correct INTEGER,
                    score REAL,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS misconceptions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    student_id TEXT,
                    misconception_type TEXT,
                    context TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.commit()

    def get_or_create_student(self, student_id: str, student_name: str = "Student") -> Dict:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT student_id, student_name FROM students WHERE student_id = ?", (student_id,))
            row = cursor.fetchone()
            if not row:
                cursor.execute(
                    "INSERT INTO students (student_id, student_name) VALUES (?, ?)",
                    (student_id, student_name)
                )
                conn.commit()
                return {"student_id": student_id, "student_name": student_name}
            return {"student_id": row[0], "student_name": row[1]}

    def log_quiz_attempt(
        self,
        student_id: str,
        question_id: str,
        question_type: str,
        topic: str,
        user_response: str,
        is_correct: bool,
        score: float
    ):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO quiz_attempts (student_id, question_id, question_type, topic, user_response, is_correct, score)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (student_id, question_id, question_type, topic, user_response, 1 if is_correct else 0, score))

            # Update topic mastery using exponential moving average
            cursor.execute("""
                SELECT mastery_score, attempts_count FROM topic_mastery
                WHERE student_id = ? AND topic = ?
            """, (student_id, topic))
            row = cursor.fetchone()

            if row:
                old_mastery, count = row
                new_mastery = round(old_mastery * 0.7 + score * 0.3, 3)
                cursor.execute("""
                    UPDATE topic_mastery
                    SET mastery_score = ?, attempts_count = ?, updated_at = CURRENT_TIMESTAMP
                    WHERE student_id = ? AND topic = ?
                """, (new_mastery, count + 1, student_id, topic))
            else:
                cursor.execute("""
                    INSERT INTO topic_mastery (student_id, topic, mastery_score, attempts_count)
                    VALUES (?, ?, ?, 1)
                """, (student_id, topic, score))

            conn.commit()

    def log_misconception(self, student_id: str, misconception_type: str, context: str = ""):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO misconceptions (student_id, misconception_type, context)
                VALUES (?, ?, ?)
            """, (student_id, misconception_type, context))
            conn.commit()

    def get_student_profile(self, student_id: str) -> Dict:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            # Topic mastery
            cursor.execute("""
                SELECT topic, mastery_score, attempts_count FROM topic_mastery WHERE student_id = ?
            """, (student_id,))
            mastery_rows = cursor.fetchall()
            topic_mastery = {row[0]: row[1] for row in mastery_rows}

            # Recent misconceptions
            cursor.execute("""
                SELECT DISTINCT misconception_type FROM misconceptions WHERE student_id = ?
                ORDER BY timestamp DESC LIMIT 5
            """, (student_id,))
            misconceptions = [row[0] for row in cursor.fetchall()]

            # Total attempts and accuracy
            cursor.execute("""
                SELECT COUNT(*), SUM(is_correct), AVG(score) FROM quiz_attempts WHERE student_id = ?
            """, (student_id,))
            stat = cursor.fetchone()
            total_attempts = stat[0] or 0
            correct_attempts = stat[1] or 0
            avg_score = round((stat[2] or 0.0) * 100, 1)

            return {
                "student_id": student_id,
                "topic_mastery": topic_mastery,
                "misconceptions": misconceptions,
                "total_attempts": total_attempts,
                "correct_attempts": correct_attempts,
                "accuracy_percentage": avg_score
            }
