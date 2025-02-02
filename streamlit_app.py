import streamlit as st
import pandas as pd
import json
import re
from utils import *


from limo import visualize_limo



st.set_page_config(layout="wide")

# choose the type of tree
tree_type = st.sidebar.selectbox("Choose Type", ["LIMO"])


if tree_type == "LIMO":
    visualize_limo()