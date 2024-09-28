import streamlit as st
import pandas as pd
import json
import re
import chardet
import networkx as nx
import matplotlib.pyplot as plt
import textwrap
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

# def visualize_tree(solution):
#     # 生成 GraphViz 的 dot 代码
#     def generate_dot(data, parent=None):  
#         dot_lines = []
#         # Use doublecircle shape for final correct answer
#         node_shape = 'shape=box, width=0.8, height=0.8'
#         if data.get("is_correct"):  
#             node_shape = 'shape=doublecircle, width=0.8, height=0.8'
        
#         node_label = f'"{data["name"]}" [label="{data["name"]}", {node_shape}, fontsize=20]'
#         dot_lines.append(node_label)
        
#         if parent:
#             dot_lines.append(f'"{parent}" -> "{data["name"]}"')
        
#         for child in data.get("children", []):  
#             dot_lines.extend(generate_dot(child, data["name"]))
        
#         return dot_lines

#     def get_nodes_at_level(data, level, current_level=0):
#         if current_level == level:
#             return [data]
#         nodes = []
#         if "children" in data:
#             for child in data["children"]:
#                 nodes.extend(get_nodes_at_level(child, level, current_level + 1))
#         return nodes

#     def get_max_depth(data, current_depth=0):
#         if not data.get("children"):
#             return current_depth
#         depths = [get_max_depth(child, current_depth + 1) for child in data["children"]]
#         return max(depths)

#     # 生成 GraphViz 图
#     dot_representation = "\n".join(generate_dot(solution))

#     dot_representation = f"""
#     digraph G {{
#         graph [size="10,10", ratio=fill, fontsize=26];
#         edge [fontsize=20];
#         {dot_representation}
#     }}
#     """
    
#     # 创建左右两栏布局
#     col1, col2 = st.columns([0.6, 0.4])

#     with col1:
#         st.graphviz_chart(dot_representation)
    
#     with col2:
#         # 获取树的最大深度
#         max_depth = get_max_depth(solution)
    
#         # 选择层级的下拉框
#         selected_level = st.selectbox("Select level to display:", list(range(max_depth + 1)))
        
#         st.write(f"### Nodes at Level {selected_level}")
        
#         # 获取所选层级的节点
#         nodes_at_level = get_nodes_at_level(solution, selected_level)
        
#         for node in nodes_at_level:
#             st.write(f"#### {node['name']}")
#             step = node['step'].replace("\n", "<br>")
#             st.write(f"{step}", unsafe_allow_html=True)


# 递归生成树的节点和边
def add_edges(graph, data, parent=None):
    node_label = data["name"]
    graph.add_node(node_label, is_correct=data.get("is_correct", False), rating=data.get("rating", -1))  # 添加节点
    
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
    for node in graph.nodes():
        if graph.nodes[node]["is_correct"]:
            node_colors.append("lightgreen")  # 如果 is_correct 为 True，则颜色为 lightgreen
        elif graph.nodes[node]["rating"] == -1:
            node_colors.append("lightcoral")  # 如果 rating 为 -1，则颜色为 lightcoral（相当于 lightred）
        else:
            node_colors.append("skyblue")  # 否则颜色为 skyblue

    # 绘制节点和边
    nx.draw_networkx_edges(graph, pos)
    nx.draw_networkx_nodes(graph, pos, node_color=node_colors, node_size=500, node_shape='o')
    
    # 在节点上显示标签
    nx.draw_networkx_labels(graph, pos, font_size=6, font_weight='bold')

    # 显示图形
    plt.axis('off')
    
    st.pyplot(plt, dpi=500)  # 使用streamlit显示matplotlib图像

def visualize_tree(solution):
    G = nx.DiGraph()  # 创建一个有向图
    add_edges(G, solution)  # 添加节点和边
    draw_tree(G)  # 可视化树



def get_steps_at_level(node, level):
    if level == 0:
        # 如果是目标层，返回该节点的 name 和 step
        return [(node['name'], node['step'])]
    else:
        # 否则递归遍历其子节点
        steps = []
        for child in node.get('children', []):
            steps.extend(get_steps_at_level(child, level - 1))
        return steps