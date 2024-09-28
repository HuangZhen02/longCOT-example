import streamlit as st
import pandas as pd
import json
import re
from utils import *


def visualize_prm_800k():
    # Load the data based on user choice
    
    file_type = st.sidebar.selectbox("Choose File Type", ["Synthetic longCoT", "SFT Results"])
    
    if file_type == "Synthetic longCoT":
        file_choice = st.multiselect("Choose 1 or 2 Files", [os.path.splitext(file)[0] for file in os.listdir('./data/longCoT_from_prm800k/') if file.endswith('.json')], max_selections=2)
        if len(file_choice) == 1:    
            df = load_data(f'data/longCoT_from_prm800k/{file_choice[0]}.json')
        elif len(file_choice) == 2:
            df = load_data(f'data/longCoT_from_prm800k/{file_choice[0]}.json')
            df_compare = load_data(f'data/longCoT_from_prm800k/{file_choice[1]}.json')
        else:
            st.warning("Please select at least 1 file to continue.")
            st.stop()
            
        trees = read_json('data/prm800k_tree_train_678.json')
        
    elif file_type == "SFT Results":
        with st.sidebar:
            show_baseline = st.checkbox("Show Baseline")
            if show_baseline:
                
                def calculate_overall_accuracy(df):
                    overall_count = 0
                    correct_count = 0
                    for index, row in df.iterrows():
                        overall_count += 1
                        if row['result']:
                            correct_count += 1
                    return correct_count / overall_count
                            
                accuracy_list = []
                for file in os.listdir('./data/sft_results/'):
                    if file.endswith('.jsonl'):
                        file_path = os.path.join('./data/sft_results/', file)
                        result_df = load_data(file_path)
                        accuracy = calculate_overall_accuracy(result_df)
                        # 将文件名和准确率存入列表
                        accuracy_list.append((os.path.splitext(file)[0], accuracy))

                accuracy_list.sort(key=lambda x: x[1])

                for file_name, accuracy in accuracy_list:
                    st.write(f"{file_name}: {accuracy}")
                
        
        file_choice = st.multiselect("Choose 1 or 2 Files", [os.path.splitext(file)[0] for file in os.listdir('./data/SFT_results/') if file.endswith('.jsonl')], max_selections=2)
        if len(file_choice) == 1:
            df = load_data(f'data/sft_results/{file_choice[0]}.jsonl')
        elif len(file_choice) == 2:
            df = load_data(f'data/sft_results/{file_choice[0]}.jsonl')
            df_compare = load_data(f'data/sft_results/{file_choice[1]}.jsonl')
        else:
            st.warning("Please select at least 1 file to continue.")
            st.stop()
            
        

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
    
    if len(file_choice) == 2:
        row_compare = df_compare.iloc[st.session_state.selected_example - 1]
        

    

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
            
    
    if file_type == "Synthetic longCoT": # sythetic longCoT
        st.subheader("Tree Structure")
        show_tree = st.checkbox("Show Tree Structure")
        current_tree = trees[st.session_state.selected_example - 1]
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
        
        
        st.subheader("Synthetic Long CoT")
        
        def show_long_cot(row, version):
            st.subheader(f"**LongCoT-{version}**")
            highlighted_long_cot = highlight_wait(row['longCOT'].replace("\n", "<br>"))
            st.markdown(highlighted_long_cot, unsafe_allow_html=True)
        
        if len(file_choice) == 2:
            left, right = st.columns(2)
            with left:
                show_long_cot(row, file_choice[0])
            with right:
                show_long_cot(row_compare, file_choice[1])
        elif len(file_choice) == 1:
            show_long_cot(row, file_choice[0])
    
    elif file_type == "SFT Results":
        
        def show_pred_result(row, model_name):
            if row['result']:
                st.subheader(f"Pred of {model_name} ✅")
            else:
                st.subheader(f"Pred of {model_name} ❌")
                
            highlighted_response = highlight_wait(row['response'].replace("\n", "<br>"))
            st.markdown(highlighted_response, unsafe_allow_html=True)
            
        
        if len(file_choice) == 2:
            left, right = st.columns(2)
            with left:
                show_pred_result(row, file_choice[0])
            with right:
                show_pred_result(row_compare, file_choice[1])
        
        elif len(file_choice) == 1:
            show_pred_result(row, file_choice[0])