import streamlit as st
import pandas as pd
import json
import re
from utils import *


correctness_map = {
    "✅": True,
    "❌": False,
    "None": "None"
}

def calculate_overall_accuracy(df):
    correct_count = df['result'].sum()
    overall_count = len(df)
    return correct_count / overall_count if overall_count > 0 else 0

def display_baseline(sft_dir):
    accuracy_list = []
    for file in os.listdir(sft_dir):
        if file.endswith('.jsonl'):
            file_path = os.path.join(sft_dir, file)
            result_df = load_data(file_path)
            accuracy = calculate_overall_accuracy(result_df)
            accuracy_list.append((os.path.splitext(file)[0], accuracy))

    accuracy_df = pd.DataFrame(accuracy_list, columns=['File Name', 'Accuracy']).sort_values(by='Accuracy').reset_index(drop=True)
    
    st.dataframe(accuracy_df)
        
        
def filter_correct_problems_1(df):
    correctness = st.selectbox("Select correctness", ["None", "✅", "❌"])
    
    if correctness == "None":
        return df
    
    matching_indices = []
    for idx in df.index:
        if df.at[idx, 'result'] == correctness_map[correctness]:
            matching_indices.append(idx)
    filtered_df = df.loc[matching_indices]
    return filtered_df

def filter_correct_problems_2(df1, df2):
    left, right = st.columns(2)
    with left:
        correctness1 = st.selectbox("Select correctness for the first file", ["None", "✅", "❌"])
    with right:
        correctness2 = st.selectbox("Select correctness for the second file", ["None", "✅", "❌"])
    
    matching_indices = []

    for idx in df1.index:
        assert df1.at[idx, 'id'] == df2.at[idx, 'id']
        
        result1 = df1.at[idx, 'result']
        result2 = df2.at[idx, 'result']
        
        if ((correctness1 == "None" or result1 == correctness_map[correctness1]) and
            (correctness2 == "None" or result2 == correctness_map[correctness2])):
            matching_indices.append(idx)
    
    filtered_df1 = df1.loc[matching_indices]
    filtered_df2 = df2.loc[matching_indices]
    
    return filtered_df1, filtered_df2


def filter_wait_statement_1(df, key="response"):
    wait_flag = st.selectbox("Whether there is a wait statement", ["None", "✅", "❌"])
    
    if wait_flag == "None":
        return df
    
    matching_indices = []
    for idx in df.index:
        if ("wait," in df.at[idx, key].lower()) == correctness_map[wait_flag]:
            matching_indices.append(idx)
    filtered_df = df.loc[matching_indices]
    return filtered_df
    
def filter_wait_statement_2(df1, df2, key="response"):
    left, right = st.columns(2)
    with left:
        wait_flag1 = st.selectbox("Whether there is a wait statement in the first file", ["None", "✅", "❌"])
    with right:
        wait_flag2 = st.selectbox("Whether there is a wait statement in the second file", ["None", "✅", "❌"])
        
    matching_indices = []
    
    for idx in df1.index:
        assert df1.at[idx, 'id'] == df2.at[idx, 'id']
        
        response1 = df1.at[idx, key].lower()
        response2 = df2.at[idx, key].lower()
        
        has_wait1 = "wait," in response1
        has_wait2 = "wait," in response2

        flag1 = correctness_map[wait_flag1]
        flag2 = correctness_map[wait_flag2]

        is_valid1 = (flag1 == "None" or has_wait1 == flag1)
        is_valid2 = (flag2 == "None" or has_wait2 == flag2)
        
        if is_valid1 and is_valid2:
            matching_indices.append(idx)
    
    filtered_df1 = df1.loc[matching_indices]
    filtered_df2 = df2.loc[matching_indices]
    
    return filtered_df1, filtered_df2
        


