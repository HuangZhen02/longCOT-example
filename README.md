# LongThought可视化界面

## 说明

**三种构树方式：** PRM800k-based, Teacher-student-based(暂未), Teacher-only-based(暂未)

### PRM800k-based

#### Tree -> LongCoT
prm800k_cot_from_tree_train_678: 原始的基于PRM800k的CoT，但是有大量重复和冗余

实际用于训练的CoT以及SFT后得到的模型：

| Training Data                                | Model                                     |
|----------------------------------------------|-------------------------------------------|
| prm800k_cot_from_tree_train_678_v1            | deepseek-math-7b-base-sft-math-v1         |
| prm800k_cot_from_tree_train_678_v2            | deepseek-math-7b-base-sft-math-v2         |