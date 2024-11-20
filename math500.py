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
    "None": "None"
}

    
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



def visualize_math500():
    sft_data_path = "./data/math500/math_500_after-sft.jsonl"

    
    data = load_data(sft_data_path)
    
    data["id"] = range(len(data))
    total_before_filter = len(data)

    data = Filter.filter_word_statement_1("wait", data, key="output")
    
    # 筛选后总数
    total_after_filter = len(data)

    # 显示总数信息
    st.markdown(f"**Total Problems Before Filter:** {total_before_filter}")
    st.markdown(f"**Total Problems After Filter:** {total_after_filter}")



    selected_ids = st.selectbox("Select a problem", data['id'].tolist())
    
    selected_data = data[data['id'] == selected_ids].iloc[0]
    
    
    st.header(f"Problem")
    st.markdown(selected_data['problem'])
    
    st.header("Gold Solution")
    st.markdown(selected_data['solution'])
    
    st.header("Answer")
    st.markdown(selected_data['answer'])
    
    st.header("Output")
    output = selected_data['output'].replace("\n", "<br>")
    render_markdown_with_mathjax(highlight_key_words(output, key_words=KEY_WORDS))
    
    