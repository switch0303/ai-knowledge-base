# AI 知识库愿景

## 1. 采集目标
- 每日采集 20 条信息
- 自动抓取：RSS 订阅 + 关键词搜索
- 关键词：AI, machine learning, deep learning, LLM, NLP, computer vision, AGI, GPT, diffusion, transformers, multimodal
- 采集时间：每天 UTC 00:00 (北京时间 08:00)

## 2. 信息源

### RSS 订阅
- ArXiv 官方：https://arxiv.org/rss/stat.ML, cs.CL, cs.LG
- Import AI: https://importai.io (RSS)
- MIT News AI
- Hacker News: https://hnrss.org/frontpage
- OpenAI Blog
- Anthropic Blog
- Google AI Blog
- Meta AI Blog
- The Batch (邮件订阅)

### YouTube (暂不需要)
- Two Minute Papers
- Yannic Kilcher

## 3. Agent
- 使用 DeepSeek API 分析内容
- 等待 API Key

## 4. 分析维度
- 一级结论：一句话总结
- 多级论据：支撑论点的证据列表
- 可追溯链接：原文链接
- 评论：个人见解
- 推荐度：1-5 (基于来源可信度)
- 置信度：基于来源可信度

## 5. 存储格式
- md 格式
- 目录结构：
  ```
  /knowledge-base
    /papers     (论文)
    /news       (新闻、 newsletters)
    /blog       (技术博客)
    /tool       (工具)
  ```

## 6. 目标
- 纯个人学习笔记