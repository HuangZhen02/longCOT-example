import streamlit as st
import pandas as pd
import json
import re
from utils import *
import tiktoken



def visualize_safety():

    before_sft_data_path = "./data/safety/safety_prompt-and-response_before-sft_and_labels.json"

    after_sft_data_path = "./data/safety/safety_prompt-and-response_after-sft_and_labels.json"

    with open(before_sft_data_path, "r") as f:
        before_sft_data = json.load(f)

    with open(after_sft_data_path, "r") as f:
        after_sft_data = json.load(f)


    select_id = st.selectbox("Select an example", [i for i in range(len(before_sft_data))])

    before_sft = before_sft_data[select_id]
    after_sft = after_sft_data[select_id]


    st.header("Query:")
    st.markdown(before_sft["query"])


    left, right = st.columns(2)
    with left.container(height=800):
        st.header("Before SFT")
        
        st.header("Response:")
        st.markdown(before_sft["response"])
        
        st.header("Label:")
        st.markdown(before_sft["label"])
        
        st.header("Analysis:")
        st.markdown(before_sft["analysis"])
        
        
        
    with right.container(height=800):
        st.header("After SFT")
        
        st.header("Response:")
        st.markdown(after_sft["response"])
        
        st.header("Label:")
        st.markdown(after_sft["label"])
        
        st.header("Analysis:")
        st.markdown(after_sft["analysis"])