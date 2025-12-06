# AI语音助手Windows安装与运行指南

## 一、Python安装指南

### 1. 下载Python

访问Python官方下载页面：[https://www.python.org/downloads/windows/](https://www.python.org/downloads/windows/)

- 选择**Python 3.8或更高版本**（推荐使用3.10或3.11）
- 点击"Download Python X.X.X"按钮

### 2. 安装Python

运行下载的安装程序（如`python-3.11.5-amd64.exe`）：

1. **重要**：勾选"Add Python X.X to PATH"选项
2. 点击"Install Now"（推荐）或"Customize Installation"
3. 等待安装完成
4. 点击"Close"结束安装

### 3. 验证Python安装

按`Win + R`打开运行窗口，输入`cmd`并按Enter打开命令提示符，执行以下命令：

```cmd
python --version
```

如果显示Python版本号（如`Python 3.11.5`），说明安装成功。

如果仍然显示"'python' 不是内部或外部命令"，请尝试以下步骤：

#### 方法1：使用python3命令

```cmd
python3 --version
```

#### 方法2：手动添加Python到PATH

1. 找到Python安装目录（通常是`C:\Users\你的用户名\AppData\Local\Programs\Python\Python311\`）
2. 按`Win + X`，选择"系统"，然后点击"高级系统设置"
3. 点击"环境变量"按钮
4. 在"系统变量"中找到"Path"，点击"编辑"
5. 点击"新建"，添加Python安装目录和Scripts目录（如`C:\Users\你的用户名\AppData\Local\Programs\Python\Python311\`和`C:\Users\你的用户名\AppData\Local\Programs\Python\Python311\Scripts\`）
6. 点击"确定"保存所有更改
7. 重新打开命令提示符，再次尝试`python --version`

## 二、运行AI语音助手

### 1. 使用批处理脚本（推荐）

1. 找到项目目录中的`run_on_windows.bat`文件
2. 双击运行该文件

脚本会自动完成以下操作：
- 检查Python安装情况
- 检查pip安装情况
- 安装所需依赖
- 启动语音助手

### 2. 手动运行

如果批处理脚本遇到问题，可以尝试手动运行：

1. 打开命令提示符，切换到项目目录：
   ```cmd
   cd C:\Users\Ln\Documents\trae_projects\AI
   ```

2. 安装依赖：
   ```cmd
   pip install -r requirements.txt
   ```

3. 启动语音助手：
   ```cmd
   python src/main.py
   ```

## 三、常见问题与解决方案

### 1. Python/Pip命令无法识别

**问题**：'python' 不是内部或外部命令，也不是可运行的程序或批处理文件。

**解决方案**：
- 检查Python安装时是否勾选了"Add Python to PATH"选项
- 手动添加Python到系统环境变量
- 尝试使用`python3`命令代替`python`

### 2. 依赖安装失败

**问题**：pip install -r requirements.txt 执行失败

**解决方案**：
- 检查网络连接是否正常
- 升级pip：`python -m pip install --upgrade pip`
- 使用国内镜像源安装：
  ```cmd
  pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
  ```

### 3. PyAudio安装失败

**问题**：Failed building wheel for pyaudio

**解决方案**：

1. 安装Microsoft Visual C++ 14.0或更高版本（可通过[Build Tools for Visual Studio](https://visualstudio.microsoft.com/zh-hans/downloads/#build-tools-for-visual-studio-2022)安装）

2. 或使用预编译的wheel文件：
   - 访问[PyAudio Windows wheels](https://www.lfd.uci.edu/~gohlke/pythonlibs/#pyaudio)
   - 下载适合你Python版本的whl文件（如`PyAudio-0.2.11-cp311-cp311-win_amd64.whl`）
   - 使用pip安装下载的文件：
     ```cmd
     pip install PyAudio-0.2.11-cp311-cp311-win_amd64.whl
     ```

### 4. 语音助手启动失败

**问题**：运行`python src/main.py`后程序崩溃

**解决方案**：
- 检查是否所有依赖都已正确安装
- 检查是否有麦克风和扬声器权限
- 查看程序输出的错误信息，根据具体错误进行排查

## 四、其他注意事项

1. **麦克风权限**：确保语音助手可以访问你的麦克风
   - Windows设置 → 隐私 → 麦克风 → 允许应用访问你的麦克风

2. **扬声器设置**：确保你的默认音频输出设备正常工作

3. **防火墙设置**：如果语音助手需要联网功能，确保防火墙不会阻止程序访问网络

4. **Python版本**：推荐使用Python 3.8-3.11版本，过高或过低的版本可能导致兼容性问题

## 五、联系支持

如果按照以上步骤操作后仍遇到问题，请提供以下信息寻求帮助：
- 操作系统版本
- Python版本
- 完整的错误信息
- 已尝试的解决方法

---

祝你使用愉快！