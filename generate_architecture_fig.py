"""
Generates high-resolution architecture flowchart diagram for Deadlock LLM Tutor.
"""
import os
import matplotlib.pyplot as plt
import matplotlib.patches as patches

output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "report_assets")
os.makedirs(output_dir, exist_ok=True)

fig, ax = plt.subplots(figsize=(10, 5), dpi=200)
ax.set_facecolor("#f8fafc")
fig.patch.set_facecolor("#f8fafc")

# Box definition helper
def draw_card(ax, x, y, w, h, title, subtitle, bg_color="#ffffff", border_color="#3b82f6", text_color="#1e293b"):
    rect = patches.FancyBboxPatch(
        (x, y), w, h,
        boxstyle="round,pad=0.04,rounding_size=0.08",
        facecolor=bg_color,
        edgecolor=border_color,
        linewidth=1.8,
        zorder=2
    )
    ax.add_patch(rect)
    ax.text(x + w/2, y + h*0.65, title, fontsize=9.5, fontweight="bold", color=text_color, ha="center", va="center", zorder=3)
    ax.text(x + w/2, y + h*0.3, subtitle, fontsize=7.5, color="#64748b", ha="center", va="center", zorder=3)

# Arrow helper
def draw_arrow(ax, x1, y1, x2, y2, label=""):
    ax.annotate(
        "", xy=(x2, y2), xytext=(x1, y1),
        arrowprops=dict(arrowstyle="-|>", color="#0284c7", lw=1.8, mutation_scale=14),
        zorder=4
    )
    if label:
        ax.text((x1+x2)/2, (y1+y2)/2 + 0.04, label, fontsize=7.0, color="#0369a1", ha="center", va="bottom", fontweight="bold", zorder=5)

# Layer 1: Client & Interface
draw_card(ax, 0.05, 0.65, 0.22, 0.24, "Student Interface", "Streamlit Web Application\n(5 Interactive Tabs)", "#eff6ff", "#2563eb", "#1e3a8a")

# Layer 2: Adaptive Planner
draw_card(ax, 0.38, 0.65, 0.24, 0.24, "Learning Planner", "Diagnostic Knowledge Tracing\n& Topic Scheduler", "#f0fdf4", "#16a34a", "#14532d")

# Layer 3: RAG & LLM
draw_card(ax, 0.72, 0.65, 0.24, 0.24, "RAG & LLM Tutor", "BM25 Retriever + Grounded LLM\n(Silberschatz OS Knowledge)", "#faf5ff", "#9333ea", "#581c87")

# Layer 4: Symbolic Solvers (Lower row)
draw_card(ax, 0.72, 0.15, 0.24, 0.26, "Symbolic Engine", "Banker's Safety & Speculation\nNetworkX RAG Cycle Reducer", "#fff7ed", "#ea580c", "#7c2d12")

# Layer 5: Evaluator & Misconceptions
draw_card(ax, 0.38, 0.15, 0.24, 0.26, "Student Evaluator", "Sequence Verifier, Misconception\nDetector & Progressive Hints", "#fef2f2", "#dc2626", "#7f1d1d")

# Layer 6: Persistence Profile
draw_card(ax, 0.05, 0.15, 0.22, 0.26, "Student Profile DB", "SQLite Database\n(Mastery, Attempts, History)", "#f1f5f9", "#475569", "#0f172a")

# Connecting Arrows (The Learning Cycle)
draw_arrow(ax, 0.27, 0.77, 0.38, 0.77, "Query / Action")
draw_arrow(ax, 0.62, 0.77, 0.72, 0.77, "Select Activity")
draw_arrow(ax, 0.84, 0.65, 0.84, 0.41, "Symbolic Math Hook")
draw_arrow(ax, 0.72, 0.28, 0.62, 0.28, "Verified Traces")
draw_arrow(ax, 0.38, 0.28, 0.27, 0.28, "Log Mastery")
draw_arrow(ax, 0.16, 0.41, 0.16, 0.65, "Adaptive Path")

# Direct user response flow
ax.annotate(
    "", xy=(0.50, 0.41), xytext=(0.20, 0.65),
    arrowprops=dict(arrowstyle="-|>", color="#dc2626", lw=1.5, ls="--", mutation_scale=12),
    zorder=4
)
ax.text(0.33, 0.52, "Student Solution", fontsize=7.0, color="#b91c1c", rotation=36, ha="center", va="center", fontweight="bold")

ax.set_xlim(0, 1.0)
ax.set_ylim(0.05, 0.98)
ax.axis("off")
plt.title("Deadlock Intelligent LLM Tutor — Neuro-Symbolic System Architecture", fontsize=12, fontweight="bold", pad=12, color="#0f172a")
plt.tight_layout()

save_path = os.path.join(output_dir, "fig_architecture.png")
plt.savefig(save_path, facecolor="#f8fafc", bbox_inches="tight")
plt.close(fig)
print("Architecture figure generated:", save_path)
