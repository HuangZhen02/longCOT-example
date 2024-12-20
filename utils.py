import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import json
import os
import re
import chardet
import networkx as nx
import matplotlib.pyplot as plt
from networkx.drawing.nx_agraph import graphviz_layout


def load_data(file_path): # Function to load data from a JSONL file
    data = []
    with open(file_path, 'r') as f:
        for line in f:
            data.append(json.loads(line))
    return pd.DataFrame(data)

def get_encoding_type(file_path):
    with open(file_path, 'rb') as f:
        sample = f.read(1024)
        cur_encoding = chardet.detect(sample)['encoding']
        return cur_encoding

def read_json(file_path):
    with open(file_path, 'r', encoding=get_encoding_type(file_path), errors="ignore") as f:
        data = json.load(f)
        return data
    
def write_json(data, file_path):
    with open(file_path, 'w', encoding='utf-8', errors="ignore") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
        

def render_markdown_with_mathjax(markdown_text):
    """
    渲染带有MathJax支持的Markdown文本，使用st.components.v1.html。
    
    Args:
        markdown_text (str): 需要渲染的Markdown字符串。
    """
    # HTML 模板，包含 MathJax 脚本和输入的 Markdown 内容
    html_template = f"""
    <script type="text/javascript" async
      src="https://cdnjs.cloudflare.com/ajax/libs/mathjax/3.2.0/es5/tex-mml-chtml.js">
    </script>
    <div style="font-size: 16px; line-height: 1.6; margin: 10px 0;">
      {markdown_text}
    </div>
    """
    
    # 使用 st.components.v1.html 渲染 HTML 内容
    components.html(html_template, height=800, scrolling=True)


def highlight_wait(text):
    return re.sub(r'(Wait,)', r'<span style="color: red; font-weight: bold;">\1</span>', text)

def highlight_key_words(text, key_words):
    for key_word in key_words:
        text = re.sub(rf'({re.escape(key_word)})', r'<span style="color: red; font-weight: bold;">\1</span>', text, flags=re.IGNORECASE)
    return text



def add_edges(graph, data, level_dict=None, level=0, parent=None):
    # Initialize level_dict if not passed
    if level_dict is None:
        level_dict = {}

    node_label = data["name"]
    graph.add_node(
        node_label, 
        is_correct=data.get("is_correct", False), 
        rating=data.get("rating", -1),
        reward_conflict=data.get("reward_conflict", False)
    )  # 添加节点

    # Collect the node in the level_dict based on the current level
    if level not in level_dict:
        level_dict[level] = []
    level_dict[level].append(data)

    if parent:
        graph.add_edge(parent, node_label)  # 添加从父节点到当前节点的边
    
    # Recursively process the children
    for child in data.get('children', []):
        add_edges(graph, child, level_dict, level + 1, node_label)

    return level_dict

# 自定义节点颜色和大小
def draw_tree(graph):
    # 使用 graphviz_layout 来生成树的层次布局
    pos = graphviz_layout(graph, prog="dot")  # prog="dot" 确保是树形结构
    
    plt.figure(figsize=(10, 10))

    node_colors = []
    edge_colors = []
    
    for node in graph.nodes():
        if graph.nodes[node]["is_correct"] == True:
            node_colors.append("lightgreen")  # 如果 is_correct 为 True，则颜色为 lightgreen
        elif graph.nodes[node]["rating"] == 1:
            node_colors.append("lightgreen")
        elif graph.nodes[node]["rating"] == -1:
            node_colors.append("lightcoral")  # 如果 rating 为 -1，则颜色为 lightcoral（相当于 lightred）
        elif graph.nodes[node]["rating"] == 0:
            node_colors.append("lightyellow")
        else:
            node_colors.append("skyblue")  # 否则颜色为 skyblue
            
            
        if graph.nodes[node]["reward_conflict"]:
            edge_colors.append("red")
        else:
            edge_colors.append("black")

    # 绘制节点和边
    nx.draw_networkx_edges(graph, pos)
    nx.draw_networkx_nodes(graph, pos, node_color=node_colors, edgecolors=edge_colors, node_size=500, node_shape='o')
    
    # 在节点上显示标签
    nx.draw_networkx_labels(graph, pos, font_size=6, font_weight='bold')

    # 显示图形
    plt.axis('off')
    
    st.pyplot(plt, dpi=500)  # 使用streamlit显示matplotlib图像

def visualize_tree(solution):
    G = nx.DiGraph()  # 创建一个有向图
    levels_dict = add_edges(G, solution)  # 添加节点和边
    draw_tree(G)  # 可视化树
    return levels_dict

