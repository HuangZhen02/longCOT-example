import streamlit as st
import pandas as pd
import json
import re
from utils import *


def visualize_prm_800k():
    # Load the data based on user choice
    file_choice = st.sidebar.selectbox("Choose File", ["longCoT", "longCoT_with_limitation_v1", "longCoT_with_limitation_v2", "deepseek-math-7b-base-sft-math-v1", "deepseek-math-7b-base-sft-math-v2"])

    if file_choice == "longCoT_with_limitation_v1":
        df = load_data('data/prm800k_cot_from_tree_train_678_max_total_attempts_3.json')
    elif file_choice == "longCoT_with_limitation_v2":
        df = load_data('data/prm800k_cot_from_tree_train_678_max_total_attempts_3_max_attempts_2_v2.json')
    elif file_choice == "longCoT":
        df = load_data('data/prm800k_cot_from_tree_train_678.json')
    elif file_choice == "deepseek-math-7b-base-sft-math-v1":
        df = load_data('data/deepseek-math-7b-base-sft-math-v1.jsonl')
    elif file_choice == "deepseek-math-7b-base-sft-math-v2":
        df = load_data('data/deepseek-math-7b-base-sft-math-v2.jsonl')
        
    trees = read_json('data/prm800k_tree_train_678.json')

    if 'selected_example' not in st.session_state:
        st.session_state.selected_example = 1

    # Create a dictionary to hold examples by difficulty level
    difficulty_levels = {1: [], 2: [], 3: [], 4: [], 5: []}
    for index, row in df.iterrows():
        difficulty_levels[row['level']].append(index + 1)  # Assuming 'difficulty_level' is a key in your JSON

    # Sidebar for difficulty levels
    selected_level = st.sidebar.selectbox("Select Difficulty Level", [1, 2, 3, 4, 5])

    # Sidebar for example selection based on difficulty level
    example_options = difficulty_levels[selected_level]

    selected_example = st.sidebar.selectbox("Select Example", example_options)

    st.session_state.selected_example = selected_example
    
    row = df.iloc[st.session_state.selected_example - 1]
    current_tree = trees[st.session_state.selected_example - 1]

    idx_col, subject_col, difficulty_col = st.columns(3)
    
    with idx_col:
        st.header(f"Idx: {st.session_state.selected_example}")
    with subject_col:
        st.header(f"{row['subject']}")
    with difficulty_col:
        st.header(f"Level: {row['level']}")
        
    st.subheader("Question")
    st.markdown(row['question'].replace("\n", "<br>"), unsafe_allow_html=True)
    
    st.subheader("Gold Solution")
    st.markdown(row['gt_solution'].replace("\n", "<br>"), unsafe_allow_html=True)
            
    
    if file_choice.startswith("longCoT"): # sythetic longCoT
        st.subheader("Tree Structure")
        show_tree = st.checkbox("Show Tree Structure")
        if show_tree:
            tree_col, step_col = st.columns([6, 4])
            with tree_col:
                visualize_tree(current_tree['solution'])
            with step_col:
                level = st.number_input("Select tree level", min_value=0, value=0)
                
                steps_at_level = get_steps_at_level(current_tree['solution'], level)

                st.subheader(f"Steps at level {level}")
                for path, step in steps_at_level:
                    text = f"**{path}:** {step}"
                    st.write(text.replace("\n", "<br>"), unsafe_allow_html=True)
                    
                    
        st.subheader("Shortcut CoT")
        st.markdown(row['shortCOT'].replace("\n", "<br>"), unsafe_allow_html=True)
        
        st.subheader("Long CoT")
        highlighted_long_cot = highlight_wait(row['longCOT'].replace("\n", "<br>"))
        st.markdown(highlighted_long_cot, unsafe_allow_html=True)
    
    elif file_choice.startswith("deepseek-math-7b-base-sft"):
        if row['result']:
            st.subheader("Pred Solution of the model ✅")
        else:
            st.subheader("Pred Solution of the model ❌")
            
        highlighted_response = highlight_wait(row['response'].replace("\n", "<br>"))
        st.markdown(highlighted_response, unsafe_allow_html=True)