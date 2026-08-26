# 技术博客内容规划（DevOps & AI 栏目）

> 目标：让博客成为工作中的"能力名片"——面试官、领导、同事打开就知道你能干什么、干得怎么样。
> 本文是内部写作指南，不对外展示。

---

## 一、定位

**一句话定位：**

> Deep Linux DevOps × AI 自动化工作流 —— 从基础设施到 AI 应用的全栈自动化工程师

**目标读者：** 同行 DevOps 工程师、技术面试官、想了解 AI 自动化的业务同事

**博客的三种用途：**
1. **简历名片** —— 面试/晋升时直接把链接甩过去，比简历上的"精通 XXX"有说服力 100 倍
2. **知识沉淀** —— 踩过的坑写下来，半年后自己翻也有价值
3. **影响力** —— 差异化内容（AI Agent 协同、ComfyUI 流水线）能吸引关注

---

## 二、你的差异化优势（别人没有的组合）

| 能力 | 背书/证据 | 稀缺度 |
|------|----------|--------|
| Linux 系统与集群维护 | **RHCE**（红帽认证工程师） | 高 |
| Oracle 数据库运维 | **OCP**（Oracle 认证专家） | 高 |
| 自动化开发 Python / Go / Shell | 实战项目 | 中 |
| CI/CD 流水线 | 实战项目 | 中 |
| Dify & n8n workflow | 实战 | 高（DevOps 里少有人做） |
| Hermes & OpenClaw agent 协同 | 实战（前沿） | **极高** |
| ComfyUI workflow | 实战（AI 内容生产） | **极高** |

**核心叙事：** 传统 DevOps 硬功底（认证背书）+ 自动化开发 + AI 工作流三合一。
大多数 DevOps 只会前三条，你多了 AI 工作流和 Agent 协同 —— 这就是文章里要反复强化的"人设"。

---

## 三、六大内容支柱与选题库

### 支柱 1：Linux 系统与集群维护（你的地基）
文章类型以**实战复盘**为主，最有说服力。

- [ ] `How I debugged an OOM on a production K8s node`（生产 K8s 节点 OOM 排查全过程）
- [ ] `Linux performance triage: my toolbox from top to eBPF`（性能排查工具箱）
- [ ] `RHCE study notes: 50 commands I must remember`（备考笔记，知识清单类）
- [ ] `Cluster scaling best practices: what the docs don't tell you`（集群扩缩容实践）
- [ ] `journald power tricks for log forensics`（日志分析进阶）

### 支柱 2：自动化开发（Python / Go / Shell）
- [ ] `Writing a batch ops tool in Python that my team actually uses`（Python 批量运维工具）
- [ ] `Why Go is a great language for CLI ops tools`（Go 写运维 CLI）
- [ ] `The art of maintainable shell scripts`（可维护的 Shell 脚本）
- [ ] `My dotfiles & personal automation toolbox`（个人自动化工具箱）

### 支柱 3：CI/CD
- [ ] `From 0 to 1: a CI/CD pipeline that survives production`（CI/CD 从 0 到 1）
- [ ] `Cutting build time from 20 min to 5 min`（构建时间优化，有量化数据）
- [ ] `Blue-green & canary releases without fear`（蓝绿/金丝雀发布）
- [ ] `GitHub Actions: the good, the bad, the gotchas`（Actions 实战避坑）

### 支柱 4：Dify & n8n 工作流
- [ ] `n8n: automating my daily repetitive work`（n8n 自动化日常）
- [ ] `Building a knowledge-base bot with Dify`（Dify 知识库机器人）
- [ ] `n8n + Dify: a combo for business automation`（组合拳）

### 支柱 5：Hermes & OpenClaw Agent 协同（王牌内容，几乎没人写）
- [ ] `How I let AI agents manage my servers`（让 Agent 帮我管服务器）
- [ ] `Multi-agent orchestration: Hermes + OpenClaw in practice`（多 Agent 协同实战）
- [ ] `A day in my life with an AI ops assistant`（AI 运维助手的一天，故事性强）

