import streamlit as st
import pandas as pd
import json
import re


# Function to load data from a JSONL file
def load_data(file_path):
    data = []
    with open(file_path, 'r') as f:
        for line in f:
            data.append(json.loads(line))
    return pd.DataFrame(data)

def highlight_wait(text):
    return re.sub(r'(Wait,)', r'<span style="color: red; font-weight: bold;">\1</span>', text)