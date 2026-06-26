### 2026-06-26 19:42 UTC+10

- 执行模型：GPT-5.5
- 变更类型：配置分层
- 涉及文件：
  - backend/app/core/config.py
  - backend/app/core/llm.py
  - backend/.env.example
  - backend/tests/test_llm.py
  - CHANGE_LOG.md
- 变更内容：
  - 将 DeepSeek base URL 和默认模型纳入 Settings/env 配置，默认值分别为 https://api.deepseek.com 与 deepseek-v4-flash。
  - chat() 调用层改为基于 DEEPSEEK_BASE_URL 拼接固定 /chat/completions endpoint，并继续支持调用方显式覆盖 model。
  - 更新 LLM 单元测试，覆盖配置默认模型、配置 base URL 以及尾随斜杠规整行为。
- 验证：
  - 已执行 ..\.venv\Scripts\python.exe -m pytest tests\test_llm.py --cov=app.core.llm --cov-report=term-missing，21 passed，app/core/llm.py 覆盖率 100%。
  - 已执行 ..\.venv\Scripts\python.exe -m pytest --cov=app --cov-report=term-missing，22 passed，总覆盖率 99%，app/core/llm.py 覆盖率 100%；存在 FastAPI/TestClient 依赖层 StarletteDeprecationWarning。
  - 已执行 ..\.venv\Scripts\python.exe -m ruff check app\core\llm.py app\core\config.py tests\test_llm.py，检查通过。
  - IDE 诊断未发现 backend/app/core/llm.py、backend/app/core/config.py、backend/tests/test_llm.py 错误。

### 2026-06-26 19:17 UTC+10

- 执行模型：GPT-5.5
- 变更类型：测试增强
- 涉及文件：
  - backend/app/core/llm.py
  - backend/tests/test_llm.py
  - CHANGE_LOG.md
- 变更内容：
  - 评估并采纳 DeepSeek chat() 黑盒边界覆盖建议。
  - 补充默认模型、默认温度、默认 timeout、Content-Type 请求头、API Key 修剪、中文 prompt/响应、多轮标准 messages 的测试。
  - 参数化覆盖更多畸形 JSON 响应结构，以及 null、数组、字符串等合法 JSON 但非预期对象的响应。
  - 为 TimeoutError 补充统一 DeepSeekChatError 包装和对应测试。
- 验证：
  - 已执行 ..\.venv\Scripts\python.exe -m pytest tests\test_llm.py --cov=app.core.llm --cov-report=term-missing，20 passed，app/core/llm.py 覆盖率 100%。
  - 已执行 ..\.venv\Scripts\python.exe -m pytest --cov=app --cov-report=term-missing，21 passed，总覆盖率 99%，app/core/llm.py 覆盖率 100%。
  - 已执行 ..\.venv\Scripts\python.exe -m ruff check app\core\llm.py tests\test_llm.py，检查通过。

### 2026-06-26 18:54 UTC+10

- 执行模型：GPT-5.5
- 变更类型：缺陷修复
- 涉及文件：
  - backend/app/core/llm.py
  - backend/tests/test_llm.py
  - CHANGE_LOG.md
- 变更内容：
  - 为 DeepSeek chat() 响应解析补充 JSONDecodeError 捕获，非 JSON 的 200 响应会统一抛出 DeepSeekChatError。
  - 新增非 JSON 响应体单元测试，防止原始 JSONDecodeError 泄漏给调用方。
- 验证：
  - 已执行 ..\.venv\Scripts\python.exe -m pytest tests\test_llm.py --cov=app.core.llm --cov-report=term-missing，9 passed，app/core/llm.py 覆盖率 100%。
  - 已执行 ..\.venv\Scripts\python.exe -m pytest --cov=app --cov-report=term-missing，10 passed，总覆盖率 99%，app/core/llm.py 覆盖率 100%。
  - 已执行 ..\.venv\Scripts\python.exe -m ruff check app\core\llm.py tests\test_llm.py，检查通过。

### 2026-06-26 18:48 UTC+10

- 执行模型：GPT-5.5
- 变更类型：测试新增
- 涉及文件：
  - backend/tests/test_llm.py
  - CHANGE_LOG.md
- 变更内容：
  - 为 backend/app/core/llm.py 新增 DeepSeek chat() 单元测试。
  - 覆盖成功调用、messages 调用、缺少 API Key、空消息、HTTPError、URLError、异常响应结构和非字符串 content。
- 验证：
  - 已执行 ..\.venv\Scripts\python.exe -m pytest tests\test_llm.py --cov=app.core.llm --cov-report=term-missing，8 passed，app/core/llm.py 覆盖率 100%。
  - 已执行 ..\.venv\Scripts\python.exe -m pytest --cov=app --cov-report=term-missing，9 passed，总覆盖率 99%，app/core/llm.py 覆盖率 100%。
  - 已执行 ..\.venv\Scripts\python.exe -m ruff check tests\test_llm.py，检查通过。

### 2026-06-26 18:39 UTC+10

- 执行模型：GPT-5.5
- 变更类型：脚本修复
- 涉及文件：
  - scripts/test.bat
  - CHANGE_LOG.md
- 变更内容：
  - 修复本地 coverage 工作流因 .venv 未安装 pytest-cov 导致 --cov 参数无法识别的问题。
  - scripts/test.bat 在执行 lint、pytest、coverage 前会先安装 backend 的 .[dev] 依赖。
- 验证：
  - 已执行 cmd /c "scripts\test.bat coverage < nul"。
  - pytest-cov 插件加载成功，coverage 工作流通过：1 passed，生成 coverage.xml。

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
