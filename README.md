# AI 知识库

一个自动采集、分析、整理 AI 相关信息的个人知识库。

## 目标
每日自动采集 20 条 AI 相关信息，使用 DeepSeek API 分析内容，生成结构化笔记。

## 目录结构
- `v1-skeleton/specs/` - 项目规划和愿景文档
- `knowledge-base/` - 采集的知识库（待生成）
  - `papers/` - 论文
  - `news/` - 新闻
  - `blog/` - 技术博客
  - `tool/` - 工具

## 如何使用
1. 安装依赖（待补充）
2. 配置 DeepSeek API Key
3. 运行采集脚本

## 推送到 GitHub
本地仓库已初始化。推送到 GitHub：

1. 在 GitHub 创建新仓库 `ai-knowledge-base`
2. 添加远程仓库：
   ```bash
   git remote add origin https://github.com/YOUR_USERNAME/ai-knowledge-base.git
   ```
3. 推送代码：
   ```bash
   git push -u origin master
   ```