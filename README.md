# Peihao's Garden 🌿

A clean personal blog — **DevOps & AI / Interests & Life / Economy & Current Events / Language Learning**

Built with **Jekyll**, hosted on **GitHub Pages**: push to `master` and it builds & deploys automatically. Zero cost, no server.

---

## ✍️ How to publish a post

Create a Markdown file in `_posts/`, named `YYYY-MM-DD-slug.md` (e.g. `2026-08-26-hello-world.md`).

The frontmatter decides which column the post lands in (**categories**):

```markdown
---
layout: post
title: "My Post Title"
date: 2026-08-26
categories: [tech]          # tech | hobby | economy | language
tags: [kubernetes, devops]
description: "One-line summary shown under the title"
---

Markdown body. Code highlighting, tables, images and blockquotes supported.
```

> Images go in `assets/images/`, referenced as `![alt](/assets/images/xxx.png)`.

Push to GitHub — GitHub Pages rebuilds in about a minute.

---

## 🗂 Columns

| Column | categories value | Topics |
|--------|------------------|--------|
| DevOps & AI | `tech` | Kubernetes, CI/CD, cloud-native, AI engineering |
| Interests & Life | `hobby` | Basketball, music, daily life |
| Economy & Current Events | `economy` | Macro trends, markets, current events |
| Language Learning | `language` | English learning journey, tips, practice logs |

Column names, icons and descriptions live in `_config.yml` under `category_*`.

---

## 🛠 Local development

```bash
# macOS system ruby works (ruby 2.6+)
gem install bundler
bundle install

# Serve at http://localhost:4000
bundle exec jekyll serve
```

## 📁 Project structure

```
├── _config.yml          # Site config (title, columns)
├── _posts/              # Posts — the only directory you touch regularly
├── _layouts/            # Templates (default / post / page)
├── _includes/           # Components (nav, footer, head)
├── css/                 # main.css theme + syntax.css code highlighting
├── assets/              # favicon, js, images
├── index.html           # Home — latest posts + columns
├── tech.html            # DevOps & AI column
├── hobby.html           # Interests & Life column
├── economy.html         # Economy & Current Events column
├── language.html        # Language Learning column
├── about.html           # About
└── 404.html
```

## 📄 License

MIT
