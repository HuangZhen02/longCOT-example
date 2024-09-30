# LongThought可视化界面

## 说明

**三种构树方式：** PRM800k-based, Teacher-student-based(暂未), Teacher-only-based(暂未)

**树的可视化**: 红色节点表示rating为-1，黄色节点表示rating为0，绿色节点表示rating为1。


### PRM800k-based

#### Tree -> LongCoT

实际用于训练的CoT以及SFT后得到的模型：

| Training Data                                | Model                                     |
|----------------------------------------------|-------------------------------------------|
| ground truth solution                         | deepseek-math-7b-base-sft-math-vanilla   |
| prm800k_cot_from_tree_train_678_shortcut      | deepseek-math-7b-base-sft-math-shortcut  |
| prm800k_cot_from_tree_train_678（大量重复和冗余）| deepseek-math-7b-base-sft-math           |
| prm800k_cot_from_tree_train_678_v1            | deepseek-math-7b-base-sft-math-v1         |
| prm800k_cot_from_tree_train_678_v2            | deepseek-math-7b-base-sft-math-v2         |
| prm800k_cot_from_tree_train_678_v3            | deepseek-math-7b-base-sft-math-v3         |


### Teacher-Student-based

三个例子

其中，将gpt4o给出的rating为-1或者0，但是在beam-search过程中根据reward model给出的打分被选择的冲突节点，用红色圆框标识。