import streamlit as st
import pandas as pd
import json
import re
from utils import *
from longcot_and_experiments import visualize_longcot_and_experiments
from teacher_student import visualize_teacher_student
from teacher_only import visualize_teacher_only


st.set_page_config(layout="wide")

# choose the type of tree
tree_type = st.sidebar.selectbox("Choose Tree Type", ["longcot&experiments", "Teacher-student-based(3 Examples)", "Teacher-only-based(10 Examples)"])


if tree_type == "longcot&experiments":
    visualize_longcot_and_experiments()

elif tree_type == "Teacher-student-based(3 Examples)":
    visualize_teacher_student()
    
elif tree_type == "Teacher-only-based(10 Examples)":
    visualize_teacher_only()