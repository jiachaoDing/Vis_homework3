# SDU数据可视化 - 作业三

## 项目简介
本项目是对Microsoft LIDA（Language Interface for Data Analysis）开源项目的学习与测试。LIDA是一个基于大语言模型的数据可视化工具，能够通过自然语言交互生成数据可视化图表。本项目旨在通过实践学习LIDA的使用方法，并测试其在数据可视化任务中的应用效果。

## 环境要求
- Python 3.8+
- Jupyter Notebook
- OpenAI API密钥
- 相关Python包（见requirements.txt）

## 安装步骤
1. 克隆LIDA仓库
```bash
git clone https://github.com/microsoft/lida.git
cd lida
```

2. 安装依赖
```bash
pip install -r requirements.txt
```

3. 配置环境变量
- 创建`.env`文件
- 添加OpenAI API密钥：
```
OPENAI_API_KEY=your_api_key_here
```

## 测试内容
本项目使用世界银行发展指标数据集对LIDA进行以下功能测试：

1. 数据总结功能测试
   - 测试LIDA对数据集的自动分析和总结能力
   - 验证数据字段识别和统计信息生成
   - 测试多国家、多指标数据的处理能力

2. 可视化目标生成测试
   - 测试LIDA根据数据自动生成可视化目标的能力
   - 验证目标生成的合理性和多样性
   - 测试时间序列和地理数据的可视化目标生成

3. 可视化方案生成测试
   - 测试LIDA根据目标生成具体可视化方案的能力
   - 验证可视化代码的可用性和效果
   - 测试多维度数据的可视化方案生成

4. 数据洞察生成测试
   - 测试LIDA对可视化结果的自动分析和评论能力
   - 验证洞察的准确性和价值
   - 测试跨国家、跨时间的数据洞察生成

## 数据集说明
世界银行发展指标数据集包含以下主要指标：
- GDP（国内生产总值）
- 人口数据
- 教育指标
- 健康指标
- 环境指标
- 基础设施指标
- 贸易数据
- 金融指标

数据特点：
- 时间跨度：1960年至今
- 覆盖国家：全球200多个国家和地区
- 数据维度：多维度指标
- 更新频率：年度更新

## 项目结构
```
.
├── README.md                 # 项目说明文档
├── requirements.txt          # 项目依赖
├── .gitignore               # Git忽略文件
├── test_notebook.ipynb      # 测试记录notebook
├── data/                    # 数据目录
│   ├── world_bank_data.csv  # 世界银行数据集
│   └── processed/           # 处理后的数据
└── visualizations/          # 可视化结果目录
```

## 测试过程
1. 环境准备
   - 安装Python 3.8+
   - 安装Jupyter Notebook
   - 配置OpenAI API密钥

2. LIDA部署
   - 克隆LIDA仓库
   - 安装所需依赖
   - 配置环境变量

3. 数据准备
   - 下载世界银行数据集
   - 数据预处理和清洗
   - 数据格式转换

4. 功能测试
   - 数据总结测试
   - 可视化目标生成测试
   - 可视化方案生成测试
   - 数据洞察生成测试

## 测试结果
[待补充测试结果]

## 注意事项
- 请确保API密钥的安全性
- 建议使用虚拟环境运行项目
- 注意数据集的更新和维护
- 关注数据质量和完整性

## 参考资料
- [LIDA项目地址](https://github.com/microsoft/lida)
- [LIDA论文](https://arxiv.org/abs/2303.02927)
- [世界银行数据](https://data.worldbank.org/)

## 许可证
MIT License 