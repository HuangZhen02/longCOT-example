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
from safety import visualize_safety
from lima import visualize_lima
from math500 import visualize_math500
from monkey import visualize_monkey


st.set_page_config(layout="wide")

# choose the type of tree
tree_type = st.sidebar.selectbox("Choose Type", ["hack o1 data", "policy model data", "journey learning", "hallucination", "safety", "lima and autoJ", "math500", "monkey"])


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
    
elif tree_type == "safety":
    visualize_safety()
    
elif tree_type == "lima and autoJ":
    visualize_lima()
    
elif tree_type == "math500":
    visualize_math500()
    
elif tree_type == "monkey":
    visualize_monkey()