# 数据可视化项目

## 项目简介
本项目使用Jupyter Notebook进行数据可视化分析，结合ChatGPT API实现智能数据分析和可视化生成。

## 环境要求
- Python 3.8+
- Jupyter Notebook
- 相关Python包（见requirements.txt）

## 安装步骤
1. 克隆仓库
```bash
git clone [仓库地址]
cd [项目目录]
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

## 使用方法
1. 启动Jupyter Notebook
```bash
jupyter notebook
```

2. 打开`lida_with_chatgpt.ipynb`文件

3. 按照notebook中的说明运行代码

## 项目结构
```
.
├── README.md
├── requirements.txt
├── .gitignore
├── lida_with_chatgpt.ipynb    # 测试使用notebook文件
└── sales_data.csv             # 示例数据
```

## 注意事项
- 请确保API密钥的安全性
- 建议使用虚拟环境运行项目
- 数据文件请根据实际需求替换

## 贡献指南
1. Fork 项目
2. 创建特性分支
3. 提交更改
4. 推送到分支
5. 创建Pull Request

## 许可证
MIT License 