# Peihao's Garden 🌿

清新风格的个人博客 —— DevOps & AI / 兴趣生活 / 经济时事

基于 **Jekyll** 构建，托管于 **GitHub Pages**：push 到 `master` 分支自动构建上线，零成本、无需服务器。

---

## ✍️ 怎么发新文章（最重要的部分）

在 `_posts/` 目录新建一个 Markdown 文件，文件名格式：`YYYY-MM-DD-文章标题.md`（如 `2026-08-26-hello-world.md`）。

文件开头写 frontmatter（三横线之间），**categories 决定文章进哪个栏目**：

```markdown
---
layout: post
title: "文章标题"
date: 2026-08-26
categories: [tech]          # tech=DevOps & AI | hobby=兴趣生活 | economy=经济时事
tags: [kubernetes, devops]
description: "一句话摘要，会显示在文章页标题下方"
---

正文用 Markdown 写，支持代码高亮、表格、图片、引用块。

```
```

> 图片放在 `assets/images/` 目录，正文里用 `![描述](/assets/images/xxx.png)` 引用。

写好后 push 到 GitHub，等一两分钟 GitHub Pages 自动构建上线。

---

## 🗂 栏目说明

| 栏目 | categories 值 | 内容 |
|------|--------------|------|
| DevOps & AI | `tech` | Kubernetes、CI/CD、云原生、AI 工程实践 |
| 兴趣生活 | `hobby` | 篮球、音乐、生活日常 |
| 经济时事 | `economy` | 宏观走势、市场热点、观察思考 |

栏目名称、图标、简介都在 `_config.yml` 的 `category_*` 配置里，想改直接编辑。

---

## 🛠 本地预览

```bash
# 首次需要装依赖（macOS 系统自带 ruby 即可）
gem install bundler
bundle install

# 启动本地服务，浏览器打开 http://localhost:4000
bundle exec jekyll serve
```

## 📁 项目结构

```
├── _config.yml          # 站点配置（标题、栏目定义）
├── _posts/              # 文章目录（唯一需要经常动的目录）
├── _layouts/            # 页面模板（default / post / page）
├── _includes/           # 公共组件（导航、页脚、head）
├── css/                 # main.css 主题样式 + syntax.css 代码高亮
├── assets/              # favicon、js、图片
├── index.html           # 首页
├── tech.html            # DevOps & AI 栏目页
├── hobby.html           # 兴趣生活栏目页
├── economy.html         # 经济时事栏目页
├── about.html           # 关于我
└── 404.html
```

## 📄 License

MIT
