## 现阶段核心目标：打通「单回合最小闭环」

> 目标：让玩家输入一句话 → 经过一个最简化的 Agent 流程 → 返回一段叙事文本，并能把状态存进 SQLite。这是验证整个架构是否成立的最小可行产品。

### 按依赖顺序，分成 4 个子阶段：

#### 阶段 A — 基础设施补齐（地基）

1. 补全依赖 pyproject.toml：添加 langgraph、langchain、pydantic-settings、chromadb、sqlalchemy（或直接用 sqlite3）
2. DeepSeek 接入层 app/core/llm.py：封装一个 chat() 调用函数（用 .env 里的 Key），先做到能成功调通一次 API
3. 数据库初始化 app/db/：定义 GameState 表（存档 JSON），写一个 init_db()

#### 阶段 B — 数据模型先行（结构化状态）

1. 定义状态 Schema app/models/state.py：用 Pydantic 定义世界状态（如 rank、hp、hunger、ammo、npc_affinity、location、turn）
2. 存读档逻辑 app/services/save.py：save_state() / load_state()，把状态序列化进 SQLite

#### 阶段 C — 单 Agent 跑通（先不做多 Agent）

1. Director Agent 单体版 app/agents/director.py：接收「玩家输入 + 当前状态」→ 调 LLM → 返回叙事。先不接 Logic Prosecutor 和 State Manager
2. 游戏接口 app/api/routes/game.py：新增 POST /game/turn，串起「读档 → Director → 存档 → 返回叙事」

#### 阶段 D — 引入 LangGraph 编排骨架

1. LangGraph 图 app/graph/：把流程从「直接调用」改写成 LangGraph 节点（哪怕只有 1 个节点），为后续插入 Prosecutor / State Manager 预留扩展点
2. 补测试：为 /game/turn 写一个 mock LLM 的集成测试
