# 🤖 小智语音助手 - Android打包指南

## 📋 打包方式选择

由于您使用的是Windows系统，有以下几种打包方式：

### 方式一：使用WSL2（推荐）⭐

WSL2是Windows上运行Linux的最佳方式，打包成功率最高。

### 方式二：使用Google Colab（免费云端）

无需配置本地环境，直接在云端打包。

### 方式三：使用GitHub Actions（自动化）

提交代码后自动打包，适合持续集成。

---

## 🚀 方式一：WSL2打包（推荐）

### 步骤1：安装WSL2

```powershell
# 在PowerShell（管理员）中运行
wsl --install -d Ubuntu-22.04
```

重启电脑后，设置Ubuntu用户名和密码。

### 步骤2：配置WSL2环境

```bash
# 进入WSL Ubuntu
wsl

# 更新系统
sudo apt update && sudo apt upgrade -y

# 安装依赖
sudo apt install -y \
    python3-pip \
    python3-venv \
    git \
    zip \
    unzip \
    openjdk-17-jdk \
    autoconf \
    libtool \
    pkg-config \
    zlib1g-dev \
    libncurses5-dev \
    libncursesw5-dev \
    cmake \
    libffi-dev \
    libssl-dev \
    ccache

# 安装Buildozer和Cython
pip3 install --upgrade pip
pip3 install buildozer cython==0.29.33
```

### 步骤3：复制项目到WSL

```bash
# 在WSL中，项目位于 /mnt/c/Users/Ln/Documents/trae_projects/AI
cd /mnt/c/Users/Ln/Documents/trae_projects/AI

# 或者复制到WSL本地（更快）
cp -r /mnt/c/Users/Ln/Documents/trae_projects/AI ~/xiaozhi
cd ~/xiaozhi
```

### 步骤4：开始打包

```bash
# 清理之前的构建（如果有）
buildozer android clean

# 开始打包（首次需要下载SDK/NDK，约30分钟）
buildozer -v android debug
```

### 步骤5：获取APK

```bash
# APK文件位置
ls -la dist/

# 复制到Windows
cp dist/*.apk /mnt/c/Users/Ln/Desktop/
```

---

## ☁️ 方式二：Google Colab打包（免费）

### 步骤1：打开Google Colab

访问 https://colab.research.google.com/

### 步骤2：创建新笔记本，运行以下代码

```python
# 单元格1：安装依赖
!pip install buildozer cython==0.29.33
!sudo apt update
!sudo apt install -y git zip unzip openjdk-17-jdk autoconf libtool pkg-config zlib1g-dev libncurses5-dev cmake libffi-dev libssl-dev

# 单元格2：上传项目
from google.colab import files
import zipfile
import os

# 上传项目zip文件
uploaded = files.upload()

# 解压
for filename in uploaded.keys():
    if filename.endswith('.zip'):
        with zipfile.ZipFile(filename, 'r') as zip_ref:
            zip_ref.extractall('project')

# 单元格3：打包
%cd project
!buildozer -v android debug

# 单元格4：下载APK
files.download('dist/xiaozhi-2.0.0-debug.apk')
```

### 准备上传的zip文件

在Windows上，将项目打包为zip：
```powershell
# 在项目目录运行
Compress-Archive -Path * -DestinationPath xiaozhi.zip -Force
```

---

## 🔄 方式三：GitHub Actions自动打包

### 步骤1：创建GitHub仓库

将项目推送到GitHub。

### 步骤2：创建工作流文件

创建 `.github/workflows/build.yml`：

```yaml
name: Build Android APK

on:
  push:
    branches: [ main ]
  workflow_dispatch:

jobs:
  build:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.10'
    
    - name: Install dependencies
      run: |
        sudo apt update
        sudo apt install -y git zip unzip openjdk-17-jdk autoconf libtool pkg-config zlib1g-dev libncurses5-dev cmake libffi-dev libssl-dev
        pip install buildozer cython==0.29.33
    
    - name: Build APK
      run: |
        buildozer -v android debug
    
    - name: Upload APK
      uses: actions/upload-artifact@v3
      with:
        name: xiaozhi-apk
        path: dist/*.apk
```

### 步骤3：触发构建

推送代码或手动触发工作流，在Actions页面下载APK。

---

## 📱 安装APK到手机

### 方法1：USB传输
1. 用USB线连接手机和电脑
2. 将APK复制到手机
3. 在手机上点击APK安装

### 方法2：ADB安装
```bash
# 安装ADB
sudo apt install android-tools-adb

# 连接手机（开启USB调试）
adb devices

# 安装APK
adb install dist/xiaozhi-2.0.0-debug.apk
```

### 方法3：网络传输
- 通过微信/QQ发送APK文件
- 上传到网盘后下载

---

## ⚠️ 常见问题

### 1. 打包失败：SDK/NDK下载超时

**解决方案**：使用代理或手动下载
```bash
# 设置代理
export http_proxy=http://127.0.0.1:7890
export https_proxy=http://127.0.0.1:7890
```

### 2. 内存不足

**解决方案**：增加WSL内存
创建 `C:\Users\Ln\.wslconfig`：
```ini
[wsl2]
memory=8GB
swap=4GB
```

### 3. 应用闪退

**解决方案**：查看日志
```bash
adb logcat | grep python
```

### 4. 权限问题

确保手机已授予以下权限：
- 麦克风（语音识别）
- 存储（保存数据）
- 网络（联网查询）

---

## 📝 打包前检查清单

- [ ] Python依赖已安装：`pip install kivy kivymd requests beautifulsoup4 jieba`
- [ ] 项目文件完整：`src/`, `config/`, `mobile_app.py`, `buildozer.spec`
- [ ] 无语法错误：`python -m py_compile mobile_app.py`
- [ ] WSL2/Colab环境已配置
- [ ] 手机已开启"未知来源应用"安装

---

## 🎯 快速开始命令

```bash
# WSL2一键打包
cd ~/xiaozhi && buildozer -v android debug && cp dist/*.apk /mnt/c/Users/Ln/Desktop/

# 查看打包日志
buildozer -v android debug 2>&1 | tee build.log
```

祝打包顺利！🚀
