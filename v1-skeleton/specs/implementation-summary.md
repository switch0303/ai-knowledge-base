# AI 知识库实现总结

## 项目概述
本项目是一个自动采集、分析、整理 AI 相关信息的个人知识库，通过 RSS 订阅抓取 AI 领域最新信息，使用 DeepSeek API 进行分析，生成结构化的 Markdown 笔记。

## 愿景 vs 实际实现

### 原始愿景（project-vision.md）
1. **每日采集 20 条信息** - ✅ 已实现，可配置
2. **自动抓取：RSS 订阅 + 关键词搜索** - ✅ 已实现 RSS 订阅，关键词过滤
3. **信息源** - 🔄 部分调整（详见下方）
4. **Agent：DeepSeek API** - ✅ 已集成
5. **分析维度** - ✅ 完全实现
6. **存储格式：Markdown** - ✅ 已实现
7. **目标：纯个人学习笔记** - ✅ 已实现

## 实际实现详情

### 1. 项目初始化与版本控制
- ✅ 初始化 Git 仓库
- ✅ 创建 GitHub 远程仓库：https://github.com/switch0303/ai-knowledge-base
- ✅ 配置 SSH 密钥认证推送

### 2. 技术栈与依赖
```
Python 3.8.5
依赖包：
- requests（HTTP 请求）
- feedparser（RSS 解析）
- beautifulsoup4（HTML 解析）
- openai（DeepSeek API 客户端）
- python-dotenv（环境变量管理）
- schedule（定时任务）
- pytz（时区处理）
```

### 3. 目录结构
```
ai-knowledge-base/
├── .env                    # 环境变量（本地，不上传）
├── .env.example           # 环境变量模板
├── .gitignore            # Git 忽略规则
├── requirements.txt      # Python 依赖
├── README.md            # 项目文档
├── src/
│   ├── config.py        # 配置文件
│   └── collect.py       # 核心采集脚本
└── knowledge-base/      # 采集的知识库（按来源自动分类）
    ├── papers/         # 学术论文（arXiv）
    ├── news/          # AI 新闻（Hacker News 等）
    ├── blog/          # 技术博客
    └── tool/          # 工具更新
```

### 4. 信息源调整
**原始计划**：
- ArXiv 官方 RSS（stat.ML, cs.CL, cs.LG）
- Import AI、MIT News AI、OpenAI Blog 等

**实际实现**（因连接问题调整）：
- Hacker News 首页（https://hnrss.org/frontpage）
- arXiv 特定类别：
  - cs.AI（人工智能）
  - cs.LG（机器学习）
  - cs.CL（计算语言学）

**原因**：
- 部分 RSS 源（Import AI, OpenAI Blog）返回 404/403 错误
- ArXiv 官方 RSS 需使用 export.arxiv.org 域名
- 网络 SSL 连接问题，使用 `verify=False` 绕过证书验证

### 5. 核心功能实现

#### 5.1 RSS 采集器 (`src/collect.py`)
```python
class RSSCollector:
    - fetch_feeds(): 抓取并解析 RSS 源
    - _contains_keywords(): 关键词过滤
    - save_to_markdown(): 保存为结构化 Markdown
    - _categorize_entry(): 自动分类（papers/news/blog/tool）
```

#### 5.2 DeepSeek 分析器
```python
class DeepSeekAnalyzer:
    - analyze(): 调用 DeepSeek API 分析内容
    - 输出 JSON 格式分析结果
    - 包含：总结、证据、评论、推荐度、置信度
```

#### 5.3 分析维度（与愿景一致）
1. **一级结论** - 一句话总结
2. **多级论据** - 支撑论点的证据列表
3. **可追溯链接** - 原文链接
4. **评论** - AI 专家视角的见解
5. **推荐度** - 1-5（基于来源可信度）
6. **置信度** - 1-5（基于来源可信度）

### 6. 配置文件 (`src/config.py`)
```python
# 主要配置项
DEEPSEEK_API_KEY = "sk-..."           # DeepSeek API Key
RSS_FEEDS = [...]                     # RSS 源列表
KEYWORDS = [...]                      # 关键词过滤
DAILY_LIMIT = 20                      # 每日采集上限
MAX_ENTRIES_PER_FEED = 30             # 每源处理上限
COLLECTION_TIME = "00:00"             # UTC 采集时间
```

### 7. 环境变量（`.env`）
```env
DEEPSEEK_API_KEY=your_api_key_here
RSS_FEEDS=https://hnrss.org/frontpage,https://export.arxiv.org/rss/cs.AI,...
KEYWORDS=AI,machine learning,deep learning,...
DAILY_LIMIT=20
MAX_ENTRIES_PER_FEED=30
COLLECTION_TIME=00:00
```

## 调试与解决方案

### 1. SSL 连接问题
**问题**：`ConnectionResetError: [Errno 54] Connection reset by peer`
**解决方案**：
```python
# 使用 requests 并禁用 SSL 验证
response = requests.get(url, verify=False)
# 同时抑制警告
warnings.filterwarnings('ignore', message='Unverified HTTPS request')
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
```

