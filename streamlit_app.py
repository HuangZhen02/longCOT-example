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

st.set_page_config(layout="wide")

# choose the type of tree
tree_type = st.sidebar.selectbox("Choose Type", ["longcot&experiments", "DPO", "hack o1", "policy model", "journey learning"])


if tree_type == "longcot&experiments":
    visualize_longcot_and_experiments()

elif tree_type == "DPO":
    visualize_dpo()
    
elif tree_type == "hack o1":
    visualize_hack_o1()
    
elif tree_type == "policy model":
    visualize_policy_model()

elif tree_type == "journey learning":
    visualize_jl()