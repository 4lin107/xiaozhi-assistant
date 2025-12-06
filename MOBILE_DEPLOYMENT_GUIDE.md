# 语音助手移动端部署指南

本指南将帮助您将语音助手应用打包为移动应用并在Android设备上运行。

## 技术栈
- **框架**: Kivy + KivyMD
- **打包工具**: Buildozer
- **平台**: Android

## 环境准备

### 1. 安装依赖

首先，确保您的Python环境已安装以下依赖：

```bash
# 安装Kivy和KivyMD
pip install -r requirements.txt

# 安装Buildozer
pip install buildozer
```

### 2. 创建Buildozer配置

运行以下命令初始化Buildozer配置：

```bash
buildozer init
```

这将在项目根目录创建一个`buildozer.spec`文件。

## 配置Buildozer

编辑`buildozer.spec`文件，进行以下配置：

```ini
# (str) Title of your application
title = 语音助手

# (str) Package name
package.name = voiceassistant

# (str) Package domain (needed for android/ios packaging)
package.domain = com.example

# (str) Source code where the main.py live
source.dir = .

# (list) Source files to include (let empty to include all the files)
source.include_exts = py,png,jpg,kv,atlas

# (list) Application requirements
# comma separated e.g. requirements = sqlite3,kivy
requirements = python3,kivy,kivymd,speechrecognition,pyttsx3,jieba,nltk,requests

# (str) Supported orientation (one of landscape, sensorLandscape, portrait or all)
orientation = portrait

# (list) Permissions
android.permissions = INTERNET,RECORD_AUDIO,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE

# (int) Android API to use
android.api = 27

# (int) Minimum API your APK will support
android.minapi = 21

# (int) Android SDK version to use
android.sdk = 24

# (str) Android NDK version to use
android.ndk = 17c

# (str) Android NDK directory (if empty, it will be automatically downloaded.)
android.ndk_path =

# (str) Android SDK directory (if empty, it will be automatically downloaded.)
android.sdk_path =

# (str) Android NDK directory (if empty, it will be automatically downloaded.)
android.ndk_path =

# (bool) Indicate whether the application should be fullscreen or not
fullscreen = 0
```

## 打包应用

### 1. 构建APK

运行以下命令构建Android APK：

```bash
buildozer -v android debug
```

这个过程会自动下载所需的Android SDK、NDK等依赖，并将应用打包为APK文件。

### 2. 查找APK文件

构建完成后，APK文件将位于以下位置：

```
bin/voiceassistant-0.1-debug.apk
```

## 安装到手机

### 1. 启用开发者模式

在Android手机上：
- 打开"设置" -> "关于手机"
- 连续点击"版本号"7次，启用开发者模式

### 2. 启用USB调试

- 打开"设置" -> "开发者选项"
- 启用"USB调试"
- 启用"允许安装未知来源的应用"

### 3. 安装APK

将构建好的APK文件传输到手机上，然后点击安装即可。

## 运行应用

安装完成后，在应用列表中找到"语音助手"应用并点击运行。

## 功能说明

### 核心功能
1. **文本输入**：通过输入框发送文本消息
2. **语音识别**：点击"开始语音识别"按钮进行语音输入
3. **实时对话**：与语音助手进行实时对话
4. **API集成**：支持天气、新闻等API调用

### 权限说明

应用需要以下权限：
- **INTERNET**：用于API调用
- **RECORD_AUDIO**：用于语音识别
- **WRITE_EXTERNAL_STORAGE**：用于保存日志和数据
- **READ_EXTERNAL_STORAGE**：用于读取配置和数据

## 调试

### 1. 查看日志

使用以下命令查看应用运行日志：

```bash
buildozer android logcat
```

### 2. 常见问题

#### 问题1：语音识别失败
- 检查是否已授予麦克风权限
- 确保网络连接正常

#### 问题2：API调用失败
- 检查网络连接
- 检查API密钥配置

#### 问题3：应用崩溃
- 查看日志获取详细错误信息
- 检查依赖版本兼容性

## iOS部署（可选）

部署到iOS需要macOS环境和Xcode。可以使用以下命令构建IPA文件：

```bash
buildozer -v ios debug
```

## 更新日志

- v1.0：初始版本，支持文本输入和语音识别
