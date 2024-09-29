# LongThought可视化界面

## 说明

**三种构树方式：** PRM800k-based, Teacher-student-based(暂未), Teacher-only-based(暂未)

### PRM800k-based

#### Tree -> LongCoT

实际用于训练的CoT以及SFT后得到的模型：

| Training Data                                | Model                                     |
|----------------------------------------------|-------------------------------------------|
| ground truth solution                         | deepseek-math-7b-base-sft-math-vanilla   |
| prm800k_cot_from_tree_train_678_shortcut      | deepseek-math-7b-base-sft-math-shortcut  |
| prm800k_cot_from_tree_train_678（大量重复和冗余）|         |
| prm800k_cot_from_tree_train_678_v1            | deepseek-math-7b-base-sft-math-v1         |
| prm800k_cot_from_tree_train_678_v2            | deepseek-math-7b-base-sft-math-v2         |
| prm800k_cot_from_tree_train_678_v3            | deepseek-math-7b-base-sft-math-v3         |