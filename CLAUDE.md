# CLAUDE.md — Project Instructions for Claude Code

## Research & Fact-Checking

When performing fact-checking or research tasks, never include unverified details. Flag any claim you cannot verify with [UNVERIFIED] and ask the user before including it. Do not fabricate specific numbers, names, or details.

## File Operations

Before reading or editing files, confirm you are working in the correct directory/worktree. If the project uses git worktrees, ask which one before proceeding.

## Code Review

When the user asks for a 'full code review and bug fix', present a short numbered plan of what you'll review first and wait for approval before starting. Do not begin large-scale reads without confirming scope.

## Autonomous Development Workflow

本项目支持 Claude Code 长期自主编程工作流。核心文件与 Skills：

### 持久化状态文件
- `feature_list.json` — 单一事实源，记录所有 feature 及其通过状态（仅允许修改 `passes` 字段）
- `claude-progress.txt` — 会话间传递笔记，每次会话结束更新
- Git 历史 — 每完成一个 feature 必须 commit

### 开发 Skills
- `/autonomous-init` — 初始化长期开发项目（拆解规格 → 生成 feature_list.json）
- `/autonomous-continue` — 续行编码会话（10 步工作流：定位 → 回归 → 选任务 → 实现 → 验证 → 提交 → 记录）
- `/warmup` — 快速了解项目现状
- `/factcheck` — 严格事实核查模式

### 核心原则
1. **外部化状态**：一切重要信息持久化到文件系统，不依赖对话记忆
2. **不可变清单**：feature_list.json 的描述和步骤一旦确认不可修改
3. **先修后建**：每次会话先回归验证已通过功能，再开始新工作
4. **单任务聚焦**：一个 feature 做到完美再做下一个
5. **干净退出**：每次会话结束前确保无未提交变更、应用可运行

### 方法论文档
详见 `docs/autonomous-dev-methodology.md`
