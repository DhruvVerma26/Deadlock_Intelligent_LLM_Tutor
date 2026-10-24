"""
Resource Allocation Graph (RAG) Engine
Implements bipartite directed graphs of Processes and Resources using NetworkX.
Detects cycles, analyzes single-instance vs multi-instance deadlock semantics,
and provides graph reduction / knot analysis.
"""
from typing import List, Dict, Tuple, Set
import networkx as nx


class RAGGraphEngine:
    def __init__(self):
        self.graph = nx.DiGraph()
        self.processes: Set[str] = set()
        self.resources: Dict[str, int] = {}  # resource_name -> total_instances
        self.allocation_edges: List[Tuple[str, str]] = []  # (resource, process)
        self.request_edges: List[Tuple[str, str]] = []     # (process, resource)

    def add_process(self, process_name: str):
        self.processes.add(process_name)
        self.graph.add_node(process_name, node_type="process")

    def add_resource(self, resource_name: str, instances: int = 1):
        self.resources[resource_name] = instances
        self.graph.add_node(resource_name, node_type="resource", instances=instances)

    def add_allocation(self, resource: str, process: str):
        """Resource is assigned to Process (R -> P)"""
        if resource not in self.resources:
            self.add_resource(resource, 1)
        if process not in self.processes:
            self.add_process(process)
        self.graph.add_edge(resource, process, edge_type="allocation")
        self.allocation_edges.append((resource, process))

    def add_request(self, process: str, resource: str):
        """Process requests Resource (P -> R)"""
        if process not in self.processes:
            self.add_process(process)
        if resource not in self.resources:
            self.add_resource(resource, 1)
        self.graph.add_edge(process, resource, edge_type="request")
        self.request_edges.append((process, resource))

    def find_all_cycles(self) -> List[List[str]]:
        """Finds all simple cycles in the directed graph."""
        try:
            return list(nx.simple_cycles(self.graph))
        except Exception:
            return []

    def analyze_deadlock(self) -> Dict:
        """
        Comprehensive deadlock analysis:
        1. Checks for cycles.
        2. Determines if all involved resources are single-instance.
        3. For single-instance resources: Cycle <=> Deadlock.
        4. For multi-instance resources: Runs graph reduction algorithm.
        """
        cycles = self.find_all_cycles()
        has_cycles = len(cycles) > 0
        all_single_instance = all(inst == 1 for inst in self.resources.values())

        if not has_cycles:
            return {
                "deadlock_present": False,
                "has_cycles": False,
                "cycles": [],
                "single_instance_only": all_single_instance,
                "deadlocked_processes": [],
                "reduced_sequence": list(self.processes),
                "explanation": (
                    "No cycles exist in the Resource Allocation Graph. "
                    "According to RAG theorems, if there are no cycles, the system cannot be in a deadlock."
                )
            }

        if all_single_instance:
            # Single-instance theorem: Cycle is necessary and sufficient
            deadlocked_procs = set()
            for cycle in cycles:
                for node in cycle:
                    if node in self.processes:
                        deadlocked_procs.add(node)
            return {
                "deadlock_present": True,
                "has_cycles": True,
                "cycles": cycles,
                "single_instance_only": True,
                "deadlocked_processes": sorted(list(deadlocked_procs)),
                "reduced_sequence": [],
                "explanation": (
                    f"Deadlock Detected! The graph contains cycle(s) ({cycles}) and each resource type has exactly 1 instance. "
                    f"In single-instance RAG, a cycle is BOTH necessary and sufficient for deadlock. "
                    f"Deadlocked processes: {', '.join(sorted(list(deadlocked_procs)))}."
                )
            }

        # Multi-instance reduction algorithm
        # A process Pi can be reduced if all its requested resources can be satisfied by currently available instances
        reduction_result = self._reduce_graph()
        return {
            "deadlock_present": reduction_result["deadlock_present"],
            "has_cycles": True,
            "cycles": cycles,
            "single_instance_only": False,
            "deadlocked_processes": reduction_result["deadlocked_processes"],
            "reduced_sequence": reduction_result["reduced_sequence"],
            "explanation": reduction_result["explanation"]
        }

    def _reduce_graph(self) -> Dict:
        """Graph reduction for multi-instance resource systems."""
        # Calculate available instances
        allocated_count = {r: 0 for r in self.resources}
        for r, p in self.allocation_edges:
            allocated_count[r] += 1
            
        available = {r: self.resources[r] - allocated_count[r] for r in self.resources}
        
        # Track pending requests per process
        requests_per_proc = {p: {} for p in self.processes}
        for p, r in self.request_edges:
            requests_per_proc[p][r] = requests_per_proc[p].get(r, 0) + 1
            
        allocations_per_proc = {p: {} for p in self.processes}
        for r, p in self.allocation_edges:
            allocations_per_proc[p][r] = allocations_per_proc[p].get(r, 0) + 1

        active_procs = set(self.processes)
        reduced_sequence = []
        
        while True:
            progress = False
            for p in list(active_procs):
                # Check if process p can complete: requests <= available
                can_finish = True
                for r, req_count in requests_per_proc[p].items():
                    if req_count > available.get(r, 0):
                        can_finish = False
                        break
                
                if can_finish:
                    # Process finishes and releases all allocated resources
                    for r, alloc_count in allocations_per_proc[p].items():
                        available[r] += alloc_count
                    reduced_sequence.append(p)
                    active_procs.remove(p)
                    progress = True
                    break
                    
            if not progress:
                break
                
        deadlocked = sorted(list(active_procs))
        is_deadlock = len(deadlocked) > 0
        
        if is_deadlock:
            expl = (
                f"Deadlock Detected in Multi-Instance RAG! After graph reduction, the following processes "
                f"cannot finish: {', '.join(deadlocked)}. Even though other processes were reduced ({reduced_sequence}), "
                f"the remaining processes form an unbreakable circular dependency."
            )
        else:
            expl = (
                f"No Deadlock! Even though cycles exist in the graph, the graph can be completely reduced "
                f"in sequence <{' -> '.join(reduced_sequence)}>. Processes outside the deadlock cycle released their resources, "
                f"allowing all processes to eventually execute."
            )

        return {
            "deadlock_present": is_deadlock,
            "deadlocked_processes": deadlocked,
            "reduced_sequence": reduced_sequence,
            "explanation": expl
        }
