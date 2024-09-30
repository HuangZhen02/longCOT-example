import streamlit as st
import pandas as pd
import json
import re
from utils import *



def visualize_teacher_student():
    folder_path = "./data/teacher_student_based/"

    with open(os.path.join(folder_path, "evaluated_problem_trees3.json"), "r") as f:
        data = json.load(f)
        
    selected_example = st.sidebar.selectbox("Choose Example", [f"Example{idx+1}" for idx, _ in enumerate(data)])

    idx = int(selected_example[7:])
    example = data[idx - 1]

    st.subheader(f"Example{idx}")

    st.subheader("Question")
    st.markdown(example['question'].replace("\n", "<br>"), unsafe_allow_html=True)

    st.subheader("Tree Structure")
    show_tree = st.checkbox("Show Tree Structure")
    if show_tree:
        tree_col, step_col = st.columns([6, 4])
        with tree_col:
            steps_at_level = visualize_tree(example['solution'])
        with step_col:

            # steps_at_level = collect_steps_by_level(example['solution'])
            level = st.number_input("Select tree level", min_value=0, value=0, max_value=max(steps_at_level.keys()))

            st.subheader(f"Steps at level {level}")
            for node in steps_at_level[level]:
                reward_text = f"{node['reward']:.2f}"

                text = f"**{node['name']}:**\n**reward: {reward_text}**\n{node['step']}"

                # Perform the replacement outside of the f-string
                html_text = text.replace("\n", "<br>")

                # If reward_conflict is True, wrap the text with red color HTML style
                if node.get('reward_conflict', False):
                    html_text = f'<span style="color:red;">{html_text}</span>'

                # Display the text with HTML rendering enabled
                st.write(html_text, unsafe_allow_html=True)