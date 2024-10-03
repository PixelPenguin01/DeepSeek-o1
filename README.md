# DeepSeek-o1

DeepSeek-o1 是一个使用 DeepSeek 模型创建推理链以提高输出准确性的原型应用。

## 功能特点

- 使用 DeepSeek API 进行多步推理
- 实时显示推理过程和思考时间
- 美观的用户界面

## 安装

1. 克隆仓库：
   ```bash
   git clone https://github.com/your-username/deepseek-o1.git
   cd deepseek-o1
   ```

2. 安装依赖：
   ```bash
   pip install -r requirements.txt
   ```

3. 配置 API 密钥：
   在项目根目录创建 `.env` 文件，添加以下内容：
   ```bash
   DEEPSEEK_API_KEY=your_api_key_here
   ```

## 运行应用

执行以下命令启动应用：

```bash
streamlit run app_deepseek.py
```

## 测试效果

以下是两张测试效果图，展示了应用的界面和功能：

![测试效果图1](path_to_image1.png)

*图1：应用主界面*

![测试效果图2](path_to_image2.png)

*图2：推理过程展示*

## 文件说明

- `app_deepseek.py`: 主应用程序文件
- `style.css`: 自定义样式文件
- `requirements.txt`: 项目依赖列表
- `.env`: 环境变量配置文件
- `LICENSE`: 项目许可证文件

## 许可证

本项目采用 MIT 许可证。详情请见 [LICENSE](LICENSE) 文件。
