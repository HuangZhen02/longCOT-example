import streamlit as st
import pandas as pd
import json
import re
from utils import *
from longcot_and_experiments import visualize_longcot_and_experiments
# from teacher_student import visualize_teacher_student
# from teacher_only import visualize_teacher_only
from dpo import visualize_dpo
from hack_o1 import visualize_hack_o1
from policy_model import visualize_policy_model
from jl import visualize_jl
from hallucination import visualize_hallucination



st.set_page_config(layout="wide")

# choose the type of tree
tree_type = st.sidebar.selectbox("Choose Type", ["hack o1 data", "policy model data", "journey learning", "hallucination"])


# if tree_type == "longcot&experiments":
#     visualize_longcot_and_experiments()

# elif tree_type == "DPO":
#     visualize_dpo()
    
if tree_type == "hack o1 data":
    visualize_hack_o1()
    
elif tree_type == "policy model data":
    visualize_policy_model()

elif tree_type == "journey learning":
    visualize_jl()

elif tree_type == "hallucination":
    visualize_hallucination()