### 支柱 6：ComfyUI 工作流（另一张王牌）
- [ ] `ComfyUI workflows 101 for engineers`（工程师视角的 ComfyUI 入门）
- [ ] `My AI comic-drama production pipeline`（AI 漫剧生产流水线 —— 独特性拉满）
- [ ] `Batch image generation with ComfyUI API`（ComfyUI API 批量出图）

---

## 四、文章类型模板（写之前选一种）

### 类型 A：实战复盘 ⭐最推荐（占 50%）
结构：**背景 → 问题 → 排查过程（带截图/命令）→ 根因 → 解决方案 → 效果数据 → 经验教训**
- 开头 3 行内说清：什么系统、什么问题、影响多大（"线上 3 个节点 OOM，业务中断 20 分钟"）
- 效果必须有数据：耗时从 X 到 Y、节省 Z 小时/月
- 结尾总结"下次遇到先查什么"

### 类型 B：教程
结构：**目标 → 环境（版本写清楚）→ 步骤（可复现，命令可复制）→ 结果 → 常见坑**
- 保证读者照做能跑通，这是口碑来源

### 类型 C：对比评测
结构：**场景 → 对比维度 → 实测（不要纯抄文档）→ 结论（适合谁）**
- 例：n8n vs Dify、Hermes vs 其他 Agent 框架

### 类型 D：知识清单
结构：**结构化清单 + 每项一句话说明**
- 例：RHCE 必背命令、集群巡检清单
- 适合备考和日常自查，容易被收藏

---

## 五、展示策略（如何让博客在工作中"变现"）

1. **简历 & LinkedIn 挂博客链接**：写"博客：zph0713.github.io（X 篇文章，覆盖 Linux 集群/CI/CD/AI 自动化）"
2. **面试话术**："我在博客里写过一次 OOM 排查全过程" —— 比"我精通排查"可信
3. **绩效/晋升材料**：从博客挑 2-3 篇代表作，附在材料里（体现总结能力和沉淀意识）
4. **每篇必带 3 个数据点**：问题规模、解决耗时、量化收益
5. **精品文同步外发**：每支柱 1-2 篇代表作同步 LinkedIn / 掘金 / 知乎（英文写，LinkedIn 面向国际化）
6. **保持英文写作**：国际化形象 + 搜索流量（英文技术文章 Google 收录价值高）

---

## 六、发布节奏

- 稳定期：**每周 1 篇**，不要断更超过两周
- 前 6 篇攒"弹药"：完成 6 个支柱各 1 篇，让博客打开就有完整能力地图
- 单篇质量 > 数量：一篇实战复盘（类型 A）顶三篇笔记

---

## 七、开局 6 篇（按顺序）

| # | 文章 | 支柱 | 目的 |
|---|------|------|------|
| 1 | `My DevOps toolbox 2026`（我的 DevOps 工具箱总览） | 合集 | 展示广度，让读者 3 分钟了解你 |
| 2 | 一次真实的生产故障复盘（OOM / 集群抖动等） | Linux 集群 | 展示深度与实战 |
| 3 | `How I let AI agents manage my servers` | Agent 协同 | 差异化王牌，全网稀缺 |
| 4 | `My AI comic-drama production pipeline`（ComfyUI） | ComfyUI | 独特性 + 趣味性，容易传播 |
| 5 | `From 0 to 1: CI/CD pipeline` | CI/CD | 中规中矩但求职刚需 |
| 6 | `n8n: automating my daily repetitive work` | Dify/n8n | 覆盖第六支柱 |

6 篇完成后，博客即拥有完整能力地图，可对外展示。

---

## 八、写作规范速查

- 全站英文（界面已是英文，文章默认英文；中文读者多的选题可中英双语）
- 每篇 frontmatter 模板：

```yaml
---
layout: post
title: "Post Title"
date: 2026-08-26
categories: [tech]
tags: [linux, kubernetes, troubleshooting]
description: "One-line summary with the key result (e.g. found root cause in 2h)"
---
```

- 截图规范：故障现场、监控图、最终效果图，都放 `assets/images/`
- 代码规范：命令可复制、注明版本、输出关键结果
- 检查清单：有没有数据点？读者能复现吗？3 个月后自己看得懂吗？
