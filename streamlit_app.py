import streamlit as st
import pandas as pd
import json
import re
from utils import *


from jl import visualize_jl



st.set_page_config(layout="wide")

# choose the type of tree
tree_type = st.sidebar.selectbox("Choose Type", ["journey learning"])



if tree_type == "journey learning":
    visualize_jl()

