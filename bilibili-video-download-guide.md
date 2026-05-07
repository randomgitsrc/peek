# Bilibili/B站视频下载完全指南

## 🥇 推荐工具：BBDown（B站专用神器）

### 特点
- ✅ 专为 B 站设计，解析最稳定
- ✅ 支持番剧、多P视频、合集批量下载
- ✅ 支持 4K/8K/杜比视界等高清画质（需登录）
- ✅ 自动下载字幕、弹幕、封面
- ✅ 支持 TV 版接口（部分视频免登录）

---

## 📥 安装

### Linux/macOS
```bash
# 下载最新版
curl -L -o BBDown.zip "https://github.com/nilaoda/BBDown/releases/latest/download/BBDown_linux-x64.zip"
unzip BBDown.zip
chmod +x BBDown

# 安装 ffmpeg（必需，用于合并音画）
# Ubuntu/Debian: sudo apt install ffmpeg
# macOS: brew install ffmpeg
```

### Windows
```powershell
# 下载地址：https://github.com/nilaoda/BBDown/releases
# 下载 BBDown_win-x64.zip，解压到任意目录
# 需要同时下载 ffmpeg.exe 放在同一目录
```

---

## 🚀 使用方法

### 基础下载（完整视频+音频）
```bash
BBDown "https://www.bilibili.com/video/BV1MX9DBtE1b"
```

### 仅下载视频（无声音）
```bash
BBDown "BV1MX9DBtE1b" --video-only
```

### 仅下载音频
```bash
BBDown "BV1MX9DBtE1b" --audio-only
```

### 交互式选择清晰度
```bash
BBDown "BV1MX9DBtE1b" --interactive
```

### 下载多P视频（全部）
```bash
BBDown "BV1MX9DBtE1b" -p ALL
```

### 下载特定分P
```bash
BBDown "BV1MX9DBtE1b" -p 1,3,5
```

### 下载番剧全集
```bash
BBDown "https://www.bilibili.com/bangumi/play/ssxxxxx" -p ALL
```

---

## 🔐 登录获取高画质

未登录限制：最高 720P
登录后可获取：1080P、4K、HDR、杜比视界

### 扫码登录
```bash
BBDown login
```

### 使用 TV 接口（部分视频免登录得 1080P）
```bash
BBDown "BV1MX9DBtE1b" --use-tv-api
```

---

## 📋 常用参数速查

| 参数 | 说明 |
|------|------|
| `--video-only` | 仅下载视频 |
| `--audio-only` | 仅下载音频 |
| `--danmaku-only` | 仅下载弹幕 |
| `--sub-only` | 仅下载字幕 |
| `--cover-only` | 仅下载封面 |
| `--interactive` | 交互式选择清晰度 |
| `-p ALL` | 下载所有分P |
| `-p 1,3,5` | 下载指定分P |
| `--use-tv-api` | 使用TV端接口 |
| `--work-dir ./dir` | 指定下载目录 |
| `--skip-mux` | 跳过混流（保留分离的音视频）|
| `--multi-thread` | 多线程下载（默认开启）|
| `--only-show-info` | 仅显示信息不下载 |

---

## 📝 完整示例

```bash
# 登录
BBDown login

# 下载 1080P 高码率视频（带字幕、弹幕）
BBDown "BV1MX9DBtE1b" --interactive

# 下载纯音频（比如想听课程/访谈）
BBDown "BV1MX9DBtE1b" --audio-only -o "何以当归.mp3"

# 下载到指定文件夹
BBDown "BV1MX9DBtE1b" --work-dir ~/Downloads/B站视频/

# 下载合集全部视频
BBDown "BV1MX9DBtE1b" -p ALL --work-dir ./合集/
```

---

## ⚠️ 注意事项

1. **版权提醒**：下载内容仅供个人学习使用，请勿用于商业用途或二次传播
2. **登录状态**：Cookie 会过期，如遇 412 错误请重新登录
3. **ffmpeg 必需**：合并音视频需要 ffmpeg，务必提前安装
4. **长视频**：支持数小时的视频下载，稳定性好
5. **会员专享**：部分视频需要大会员账号才能下载完整版

---

## 🔄 备用方案：yt-dlp

如果 BBDown 失效，可使用 yt-dlp（通用型下载器）：

```bash
# 安装
pip install -U yt-dlp

# 基础使用
yt-dlp "https://www.bilibili.com/video/BV1MX9DBtE1b"

# 使用浏览器 Cookie（需登录的会员视频）
yt-dlp --cookies-from-browser chrome "BV1MX9DBtE1b"

# 查看可用画质
yt-dlp -F "BV1MX9DBtE1b"
```

---

## 📚 相关链接

- BBDown 官方仓库：https://github.com/nilaoda/BBDown
- yt-dlp 官方仓库：https://github.com/yt-dlp/yt-dlp
- ffmpeg 下载：https://github.com/BtbN/FFmpeg-Builds/releases

---

*文档生成时间：2026-05-07*
*测试视频：「为何我们如此在意台湾？和苑举正老师看《何以当归》寻找答案」*