### 2. RSS 源问题
**问题**：
- `https://arxiv.org/rss/...` 返回 302 重定向
- `https://importai.io/feed` 返回 404
- `https://openai.com/blog/rss/` 返回 403

**解决方案**：
- 使用 `https://export.arxiv.org/rss/` 替代
- 暂时移除不可用源
- 保留 Hacker News 作为可靠源

### 3. 关键词过滤优化
**问题**：arXiv 论文标题简短，关键词匹配不准确
**解决方案**：
```python
def _contains_keywords(self, text: str) -> bool:
    # 对短文（如标题）使用更宽松的 AI 相关词检测
    ai_indicators = ["learning", "neural", "network", "transformer", "gpt", "llm"]
    if len(text_lower) < 100:
        if any(indicator in text_lower for indicator in ai_indicators):
            return True
    # 原始关键词检查
    return any(keyword in text_lower for keyword in KEYWORDS)
```

### 4. 去重处理
**问题**：同一文章可能出现在多个 RSS 源
**解决方案**：
```python
seen_urls = set()  # 存储已处理的 URL
if entry_url in seen_urls:
    continue  # 跳过重复项
```

## 使用说明

### 1. 首次设置
```bash
# 克隆仓库
git clone https://github.com/switch0303/ai-knowledge-base.git
cd ai-knowledge-base

# 创建虚拟环境
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# 或 venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env
# 编辑 .env 文件，填入 DeepSeek API Key
```

### 2. 运行采集
```bash
# 单次运行（测试）
python src/collect.py

# 后台运行（每日自动采集）
nohup python src/collect.py > collection.log 2>&1 &

# 使用系统定时任务（crontab）
0 0 * * * cd /path/to/ai-knowledge-base && /path/to/venv/bin/python src/collect.py >> collection.log 2>&1
```

### 3. 查看结果
采集内容保存到 `knowledge-base/` 目录：
- `papers/` - arXiv 学术论文
- `news/` - Hacker News AI 相关新闻
- `blog/` - 技术博客（预留）
- `tool/` - AI 工具更新

每个文件为 Markdown 格式，包含完整的分析和评分。

## 配置建议

### 1. 控制 API 成本
```env
# 降低采集量
DAILY_LIMIT=10
MAX_ENTRIES_PER_FEED=15

# 使用更精确的关键词
KEYWORDS=LLM,GPT,transformer,diffusion,AGI
```

### 2. 扩展 RSS 源
在 `.env` 中添加：
```env
RSS_FEEDS=https://hnrss.org/frontpage,https://export.arxiv.org/rss/cs.AI,https://export.arxiv.org/rss/cs.LG,https://export.arxiv.org/rss/cs.CL,https://hnrss.org/newest?points=100
```

### 3. 调整采集时间
```env
# UTC 时间，北京时间 UTC+8
COLLECTION_TIME=16:00  # 北京时间 00:00
```

## 已知限制与未来改进

### 1. 当前限制
- 部分 RSS 源不可用（OpenAI Blog, Anthropic Blog 等）
- SSL 证书验证被禁用（安全风险）
- arXiv RSS 返回条目过多（339+ 条/天）
- DeepSeek API 有调用成本

### 2. 建议改进
1. **添加更多可靠 RSS 源**
   - Google AI Blog（需找到正确 RSS URL）
   - MIT News AI（需确认 RSS 可用性）
   - The Batch（邮件转 RSS）

2. **增强内容获取**
   - 抓取文章全文而不仅是摘要
   - 支持 PDF 论文下载和分析
   - 添加 YouTube 视频转录分析

3. **优化分析质量**
   - 多模型对比分析（DeepSeek vs GPT vs Claude）
   - 添加自定义评分标准
   - 支持用户反馈和修正

4. **改进用户体验**
   - Web 界面查看知识库
   - 搜索和筛选功能
   - 导出为其他格式（JSON, CSV）

5. **解决安全问题**
   - 修复 SSL 证书验证
   - 添加请求重试和错误处理
   - 实现 API 用量监控

## 贡献与维护

### 1. 代码贡献
- 项目地址：https://github.com/switch0303/ai-knowledge-base
- 遵循现有代码风格和结构
- 提交 Pull Request 前确保功能测试通过

### 2. 问题反馈
- 创建 GitHub Issue 报告问题
- 提供详细的错误日志和环境信息
- 建议可行的解决方案

### 3. 维护指南
- 定期更新依赖版本
- 监控 RSS 源可用性
- 跟踪 DeepSeek API 变更

## 结语
本项目成功实现了自动化 AI 知识库的核心功能，能够持续跟踪 AI 领域最新发展。虽然存在一些限制和待改进之处，但已经为个人学习提供了一个有效的工具基础。

**创建时间**：2026-04-16  
**最后更新**：2026-04-16  
**维护者**：AI 助手（基于 DeepSeek）