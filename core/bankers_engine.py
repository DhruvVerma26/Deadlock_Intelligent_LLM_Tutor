"""
Banker's Algorithm Symbolic Engine
Computes Need matrix, runs Safety Algorithm step-by-step,
validates user proposed safety sequences, and simulates Resource-Request transactions.
"""
from typing import List, Dict, Tuple, Optional
import numpy as np


class BankersEngine:
    def __init__(
        self,
        processes: List[str],
        resources: List[str],
        allocation: List[List[int]],
        max_matrix: List[List[int]],
        available: List[int]
    ):
        self.processes = processes
        self.resources = resources
        self.n = len(processes)
        self.m = len(resources)
        
        self.allocation = np.array(allocation, dtype=int)
        self.max_matrix = np.array(max_matrix, dtype=int)
        self.available = np.array(available, dtype=int)
        self.need = self.max_matrix - self.allocation

    def validate_matrices(self) -> Tuple[bool, str]:
        """Validates basic invariant conditions: Need >= 0, Allocation >= 0, Available >= 0."""
        if (self.allocation < 0).any():
            return False, "Allocation elements cannot be negative."
        if (self.max_matrix < 0).any():
            return False, "Max matrix elements cannot be negative."
        if (self.available < 0).any():
            return False, "Available resources cannot be negative."
        if (self.need < 0).any():
            return False, "Allocation exceeds Maximum claim for one or more processes (Need < 0)."
        return True, "Matrices are valid."

    def run_safety_algorithm(self) -> Dict:
        """
        Executes the Safety Algorithm and logs step-by-step traces.
        Returns whether the state is safe, the safe sequence found, and step-by-step logs.
        """
        work = self.available.copy()
        finish = [False] * self.n
        safe_sequence = []
        steps = []
        
        step_num = 1
        while len(safe_sequence) < self.n:
            found = False
            for i in range(self.n):
                if not finish[i]:
                    # Check condition: Need[i] <= Work
                    p_name = self.processes[i]
                    p_need = self.need[i].tolist()
                    current_work = work.tolist()
                    
                    if np.all(self.need[i] <= work):
                        # Process can finish
                        work_before = work.copy().tolist()
                        work += self.allocation[i]
                        finish[i] = True
                        safe_sequence.append(p_name)
                        found = True
                        
                        steps.append({
                            "step": step_num,
                            "process": p_name,
                            "need": p_need,
                            "work_before": work_before,
                            "allocated": self.allocation[i].tolist(),
                            "work_after": work.tolist(),
                            "status": "Satisfied and executed",
                            "explanation": f"Process {p_name} has Need {p_need} <= Work {work_before}. It completes and releases its allocated {self.allocation[i].tolist()}, resulting in new Work {work.tolist()}."
                        })
                        step_num += 1
                        break
                    else:
                        steps.append({
                            "step": step_num,
                            "process": p_name,
                            "need": p_need,
                            "work_before": current_work,
                            "allocated": self.allocation[i].tolist(),
                            "work_after": current_work,
                            "status": "Waiting",
                            "explanation": f"Process {p_name} has Need {p_need} > Work {current_work}. Must wait."
                        })
            
            if not found:
                # No process could proceed
                break
                
        is_safe = (len(safe_sequence) == self.n)
        return {
            "is_safe": is_safe,
            "safe_sequence": safe_sequence,
            "unfinished_processes": [self.processes[i] for i in range(self.n) if not finish[i]],
            "steps": steps,
            "final_work": work.tolist()
        }

    def verify_student_sequence(self, student_seq: List[str]) -> Tuple[bool, str, List[Dict]]:
        """
        Verifies if a specific sequence provided by a student is a valid safe sequence.
        Provides precise diagnostic feedback if incorrect.
        """
        if len(student_seq) != self.n:
            return False, f"Sequence length mismatch. Expected {self.n} processes, got {len(student_seq)}.", []
        if set(student_seq) != set(self.processes):
            return False, "The sequence does not contain each process exactly once.", []

        work = self.available.copy()
        proc_to_idx = {name: idx for idx, name in enumerate(self.processes)}
        validation_steps = []

        for step_idx, p_name in enumerate(student_seq):
            if p_name not in proc_to_idx:
                return False, f"Unknown process: {p_name}", validation_steps
            idx = proc_to_idx[p_name]
            p_need = self.need[idx]
            
            if not np.all(p_need <= work):
                error_msg = (
                    f"Step {step_idx + 1}: Process {p_name} cannot execute at this point! "
                    f"Its Need {p_need.tolist()} exceeds current Work {work.tolist()}."
                )
                validation_steps.append({
                    "step": step_idx + 1,
                    "process": p_name,
                    "valid": False,
                    "reason": error_msg
                })
                return False, error_msg, validation_steps
            
            work_before = work.tolist()
            work += self.allocation[idx]
            validation_steps.append({
                "step": step_idx + 1,
                "process": p_name,
                "valid": True,
                "need": p_need.tolist(),
                "work_before": work_before,
                "work_after": work.tolist()
            })

        return True, "Congratulations! The provided sequence is a valid Safe Sequence.", validation_steps

    def request_resources(self, process_idx: int, request_vector: List[int]) -> Dict:
        """
        Simulates the Resource-Request Algorithm for process Pi.
        """
        req = np.array(request_vector, dtype=int)
        p_name = self.processes[process_idx]
        
        # Condition 1: Request <= Need
        if not np.all(req <= self.need[process_idx]):
            exceeded = np.where(req > self.need[process_idx])[0].tolist()
            res_exceeded = [self.resources[r] for r in exceeded]
            return {
                "granted": False,
                "stage": "Request > Need",
                "message": f"Error: Process {p_name} has exceeded its maximum claim for resource(s): {', '.join(res_exceeded)}.",
                "details": f"Request {request_vector} > Need {self.need[process_idx].tolist()}"
            }
            
        # Condition 2: Request <= Available
        if not np.all(req <= self.available):
            lacking = np.where(req > self.available)[0].tolist()
            res_lacking = [self.resources[r] for r in lacking]
            return {
                "granted": False,
                "stage": "Request > Available",
                "message": f"Process {p_name} must wait because sufficient resources are not available ({', '.join(res_lacking)}).",
                "details": f"Request {request_vector} > Available {self.available.tolist()}"
            }
            
        # Speculative Allocation
        temp_available = self.available - req
        temp_allocation = self.allocation.copy()
        temp_allocation[process_idx] += req
        
        speculative_engine = BankersEngine(
            processes=self.processes,
            resources=self.resources,
            allocation=temp_allocation.tolist(),
            max_matrix=self.max_matrix.tolist(),
            available=temp_available.tolist()
        )
        
        safety_result = speculative_engine.run_safety_algorithm()
        
        if safety_result["is_safe"]:
            return {
                "granted": True,
                "stage": "Safe State Verified",
                "message": f"Request granted immediately! A safe sequence <{' -> '.join(safety_result['safe_sequence'])}> exists in the speculative state.",
                "safe_sequence": safety_result["safe_sequence"],
                "new_available": temp_available.tolist(),
                "new_allocation": temp_allocation.tolist(),
                "new_need": (self.max_matrix - temp_allocation).tolist(),
                "safety_steps": safety_result["steps"]
            }
        else:
            return {
                "granted": False,
                "stage": "Unsafe State (Deadlock Risk)",
                "message": f"Request denied/must wait. Granting request leads to an UNSAFE state with no safe sequence.",
                "unfinished": safety_result["unfinished_processes"],
                "safety_steps": safety_result["steps"]
            }
