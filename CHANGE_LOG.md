### 2026-06-26 18:33 UTC+10

- 执行模型：GPT-5.5
- 变更类型：脚本增强
- 涉及文件：
  - scripts/test.bat
  - CHANGE_LOG.md
- 变更内容：
  - 为本地测试脚本增加 lint、pytest、coverage、all 四种工作流入口。
  - lint 对应 ruff check .，pytest 对应 pytest -v，coverage 对应 pytest --cov=app --cov-report=term-missing --cov-report=xml。
  - 默认不传参数时执行 all，顺序运行 lint、pytest、coverage。
- 验证：
  - 已执行 cmd /c "scripts\test.bat lint < nul"，脚本入口可运行。
  - lint 因当前 .venv 未安装 ruff 失败：No module named ruff。
  - IDE 诊断未发现 scripts/test.bat 错误。

### 2026-06-26 18:31 UTC+10

- 执行模型：GPT-5.5
- 变更类型：CI 配置新增
- 涉及文件：
  - .github/workflows/backend-ci.yml
  - CHANGE_LOG.md
- 变更内容：
  - 新增 GitHub Actions 后端 CI，拆分 lint、pytest、coverage 三个 job。
  - 每个 job 均安装 backend 的 dev 依赖，分别执行 ruff、pytest、pytest coverage。
  - coverage job 生成 coverage.xml 并作为 artifact 上传。
- 验证：
  - 已读取检查 .github/workflows/backend-ci.yml 结构。
  - IDE 诊断未发现 workflow 和 CHANGE_LOG.md 错误。

### 2026-06-26 17:41 UTC+10

- 执行模型：GPT-5.5
- 变更类型：功能新增
- 涉及文件：
  - backend/app/core/llm.py
  - CHANGE_LOG.md
- 变更内容：
  - 新增 DeepSeek Chat Completions 接入层，封装 chat() 调用函数并从 .env 配置读取 DEEPSEEK_API_KEY。
  - 支持字符串 prompt 或标准 messages 列表调用，并统一抛出 DeepSeekChatError。
- 验证：
  - 已通过 app.core.llm 导入校验。
  - 已发起 DeepSeek API 冒烟请求，请求到达 API 但返回 401 Unauthorized，当前 .env 中的 Key 无效，需替换为有效 DEEPSEEK_API_KEY 后可完成成功调用。
  - python -m pytest 未执行成功：当前 Python 环境未安装 pytest。
  - IDE 诊断未发现 backend/app/core/llm.py 错误。

### 2026-06-26 17:22 UTC+10

- 执行模型：GPT-5.5
- 变更类型：依赖补全
- 涉及文件：
  - backend/pyproject.toml
  - CHANGE_LOG.md
- 变更内容：
  - 为后端运行时依赖补充 langgraph、langchain、pydantic-settings、chromadb、sqlalchemy。
- 验证：
  - 已通过 Python tomllib 解析 backend/pyproject.toml。

## EXAMPLE

### YYYY-MM-DD HH:MM UTC+10

- 执行模型：xxxx
- 变更类型：xxxx
- 涉及文件：
  - xxxxx
- 变更内容：
  - xxxxx
- 验证：
  - xxxxx
