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

# Load the data based on user choice
file_choice = st.sidebar.selectbox("Choose File", ["cot_from_prm800_with_attempts_limitation", "cot_from_prm800", "deepseek-math-7b-base-sft-result"])

if file_choice == "cot_from_prm800_with_attempts_limitation":
    df = load_data('data/prm800k_cot_from_tree_train_678_max_total_attempts_3.json')
elif file_choice == "cot_from_prm800":
    df = load_data('data/prm800k_cot_from_tree_train_678.json')
else:
    df = load_data('data/deepseek-math-7b-base-sft-math-shortcut-epoch1-DATASET-MATH-longCOT-max-total-attempts-3-LR-2e-5-BS-128_eval_math_test.jsonl')


# Initialize session state for selected example
if 'selected_example' not in st.session_state:
    st.session_state.selected_example = 1

# Function to highlight "Wait,"
def highlight_wait(text):
    return re.sub(r'(Wait,)', r'<span style="color: red; font-weight: bold;">\1</span>', text)

# Create a dictionary to hold examples by difficulty level
difficulty_levels = {1: [], 2: [], 3: [], 4: [], 5: []}
for index, row in df.iterrows():
    difficulty_levels[row['level']].append(index + 1)  # Assuming 'difficulty_level' is a key in your JSON

# Sidebar for difficulty levels
selected_level = st.sidebar.selectbox("Select Difficulty Level", [1, 2, 3, 4, 5])

# Sidebar for example selection based on difficulty level
example_options = difficulty_levels[selected_level]

selected_example = st.sidebar.selectbox("Select Example", example_options)

# Update session state based on dropdown selection
st.session_state.selected_example = selected_example

# Sidebar for example selection
# example_options = list(range(1, len(df) + 1))
# selected_example = st.sidebar.selectbox("Select Example", example_options, index=st.session_state.selected_example - 1)

st.title("🎈 ThoughtPlut COT Examples Analysis")

row = df.iloc[st.session_state.selected_example - 1]
st.header(f"Example {st.session_state.selected_example}")

# Adjusted to show the relevant keys based on the selected file
if file_choice.startswith("cot_from_prm800"):
    # Display the selected example
    st.subheader("Question")
    st.markdown(row['question'].replace("\n", "<br>"), unsafe_allow_html=True)

    st.subheader("Subject")
    st.write(row['subject'])

    st.subheader("Level")
    st.write(row['level'])


    st.subheader("Gold Solution")
    st.markdown(row['gt_solution'].replace("\n", "<br>"), unsafe_allow_html=True)

    st.subheader("Short COT")
    st.markdown(row['shortCOT'].replace("\n", "<br>"), unsafe_allow_html=True)

    st.subheader("Long COT")
    highlighted_long_cot = highlight_wait(row['longCOT'].replace("\n", "<br>"))
    st.markdown(highlighted_long_cot, unsafe_allow_html=True)
else:
    # Display the selected example
    st.subheader("Question")
    st.markdown(row['question'].replace("\n", "<br>"), unsafe_allow_html=True)

    st.subheader("Subject")
    st.write(row['subject'])

    st.subheader("Level")
    st.write(row['level'])

    st.subheader("Gold Solution")
    st.markdown(row['gt_solution'].replace("\n", "<br>"), unsafe_allow_html=True)

    st.subheader("Gold Answer")
    st.markdown(row['gold'].replace("\n", "<br>"), unsafe_allow_html=True)

    st.subheader("Pred Solution")
    highlighted_response = highlight_wait(row['response'].replace("\n", "<br>"))
    st.markdown(highlighted_response, unsafe_allow_html=True)

    st.subheader("Pred Answer")
    st.markdown(row['pred'].replace("\n", "<br>"), unsafe_allow_html=True)

    st.subheader("Is correct")
    st.write(row['result'])

# Next Example button
# if st.button("Next Example"):
#     if st.session_state.selected_example < len(df):
#         st.session_state.selected_example += 1
#     else:
#         st.warning("This is the last example.")