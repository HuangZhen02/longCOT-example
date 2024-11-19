import streamlit as st
import pandas as pd
import json
import re
from utils import *
import tiktoken


def visualize_safety():
    # 数据文件路径
    before_sft_data_path = "./data/safety/safety_prompt-and-response_before-sft_and_labels.json"
    after_sft_data_path = "./data/safety/safety_prompt-and-response_after-sft_and_labels.json"

    # 加载数据
    with open(before_sft_data_path, "r") as f:
        before_sft_data = json.load(f)

    with open(after_sft_data_path, "r") as f:
        after_sft_data = json.load(f)

    # 保证两个数据集一一对应
    all_data = [
        {"before": before_sft_data[i], "after": after_sft_data[i]}
        for i in range(min(len(before_sft_data), len(after_sft_data)))
    ]

    # 左右筛选条件
    before_filter_label = st.sidebar.radio("筛选 Before SFT 标签:", ["所有", "安全", "不安全"], key="before")
    after_filter_label = st.sidebar.radio("筛选 After SFT 标签:", ["所有", "安全", "不安全"], key="after")

    # 筛选逻辑：交集筛选
    def filter_data(data, before_label, after_label):
        filtered_data = []
        for item in data:
            if before_label != "所有" and item["before"]["label"] != before_label:
                continue
            if after_label != "所有" and item["after"]["label"] != after_label:
                continue
            filtered_data.append(item)
        return filtered_data

    filtered_data = filter_data(all_data, before_filter_label, after_filter_label)

    # 显示筛选后数据数量
    st.sidebar.write(f"筛选后数据数量: {len(filtered_data)}")

    # 提供示例选择
    select_id = st.selectbox("选择一个示例 ID", [i for i in range(len(filtered_data))])

    # 获取选定的示例
    selected_example = filtered_data[select_id]
    before_sft = selected_example["before"]
    after_sft = selected_example["after"]

    # 显示查询内容
    st.header("Query:")
    st.markdown(before_sft["query"])

    # 左右分栏展示
    left, right = st.columns(2)
    with left.container(height=800):
        st.header("Before SFT")
        st.subheader("Response:")
        st.markdown(before_sft["response"])
        st.subheader("Label:")
        st.markdown(before_sft["label"])
        st.subheader("Analysis:")
        st.markdown(before_sft["analysis"])

    with right.container(height=800):
        st.header("After SFT")
        st.subheader("Response:")
        st.markdown(after_sft["response"])
        st.subheader("Label:")
        st.markdown(after_sft["label"])
        st.subheader("Analysis:")
        st.markdown(after_sft["analysis"])
