import streamlit as st
import pandas as pd
import json
import re
from utils import *
import tiktoken

KEY_WORDS = ["verify", "check", "identify", "summarize", "note that", "notice that", "recall that", "wait", "realize"]

enc = tiktoken.encoding_for_model("gpt-4o")


correctness_map = {
    "✅": True,
    "❌": False,
    "None": "None"
}

def fix_df_key(df):
    # Iterate over each row in the DataFrame
    for idx, row in df.iterrows():
        # Check if 'generated_responses' has at least one element
        if 'generated_responses' in row and isinstance(row['generated_responses'], list) and len(row['generated_responses']) > 0:
            # Replace the first element with 'solution'
            df.at[idx, 'solution'] = row['generated_responses'][0]
        
        if "idx" in row:
            df.at[idx, 'id'] = row["idx"]
    
    return df

def get_common_rows(df1, df2):
    # Find common 'id' values between the two DataFrames
    common_ids = set(df1['id']).intersection(df2['id'])
    
    # Filter both DataFrames to keep only rows with common 'id' values
    filtered_df1 = df1[df1['id'].isin(common_ids)]
    filtered_df2 = df2[df2['id'].isin(common_ids)]
    
    return filtered_df1, filtered_df2


def calculate_overall_accuracy(df):
    correct_count = df['result'].sum()
    overall_count = len(df)
    return correct_count / overall_count if overall_count > 0 else 0


def calculate_token(df):
    total_token_count = 0
    total_problem_count = 0
    
    for _, row in df.iterrows():
        try:
            text = row['generated_responses'][0]
        except:
            text = row["solution"]
            
        total_token_count += len(enc.encode(text))
        total_problem_count += 1
    
    st.subheader(f"Average Token:{total_token_count/total_problem_count}")
    

def statistics_key_words(df):
    key_word_count = {}
    for key_word in KEY_WORDS:
        key_word_count[key_word] = 0
    for key_word in KEY_WORDS:
        for _, row in df.iterrows():
            try:
                text = row['generated_responses'][0].lower()
            except:
                text = row['solution'].lower()
            if key_word in text:
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
    # Find common 'id' values between the two DataFrames
    common_ids = set(df1['id']).intersection(df2['id'])
    
    # Filter both DataFrames to keep only rows with common 'id' values
    filtered_df1 = df1[df1['id'].isin(common_ids)]
    filtered_df2 = df2[df2['id'].isin(common_ids)]
    
    return filtered_df1, filtered_df2
    
    
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



def visualize_jl():
    # Load the data based on user choice
    
    file_type = st.sidebar.selectbox("Choose File Type", ["Training Data", "Results"])
    
    
    if file_type == "Training Data":
        folder_path = './data/jl/training_data'
        
        dataset = st.selectbox("Choose Dataset", ["Math"])
        folder_path = os.path.join(folder_path, dataset)
        
        file_choice = st.multiselect("Choose 1 or 2 Files", sorted([os.path.splitext(file)[0] for file in os.listdir(folder_path) if file.endswith('.jsonl')]), max_selections=2)
        
        if len(file_choice) == 1:
            df = load_data(os.path.join(folder_path, f'{file_choice[0]}.jsonl'))
            df = fix_df_key(df)
            count_total = len(df)
            df = Filter.filter_jl_1(df)
            df = Filter.filter_word_statement_1("wait,", df, key="solution")
            df = Filter.filter_word_statement_1("realize", df, key="solution")


        elif len(file_choice) == 2:
            df = load_data(os.path.join(folder_path, f'{file_choice[0]}.jsonl'))
            count_total = len(df)
            df_compare = load_data(os.path.join(folder_path, f'{file_choice[1]}.jsonl'))
            df, df_compare = fix_df_key(df), fix_df_key(df_compare)
            df, df_compare = get_common_rows(df, df_compare)
            df, df_compare = Filter.filter_jl_2(df, df_compare)
            df, df_compare = Filter.filter_word_statement_2("wait,", df, df_compare, key="solution")
            df, df_compare = Filter.filter_word_statement_2("realize", df, df_compare, key="solution")


        else:
            st.warning("Please select at least 1 file to continue.")
            st.stop()
    
        
    elif file_type == "Results":
        folder_path = './data/jl/results'
        
        benchmark = st.selectbox("Choose Benchmark", ["Math500", "AIME2024"])
        folder_path = os.path.join(folder_path, benchmark)
        
        # show_baseline = st.checkbox("Show Baseline")
        # if show_baseline:
        #     display_baseline(folder_path)
                
        file_choice = st.multiselect("Choose 1 or 2 Files", sorted([os.path.splitext(file)[0] for file in os.listdir(folder_path) if file.endswith('.jsonl')]), max_selections=2)
        
        st.subheader('Filtering ("None" means no filtering)')
        
        if len(file_choice) == 1:
            df = load_data(os.path.join(folder_path, f'{file_choice[0]}.jsonl'))
            df = fix_df_key(df)
            df["id"] = range(1, len(df) + 1)
            count_total = len(df)
            df = Filter.filter_correct_problems_1(df)
            df = Filter.filter_word_statement_1("wait,", df, key="solution")
            df = Filter.filter_word_statement_1("realize", df, key="solution")

        elif len(file_choice) == 2:
            df = load_data(os.path.join(folder_path, f'{file_choice[0]}.jsonl'))
            count_total = len(df)
            df_compare = load_data(os.path.join(folder_path, f'{file_choice[1]}.jsonl'))
            df, df_compare = fix_df_key(df), fix_df_key(df_compare)
            df["id"] = range(1, len(df) + 1)
            df_compare["id"] = range(1, len(df_compare) + 1)
            df, df_compare = Filter.filter_correct_problems_2(df, df_compare)
            df, df_compare = Filter.filter_word_statement_2("wait,", df, df_compare, key="solution")
            df, df_compare = Filter.filter_word_statement_2("realize", df, df_compare, key="solution")

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
    
    if "gold_answer" in row:
        st.subheader("Answer")
        st.markdown(row['gold_answer'].replace("\n", "<br>"), unsafe_allow_html=True)


    if file_type == "Training Data":
        def show_cot(row, data_name):
            st.subheader(f"CoT of {data_name}")
            st.subheader(f"Token: {len(enc.encode(row['solution']))}")
            response = row['solution'].replace("\n", "<br>")
            render_markdown_with_mathjax(highlight_key_words(response, KEY_WORDS))
            
        st.subheader("Training Data")
        
        if len(file_choice) == 2:
            left, right = st.columns(2)
            with left:
                show_cot(row, file_choice[0])
            with right:
                show_cot(row_compare, file_choice[1])
        
        elif len(file_choice) == 1:
            show_cot(row, file_choice[0])


    elif file_type == "Results":
        def show_pred_result(row, model_name):
            if row['answers_correctness'][0]:
                st.subheader(f"Pred of {model_name} ✅")
            else:
                st.subheader(f"Pred of {model_name} ❌")
            
            st.subheader(f"Token: {len(enc.encode(row['solution']))}")
            
            response = row['solution'].replace("\n", "<br>")
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
            
            