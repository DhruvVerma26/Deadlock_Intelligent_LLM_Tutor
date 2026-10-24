"""
Student Response Evaluator & Diagnostic Engine
Evaluates MCQ answers, numerical safe sequences, and viva short answers.
Detects misconceptions (e.g., confusing prevention with avoidance, miscalculating Need),
and yields progressive hints and constructive feedback.
"""
import re
from typing import Dict, List, Tuple


class StudentEvaluator:
    def __init__(self):
        self.known_misconceptions = {
            "prevention_vs_avoidance": [
                "prevention uses banker", "prevention tracks runtime safe states",
                "avoidance invalidates conditions", "avoidance strictly orders resources"
            ],
            "unsafe_equals_deadlock": [
                "unsafe state is always deadlock", "unsafe state means deadlock has occurred"
            ],
            "cycle_means_deadlock_multi": [
                "any cycle guarantees deadlock", "cycle always means deadlock even for multiple instances"
            ],
            "preemption_confusion": [
                "preemption is a necessary condition", "preemption causes deadlock"
            ]
        }

    def evaluate_mcq(self, question_item: Dict, selected_option: str) -> Dict:
        """Evaluates an MCQ selection, returning score, status, and targeted explanation."""
        selected_letter = selected_option.strip()[:1].upper()
        correct_letter = question_item["correct_answer"].strip()[:1].upper()
        is_correct = (selected_letter == correct_letter)

        return {
            "is_correct": is_correct,
            "score": 1.0 if is_correct else 0.0,
            "selected": selected_letter,
            "correct": correct_letter,
            "explanation": question_item.get("explanation", ""),
            "feedback": (
                "🎯 Correct! Well done." if is_correct 
                else f"❌ Not quite right. The correct option is {correct_letter}. Review the explanation below."
            )
        }

    def evaluate_safe_sequence(self, user_sequence_input: str, bankers_engine) -> Dict:
        """
        Parses and evaluates a student's proposed Banker's algorithm safe sequence.
        e.g. '<P1, P3, P4, P0, P2>' or 'P1, P3, P4, P0, P2' or 'P1->P3->P4->P0->P2'
        """
        # Parse process names from input
        cleaned = re.findall(r"\b[P|p]\d+\b", user_sequence_input)
        cleaned = [p.upper() for p in cleaned]

        if not cleaned:
            return {
                "is_correct": False,
                "score": 0.0,
                "feedback": "Could not identify process IDs in your answer. Please use standard format like 'P1, P3, P4, P0, P2'.",
                "validation_steps": []
            }

        is_valid, message, steps = bankers_engine.verify_student_sequence(cleaned)
        
        return {
            "is_correct": is_valid,
            "score": 1.0 if is_valid else 0.0,
            "parsed_sequence": cleaned,
            "feedback": message,
            "validation_steps": steps
        }

    def evaluate_viva_text(self, question_item: Dict, student_text: str) -> Dict:
        """
        Evaluates a student's descriptive or viva answer using concept keyword coverage
        and misconception checks.
        """
        text_lower = student_text.lower()
        if len(text_lower.strip()) < 10:
            return {
                "score": 0.0,
                "feedback": "Answer is too brief. Please explain your reasoning in more detail.",
                "detected_misconceptions": [],
                "missing_keywords": []
            }

        # Check for common misconceptions
        detected = []
        for mis_key, patterns in self.known_misconceptions.items():
            for p in patterns:
                if p in text_lower:
                    detected.append(mis_key)
                    break

        # Check key concepts present in correct answer
        expected_sample = question_item.get("correct_answer", "").lower()
        expected_words = set(re.findall(r"\b\w{4,}\b", expected_sample))
        student_words = set(re.findall(r"\b\w{4,}\b", text_lower))
        
        common = expected_words.intersection(student_words)
        coverage_ratio = len(common) / max(1, len(expected_words))
        score = min(1.0, round(coverage_ratio * 1.5, 2))  # Scaled

        feedback_parts = []
        if score >= 0.7:
            feedback_parts.append("Excellent answer! You captured the core technical concepts accurately.")
        elif score >= 0.4:
            feedback_parts.append("Good attempt, but your answer is missing some critical mechanisms.")
        else:
            feedback_parts.append("Your response lacks the necessary technical keywords and justification.")

        if "unsafe_equals_deadlock" in detected:
            feedback_parts.append("⚠️ Note: Be careful! An unsafe state is NOT synonymous with deadlock; it simply means safety cannot be guaranteed.")
        if "prevention_vs_avoidance" in detected:
            feedback_parts.append("⚠️ Note: Avoid confusing Prevention with Avoidance! Prevention invalidates one of the 4 conditions statically, whereas Avoidance monitors states dynamically.")

        return {
            "score": score,
            "feedback": " ".join(feedback_parts),
            "detected_misconceptions": detected,
            "matched_concepts": list(common)[:8],
            "reference_answer": question_item.get("correct_answer", "")
        }

    def get_progressive_hint(self, question_item: Dict, hint_level: int) -> str:
        """Returns hint 1, hint 2, or full explanation depending on current hint level."""
        hints = question_item.get("hints", [])
        if not hints:
            return "No hints available for this question."
        if hint_level <= len(hints):
            return hints[hint_level - 1]
        return f"💡 Complete Solution / Explanation: {question_item.get('explanation', '')}"
