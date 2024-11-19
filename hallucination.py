import streamlit as st
import pandas as pd
import json
import re
from utils import *
import tiktoken



def visualize_hallucination():

    before_sft_data_path = "/Users/huangzhen/VscodeProject/O1/longCOT-example/data/hallucination/output_before-sft_extracted.jsonl"

    after_sft_data_path = "/Users/huangzhen/VscodeProject/O1/longCOT-example/data/hallucination/output_after-sft_extracted.jsonl"

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
        
