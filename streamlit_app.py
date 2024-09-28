import streamlit as st
import pandas as pd
import json
import re
from utils import *
from prm_800k import visualize_prm_800k


st.set_page_config(layout="wide")
# choose the type of tree
tree_type = st.sidebar.selectbox("Choose Tree Type", ["PRM800k-based", "Teacher-student-based", "Teacher-only-based"])


if tree_type == "PRM800k-based":
    visualize_prm_800k()

elif tree_type == "Teacher-student-based":
    st.header("To be done!")
    
elif tree_type == "Teacher-only-based":
    st.header("To be done!")