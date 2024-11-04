import streamlit as st
import pandas as pd
import json
import re
from utils import *
import tiktoken

KEY_WORDS = ["verify", "check", "identify", "summarize", "note that", "notice that", "recall that", "wait"]

enc = tiktoken.encoding_for_model("gpt-4o")


correctness_map = {
    "✅": True,
    "❌": False,
    "None": "None"
}


def calculate_overall_accuracy(df):
    correct_count = df['result'].sum()
    overall_count = len(df)
    return correct_count / overall_count if overall_count > 0 else 0


def calculate_token(df):
    total_token_count = 0
    total_problem_count = 0
    
    for _, row in df.iterrows():
        text = row['generated_responses'][0]
        total_token_count += len(enc.encode(text))
        total_problem_count += 1
    
    st.subheader(f"Average Token:{total_token_count/total_problem_count}")
    

def statistics_key_words(df):
    key_word_count = {}
    for key_word in KEY_WORDS:
        key_word_count[key_word] = 0
    for key_word in KEY_WORDS:
        for _, row in df.iterrows():
            if key_word in row['generated_responses'][0].lower():
                if key_word not in key_word_count:
                    key_word_count[key_word] = 0
                key_word_count[key_word] += 1
                
    fig, ax = plt.subplots(figsize=(10, 6))
    bars = ax.bar(key_word_count.keys(), key_word_count.values())
    ax.bar(key_word_count.keys(), key_word_count.values())
    ax.set_xlabel('Key Words')
    ax.set_ylabel('Count')
    ax.set_title('Keyword Occurrences')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    
    for bar in bars:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height,
                f'{int(height)}', ha='center', va='bottom')

    st.pyplot(fig)


def display_baseline(result_dir):
    accuracy_list = []
    for file in os.listdir(result_dir):
        if file.endswith('.jsonl'):
            file_path = os.path.join(result_dir, file)
            result_df = load_data(file_path)
            accuracy = calculate_overall_accuracy(result_df)
            accuracy_list.append((os.path.splitext(file)[0], accuracy))

    accuracy_df = pd.DataFrame(accuracy_list, columns=['File Name', 'Accuracy']).sort_values(by='Accuracy').reset_index(drop=True)
    
    st.dataframe(accuracy_df)
        
        
def get_common_rows(df1, df2):
    common_idx = pd.merge(df1[['idx']], df2[['idx']], on='idx').sort_values(by='idx')

    new_df1 = df1[df1['idx'].isin(common_idx['idx'])].set_index('idx')
    new_df2 = df2[df2['idx'].isin(common_idx['idx'])].set_index('idx')

    new_df1 = new_df1.loc[common_idx['idx']].reset_index()
    new_df2 = new_df2.loc[common_idx['idx']].reset_index()

    return new_df1, new_df2
    
    
class Filter:    
    def filter_correct_problems_1(df):
        correctness = st.selectbox("Select correctness", ["None", "✅", "❌"])
        
        if correctness == "None":
            return df
        
        matching_indices = []
        for idx in df.index:
            if df.at[idx, 'answers_correctness'][0] == correctness_map.get(correctness):
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
            
            result1 = df1.at[idx, 'answers_correctness'][0]
            result2 = df2.at[idx, 'answers_correctness'][0]
            
            if ((correctness1 == "None" or result1 == correctness_map.get(correctness1)) and
                (correctness2 == "None" or result2 == correctness_map.get(correctness2))):
                matching_indices.append(idx)
        
        filtered_df1 = df1.loc[matching_indices]
        filtered_df2 = df2.loc[matching_indices]
        
        return filtered_df1, filtered_df2
            

def visualize_jl():
    # Load the data based on user choice
    
    file_type = st.sidebar.selectbox("Choose File Type", ["Results"])
    
        
    if file_type == "Results":
        folder_path = './data/jl'
        
        benchmark = st.selectbox("Choose Benchmark", ["Math500", "AIME2024"])
        folder_path = os.path.join(folder_path, benchmark)
        
        # show_baseline = st.checkbox("Show Baseline")
        # if show_baseline:
        #     display_baseline(folder_path)
                
        file_choice = st.multiselect("Choose 1 or 2 Files", sorted([os.path.splitext(file)[0] for file in os.listdir(folder_path) if file.endswith('.jsonl')]), max_selections=2)
        
        st.subheader('Filtering ("None" means no filtering)')
        
        if len(file_choice) == 1:
            df = load_data(os.path.join(folder_path, f'{file_choice[0]}.jsonl'))
            df["id"] = range(1, len(df) + 1)
            count_total = len(df)
            df = Filter.filter_correct_problems_1(df)

        elif len(file_choice) == 2:
            df = load_data(os.path.join(folder_path, f'{file_choice[0]}.jsonl'))
            df["id"] = range(1, len(df) + 1)
            count_total = len(df)
            df_compare = load_data(os.path.join(folder_path, f'{file_choice[1]}.jsonl'))
            df_compare["id"] = range(1, len(df_compare) + 1)
            df, df_compare = Filter.filter_correct_problems_2(df, df_compare)

        else:
            st.warning("Please select at least 1 file to continue.")
            st.stop()
            
    count_after_filter = len(df)
            
    if df.empty:
        st.warning("No data available to display.")
        st.stop()

    if 'selected_example' not in st.session_state:
        st.session_state.selected_example = 1

    

    examples = []
    for _, row in df.iterrows():
        try:    
            examples.append(row["idx"])
        except:
            examples.append(row["id"])
        
    st.subheader(f"Select Example **(Count: {count_after_filter}/{count_total})**")

            
    selected_example = st.selectbox(f"Select Example", examples)


    st.session_state.selected_example = selected_example
    
    
    if file_type == "Synthetic longCoT":
        row = df[df['idx'] == st.session_state.selected_example].iloc[0]
        if len(file_choice) == 2:
            row_compare = df_compare[df_compare['idx'] == st.session_state.selected_example].iloc[0]
    elif file_type == "Results":
        row = df[df['id'] == st.session_state.selected_example].iloc[0]
        if len(file_choice) == 2:
            row_compare = df_compare[df_compare['id'] == st.session_state.selected_example].iloc[0]
        
    def show_statistics(df):
        st.subheader("Statistics")
        calculate_token(df)
        statistics_key_words(df)
    
    if len(file_choice) == 1:
        show_statistics(df)
    elif len(file_choice) == 2:
        left, right = st.columns(2)
        with left:
            show_statistics(df)
        with right:
            show_statistics(df_compare)
        

    st.header(f"Idx: {st.session_state.selected_example}")

    st.subheader("Question")
    st.markdown(row['question'].replace("\n", "<br>"), unsafe_allow_html=True)
    
    st.subheader("Answer")
    st.markdown(row['gold_answer'].replace("\n", "<br>"), unsafe_allow_html=True)

    if file_type == "Results":
        
        def show_pred_result(row, model_name):
            if row['answers_correctness'][0]:
                st.subheader(f"Pred of {model_name} ✅")
            else:
                st.subheader(f"Pred of {model_name} ❌")
            
            st.subheader(f"Token: {len(enc.encode(row['generated_responses'][0]))}")
            
            response = row['generated_responses'][0].replace("\n", "<br>")
            render_markdown_with_mathjax(highlight_key_words(response, KEY_WORDS))
            
        st.subheader("Model's Prediction")
        
        if len(file_choice) == 2:
            left, right = st.columns(2)
            with left:
                show_pred_result(row, file_choice[0])
            with right:
                show_pred_result(row_compare, file_choice[1])
        
        elif len(file_choice) == 1:
            show_pred_result(row, file_choice[0])
            
            