def visualize_prm_800k():
    # Load the data based on user choice
    
    file_type = st.sidebar.selectbox("Choose File Type", ["Synthetic longCoT", "SFT Results"])
    
    if file_type == "Synthetic longCoT":
        
        folder_path = "./data/prm_800k_based/longCoT_from_prm800k"
        
        file_choice = st.multiselect("Choose 1 or 2 Files", [os.path.splitext(file)[0] for file in os.listdir(folder_path) if file.endswith('.json')], max_selections=2)
        
        if len(file_choice) == 1:    
            df = load_data(os.path.join(folder_path, f'{file_choice[0]}.json'))
        elif len(file_choice) == 2:
            df = load_data(os.path.join(folder_path, f'{file_choice[0]}.json'))
            df_compare = load_data(os.path.join(folder_path, f'{file_choice[1]}.json'))
        else:
            st.warning("Please select at least 1 file to continue.")
            st.stop()
            
        trees = read_json("./data/prm_800k_based/prm800k_tree_train_678.json")
        
        
    elif file_type == "SFT Results":
        folder_path = './data/prm_800k_based/sft_results'
        show_baseline = st.checkbox("Show Baseline")
        if show_baseline:
            display_baseline(folder_path)
                
        file_choice = st.multiselect("Choose 1 or 2 Files", [os.path.splitext(file)[0] for file in os.listdir(folder_path) if file.endswith('.jsonl')], max_selections=2)
        
        st.subheader('Filtering ("None" means no filtering)')
        
        if len(file_choice) == 1:
            df = load_data(os.path.join(folder_path, f'{file_choice[0]}.jsonl'))
            df = filter_correct_problems_1(df)
            df = filter_wait_statement_1(df)
        elif len(file_choice) == 2:
            df = load_data(os.path.join(folder_path, f'{file_choice[0]}.jsonl'))
            df_compare = load_data(os.path.join(folder_path, f'{file_choice[1]}.jsonl'))
            df, df_compare = filter_correct_problems_2(df, df_compare)
            df, df_compare = filter_wait_statement_2(df, df_compare)
        else:
            st.warning("Please select at least 1 file to continue.")
            st.stop()
            
    count_after_filter = len(df)
            
    if df.empty:
        st.warning("No data available to display.")
        st.stop()

    if 'selected_example' not in st.session_state:
        st.session_state.selected_example = 1

    # Create a dictionary to hold examples by difficulty level
    difficulty_levels = {1: [], 2: [], 3: [], 4: [], 5: []}
    for index, row in df.iterrows():
        difficulty_levels[row['level']].append(index + 1)
        
    st.subheader(f"Select Example **(Count: {count_after_filter})**")
    difficulty, example = st.columns(2)
    with difficulty:
        selected_level = st.selectbox("Select Difficulty Level", [1, 2, 3, 4, 5])
    with example:
        example_options = difficulty_levels[selected_level]
        count_at_difficulty = len(example_options)
        if count_at_difficulty == 0:
            st.warning("No examples available for the selected difficulty level.")
            st.stop()
        selected_example = st.selectbox(f"Select Example **(Count: {count_at_difficulty})**", example_options)


    st.session_state.selected_example = selected_example
    
    
    if file_type == "Synthetic longCoT":
        row = df[df['idx'] == st.session_state.selected_example - 1].iloc[0]
        if len(file_choice) == 2:
            row_compare = df_compare[df_compare['idx'] == st.session_state.selected_example - 1].iloc[0]
    elif file_type == "SFT Results":
        row = df[df['id'] == st.session_state.selected_example - 1].iloc[0]
        if len(file_choice) == 2:
            row_compare = df_compare[df_compare['id'] == st.session_state.selected_example - 1].iloc[0]
        
        
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
        current_example = trees[st.session_state.selected_example - 1]
        if show_tree:
            tree_col, step_col = st.columns([6, 4])
            with tree_col:
                steps_at_level = visualize_tree(current_example['solution'])
            with step_col:

                # steps_at_level = collect_steps_by_level(current_example['solution'])
                level = st.number_input("Select tree level", min_value=0, value=0, max_value=max(steps_at_level.keys()))
                

                st.subheader(f"Steps at level {level}")
                for node in steps_at_level[level]:
                    text = f"**{node['name']}:**\n{node['step']}"
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
            with left.container(height=800):
                show_long_cot(row, file_choice[0])
            with right.container(height=800):
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
            
        st.subheader("Model's Prediction")
        
        if len(file_choice) == 2:
            left, right = st.columns(2)
            with left.container(height=800):
                show_pred_result(row, file_choice[0])
            with right.container(height=800):
                show_pred_result(row_compare, file_choice[1])
        
        elif len(file_choice) == 1:
            show_pred_result(row, file_choice[0])