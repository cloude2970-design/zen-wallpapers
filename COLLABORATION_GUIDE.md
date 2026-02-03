# Zen Wallpapers 团队协作指南

> 项目地址：https://github.com/cloude2970-design/zen-wallpapers  
> 线上预览：https://cloude2970-design.github.io/zen-wallpapers/

## 一、准备工作

### 1. 注册 GitHub 账号
如果你还没有 GitHub 账号，请前往 https://github.com/signup 注册。

### 2. 安装 Git
- **macOS**: 打开 Terminal，输入 `git --version`，如果没有安装，系统会提示安装 Xcode Command Line Tools
- **Windows**: 下载安装 https://git-scm.com/download/win
- **验证安装**: `git --version`

### 3. 配置 Git
```bash
git config --global user.name "你的名字"
git config --global user.email "你的邮箱@example.com"
```

## 二、获取仓库权限

联系项目管理员（Bob），将你的 GitHub 用户名发送给他，他会把你添加为 **Collaborator**。

收到邀请邮件后，点击接受邀请。

## 三、标准工作流程

### 1. 克隆仓库到本地
```bash
git clone https://github.com/cloude2970-design/zen-wallpapers.git
cd zen-wallpapers
```

### 2. 创建新分支（重要！）
每次添加新功能或修改，都要创建新分支，避免直接在 `main` 上修改：

```bash
# 拉取最新代码
git pull origin main

# 创建并切换到新分支（分支名要描述清楚做什么）
git checkout -b add-calm-ocean-wallpapers
```

### 3. 添加/修改壁纸

#### S-Class 精选集标准（重要！）
所有添加到 `s-grade-curated.json` 的图片必须符合 **V2.1 标准**：

1. **左右居中**: 主体必须在视觉中心线上 (fp-x=0.5)
2. **黄金分割以下**: 主体纵向坐标在 **61.8% 以下** (fp-y ≥ 0.62)
3. **顶部留白**: 画面上方 1/3 必须为纯净背景，不遮挡手机时钟
4. **禅意美学**: 极简、中性色调、宁静感

#### JSON 格式示例
```json
{
  "id": "calm-ocean-25",
  "url": "https://images.unsplash.com/photo-xxx?q=80&w=1320&h=2868&auto=format&fit=crop&crop=focalpoint&fp-x=0.5&fp-y=0.8",
  "score": 94,
  "reason": "V2.1: 海面平静，地平线位于画面下 1/3，上方天空纯净适合时钟显示",
  "author": "摄影师名字"
}
```

#### 获取 Unsplash 图片 URL
1. 在 Unsplash 找到符合标准的图片
2. 点击 "Download free" 旁的下拉箭头，选择 "Custom size"
3. 设置尺寸：Width=1320, Height=2868
4. 复制图片 URL（确保包含 `w=1320&h=2868` 参数）
5. 手动添加裁切参数：`&crop=focalpoint&fp-x=0.5&fp-y=0.8`

### 4. 提交修改
```bash
# 查看修改的文件
git status

# 添加修改
git add s-grade-curated.json

# 提交（写清楚的提交信息）
git commit -m "Add 5 new ocean-themed S-Class wallpapers (V2.1 standard)"

# 推送到远程仓库
git push origin add-calm-ocean-wallpapers
```

### 5. 创建 Pull Request (PR)

1. 打开 https://github.com/cloude2970-design/zen-wallpapers
2. 点击 "Compare & pull request" 按钮（如果你刚推送了分支）
3. 填写 PR 标题和描述：
   - 标题：简明扼要，如 "Add 5 new ocean wallpapers"
   - 描述：说明添加了哪些图片，为什么选择它们（符合 V2.1 标准）
4. 点击 "Create pull request"
5. 等待 Bob 审核并合并

## 四、审核清单 (Checklist)

提交 PR 前，请自检以下项目：

- [ ] 图片主体是否左右居中？
- [ ] 图片主体是否位于纵向 61.8% 以下？
- [ ] 裁切后顶部是否有足够留白（>30%）？
- [ ] URL 是否包含 `w=1320&h=2868&crop=focalpoint&fp-x=0.5` 参数？
- [ ] JSON 格式是否正确（无多余逗号、引号闭合）？
- [ ] 是否有重复图片（检查 id 是否唯一）？

## 五、本地预览

如果你想在本地查看修改效果：

```bash
# 在项目目录下启动本地服务器
python3 -m http.server 8000

# 浏览器打开
open http://localhost:8000
```

点击 "S-CLASS CURATED" 和 "REFRESH" 按钮测试是否正常显示。

## 六、常见问题

### Q: 我的修改没有显示在网站上？
A: 需要等待 PR 被合并到 `main` 分支，并且 GitHub Pages 自动部署（通常 1-2 分钟）。刷新网页缓存（Cmd/Ctrl + Shift + R）。

### Q: Unsplash API 报错？
A: 当前项目使用默认 API Key，如果频繁测试可能会触发限流。建议：
- 在 `index.html` 中输入你自己的 Unsplash API Key
- 或只测试本地 JSON 修改，不频繁搜索

### Q: 如何更新本地仓库？
```bash
git checkout main
git pull origin main
```

### Q: 冲突了怎么办？
```bash
git checkout main
git pull origin main
git checkout 你的分支
git rebase main
# 解决冲突后
git push origin 你的分支 --force
```

## 七、联系

有问题随时在 Telegram 群里 @Bob 或发 Issue 到 GitHub。

---

**记住我们的目标：为用户提供最符合手机壁纸使用场景（顶部留白、主体下沉）的禅意极简美学。**
