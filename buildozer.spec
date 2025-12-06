[app]

# 应用名称
title = 小智语音助手

# 包名
package.name = xiaozhi

# 包域名
package.domain = com.assistant

# 源代码目录
source.dir = .

# 包含的文件类型
source.include_exts = py,png,jpg,kv,atlas,txt,db

# 包含的目录
source.include_patterns = src/**/*,config/*,data/*,mobile_app.py

# 排除的目录
source.exclude_dirs = .buildozer,.git,__pycache__,bin,dist,venv,.kiro

# 排除的文件
source.exclude_patterns = *.pyc,*.pyo,*.log,test_*.py

# 应用版本
version = 2.0.0

# 依赖项 (精简版，减少网络下载)
requirements = python3,kivy==2.2.1,requests,certifi,charset-normalizer,idna,urllib3,plyer

# 屏幕方向
orientation = portrait

# 全屏
fullscreen = 0

# Android权限
android.permissions = INTERNET,RECORD_AUDIO,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE,ACCESS_NETWORK_STATE

# Android API版本
android.api = 31

# 最低API版本
android.minapi = 21

# Android SDK版本
android.sdk = 31

# Android NDK版本
android.ndk = 25b

# 架构 (单架构减少编译问题)
android.archs = arm64-v8a

# 是否接受SDK许可
android.accept_sdk_license = True

# 应用图标（可选）
# icon.filename = %(source.dir)s/icon.png

# 启动画面（可选）
# presplash.filename = %(source.dir)s/presplash.png

# 应用主题
android.theme = @android:style/Theme.NoTitleBar

# 调试模式
android.debug = True

# 日志过滤
android.logcat_filters = *:S python:D

# 复制库
android.copy_libs = 1

# Gradle依赖
android.gradle_dependencies = 

# 启用AndroidX
android.enable_androidx = True

# 跳过 Gradle 更新
android.skip_update = False

# 添加 Gradle 选项
android.add_gradle_repositories = google(),mavenCentral()

[buildozer]

# 日志级别 (0 = error, 1 = info, 2 = debug)
log_level = 2

# root警告
warn_on_root = 1

# 构建目录
build_dir = ./.buildozer

# 输出目录
dist_dir = ./dist
