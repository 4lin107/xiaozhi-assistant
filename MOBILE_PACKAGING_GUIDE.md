# AI语音助手移动端打包指南

本指南将帮助您将AI语音助手应用打包为Android APK文件，以便在手机上安装和运行。

## 一、打包环境准备

由于Buildozer（Kivy应用打包工具）在Linux环境下工作得最好，我们建议使用以下环境之一：

### 1. 选项一：使用Linux系统（推荐）

如果您有Linux系统（如Ubuntu、Debian等），可以直接在其上安装Buildozer。

### 2. 选项二：使用WSL（Windows Subsystem for Linux）

如果您使用Windows系统，可以安装WSL并在其中运行Linux环境：

1. 启用WSL功能
2. 安装Ubuntu或其他Linux发行版
3. 在WSL中执行后续打包步骤

## 二、安装依赖项

在Linux环境中，执行以下命令安装Buildozer和必要的依赖：

```bash
# 更新系统包
pip install --upgrade pip

# 安装Buildozer
pip install buildozer

# 安装系统依赖
sudo apt update
sudo apt install -y git zip unzip openjdk-11-jdk python3-pip autoconf libtool pkg-config zlib1g-dev libncurses5-dev libncursesw5-dev libtinfo5 cmake libffi-dev libssl-dev

# 安装Android SDK和NDK（Buildozer会自动下载，但这些依赖可能需要手动安装）
sudo apt install -y android-sdk-platform-tools android-sdk-build-tools
```

## 三、项目结构检查

确保项目目录结构如下：

```
AI/
├── src/
│   ├── assistant/
│   ├── api_integration/
│   ├── config/
│   ├── dialogue_manager/
│   ├── nlp/
│   ├── security/
│   └── speech_recognition/
├── data/
├── config/
├── mobile_app.py
├── buildozer.spec
└── MOBILE_PACKAGING_GUIDE.md
```

## 四、配置Buildozer

我们已经创建了`buildozer.spec`文件，包含了基本配置。您可以根据需要修改以下关键参数：

- `title`: 应用名称
- `package.name`: 包名
- `package.domain`: 域名
- `requirements`: 应用依赖项
- `android.permissions`: 应用所需权限

## 五、执行打包命令

在项目根目录下执行以下命令：

```bash
# 初始化Buildozer环境（首次运行时需要）
buildozer init

# 开始打包APK
buildozer -v android debug
```

Buildozer会自动执行以下步骤：
1. 下载并配置Android SDK和NDK
2. 编译Python解释器和依赖项
3. 将应用代码打包到APK中
4. 生成调试版本的APK文件

## 六、获取APK文件

打包完成后，APK文件将位于以下位置：

```
dist/voiceassistant-1.0.0-debug.apk
```

## 七、安装到手机

将生成的APK文件传输到您的Android手机，然后：

1. 在手机设置中启用"未知来源应用"安装
2. 点击APK文件进行安装
3. 安装完成后，即可打开并使用AI语音助手

## 八、常见问题及解决方法

### 1. 打包过程中出现依赖错误

**解决方案**：检查`buildozer.spec`文件中的`requirements`参数，确保所有依赖项的名称正确。

### 2. 内存不足错误

**解决方案**：如果打包过程中出现内存不足错误，可以尝试：
- 关闭其他占用内存的程序
- 增加系统交换空间
- 在WSL中分配更多内存（修改`.wslconfig`文件）

### 3. Android SDK/NDK下载失败

**解决方案**：可以手动下载Android SDK和NDK，并在`buildozer.spec`中指定路径：

```ini
android.sdk_path = /path/to/android-sdk
tandroid.ndk_path = /path/to/android-ndk
```

### 4. 应用在手机上无法运行

**解决方案**：
- 确保手机已授予应用所需的所有权限（录音、存储等）
- 检查应用日志以获取详细错误信息
- 尝试在调试模式下运行应用

## 九、调试应用

如果应用在手机上出现问题，可以使用以下命令查看日志：

```bash
# 查看应用日志
buildozer android logcat
```

## 十、生成发布版本

当应用测试完成后，可以生成发布版本的APK：

```bash
# 生成发布版本APK
buildozer android release
```

生成的发布版本APK需要签名才能在Google Play商店发布。有关签名APK的详细信息，请参考Android官方文档。

## 十一、iOS打包（可选）

如果您想将应用打包为iOS应用（IPA文件），需要：

1. 一台Mac电脑
2. Apple开发者账号
3. 修改`buildozer.spec`文件的iOS相关配置
4. 执行以下命令：

```bash
buildozer ios debug
```

有关iOS打包的详细信息，请参考Kivy官方文档。

---

通过以上步骤，您应该能够成功将AI语音助手应用打包为Android APK文件，并在手机上安装和运行。如果遇到任何问题，请参考Kivy和Buildozer的官方文档，或在相关社区寻求帮助。
