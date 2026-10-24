"""
Adaptive Learning Planner
Tracks topic mastery, models student knowledge, and dynamically recommends
the next learning activity (concept review, numerical practice, graph analysis, or quiz).
"""
from typing import Dict, List, Optional


class LearningPlanner:
    def __init__(self):
        self.topics = [
            "Deadlock Overview & Definition",
            "Necessary Conditions",
            "Deadlock Prevention",
            "Deadlock Avoidance",
            "Banker's Algorithm",
            "Resource Allocation Graph",
            "Deadlock Detection & Recovery"
        ]

    def recommend_next_activity(self, student_profile: Dict) -> Dict:
        """
        Determines the optimal next learning step based on current topic masteries and recent errors.
        """
        topic_scores = student_profile.get("topic_mastery", {})
        misconceptions = student_profile.get("misconceptions", [])
        
        # 1. Check for immediate critical misconceptions
        if "prevention_vs_avoidance" in misconceptions:
            return {
                "action": "concept_review",
                "target_topic": "Deadlock Strategies",
                "title": "Clarify Prevention vs. Avoidance",
                "reason": "You recently showed difficulty distinguishing Prevention from Avoidance.",
                "suggested_tab": "Concepts & RAG Tutor",
                "recommended_prompt": "Explain the difference between Deadlock Prevention and Avoidance with comparison table"
            }
            
        if "unsafe_equals_deadlock" in misconceptions:
            return {
                "action": "concept_review",
                "target_topic": "Banker's Algorithm",
                "title": "Safe vs Unsafe State Distinction",
                "reason": "Ensure you understand why an Unsafe State does not automatically mean Deadlock.",
                "suggested_tab": "Banker's Simulator",
                "recommended_prompt": "Can a system in an unsafe state finish without deadlocking?"
            }

        # 2. Find the topic with the lowest mastery score
        lowest_topic = None
        lowest_score = 1.01

        for t in self.topics:
            score = topic_scores.get(t, 0.0)
            if score < lowest_score:
                lowest_score = score
                lowest_topic = t

        if lowest_topic is None or lowest_score < 0.4:
            # Low mastery -> Focus on fundamentals or practice
            if lowest_topic == "Banker's Algorithm":
                return {
                    "action": "interactive_simulation",
                    "target_topic": "Banker's Algorithm",
                    "title": "Interactive Banker's Step-by-Step Practice",
                    "reason": f"Your mastery in {lowest_topic} is {int(lowest_score * 100)}%. Step through safety sequence checks.",
                    "suggested_tab": "Banker's Simulator"
                }
            elif lowest_topic == "Resource Allocation Graph":
                return {
                    "action": "graph_analysis",
                    "target_topic": "Resource Allocation Graph",
                    "title": "Practice RAG Cycle & Deadlock Detection",
                    "reason": f"Strengthen cycle analysis and reduction in RAG graphs.",
                    "suggested_tab": "RAG Graph Visualizer"
                }
            else:
                return {
                    "action": "practice_quiz",
                    "target_topic": lowest_topic or "Necessary Conditions",
                    "title": f"Targeted Practice: {lowest_topic or 'Necessary Conditions'}",
                    "reason": f"Reinforce concepts in {lowest_topic or 'Necessary Conditions'}.",
                    "suggested_tab": "Adaptive Quiz"
                }

        # 3. If mastery is high across topics -> Recommend challenge questions
        return {
            "action": "challenge_numerical",
            "target_topic": "Banker's Algorithm",
            "title": "Advanced Banker's Numerical Challenge",
            "reason": "Great job! All foundational topics mastered. Try complex resource-request simulation.",
            "suggested_tab": "Banker's Simulator"
        }

    def compute_overall_readiness(self, topic_mastery: Dict[str, float]) -> float:
        if not topic_mastery:
            return 0.0
        scores = [topic_mastery.get(t, 0.0) for t in self.topics]
        return round(sum(scores) / len(self.topics) * 100, 1)
