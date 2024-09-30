import streamlit as st
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
        

def highlight_wait(text):
    return re.sub(r'(Wait,)', r'<span style="color: red; font-weight: bold;">\1</span>', text)


# 递归生成树的节点和边
def add_edges(graph, data, parent=None):
    node_label = data["name"]
    graph.add_node(
        node_label, 
        is_correct=data.get("is_correct", False), 
        rating=data.get("rating", -1),
        reward_conflict=data.get("reward_conflict", False)
    )  # 添加节点
    
    if parent:
        graph.add_edge(parent, node_label)  # 添加从父节点到当前节点的边
    
    for child in data.get("children", []):
        add_edges(graph, child, node_label)

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
    add_edges(G, solution)  # 添加节点和边
    draw_tree(G)  # 可视化树


def collect_steps_by_level(node, level=0, level_dict=None):
    if level_dict is None:
        level_dict = {}

    if level not in level_dict:
        level_dict[level] = []

    level_dict[level].append(node)

    for child in node.get('children', []):
        collect_steps_by_level(child, level + 1, level_dict)

    return level_dict