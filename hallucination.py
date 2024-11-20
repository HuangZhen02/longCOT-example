import streamlit as st
import pandas as pd
import json
import re
from utils import *
import tiktoken



def visualize_hallucination():
    
    mode = st.selectbox("Select a mode", ["1: output", "2: combined_o1_hallucination", "3: combined_o1_simple_qa_hallucination"])
    
    if mode == "1: output":

        before_sft_data_path = "./data/hallucination/output_before-sft_extracted.jsonl"

        after_sft_data_path = "./data/hallucination/output_after-sft_extracted.jsonl"

        before_sft_data = []
        with open(before_sft_data_path, 'r') as f:
            for line in f:
                before_sft_data.append(json.loads(line))

        after_sft_data = []
        with open(after_sft_data_path, 'r') as f:
            for line in f:
                after_sft_data.append(json.loads(line))

        select_id = st.selectbox("Select an example", [i for i in range(len(before_sft_data))])

        before_sft = before_sft_data[select_id]
        after_sft = after_sft_data[select_id]

        


        st.header("Problem:")
        st.markdown(before_sft["prompt"])

        st.header("Gold Answer:")
        st.markdown(before_sft["answer"])


        left, right = st.columns(2)
        with left.container(height=800):
            st.header("Before SFT")
            
            st.header("Output:")
            st.markdown(before_sft["output"])
            
            st.header("Answer:")
            st.markdown(before_sft["model_answer"])
            
            
            
        with right.container(height=800):
            st.header("After SFT")
            
            st.header("Output:")
            st.markdown(after_sft["output"])
            
            st.header("Answer:")
            st.markdown(after_sft["model_answer"])
            
    elif mode == "2: combined_o1_hallucination":
        with open("./data/hallucination/combined_o1_hallucination.jsonl", 'r') as f:
            data = []
            for idx, line in enumerate(f):
                sample = json.loads(line)
                sample["id"] = idx  # 给每个样本分配唯一的 ID
                data.append(sample)
    
        # 按类别筛选
        categories = list(set(d["category"] for d in data))
        select_category = st.selectbox("选择一个类别", categories)

        # 筛选出对应类别的数据
        filtered_data = [d for d in data if d["category"] == select_category]

        # 显示筛选后的数据数量
        st.write(f"筛选后样本数量: {len(filtered_data)}")

        # 选择具体的样本
        select_id = st.selectbox(
            "选择一个样本 ID",
            [d["id"] for d in filtered_data],
            format_func=lambda x: f"Sample {x}"
        )

        # 获取选定的样本
        selected_example = next(d for d in filtered_data if d["id"] == select_id)

        # 显示问题及标准答案
        st.header("Problem:")
        st.markdown(selected_example["prompt"])
        
        st.header("Category:")
        st.markdown(selected_example["category"])

        st.header("Gold Answer:")
        st.markdown(selected_example["answer"])

        # 左右分栏展示 Before 和 After SFT
        left, right = st.columns(2)
        with left.container(height=800):
            st.header("Before SFT")
            st.subheader("Output:")
            st.markdown(selected_example["output_before_sft"])
            st.subheader("Answer:")
            st.markdown(selected_example["model_answer_before_sft"])

        with right.container(height=800):
            st.header("After SFT")
            st.subheader("Output:")
            st.markdown(selected_example["output_after_sft"])
            st.subheader("Answer:")
            st.markdown(selected_example["model_answer_after_sft"])
            
    elif mode == "3: combined_o1_simple_qa_hallucination":
        
        with open("./data/hallucination/combined_o1_simple_qa_hallucination.jsonl", 'r') as f:
            data = []
            for idx, line in enumerate(f):
                sample = json.loads(line)
                sample["id"] = idx
                data.append(sample)
        
        
        select_id = st.selectbox("Select an example", [d["id"] for d in data])
        
        selected_example = next(d for d in data if d["id"] == select_id)
        
        st.header("Problem:")
        st.markdown(selected_example["prompt"])
        

        
        st.header("Gold Answer:")
        st.markdown(selected_example["answer"])
        
        left, right = st.columns(2)
        
        with left.container(height=800):
            st.header("Before SFT")
            st.subheader("Output:")
            st.markdown(selected_example["output_before_sft"])
            st.subheader("Answer:")
            st.markdown(selected_example["model_answer_before_sft"])
            
        with right.container(height=800):
            st.header("After SFT")
            st.subheader("Output:")
            st.markdown(selected_example["output_after_sft"])
            st.subheader("Answer:")
            st.markdown(selected_example["model_answer_after_sft"])
            
        