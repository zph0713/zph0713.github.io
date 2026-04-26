---
title: Getting Started
layout: docs
permalink: /docs/getting-started/
---

# Getting Started

Welcome! This guide will help you understand the structure of this project.

## Project Layout

- `_docs/` — Markdown documents (rendered as pages)
- `_posts/` — Blog posts with dates and categories
- `css/` — Stylesheets for the cyberpunk theme
- `img/` — Images and assets

## Writing a New Post

Create a new markdown file in `_posts/`:

```markdown
---
title: "My Title"
date: 2026-04-26
categories: [AI, Research]
tags: [agent, LLM]
description: "Short description for the post."
---

# My Post Content
...
```

## Writing a Document

Create a markdown file in `_docs/`:

```markdown
---
title: "My Doc"
layout: docs
permalink: /docs/my-doc/
---

# Doc Title
...
```

## Running Locally

Install dependencies and start the Jekyll server:

```bash
bundle install
jekyll serve --host 0.0.0.0
```

Then visit `http://localhost:4000` in your browser.
