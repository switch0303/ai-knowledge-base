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

### 1. 环境设置
```bash
# 克隆仓库
git clone https://github.com/switch0303/ai-knowledge-base.git
cd ai-knowledge-base

# 创建虚拟环境（可选但推荐）
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# 或 venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt
```

### 2. 配置 API Key
1. 获取 DeepSeek API Key：https://platform.deepseek.com/api_keys
2. 复制 `.env.example` 为 `.env`：
   ```bash
   cp .env.example .env
   ```
3. 编辑 `.env` 文件，填入你的 API Key：
   ```
   DEEPSEEK_API_KEY=your_actual_api_key_here
   ```

### 3. 运行采集脚本
```bash
# 单次运行（测试）
python src/collect.py

# 后台运行（每日自动采集）
nohup python src/collect.py > collection.log 2>&1 &
```

### 4. 查看结果
采集的内容会保存到 `knowledge-base/` 目录：
- `papers/` - 学术论文
- `news/` - AI 新闻
- `blog/` - 技术博客
- `tool/` - 工具更新

每个文件为 Markdown 格式，包含：
- 原文链接
- AI 分析的一级结论和多级论据
- 推荐度和置信度评分
- 个人评论

## 配置说明
- 修改 `.env` 中的 `RSS_FEEDS` 添加/删除订阅源
- 修改 `KEYWORDS` 调整筛选关键词
- `DAILY_LIMIT` 控制每日采集数量（默认 20）
- `COLLECTION_TIME` 设置采集时间（UTC，默认 00:00）