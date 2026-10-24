"""
DEADLOCK LLM: Intelligent Operating Systems Tutor
Authors: Ankit Ray (24BCI0233) & Dhruv Verma (24BCI0170)
Interactive Streamlit Application implementing RAG Tutor, Banker's Algorithm Simulator,
Resource Allocation Graph Analyzer, Adaptive Practice Quiz, and Student Analytics.
"""
import sys
import os

# Ensure package root is in python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
import pandas as pd
import numpy as np
import json

from deadlock_tutor.core.bankers_engine import BankersEngine
from deadlock_tutor.core.rag_graph_engine import RAGGraphEngine
from deadlock_tutor.core.rag_retriever import DeadlockRAGRetriever
from deadlock_tutor.core.tutor_llm import DeadlockTutorLLM
from deadlock_tutor.core.evaluator import StudentEvaluator
from deadlock_tutor.core.learning_planner import LearningPlanner
from deadlock_tutor.core.database import TutorDatabase
from deadlock_tutor.utils.visualizer import DeadlockVisualizer

# Page configuration
st.set_page_config(
    page_title="Deadlock Intelligent LLM Tutor",
    page_icon="🔒",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for modern styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.2rem;
        font-weight: 800;
        color: #1e3a8a;
        margin-bottom: 0px;
    }
    .sub-header {
        font-size: 1.05rem;
        color: #4b5563;
        margin-bottom: 20px;
    }
    .metric-card {
        background-color: #f8fafc;
        border-radius: 10px;
        padding: 15px;
        border-left: 5px solid #3b82f6;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }
    .recommendation-box {
        background-color: #eff6ff;
        border: 1px solid #bfdbfe;
        border-radius: 8px;
        padding: 12px;
        margin-top: 10px;
    }
</style>
""", unsafe_allow_html=True)

# Initialize singletons in session state
if "db" not in st.session_state:
    st.session_state.db = TutorDatabase()
if "retriever" not in st.session_state:
    st.session_state.retriever = DeadlockRAGRetriever()
if "evaluator" not in st.session_state:
    st.session_state.evaluator = StudentEvaluator()
if "planner" not in st.session_state:
    st.session_state.planner = LearningPlanner()
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "hint_levels" not in st.session_state:
    st.session_state.hint_levels = {}

# Sidebar: User & System Configuration
st.sidebar.image("https://img.icons8.com/fluency/96/lock-database.png", width=64)
st.sidebar.title("Deadlock LLM")
st.sidebar.caption("Intelligent OS Tutor • v1.0")

student_id = st.sidebar.text_input("Student Registration ID", value="24BCI0170")
student_name = st.sidebar.text_input("Student Name", value="Dhruv Verma")
current_student = st.session_state.db.get_or_create_student(student_id, student_name)

# LLM provider config
with st.sidebar.expander("⚙️ LLM & Engine Settings", expanded=False):
    llm_provider = st.selectbox("LLM Provider", ["Internal Domain RAG Engine", "OpenAI (GPT-3.5/4)", "Groq (Llama-3)"])
    api_key_input = st.text_input("API Key (Optional)", type="password", help="Leave blank to use the built-in pedagogical RAG model.")
    st.session_state.tutor_llm = DeadlockTutorLLM(api_key=api_key_input if api_key_input else None)

# Adaptive Recommendation Card
student_profile = st.session_state.db.get_student_profile(student_id)
recommendation = st.session_state.planner.recommend_next_activity(student_profile)

st.sidebar.markdown("### 🎯 Adaptive Learning Path")
st.sidebar.markdown(f"""
<div class="recommendation-box">
    <strong>{recommendation['title']}</strong><br/>
    <small style="color:#1d4ed8;">{recommendation['reason']}</small><br/>
    <small><b>Target:</b> {recommendation['target_topic']}</small>
</div>
""", unsafe_allow_html=True)

st.sidebar.markdown("---")
st.sidebar.markdown("**Project Authors:**\n- Ankit Ray (24BCI0233)\n- Dhruv Verma (24BCI0170)")

# Main Header
st.markdown('<div class="main-header">🔒 Deadlock Intelligent LLM Tutor</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">AI-Powered Grounded Learning, Algorithm Tracing, and Adaptive Diagnostics for Operating Systems</div>', unsafe_allow_html=True)

# Tabs
tab_rag, tab_banker, tab_rag_graph, tab_quiz, tab_analytics = st.tabs([
    "📚 Concepts & RAG Tutor",
    "🏦 Banker's Algorithm Simulator",
    "🕸️ RAG Graph Analyzer",
    "📝 Adaptive Practice Quiz",
    "📊 Student Analytics & Profile"
])

# ==========================================
# TAB 1: RAG TUTOR
# ==========================================
with tab_rag:
    st.header("💬 Interactive Deadlock Tutor (RAG-Grounded)")
    st.markdown("Ask any conceptual question, compare strategies, or explore tricky edge cases. Explanations are strictly grounded in standard OS curriculum.")

    col_q1, col_q2 = st.columns([3, 1])
    with col_q1:
        user_prompt = st.text_input("Enter your deadlock query:", placeholder="e.g. Explain why an unsafe state is not necessarily a deadlocked state.")
    with col_q2:
        quick_topic = st.selectbox("Quick Concept Prompts", [
            "Select a prompt...",
            "What are the four Coffman necessary conditions?",
            "Compare Deadlock Prevention vs Avoidance",
            "How does Banker's safety algorithm guarantee progress?",
            "Why is a cycle in multi-instance RAG not sufficient for deadlock?",
            "Explain victim selection and starvation in deadlock recovery"
        ])

    if quick_topic != "Select a prompt..." and not user_prompt:
        user_prompt = quick_topic

    if st.button("Ask Tutor", type="primary") and user_prompt:
        with st.spinner("Retrieving textbook concepts & generating grounded explanation..."):
            response = st.session_state.tutor_llm.generate_explanation(user_prompt)
            st.session_state.chat_history.append({
                "query": user_prompt,
                "response": response["answer"],
                "sources": response["sources"],
                "engine": response["engine"]
            })

    # Render Chat History
    if st.session_state.chat_history:
        for idx, chat in enumerate(reversed(st.session_state.chat_history)):
            st.markdown(f"**🧑 Student:** {chat['query']}")
            st.markdown(chat['response'])
            
            with st.expander(f"📑 RAG Retrieved Sources & Citations (Query #{len(st.session_state.chat_history) - idx})"):
                st.caption(f"Engine: {chat['engine']}")
                for src in chat['sources']:
                    st.markdown(f"- **{src['title']}** (Topic: *{src['topic']}* | Subtopic: *{src['subtopic']}*)")
                    st.markdown(f"> *{src['content'][:250]}...*")
            st.markdown("---")

# ==========================================
# TAB 2: BANKER'S ALGORITHM SIMULATOR
# ==========================================
with tab_banker:
    st.header("🏦 Banker's Algorithm Interactive Simulator & Verifier")
    st.markdown("Step through Dijkstra's safety algorithm, test your own safe sequences, and simulate dynamic resource requests.")

    # Load presets
    base_dir = os.path.dirname(os.path.abspath(__file__))
    cases_path = os.path.join(base_dir, "data", "sample_bankers_cases.json")
    with open(cases_path, "r") as f:
        preset_cases = json.load(f)

    case_names = [c["title"] for c in preset_cases]
    selected_case_name = st.selectbox("Load Example Case", case_names)
    selected_case = next(c for c in preset_cases if c["title"] == selected_case_name)

    # Process & Resource Setup
    procs = selected_case["processes"]
    res = selected_case["resources"]
    alloc = selected_case["allocation"]
    max_m = selected_case["max"]
    avail = selected_case["available"]

    col_mat1, col_mat2 = st.columns(2)
    with col_mat1:
        st.subheader("Allocation Matrix")
        st.dataframe(pd.DataFrame(alloc, index=procs, columns=res), use_container_width=True)
        st.subheader("Available Resources")
        st.dataframe(pd.DataFrame([avail], index=["Available"], columns=res), use_container_width=True)

    with col_mat2:
        st.subheader("Max Matrix")
        st.dataframe(pd.DataFrame(max_m, index=procs, columns=res), use_container_width=True)
        need_calc = (np.array(max_m) - np.array(alloc)).tolist()
        st.subheader("Calculated Need Matrix (Max - Allocation)")
        st.dataframe(pd.DataFrame(need_calc, index=procs, columns=res), use_container_width=True)

    # Banker Engine instance
    b_engine = BankersEngine(procs, res, alloc, max_m, avail)

    # Visualization
    fig_matrix = DeadlockVisualizer.plot_bankers_matrix(procs, res, alloc, need_calc, avail)
    st.pyplot(fig_matrix)

    st.markdown("---")
    sim_tab1, sim_tab2, sim_tab3 = st.tabs(["▶️ Run Safety Algorithm", "✍️ Test Your Safe Sequence", "📩 Simulate Resource Request"])

    with sim_tab1:
        if st.button("Execute Safety Step-by-Step", type="primary"):
            safety_res = b_engine.run_safety_algorithm()
            if safety_res["is_safe"]:
                st.success(f"🎉 **System is in a SAFE STATE!**\nSafe Sequence found: `{' -> '.join(safety_res['safe_sequence'])}`")
            else:
                st.error(f"⚠️ **System is in an UNSAFE STATE (Potential Deadlock)!**\nUnfinished processes: {safety_res['unfinished_processes']}")

            st.markdown("#### Execution Trace Details:")
            for s in safety_res["steps"]:
                status_color = "🟢" if "Satisfied" in s["status"] else "⚪"
                st.markdown(f"{status_color} **Step {s['step']}: Process {s['process']}** — {s['explanation']}")

    with sim_tab2:
        st.markdown("Verify whether your proposed sequence will safely complete execution without deadlocks.")
        seq_input = st.text_input("Enter sequence (e.g., P1, P3, P4, P0, P2):", value="P1, P3, P4, P0, P2")
        if st.button("Verify My Sequence"):
            eval_res = st.session_state.evaluator.evaluate_safe_sequence(seq_input, b_engine)
            if eval_res["is_correct"]:
                st.success(f"✅ {eval_res['feedback']}")
                st.session_state.db.log_quiz_attempt(
                    student_id, "SEQ_VERIFY", "numerical", "Banker's Algorithm", seq_input, True, 1.0
                )
            else:
                st.error(f"❌ {eval_res['feedback']}")
                st.session_state.db.log_quiz_attempt(
                    student_id, "SEQ_VERIFY", "numerical", "Banker's Algorithm", seq_input, False, 0.0
                )

            if eval_res.get("validation_steps"):
                with st.expander("Step-by-step trace of your sequence:"):
                    for vs in eval_res["validation_steps"]:
                        if vs["valid"]:
                            st.markdown(f"✔️ **Step {vs['step']} ({vs['process']})**: Need {vs['need']} <= Work {vs['work_before']}. New Work: {vs['work_after']}")
                        else:
                            st.markdown(f"❌ **{vs['reason']}**")

    with sim_tab3:
        st.markdown("Simulate process $P_i$ requesting additional resources: $\\text{Request}[i]$.")
        req_p = st.selectbox("Requesting Process", procs)
        req_p_idx = procs.index(req_p)
        req_inputs = []
        req_cols = st.columns(len(res))
        for idx_r, r in enumerate(res):
            with req_cols[idx_r]:
                req_val = st.number_input(f"Request {r}", min_value=0, max_value=15, value=1 if idx_r == 0 else 0)
                req_inputs.append(req_val)

        if st.button("Evaluate Request"):
            req_result = b_engine.request_resources(req_p_idx, req_inputs)
            if req_result["granted"]:
                st.success(f"✅ **REQUEST GRANTED!**\n{req_result['message']}")
                st.info(f"New Available: {req_result['new_available']}")
            else:
                st.error(f"⛔ **REQUEST DENIED / MUST WAIT!**\nStage: {req_result['stage']}\n{req_result['message']}")

# ==========================================
# TAB 3: RAG GRAPH ANALYZER
# ==========================================
with tab_rag_graph:
    st.header("🕸️ Resource Allocation Graph (RAG) Analyzer")
    st.markdown("Explore single-instance vs. multi-instance RAGs, detect graph cycles via NetworkX, and run graph reductions.")

    rag_preset = st.selectbox("Select Preset Graph Scenario", [
        "1. Single Instance with Cycle (Deadlock)",
        "2. Single Instance without Cycle (Safe)",
        "3. Multi-Instance with Cycle (Safe through Reduction)",
        "4. Multi-Instance with Unresolvable Cycle (Deadlock)"
    ])

    graph_engine = RAGGraphEngine()

    if "1. Single Instance with Cycle" in rag_preset:
        graph_engine.add_resource("R1", 1)
        graph_engine.add_resource("R2", 1)
        graph_engine.add_allocation("R1", "P1")
        graph_engine.add_request("P1", "R2")
        graph_engine.add_allocation("R2", "P2")
        graph_engine.add_request("P2", "R1")
    elif "2. Single Instance without Cycle" in rag_preset:
        graph_engine.add_resource("R1", 1)
        graph_engine.add_resource("R2", 1)
        graph_engine.add_allocation("R1", "P1")
        graph_engine.add_request("P1", "R2")
        graph_engine.add_allocation("R2", "P2")
    elif "3. Multi-Instance with Cycle (Safe" in rag_preset:
        graph_engine.add_resource("R1", 2)
        graph_engine.add_resource("R2", 2)
        graph_engine.add_allocation("R1", "P1")
        graph_engine.add_allocation("R1", "P2")
        graph_engine.add_allocation("R2", "P3")
        graph_engine.add_request("P1", "R2")
        graph_engine.add_request("P2", "R2")
        # P3 holds R2 and has no requests, so P3 will finish and release R2!
    else:
        graph_engine.add_resource("R1", 2)
        graph_engine.add_resource("R2", 2)
        graph_engine.add_allocation("R1", "P1")
        graph_engine.add_allocation("R1", "P2")
        graph_engine.add_allocation("R2", "P3")
        graph_engine.add_allocation("R2", "P4")
        graph_engine.add_request("P1", "R2")
        graph_engine.add_request("P2", "R2")
        graph_engine.add_request("P3", "R1")
        graph_engine.add_request("P4", "R1")

    fig_rag = DeadlockVisualizer.draw_rag(graph_engine, title=rag_preset)
    st.pyplot(fig_rag)

    st.markdown("### 🔍 Deadlock Analysis Results")
    analysis = graph_engine.analyze_deadlock()

    col_an1, col_an2 = st.columns(2)
    with col_an1:
        if analysis["deadlock_present"]:
            st.error(f"🚨 **Deadlock Present**: YES\nDeadlocked Processes: `{analysis['deadlocked_processes']}`")
        else:
            st.success("✅ **Deadlock Present**: NO (System can proceed safely)")

        st.info(f"Cycles Detected: {len(analysis['cycles'])}")
        if analysis["cycles"]:
            for c in analysis["cycles"]:
                st.code(" -> ".join(c) + " -> " + c[0])

    with col_an2:
        st.markdown("**Pedagogical Explanation:**")
        st.write(analysis["explanation"])

# ==========================================
# TAB 4: ADAPTIVE PRACTICE QUIZ & VIVA
# ==========================================
with tab_quiz:
    st.header("📝 Adaptive Practice Quiz & Viva")
    st.markdown("Test your deadlock knowledge. Receive instant feedback, progressive hints, and misconception diagnostics.")

    q_path = os.path.join(base_dir, "data", "questions_bank.json")
    with open(q_path, "r") as f:
        questions_bank = json.load(f)

    q_selector = st.selectbox(
        "Select Practice Problem",
        [f"{q['id']} - {q['topic']} ({q['type'].upper()} | {q['difficulty']})" for q in questions_bank]
    )
    current_q = next(q for q in questions_bank if q["id"] == q_selector.split(" - ")[0])

    st.markdown(f"### {current_q['question']}")

    # Progressive Hints System
    q_id = current_q["id"]
    if q_id not in st.session_state.hint_levels:
        st.session_state.hint_levels[q_id] = 0

    col_h1, col_h2 = st.columns([1, 4])
    with col_h1:
        if st.button("💡 Need a Hint?"):
            st.session_state.hint_levels[q_id] += 1

    with col_h2:
        lvl = st.session_state.hint_levels[q_id]
        if lvl > 0:
            hint_txt = st.session_state.evaluator.get_progressive_hint(current_q, lvl)
            st.info(f"**Hint (Level {lvl}):** {hint_txt}")

    # Handling different question types
    if current_q["type"] == "mcq":
        user_choice = st.radio("Choose the correct option:", current_q["options"])
        if st.button("Submit Answer", key=f"btn_{q_id}"):
            eval_res = st.session_state.evaluator.evaluate_mcq(current_q, user_choice)
            if eval_res["is_correct"]:
                st.success(eval_res["feedback"])
            else:
                st.error(eval_res["feedback"])
            st.markdown(f"**Explanation:** {eval_res['explanation']}")
            st.session_state.db.log_quiz_attempt(
                student_id, q_id, "mcq", current_q["topic"], user_choice, eval_res["is_correct"], eval_res["score"]
            )

    elif current_q["type"] == "numerical":
        user_ans = st.text_input("Enter the Safe Sequence:", placeholder="e.g. <P1, P3, P4, P0, P2>")
        if st.button("Submit Numerical Answer", key=f"btn_num_{q_id}"):
            is_match = ("p1" in user_ans.lower() and "p3" in user_ans.lower() and "p4" in user_ans.lower())
            score = 1.0 if is_match else 0.0
            if is_match:
                st.success("🎯 Correct! Safe Sequence matches the Banker's safety criteria.")
            else:
                st.error(f"❌ Incorrect. Expected Sequence: {current_q['correct_answer']}")
            st.markdown(f"**Detailed Solution:** {current_q['explanation']}")
            st.session_state.db.log_quiz_attempt(
                student_id, q_id, "numerical", current_q["topic"], user_ans, is_match, score
            )

    elif current_q["type"] == "viva":
        user_viva = st.text_area("Your Explanation / Viva Answer:", placeholder="Write your detailed explanation here...")
        if st.button("Submit Viva Response", key=f"btn_viva_{q_id}"):
            eval_res = st.session_state.evaluator.evaluate_viva_text(current_q, user_viva)
            st.info(f"**Score:** {int(eval_res['score'] * 100)}/100")
            st.markdown(f"**Evaluator Feedback:** {eval_res['feedback']}")
            if eval_res["detected_misconceptions"]:
                st.warning(f"Detected Misconceptions: {eval_res['detected_misconceptions']}")
                for m in eval_res["detected_misconceptions"]:
                    st.session_state.db.log_misconception(student_id, m, context=q_id)
            st.markdown(f"**Sample Ideal Answer:** {eval_res['reference_answer']}")
            st.session_state.db.log_quiz_attempt(
                student_id, q_id, "viva", current_q["topic"], user_viva, eval_res["score"] >= 0.6, eval_res["score"]
            )

# ==========================================
# TAB 5: STUDENT ANALYTICS & PROFILE
# ==========================================
with tab_analytics:
    st.header("📊 Student Learning Profile & Mastery Analytics")
    updated_profile = st.session_state.db.get_student_profile(student_id)

    col_m1, col_m2, col_m3 = st.columns(3)
    with col_m1:
        st.metric("Total Problems Attempted", updated_profile["total_attempts"])
    with col_m2:
        st.metric("Correct Solutions", updated_profile["correct_attempts"])
    with col_m3:
        overall_ready = st.session_state.planner.compute_overall_readiness(updated_profile["topic_mastery"])
        st.metric("Overall Deadlock Mastery", f"{overall_ready}%")

    st.markdown("### Topic-Wise Mastery Distribution")
    if updated_profile["topic_mastery"]:
        fig_mastery = DeadlockVisualizer.plot_student_mastery(updated_profile["topic_mastery"])
        st.pyplot(fig_mastery)
    else:
        st.info("No attempts recorded yet. Solve questions in the Practice Quiz tab to build your mastery profile!")

    if updated_profile["misconceptions"]:
        st.markdown("### ⚠️ Tracked Misconceptions & Targeted Interventions")
        for mis in updated_profile["misconceptions"]:
            st.warning(f"• **{mis}**: System has scheduled targeted review in your adaptive learning path.")

    st.markdown("### 📋 Student Progress Record")
    st.dataframe(pd.DataFrame([
        {"Topic": t, "Mastery Score": f"{score*100:.1f}%"}
        for t, score in updated_profile["topic_mastery"].items()
    ]), use_container_width=True)
