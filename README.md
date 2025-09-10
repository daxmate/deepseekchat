# DeepSeek邮件助手

一个基于DeepSeek API的智能邮件回复助手，使用PySide6构建的GUI应用程序。

## 项目概述

DeepSeek邮件助手是一个专为提高邮件处理效率而设计的工具，它能够：

- 从标准输入读取邮件内容
- 通过DeepSeek API生成专业的邮件回复
- 提供直观的GUI界面进行交互
- 支持流式响应展示，实时查看生成过程
  ### 功能特点
- 智能邮件回复：基于DeepSeek API生成高质量邮件回复
- 直观GUI界面：使用PySide6构建的用户友好界面
- 流式响应：实时显示生成的邮件内容，无需等待整个回复完成
- 配置持久化：保存用户信息和提示模板
- 快捷键支持：回车发送消息，Shift+Enter换行
- 系统集成：程序关闭时自动输出最终回复内容到标准输出
  ### 依赖项
  项目依赖以下Python库：

- pyside6：用于构建GUI界面
- requests：用于HTTP请求
- openai：用于与DeepSeek API交互

  ## 安装指南

### 1. 克隆项目

```bash
git clone https://your-repository-url/deepseek-email-assistant.git
cd deepseek-email-assistant
```

### 2. 创建虚拟环境

```bash
python3 -m venv .venv
```

### 3. 激活虚拟环境

```bash

# macOS/Linux

source .venv/bin/activate

# Windows

.\.venv\Scripts\activate
```

### 4. 安装依赖

```bash
pip install -r requirements.txt
```

### 5. 配置API密钥

在`~/dotfiles/ai_api_keys`文件中添加DeepSeek API密钥：

```bash
export DEEPSEEK_API_KEY=sk-xxxxxxxxxxxxxx
```

## 配置文件

程序会在以下位置创建配置文件：

- macOS: `~/Library/Application Support/DeepSeekChat/config.json`
- Linux/Windows: `~/.config/DeepSeekChat/config.json`
  配置文件包含以下内容：

- 用户信息（姓名、职位、公司）
- 邮件回复提示模板

## 使用方法

### 基本使用

通过管道将邮件内容传递给程序：

```bash
cat email.txt | python main.py
```

在程序界面中，您可以：

1. 查看原始邮件内容和系统提示
2. 添加额外的指令或问题
3. 点击"发送"按钮或按Enter键获取回复
4. 实时查看生成的回复内容
5. 关闭窗口时，最终回复会自动输出到标准输出

### 从不同环境运行的说明
程序设计为可从macOS的Automator中加载，因此包含了从标准输入(stdin)读取邮件内容的代码。如果您直接从程序自身运行（而非通过Automator或管道提供输入），需要进行以下处理：

macOS和Linux：将输入重定向到/dev/null

```

bash
python main.py < /dev/null
```

Windows：将输入重定向到NUL
```cmd
python main.py < NUL
```
在PyCharm中运行：需要在运行配置中配置输入重定向，或者修改运行配置以避免程序等待标准输入。具体方法是：

1. 打开运行配置（Run > Edit Configurations）
2. 在配置中找到"Execution"部分
3. 选中"Redirect input from"选项
4. 对于macOS/Linux，输入"/dev/null"；对于Windows，输入"NUL"


### 快捷键

- Enter：发送消息并获取回复
- Shift+Enter：在输入框中插入换行符

## 项目结构

```plainText
├── main.py # 主程序文件
├── deepseekchat.py # UI定义文件（由Qt Designer生成）
├── deepseekchat.ui # Qt Designer UI设计文件
├── requirements.txt # 项目依赖
└── .venv/ # Python虚拟环境
```

## 开发说明

### 修改UI

如果需要修改界面，可以使用Qt Designer打开deepseekchat.ui文件，修改后重新生成Python代码：

```bash
pyside6-uic deepseekchat.ui -o deepseekchat.py
```

### 添加新功能

在修改`main.py`文件时，请注意：

所有UI相关的修改应通过Qt Designer进行，而不是直接编辑`deepseekchat.py`
功能逻辑应添加在`DeepSeekChat`类中
API调用相关代码位于`start_stream`和`read_stream`方法中

### 注意事项

请确保您的API密钥正确配置，否则程序无法连接到DeepSeek API
配置文件需要手动创建或由程序首次运行时自动生成
程序会在关闭时输出最终回复内容，请确保正确捕获输出

## 许可证

MIT License

## 贡献

欢迎提交Pull Request改进项目

## 问题反馈

如果您遇到任何问题，请通过GitHub Issues报告

## 致谢

DeepSeek API提供强大的语言模型支持
PySide6提供跨平台GUI开发能力
OpenAI Python库简化API调用流程