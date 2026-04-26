# ZPH's Cyberpunk Blog 🌃 / 赛博朋克博客

---

## About / 关于

A cyberpunk-themed personal blog built with Jekyll — where code meets neon light.
一个使用 Jekyll 构建的赛博朋克风格个人博客——代码与霓虹交织。

> *Powered by code, caffeine, and a persistent sense of wonder.*
> *由代码、咖啡和永不熄灭的好奇心驱动。*

---

## Tech Stack / 技术栈

| Layer | Technology |
|-------|------------|
| **Framework** | [Jekyll](https://jekyllrb.com/) — static site generation |
| **Styling** | Custom cyberpunk CSS (purple `#a855f7` + cyan `#22d3ee`) |
| **Typography** | Orbitron (headings) + Fira Code (body/code) |
| **Hosting** | [GitHub Pages](https://pages.github.com/) — zero-cost, auto-deploy |

---

## Features / 特性

- ✨ **Starfield Animation** — Animated background stars via CSS keyframes
- 🎨 **Neon Glow Effects** — Purple/cyan accents with `text-shadow` glow
- 🔤 **Cyberpunk Typography** — Orbitron for headings, Fira Code for monospace
- 📚 **Docs System** — Markdown docs auto-rendered as pages (`_docs/`)
- 🖼️ **Code Highlighting** — Custom dark purple syntax theme

---

## Project Structure / 项目结构

```
├── _config.yml              # Jekyll configuration
├── css/                     # Stylesheets
│   ├── cyberpunk.css        # Main theme
│   └── syntax.css           # Code highlighting
├── _includes/               # Reusable components
│   ├── head.html            # Meta tags, fonts
│   ├── nav.html             # Navigation bar
│   └── footer.html          # Footer
├── _layouts/                # Page layouts
│   ├── default.html         # Base layout (with starfield)
│   ├── post.html            # Blog posts
│   ├── page.html            # Static pages
│   └── docs.html            # Documentation
├── _posts/                  # Blog articles
├── _docs/                   # In-depth guides
├── img/                     # Generated images
├── index.html               # Homepage — latest posts
├── about.html               # About Me page
└── 404.html                 # Custom 404 page
```

---

## Running Locally / 本地运行

### Prerequisites / 前置要求

- [Ruby](https://www.ruby-lang.org/) (3.2+) with Bundler
- [Jekyll CLI](https://jekyllrb.com/docs/installation/) (`gem install jekyll bundler`)

### Steps / 步骤

```bash
# Clone the repository
git clone https://github.com/zph0713/zph0713.github.io.git
cd zph0713.github.io

# Install dependencies
bundle install

# Start the development server
jekyll serve --host 0.0.0.0
```

Visit `http://localhost:4000` to see your blog live. / 访问 localhost 查看效果。

---

## Writing Content / 写作内容

### Blog Post / 博客文章

Create a new file in `_posts/`:

```markdown
---
title: "My New Post"
date: 2026-04-26
categories: [AI, Research]
tags: [agent, LLM]
description: "A short description."
layout: post
---

# My Title
...
```

### Documentation / 文档

Create a new file in `_docs/`:

```markdown
---
title: "My Guide"
layout: docs
permalink: /docs/my-guide/
---

# Title
...
```

---

## License / 许可

This project is open source and available under the [MIT License](LICENSE). / MIT 开源许可。

---

*Stay curious. Build beautiful things.* 🚀
