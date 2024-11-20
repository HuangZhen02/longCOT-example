import streamlit as st
import pandas as pd
import json
import re
from utils import *
import tiktoken


def visualize_lima():
    # 数据文件路径
    before_sft_data_path = "./data/lima_and_auto_j/general_before-sft.json"
    after_sft_data_path = "./data/lima_and_auto_j/general_after-sft.json"

    # 加载数据
    with open(before_sft_data_path, "r") as f:
        before_sft_data = json.load(f)

    with open(after_sft_data_path, "r") as f:
        after_sft_data = json.load(f)

    
    # 提供示例选择
    select_id = st.selectbox("选择一个示例 ID", [i for i in range(len(before_sft_data))])


    before_sft = before_sft_data[select_id]
    after_sft = after_sft_data[select_id]

    # 显示查询内容
    st.header("Query:")
    st.markdown(before_sft["query"])

    # 左右分栏展示
    left, right = st.columns(2)
    with left.container(height=800):
        st.header("Before SFT")
        st.subheader("Response:")
        st.markdown(before_sft["response"])

    with right.container(height=800):
        st.header("After SFT")
        st.subheader("Response:")
        st.markdown(after_sft["response"])

