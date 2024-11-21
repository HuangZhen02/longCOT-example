import streamlit as st
import pandas as pd
import json
import re
from utils import *
import tiktoken

KEY_WORDS = ["verify", "check", "identify", "summarize", "note that", "notice that", "recall that", "wait", "realize"]

correctness_map = {
    "✅": True,
    "❌": False,
    "None": None,
    True: True,   # Adding boolean True directly
    False: False  # Adding boolean False directly
}

def visualize_monkey():
    file_path = "./data/monkey/72b_distill_v1_dpov1-1.jsonl"
    
    # 读取文件并加载所有题目数据
    with open(file_path, "r") as f:
        data = [json.loads(line) for line in f]
    
    # 添加题目选择框
    st.sidebar.header("题目选择")
    question_options = [f"{i}" for i, item in enumerate(data)]
    selected_question_idx = st.sidebar.selectbox("选择一个题目", range(len(question_options)), format_func=lambda x: question_options[x])
    selected_data = data[selected_question_idx]  # 获取用户选择的题目数据
    
    # 显示题目信息
    st.header("Problem")
    st.markdown(selected_data['question'])
    
    st.header("Gold Answer")
    st.markdown(selected_data['gold_answer'])
    
    n_response = len(selected_data['generated_responses'])
    
    st.sidebar.header("Filters")
    
    # 筛选选项
    correctness_filter = st.sidebar.radio(
        "Filter by correctness",
        options=["All", "Correct (✅)", "Incorrect (❌)"],
        index=0
    )
    
    wait_filter = st.sidebar.radio(
        "Filter by 'wait' in response",
        options=["All", "Contains 'wait'", "Does not contain 'wait'"],
        index=0
    )
    
    # 应用筛选
    filtered_indices = []
    for i, (response, correctness) in enumerate(zip(selected_data['generated_responses'], selected_data['answers_correctness'])):
        is_correct = correctness_map.get(correctness, False)
        contains_wait = "wait" in response.lower()
        
        # 应用 correctness 筛选
        if correctness_filter == "Correct (✅)" and not is_correct:
            continue
        if correctness_filter == "Incorrect (❌)" and is_correct:
            continue
        
        # 应用 'wait' 筛选
        if wait_filter == "Contains 'wait'" and not contains_wait:
            continue
        if wait_filter == "Does not contain 'wait'" and contains_wait:
            continue
        
        filtered_indices.append(i)
    
    # 显示筛选结果数量
    st.sidebar.markdown(f"**Total Responses:** {n_response}")
    st.sidebar.markdown(f"**Filtered Responses:** {len(filtered_indices)}")
    
    if not filtered_indices:
        st.warning("No responses match the selected filters.")
        return
    
    idx = st.selectbox("Select response", filtered_indices)
    
    response = selected_data['generated_responses'][idx]
    answer = selected_data['generated_answers'][idx]
    correctness = selected_data['answers_correctness'][idx]
    
    st.header("Response")
    
    if correctness_map[correctness]:
        st.markdown(f"✅")
    else:
        st.markdown(f"❌")
    
    render_markdown_with_mathjax(highlight_key_words(response.replace("\n", "<br>"), KEY_WORDS))