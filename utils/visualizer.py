"""
Visualization Utilities for Deadlock Tutor
Generates Matplotlib diagrams for Resource Allocation Graphs (RAG),
Banker's Algorithm matrices, and Student Performance radar/bar charts.
"""
import os
import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
from typing import Dict, List, Optional


class DeadlockVisualizer:
    @staticmethod
    def draw_rag(
        graph_engine,
        save_path: Optional[str] = None,
        title: str = "Resource Allocation Graph (RAG)"
    ):
        """
        Draws a bipartite directed graph: Processes (Circles, Cyan) and Resources (Squares, Orange).
        Edges in Red are cycles/deadlock paths.
        """
        fig, ax = plt.subplots(figsize=(8, 6), dpi=150)
        G = graph_engine.graph

        pos = {}
        # Layout processes on left, resources on right
        proc_list = sorted(list(graph_engine.processes))
        res_list = sorted(list(graph_engine.resources.keys()))

        for idx, p in enumerate(proc_list):
            y_pos = (len(proc_list) - idx) / max(1, len(proc_list) + 1)
            pos[p] = np.array([-1.0, y_pos])

        for idx, r in enumerate(res_list):
            y_pos = (len(res_list) - idx) / max(1, len(res_list) + 1)
            pos[r] = np.array([1.0, y_pos])

        # Node colors & shapes
        node_colors = []
        node_labels = {}
        for node in G.nodes():
            if node in graph_engine.processes:
                node_colors.append("#60a5fa")  # light blue
                node_labels[node] = f"Proc\n{node}"
            else:
                node_colors.append("#f59e0b")  # amber
                inst = graph_engine.resources.get(node, 1)
                node_labels[node] = f"Res {node}\n({inst} inst)"

        # Draw nodes
        nx.draw_networkx_nodes(
            G, pos,
            node_color=node_colors,
            node_size=2400,
            edgecolors="#1e293b",
            linewidths=2,
            ax=ax
        )
        nx.draw_networkx_labels(G, pos, labels=node_labels, font_size=9, font_weight="bold", ax=ax)

        # Draw edges: distinguish assignment vs request
        alloc_edges = [e for e in G.edges() if G.edges[e].get("edge_type") == "allocation"]
        req_edges = [e for e in G.edges() if G.edges[e].get("edge_type") == "request"]

        # Allocation edges (Green: R -> P)
        nx.draw_networkx_edges(
            G, pos,
            edgelist=alloc_edges,
            edge_color="#10b981",
            width=2.5,
            arrowsize=20,
            arrowstyle="->",
            connectionstyle="arc3,rad=0.1",
            ax=ax,
            label="Allocation (Held)"
        )

        # Request edges (Crimson: P -> R)
        nx.draw_networkx_edges(
            G, pos,
            edgelist=req_edges,
            edge_color="#ef4444",
            width=2.5,
            arrowsize=20,
            arrowstyle="->",
            connectionstyle="arc3,rad=-0.1",
            ax=ax,
            label="Request (Waiting)"
        )

        ax.set_title(title, fontsize=13, fontweight="bold", pad=15)
        ax.axis("off")
        plt.tight_layout()

        if save_path:
            os.makedirs(os.path.dirname(os.path.abspath(save_path)), exist_ok=True)
            plt.savefig(save_path, bbox_inches="tight")
            plt.close(fig)
            return save_path

        return fig

    @staticmethod
    def plot_bankers_matrix(
        processes: List[str],
        resources: List[str],
        allocation: List[List[int]],
        need: List[List[int]],
        available: List[int],
        save_path: Optional[str] = None
    ):
        """Generates a side-by-side comparative bar chart of Allocation vs Need per process."""
        fig, ax = plt.subplots(figsize=(9, 4.5), dpi=150)
        alloc_arr = np.array(allocation)
        need_arr = np.array(need)

        x = np.arange(len(processes))
        total_width = 0.8
        n_res = len(resources)
        width_per_bar = total_width / (n_res * 2)

        for j, res in enumerate(resources):
            ax.bar(
                x + j * width_per_bar - (total_width / 4),
                alloc_arr[:, j],
                width=width_per_bar,
                label=f"Alloc {res}",
                alpha=0.85
            )
            ax.bar(
                x + j * width_per_bar + (total_width / 4),
                need_arr[:, j],
                width=width_per_bar,
                label=f"Need {res}",
                alpha=0.85,
                hatch="//"
            )

        ax.set_xticks(x)
        ax.set_xticklabels(processes, fontweight="bold")
        ax.set_ylabel("Resource Instances", fontweight="bold")
        ax.set_title(f"Banker's Current State (Available: {dict(zip(resources, available))})", fontsize=12, fontweight="bold")
        ax.legend(bbox_to_anchor=(1.02, 1), loc="upper left", fontsize=8)
        ax.grid(axis="y", linestyle="--", alpha=0.5)
        plt.tight_layout()

        if save_path:
            os.makedirs(os.path.dirname(os.path.abspath(save_path)), exist_ok=True)
            plt.savefig(save_path, bbox_inches="tight")
            plt.close(fig)
            return save_path

        return fig

    @staticmethod
    def plot_student_mastery(
        topic_mastery: Dict[str, float],
        save_path: Optional[str] = None
    ):
        """Horizontal bar chart showing topic-wise mastery levels."""
        fig, ax = plt.subplots(figsize=(8, 4), dpi=150)
        topics = list(topic_mastery.keys())
        scores = [topic_mastery[t] * 100 for t in topics]

        colors = ["#ef4444" if s < 50 else "#f59e0b" if s < 75 else "#10b981" for s in scores]
        bars = ax.barh(topics, scores, color=colors, height=0.55)

        ax.set_xlim(0, 100)
        ax.set_xlabel("Mastery Level (%)", fontweight="bold")
        ax.set_title("Student Topic-Wise Mastery Profile", fontsize=12, fontweight="bold")
        ax.axvline(75, color="#10b981", linestyle="--", alpha=0.7, label="Mastery Threshold (75%)")
        ax.grid(axis="x", linestyle="--", alpha=0.5)

        for bar, score in zip(bars, scores):
            ax.text(score + 1.5, bar.get_y() + bar.get_height() / 2, f"{score:.1f}%", va="center", fontsize=8, fontweight="bold")

        plt.tight_layout()

        if save_path:
            os.makedirs(os.path.dirname(os.path.abspath(save_path)), exist_ok=True)
            plt.savefig(save_path, bbox_inches="tight")
            plt.close(fig)
            return save_path

        return fig
