# Claude Code 长期自主编程方法论

> 基于 Anthropic 官方 `claude-quickstarts/autonomous-coding` 仓库提炼，适配 Claude Code CLI 交互式场景。

---

## 一、核心思想

Claude 的上下文窗口有限，但一个项目的开发可能需要数十小时。**长期自主编程**解决的核心问题是：

> 如何让 Claude 在多轮会话中持续推进同一个项目，且每次新会话都能快速恢复上下文、不丢失进度、不引入回退？

答案是 **"外部化状态 + 刚性契约 + 分层安全"** 三位一体。

---

## 二、架构模式：双角色 Agent

### 2.1 初始化 Agent（Session 1）

| 职责 | 输出物 |
|------|--------|
| 阅读项目规格文档 | — |
| 将规格拆解为可验证的 feature 清单 | `feature_list.json` |
| 搭建项目骨架、初始化 git | 目录结构 + 首次 commit |
| 创建环境启动脚本 | `init.sh` |
| 记录本次进度 | `claude-progress.txt` |

**关键设计**：feature_list.json 的每一项都包含：
```json
{
  "category": "functional | style",
  "description": "功能描述 + 测试目标",
  "steps": ["Step 1: ...", "Step 2: ...", "Step 3: ..."],
  "passes": false
}
```

### 2.2 编码 Agent（Session 2+）

每次启动都是 **全新上下文窗口**，通过读取持久化文件恢复状态。

固定 10 步工作流：

| 步骤 | 操作 | 目的 |
|------|------|------|
| 1. 定位 | `pwd`, `ls`, 读 `app_spec.txt`, `feature_list.json`, `claude-progress.txt`, `git log` | 恢复上下文 |
| 2. 启动环境 | 执行 `init.sh` 或手动启动服务 | 确保可运行 |
| 3. 回归验证 | 选 1-2 个已通过的核心 feature 重新测试 | 发现上一轮引入的退化 |
| 4. 选择任务 | 取 `passes: false` 的最高优先级 feature | 单一聚焦 |
| 5. 实现 | 编码（前端 + 后端） | — |
| 6. UI 验证 | 浏览器自动化截图 + 交互 | 真实用户视角 |
| 7. 更新清单 | **仅修改 `passes` 字段** | 保证清单不可变性 |
| 8. 提交 | `git commit` 附详细信息 | 可追溯 |
| 9. 记录进度 | 更新 `claude-progress.txt` | 下一轮恢复上下文 |
| 10. 清理退出 | 确保无未提交变更、应用可运行 | 干净交接 |

---

## 三、五大设计原则

### 原则 1：外部化一切状态

Claude 的上下文窗口是**一次性的**。一切重要信息必须持久化到文件系统：

| 状态 | 存储位置 | 格式 |
|------|----------|------|
| 项目需求 | `app_spec.txt` / `CLAUDE.md` | 自然语言 |
| 任务清单与进度 | `feature_list.json` | 结构化 JSON |
| 会话间传递笔记 | `claude-progress.txt` | 自由文本 |
| 代码历史 | Git 仓库 | commits + log |
| 环境配置 | `init.sh` / `.env` | 脚本 |

**核心理念**：任何一个全新的 Claude 会话，只要读取这些文件，就能在 5 分钟内恢复到完整上下文。

### 原则 2：不可变任务清单

`feature_list.json` 的规则极其严格：

- **允许**：将 `"passes": false` 改为 `"passes": true`
- **禁止**：删除 feature、修改描述、修改测试步骤、重新排序、合并条目

这保证了：
1. 不会因为"太难"而悄悄删除 feature
2. 进度百分比始终可信（`passing / total`）
3. 跨会话对比时数据一致

### 原则 3：先修后建

每个编码会话必须 **先回归验证**，再开始新工作：
- 选 1-2 个已通过的核心测试重新执行
- 如果发现退化，**立即标记为 `passes: false` 并优先修复**
- 绝不在已知问题存在时叠加新功能

### 原则 4：单任务聚焦

一个会话只做一件事，做到完美：
- 选择一个 feature
- 实现 → 测试 → 验证 → 标记通过
- 如果做完了有余力，再选下一个
- 宁可一个会话只完成一个 feature，也不要半成品

### 原则 5：纵深防御安全模型

三层安全：
1. **OS 沙箱**：Bash 命令运行在隔离环境
2. **文件系统限制**：操作范围限定在项目目录
3. **命令白名单**：通过 `PreToolUse` hook 验证每个 Bash 命令

```python
ALLOWED_COMMANDS = {
    "ls", "cat", "head", "tail", "wc", "grep",  # 只读检查
    "npm", "node",                                 # 运行时
    "git",                                         # 版本控制
    "ps", "lsof", "sleep", "pkill",               # 进程管理（受限）
}
```

敏感命令（如 `pkill`、`chmod`）需要额外验证（只允许 kill 开发进程、只允许 `+x` 权限）。

---

## 四、持久化文件契约

### 4.1 `feature_list.json`

**角色**：单一事实源（Single Source of Truth）

```json
[
  {
    "category": "functional",
    "description": "用户可以通过搜索框定位国家并在地图上高亮",
    "steps": [
      "Step 1: 打开仪表盘",
      "Step 2: 在搜索框输入 'CHN'",
      "Step 3: 点击定位按钮",
      "Step 4: 验证地图上中国被高亮",
      "Step 5: 验证详情弹窗自动打开"
    ],
    "passes": false
  }
]
```

设计要点：
- 条目数量应覆盖所有规格（原版建议 200 条）
- 混合细粒度测试（2-5 步）和端到端测试（10+ 步）
- 按优先级排序：基础功能在前，锦上添花在后
- category 区分 `functional`（功能）和 `style`（视觉/UX）

