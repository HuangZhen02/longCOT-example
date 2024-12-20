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
        text = row['response']
        total_token_count += len(enc.encode(text))
        total_problem_count += 1
    
    st.subheader(f"Average Token:{total_token_count/total_problem_count}")
    

def statistics_key_words(df):
    key_word_count = {}
    for key_word in KEY_WORDS:
        key_word_count[key_word] = 0
    for key_word in KEY_WORDS:
        for _, row in df.iterrows():
            if key_word in row['response'].lower():
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
    
    
    def filter_word_statement_1(word, df, key="response"):
        wait_flag = st.selectbox(f"Whether there is a {word} statement", ["None", "✅", "❌"])
        
        if wait_flag == "None":
            return df
        
        matching_indices = []
        for idx, row in df.iterrows():
            if (word in row[key].lower()) == correctness_map[wait_flag]:
                matching_indices.append(row['id'])
        
        filtered_df = df[df['id'].isin(matching_indices)]
        return filtered_df

    def filter_word_statement_2(word, df1, df2, key="response"):
        left, right = st.columns(2)
        with left:
            wait_flag1 = st.selectbox(f"Whether there is a {word} statement in the first file", ["None", "✅", "❌"])
        with right:
            wait_flag2 = st.selectbox(f"Whether there is a {word} statement in the second file", ["None", "✅", "❌"])
        
        matching_ids = []

        for _, row1 in df1.iterrows():
            # Find the row in df2 with the same 'id'
            row2 = df2[df2['id'] == row1['id']]
            if row2.empty:
                continue
            
            response1 = row1[key].lower()
            response2 = row2.iloc[0][key].lower()
            
            has_wait1 = word in response1
            has_wait2 = word in response2
            
            flag1 = correctness_map[wait_flag1]
            flag2 = correctness_map[wait_flag2]
            
            is_valid1 = (wait_flag1 == "None" or has_wait1 == flag1)
            is_valid2 = (wait_flag2 == "None" or has_wait2 == flag2)
            
            if is_valid1 and is_valid2:
                matching_ids.append(row1['id'])
        
        filtered_df1 = df1[df1['id'].isin(matching_ids)]
        filtered_df2 = df2[df2['id'].isin(matching_ids)]
        
        return filtered_df1, filtered_df2  
    
                  
    def filter_jl_1(df):
        if 'is_jl' in df.columns:
            jl_filter = st.selectbox("Filter by 'is journey learning'", ["None", "True", "False"])
            
            if jl_filter == "True":
                filtered_df = df[df['is_jl']]
            elif jl_filter == "False":
                filtered_df = df[~df['is_jl']]
            else:  # "None"
                return df

            return filtered_df
        else:
            # Display a disabled selectbox indicating that filtering is not applicable
            st.selectbox("Filter by 'is journey learning'", ["None"], index=0, disabled=True)
            return df

    def filter_jl_2(df1, df2):
        left, right = st.columns(2)
        
        if 'is_jl' in df1.columns:
            with left:
                jl_filter1 = st.selectbox("Filter by 'is journey learning' for the first file", ["None", "True", "False"])
        else:
            with left:
                st.selectbox("Filter by 'is journey learning' for the first file", ["None"], index=0, disabled=True)
                jl_filter1 = "None"
        
        if 'is_jl' in df2.columns:
            with right:
                jl_filter2 = st.selectbox("Filter by 'is journey learning' for the second file", ["None", "True", "False"])
        else:
            with right:
                st.selectbox("Filter by 'is journey learning' for the second file", ["None"], index=0, disabled=True)
                jl_filter2 = "None"

        has_is_jl_df1 = 'is_jl' in df1.columns
        has_is_jl_df2 = 'is_jl' in df2.columns

        if (has_is_jl_df1 and jl_filter1 != "None") or (has_is_jl_df2 and jl_filter2 != "None"):
            if has_is_jl_df1 and jl_filter1 != "None":
                filtered_df1 = df1[df1['is_jl']] if jl_filter1 == "True" else df1[~df1['is_jl']]
            else:
                filtered_df1 = df1

            if has_is_jl_df2 and jl_filter2 != "None":
                filtered_df2 = df2[df2['is_jl']] if jl_filter2 == "True" else df2[~df2['is_jl']]
            else:
                filtered_df2 = df2

            # Ensure both DataFrames only keep rows with shared 'id' values
            common_ids = set(filtered_df1['id']) & set(filtered_df2['id'])
            filtered_df1 = filtered_df1[filtered_df1['id'].isin(common_ids)]
            filtered_df2 = filtered_df2[filtered_df2['id'].isin(common_ids)]
            
            return filtered_df1, filtered_df2

        # Return the original DataFrames unchanged if neither has 'is_jl' or no selection made
        return df1, df2

       

def visualize_hack_o1():
    # Load the data based on user choice
    
    file_type = st.sidebar.selectbox("Choose File Type", ["Results"])
    
        
    if file_type == "Results":
        folder_path = './data/hack_o1'
                
        file_choice = st.multiselect("Choose 1 or 2 Files", sorted([os.path.splitext(file)[0] for file in os.listdir(folder_path) if file.endswith('.jsonl')]), max_selections=2)
        
        st.subheader('Filtering ("None" means no filtering)')
        
        if len(file_choice) == 1:
            df = load_data(os.path.join(folder_path, f'{file_choice[0]}.jsonl'))
            count_total = len(df)
            df = Filter.filter_word_statement_1("wait", df, key="response")
            

        else:
            st.warning("Please select 1 file to continue.")
            st.stop()
            
    count_after_filter = len(df)
            
    if df.empty:
        st.warning("No data available to display.")
        st.stop()

    if 'selected_example' not in st.session_state:
        st.session_state.selected_example = 1


    
    # Create a dictionary to hold examples by difficulty level
    difficulty_levels = {1: [], 2: [], 3: [], 4: [], 5: []}
    difficulty_filtered_dfs = {1: None, 2: None, 3: None, 4: None, 5: None}
    
    
    for _, row in df.iterrows():
        level = row.get('level', None)
        if level and level in difficulty_levels:
            try:
                difficulty_levels[level].append(row["idx"])
            except:
                difficulty_levels[level].append(row["id"])
                
    for level in difficulty_levels:
        difficulty_filtered_dfs[level] = df[df['level'] == level]


    st.subheader(f"Select Example **(Count: {count_after_filter}/{count_total})**")



    # Create columns for selecting difficulty and example
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
    
    row = df[df['id'] == st.session_state.selected_example].iloc[0]
 
    def show_statistics(df):
        st.subheader("Statistics")
        calculate_token(df)
        statistics_key_words(df)
    
    
    show_statistics(difficulty_filtered_dfs[selected_level])        

    st.header(f"Idx: {st.session_state.selected_example}")

    st.subheader("Question")
    st.markdown(row['question'].replace("\n", "<br>"), unsafe_allow_html=True)
    

    st.subheader("Response")
    st.subheader(f"Token: {len(enc.encode(row['response']))}")
    
    response = row['response'].replace("\n", "<br>")
    # st.markdown(highlight_key_words(response, KEY_WORDS), unsafe_allow_html=True)
    
    render_markdown_with_mathjax(highlight_key_words(response, KEY_WORDS))
    