# Autonomous Continue — 续行编码会话

你正在参与一个长期自主开发任务。这是一个全新的上下文窗口，你需要通过读取持久化文件恢复上下文并继续推进。

## 触发条件
用户要求继续开发、按 feature_list 推进、或启动新的编码会话。

## 固定 10 步工作流

### STEP 1: 定位（MANDATORY）

读取以下文件恢复上下文：
- `feature_list.json` — 查看总进度和下一个待做任务
- `claude-progress.txt` — 了解上一轮做了什么、下一步建议
- `git log --oneline -10` — 了解近期变更
- `CLAUDE.md` — 项目规范和约束

向用户报告：当前进度 X/N (Y%)，上次完成了什么，本次计划做什么。

### STEP 2: 启动环境

如果有 `init.sh` 则运行，否则根据项目情况启动服务。

### STEP 3: 回归验证（CRITICAL）

从已通过（`passes: true`）的 feature 中选 1-2 个核心功能，重新验证：
- 如果是 Web 项目：打开页面、截图、检查核心交互
- 如果是数据管线：运行关键步骤、检查输出
- 如果是 API：调用核心端点、验证响应

**如果发现退化：**
- 立即标记为 `"passes": false`
- 优先修复，不开始新功能

### STEP 4: 选择任务

从 `feature_list.json` 中选择最高优先级的 `"passes": false` 条目。
告诉用户你选择了哪个 feature 以及为什么。

### STEP 5: 实现

编写代码实现选定的 feature。遵循项目现有的代码风格和架构。

### STEP 6: 验证

根据 feature 的 `steps` 逐步验证：
- Web 项目：浏览器截图 + 交互测试
- 数据管线：运行并检查输出
- API：请求并验证响应
- 自动化测试：运行 pytest / jest 等

### STEP 7: 更新 feature_list.json

**只允许将 `"passes": false` 改为 `"passes": true`**

**绝不允许：**
- 删除 feature
- 修改描述或测试步骤
- 重新排序
- 合并条目

### STEP 8: 提交 Git

```bash
git add [specific files]
git commit -m "Implement [feature name] - verified

- [具体变更]
- Updated feature_list.json: test #X passing
- Progress: X/N tests passing (Y%)
"
```

### STEP 9: 更新进度笔记

在 `claude-progress.txt` 追加本次会话记录：
- 完成了什么
- 通过了哪些测试
- 发现并修复了哪些问题
- 下一步建议
- 当前进度

### STEP 10: 清理退出

确保：
- 无未提交变更
- 应用处于可运行状态
- 所有通过的测试仍然通过

向用户报告本次会话成果和整体进度。

## 重要约束

- **先修后建**：修复退化问题优先于新功能
- **单任务聚焦**：一个 feature 做到完美再做下一个
- **必须验证**：不经验证不得标记 passes: true
- **干净退出**：每次结束都留下可恢复的状态