### 4.2 `claude-progress.txt`

**角色**：会话间记忆桥梁

每次会话结束时更新：
```
## Session 5 - 2026-03-23
- 完成：Dim1 地图渲染 + 年份滑块联动
- 通过测试：#12, #13, #14
- 发现问题：Dim2 切换后地图偶现灰色覆盖层（已修复，见 commit abc123）
- 下一步：实现 Dim2 风险因素下拉菜单
- 进度：14/50 tests passing (28%)
```

### 4.3 Git 提交规范

```bash
git commit -m "Implement [feature name] - verified end-to-end

- Added [具体变更]
- Tested with browser automation
- Updated feature_list.json: marked test #X as passing
- Progress: 15/50 tests passing (30%)
"
```

---

## 五、会话管理机制

### 5.1 自动续行循环

```
┌─────────────────────────────────────────┐
│          主控制循环 (Python)              │
│                                         │
│  while True:                            │
│    iteration++                          │
│    client = create_client()  ← 全新上下文 │
│    prompt = select_prompt()             │
│    status = run_session(client, prompt)  │
│    print_progress()                     │
│    sleep(3)  ← 短暂间隔后自动继续          │
│                                         │
│  Ctrl+C → 暂停                           │
│  重新运行 → 自动恢复                      │
└─────────────────────────────────────────┘
```

关键点：
- 每轮创建 **全新 client**（全新上下文窗口）
- Session 1 使用 `initializer_prompt`，后续使用 `coding_prompt`
- 通过文件系统（而非内存）传递状态
- 支持 `--max-iterations` 限制轮数

### 5.2 提示词设计

| 提示词 | 用途 | 核心指令 |
|--------|------|----------|
| `initializer_prompt.md` | 首次运行 | "读规格 → 生成 200 条 feature → 搭骨架 → init git" |
| `coding_prompt.md` | 后续运行 | "定位 → 回归 → 选任务 → 实现 → 验证 → 提交 → 记录" |

提示词设计原则：
1. **步骤化**：编号步骤，不留模糊空间
2. **禁止性指令**：明确列出"NEVER"清单（不删 feature、不跳过验证等）
3. **质量标准**：给出具体的验收标准（零 console 错误、截图验证等）
4. **心态设定**："You have unlimited time" — 防止 Agent 因为急于完成而走捷径

---

## 六、适配 Claude Code CLI 的实践指南

在直接使用 Claude Code CLI（而非 SDK 编程）时，上述方法论可以简化为以下工作流：

### 6.1 项目启动

1. 在 `CLAUDE.md` 中写清项目规格和开发规范
2. 让 Claude 生成 `feature_list.json`
3. 确认清单完整后，开始迭代

### 6.2 每次会话

```
你 → /warmup                          # 快速了解项目现状
你 → "继续开发，按 feature_list.json"   # Claude 自动走 10 步流程
     ... Claude 实现 + 验证 ...
你 → /commit                          # 提交进度
```

### 6.3 借助 Skills 自动化

| Skill | 用途 |
|-------|------|
| `/warmup` | 读 README、git log、TODO — 5 行摘要 |
| `/factcheck` | 严格事实核查模式 |
| `/autonomous-init` | 初始化长期开发项目（生成 feature_list.json 等） |
| `/autonomous-continue` | 续行编码（10 步工作流） |

### 6.4 上下文压缩策略

当会话变长时：
- 依赖 `feature_list.json` 和 `claude-progress.txt` 而非对话记忆
- 大文件用 `Read` 工具按需读取，不一次性全部加载
- 把已完成的工作提交 git 后，可以安全地开新会话

---

## 七、与现有 HdI 项目的结合

HdI 项目已有完整骨架，可以这样适配：

| 现有资产 | 对应角色 |
|----------|----------|
| `CLAUDE.md` | 项目规格 + 开发规范 |
| `dashread.md` | Dashboard 功能规格（中文） |
| `progress.md` | 等价于 `claude-progress.txt` |
| `notebooks/` | 分析管线（不适用自动化，需人工 review） |
| `dashboard/` | 前端部分，适合用 feature_list.json 追踪 |
| `api_output/` | 数据管线输出，可作为验收数据 |

建议步骤：
1. 为 `dashboard/` 生成 `dashboard_features.json`（功能 + 样式测试清单）
2. 为 `src/hdi/` 管线生成 `pipeline_features.json`（数据处理 + 模型测试清单）
3. 每次会话按上述 10 步流程推进

---

## 八、反模式与风险

| 反模式 | 后果 | 正确做法 |
|--------|------|----------|
| 不做回归验证就写新功能 | 累积 bug，后期难以定位 | 每次会话先验证 1-2 个核心 feature |
| 修改 feature_list 的描述或步骤 | 进度数据失去可比性 | 只改 `passes` 字段 |
| 一个会话贪多做很多 feature | 质量下降，半成品多 | 聚焦 1-3 个，做一个完美一个 |
| 不写 progress notes | 下一轮会话需要花很长时间恢复上下文 | 每次结束前更新 |
| 不提交就结束会话 | 工作丢失 | 离开前必须 `git commit` |
| 跳过 UI 验证只测后端 | 前端渲染问题被忽略 | 必须截图/浏览器自动化验证 |

---

## 九、总结

```
长期自主编程 = 外部化状态 + 不可变清单 + 回归优先 + 单任务聚焦 + 纵深安全
```

每个新会话都是一个 **无状态的 Agent**，通过读取文件系统中的持久化状态来恢复上下文。项目的"记忆"不在 Claude 的上下文窗口里，而在 `feature_list.json`、`claude-progress.txt` 和 Git 历史中。

这套方法论的本质是：**把 LLM 的短期记忆劣势，转化为工程上的显式状态管理优势。**
