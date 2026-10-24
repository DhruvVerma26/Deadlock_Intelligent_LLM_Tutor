"""
Unit and Integration Tests for Deadlock Intelligent LLM Tutor
Tests Banker's algorithm, RAG graph cycle theorems, RAG retrieval, evaluator, and database.
"""
import sys
import os
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from deadlock_tutor.core.bankers_engine import BankersEngine
from deadlock_tutor.core.rag_graph_engine import RAGGraphEngine
from deadlock_tutor.core.rag_retriever import DeadlockRAGRetriever
from deadlock_tutor.core.evaluator import StudentEvaluator
from deadlock_tutor.core.database import TutorDatabase


class TestDeadlockTutor(unittest.TestCase):
    def setUp(self):
        # Silberschatz 5-process benchmark
        self.procs = ["P0", "P1", "P2", "P3", "P4"]
        self.res = ["A", "B", "C"]
        self.alloc = [
            [0, 1, 0],
            [2, 0, 0],
            [3, 0, 2],
            [2, 1, 1],
            [0, 0, 2]
        ]
        self.max_m = [
            [7, 5, 3],
            [3, 2, 2],
            [9, 0, 2],
            [2, 2, 2],
            [4, 3, 3]
        ]
        self.avail = [3, 3, 2]
        self.bankers = BankersEngine(self.procs, self.res, self.alloc, self.max_m, self.avail)

    def test_bankers_safety_safe_state(self):
        res = self.bankers.run_safety_algorithm()
        self.assertTrue(res["is_safe"])
        self.assertEqual(len(res["safe_sequence"]), 5)
        self.assertEqual(res["safe_sequence"][0], "P1")

    def test_verify_valid_student_sequence(self):
        valid_seq = ["P1", "P3", "P4", "P0", "P2"]
        is_valid, msg, _ = self.bankers.verify_student_sequence(valid_seq)
        self.assertTrue(is_valid)

    def test_verify_invalid_student_sequence(self):
        # P0 cannot start because Need (7,4,3) > Available (3,3,2)
        invalid_seq = ["P0", "P1", "P2", "P3", "P4"]
        is_valid, msg, steps = self.bankers.verify_student_sequence(invalid_seq)
        self.assertFalse(is_valid)
        self.assertIn("cannot execute", msg)

    def test_bankers_request_granted(self):
        # P1 requests (1, 0, 2)
        res = self.bankers.request_resources(1, [1, 0, 2])
        self.assertTrue(res["granted"])
        self.assertIn("P1", res["safe_sequence"])

    def test_bankers_request_exceeds_need(self):
        # P1 has Need (1, 2, 2). If P1 requests (2, 0, 0), it exceeds Need
        res = self.bankers.request_resources(1, [2, 0, 0])
        self.assertFalse(res["granted"])
        self.assertEqual(res["stage"], "Request > Need")

    def test_rag_single_instance_cycle_deadlock(self):
        rag = RAGGraphEngine()
        rag.add_resource("R1", 1)
        rag.add_resource("R2", 1)
        rag.add_allocation("R1", "P1")
        rag.add_request("P1", "R2")
        rag.add_allocation("R2", "P2")
        rag.add_request("P2", "R1")

        analysis = rag.analyze_deadlock()
        self.assertTrue(analysis["deadlock_present"])
        self.assertTrue(analysis["has_cycles"])
        self.assertEqual(sorted(analysis["deadlocked_processes"]), ["P1", "P2"])

    def test_rag_multi_instance_resolvable_cycle(self):
        # Cycle exists between P1 and P2, but P3 can finish and release R2 to break it
        rag = RAGGraphEngine()
        rag.add_resource("R1", 2)
        rag.add_resource("R2", 2)
        rag.add_allocation("R1", "P1")
        rag.add_request("P1", "R2")
        rag.add_allocation("R2", "P2")
        rag.add_request("P2", "R1")
        rag.add_allocation("R2", "P3")  # P3 holds 2nd instance of R2 and has no requests

        analysis = rag.analyze_deadlock()
        self.assertFalse(analysis["deadlock_present"])
        self.assertIn("P3", analysis["reduced_sequence"])

    def test_rag_retriever(self):
        retriever = DeadlockRAGRetriever()
        results = retriever.retrieve("Coffman conditions mutual exclusion circular wait", top_k=2)
        self.assertGreater(len(results), 0)
        self.assertIn("Necessary Conditions", results[0]["topic"])

    def test_student_evaluator_mcq(self):
        evaluator = StudentEvaluator()
        q_item = {"correct_answer": "C", "explanation": "Preemption breaks deadlock"}
        res_correct = evaluator.evaluate_mcq(q_item, "C. Preemption Allowed")
        self.assertTrue(res_correct["is_correct"])

        res_wrong = evaluator.evaluate_mcq(q_item, "A. Mutual Exclusion")
        self.assertFalse(res_wrong["is_correct"])

    def test_database_logging(self):
        test_db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "test_temp.db")
        if os.path.exists(test_db_path):
            os.remove(test_db_path)
            
        db = TutorDatabase(test_db_path)
        db.get_or_create_student("TEST001", "Test Student")
        db.log_quiz_attempt("TEST001", "Q1", "mcq", "Banker's Algorithm", "A", True, 1.0)
        prof = db.get_student_profile("TEST001")
        
        self.assertEqual(prof["total_attempts"], 1)
        self.assertEqual(prof["correct_attempts"], 1)
        self.assertIn("Banker's Algorithm", prof["topic_mastery"])
        
        if os.path.exists(test_db_path):
            os.remove(test_db_path)


if __name__ == "__main__":
    unittest.main()
