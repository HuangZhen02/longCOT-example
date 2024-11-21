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
    
    with open(file_path, "r") as f:
        data = [json.loads(line) for line in f]
    
    data = data[0]
    
    st.header("Problem")
    st.markdown(data['question'])
    
    st.header("Gold Answer")
    st.markdown(data['gold_answer'])
    
    n_response = len(data['generated_responses'])
    
    st.sidebar.header("Filters")
    
    # Filter by correctness
    correctness_filter = st.sidebar.radio(
        "Filter by correctness",
        options=["All", "Correct (✅)", "Incorrect (❌)"],
        index=0
    )
    
    # Filter by 'wait' in response
    wait_filter = st.sidebar.radio(
        "Filter by 'wait' in response",
        options=["All", "Contains 'wait'", "Does not contain 'wait'"],
        index=0
    )
    
    # Apply filters
    filtered_indices = []
    for i, (response, correctness) in enumerate(zip(data['generated_responses'], data['answers_correctness'])):
        is_correct = correctness_map.get(correctness, False)
        contains_wait = "wait" in response.lower()
        
        # Apply correctness filter
        if correctness_filter == "Correct (✅)" and not is_correct:
            continue
        if correctness_filter == "Incorrect (❌)" and is_correct:
            continue
        
        # Apply 'wait' filter
        if wait_filter == "Contains 'wait'" and not contains_wait:
            continue
        if wait_filter == "Does not contain 'wait'" and contains_wait:
            continue
        
        filtered_indices.append(i)
    
    # Display counts
    st.sidebar.markdown(f"**Total Responses:** {n_response}")
    st.sidebar.markdown(f"**Filtered Responses:** {len(filtered_indices)}")
    
    if not filtered_indices:
        st.warning("No responses match the selected filters.")
        return
    
    idx = st.selectbox("Select response", filtered_indices)
    
    response = data['generated_responses'][idx]
    answer = data['generated_answers'][idx]
    correctness = data['answers_correctness'][idx]
    
    st.header("Response")
    
    if correctness_map[correctness]:
        st.markdown(f"✅")
    else:
        st.markdown(f"❌")
    
    render_markdown_with_mathjax(highlight_key_words(response.replace("\n", "<br>"), KEY_WORDS))