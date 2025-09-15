# DeepSeekChat

一个基于DeepSeek API的桌面应用，使用PySide6构建的GUI应用程序。在macOS上配合自动化（Automator）实现与应用的互动。目前已经实现与Mail.app的集成，用户可以在Mail.app中选中邮件，点击右键，选择“Services” -> “DeepSeekChat”，即可将选中的邮件内容发送到DeepSeekChat应用进行处理。

## 项目概述

DeepSeekChat目前支持与Mail.app的集成，用户可以在Mail.app中选中邮件，点击右键，选择“Services” -> “DeepSeekChat”，即可将选中的邮件内容发送到DeepSeekChat应用进行处理。

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
- pyside6-stubs: 用于开发环境中提供更好的IDE自动补全、类型检查等功能
- requests：用于HTTP请求
- openai：用于与DeepSeek API交互

  ## 安装指南

### 1. 克隆项目

```bash
git clone https:/github.com/daxmate/deepseekchat.git
cd deepseekchat
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

``` bash
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


## 打包应用

使用PyInstaller可以将Python应用程序打包成独立的可执行文件或应用程序包，便于在没有Python环境的系统上运行。

### 1. 安装PyInstaller

```bash
pip install pyinstaller
```

### 2. 打包为可执行文件

在项目根目录下执行以下命令：

```bash
pyinstaller --onefile --windowed --name "DeepSeekChat" --icon=your_icon.ico main.py
```

参数说明：
- `--windowed`：创建窗口化应用程序（不显示控制台窗口）
- `--name`：指定输出的应用程序名称
- `--icon`：指定应用程序图标（可选，需要提供.ico文件）

### 3. macOS 特定打包说明

在macOS上，可以打包成.app应用程序包：

```bash
pyinstaller --windowed --name "DeepSeekChat" --icon=your_icon.icns main.py
```

打包完成后，您可以在`dist`目录下找到生成的`.app`文件。

### 4. 注意事项

- 如果程序依赖外部资源（如配置文件模板），需要使用`--add-data`选项将其包含在打包中
- 打包前请确保所有依赖项已正确安装
- 在不同操作系统上打包的应用程序只能在相同操作系统上运行
- 对于macOS，生成的.app文件可以通过Disk Utility制作成DMG安装包，提供更好的分发体验
- 如果打包的APP不能正常运行，可以在终端中运行dist文件夹下面的没有.app后缀的可执行文件，以便显示更多的信息以便排错

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
