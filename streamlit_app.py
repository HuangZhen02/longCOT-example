import streamlit as st
import pandas as pd
import json
import re
from utils import *
from tree2longcot import visualize_tree2longcot
from teacher_student import visualize_teacher_student
from teacher_only import visualize_teacher_only


st.set_page_config(layout="wide")

# choose the type of tree
tree_type = st.sidebar.selectbox("Choose Tree Type", ["Tree->LongCoT", "Teacher-student-based(3 Examples)", "Teacher-only-based(10 Examples)"])


if tree_type == "Tree->LongCoT":
    visualize_tree2longcot()

elif tree_type == "Teacher-student-based(3 Examples)":
    visualize_teacher_student()
    
elif tree_type == "Teacher-only-based(10 Examples)":
    visualize_teacher_only()