# 从0到1初始化（macOS执行版）

## 需要准备什么

- macOS 与能执行本地命令的 Agent。豆包工作只负责调度；不是把测评请求交给豆包自身回答。
- Node.js 22或以上、Claude Code。此包在 macOS、Node 24.17.0、Claude Code 2.1.235 做了本地隔离与离线链路验证；运行时 doctor 会核对必需参数。
- 自己的火山 Agent Plan 套餐、Key、实际可用模型ID。套餐权限不由本 Skill 赠送或保证。
- 只有导入远程 benchmark 时需要 uv + Python 3.11；导入脚本仅用标准库。

**首发执行边界**：本适配器使用 macOS Seatbelt。Claude Code 官方支持 Linux/WSL2 不代表本包已经验证这些平台。本包在其他系统拒绝执行模型；题库格式与导入脚本可以复用。不要删掉这个检查，也不要把独立文件夹称为隔离沙箱。

## 软件没有安装

先检查 `node --version`、`claude --version`；已安装就保留，不更新或清空现有设置。

- 没有 Node：从 [Node 官方下载](https://nodejs.org/en/download) 安装22或以上版本；已有 Homebrew 也可运行 `brew install node`。
- 没有 Claude Code：按 [官方安装文档](https://code.claude.com/docs/en/setup) 安装，例如已有 Homebrew 时运行 `brew install --cask claude-code`。安装后重新打开终端，确认 `claude --version`。
- 需要 benchmark 导入且没有 uv：按 [uv 官方安装文档](https://docs.astral.sh/uv/getting-started/installation/) 安装，或已有 Homebrew 时 `brew install uv`。Python 用 uv 管理，不使用系统Python、不改项目Python版本要求。
- Agent 若无安装权限，给出缺失软件和对应官方入口，停在具体一步；不声称初始化完成。

## 第一次设置

在解压/导入后的 `liucong-model-eval` 目录运行：

```sh
node scripts/setup.mjs init --model=glm-5.3-flash
node scripts/setup.mjs doctor
node scripts/runner.mjs isolation-check
```

init 自动寻找 PATH 中的 Claude。找不到但已安装时使用 `--claude="/完整路径/claude"`。不需要修改 `~/.claude/settings.json` 或 `~/.claude.json`。重复 init 保留已有配置。

候选模型名只是例子。把用户套餐里的ID加入配置：

```sh
node scripts/setup.mjs model --id=kimi-k3
node scripts/setup.mjs model --id=deepseek-v4-pro
node scripts/setup.mjs model --id=doubao-seed-evolving
```

## Key到底放哪里

**默认不落盘。** 用户在终端A执行：

```sh
node scripts/connect.mjs
```

按隐藏输入提示粘贴自己的Key，回车。别把Key拼到命令里、发进聊天、写进Skill或截图。连接启动只说明本地代理启动了，不能据此判断上游Key有效。

连接保持在这个进程的内存中，终端保持运行；Ctrl+C关闭、电脑重启或进程退出后重新输入。适合先在本机准备，再从手机发任务。手机指令里不带Key。

已有秘密管理工具的使用者，可以让它给 connect 进程注入 `LIUCONG_AGENT_KEY` 环境变量；脚本取出后不把该变量传给被测子进程。不要写 `export LIUCONG_AGENT_KEY=真实值` 到终端历史或配置文件。默认隐藏输入更简单。

普通文件位置（均在用户自己的机器）：

|内容|默认路径|是否含真实Key|
|---|---|---|
|模型、Claude路径、偏好|`~/.local/share/liucong-model-eval/config.json`|否|
|本地代理地址与短期管理令牌|同目录 `broker-client.json`，权限0600|否，但也不公开|
|单题运行记录|同目录 `runs/<runId>/`|否|
|导出包|同目录 `exports/<时间>/`|否|

自定义根目录通过 `LIUCONG_EVAL_HOME` 指向本机非同步目录；初始化、连接、跑测必须使用同一个值。普通配置可以备份；运行目录、短期令牌不放iCloud/共享盘，不随Skill上传。答案和私有图片可能在结果中，公开前另行筛选。

## 验证之后才正式跑

保持终端A，另开终端B进入同一个Skill目录：

```sh
node scripts/runner.mjs run --cases=connection --model=glm-5.3-flash
node scripts/runner.mjs run --cases=visioncheck --model=glm-5.3-flash
node scripts/runner.mjs run --cases=toolscheck --model=glm-5.3-flash
node scripts/runner.mjs run --dry-run --cases=clock,illusion,logic
node scripts/runner.mjs run --cases=clock,illusion,logic
node scripts/runner.mjs export
```

只测文字，不需要visioncheck；不做代码题，不需要toolscheck。每个模型、每次重启连接分别验证。visioncheck是简单钟表探针，不是视觉能力排名；答错不能证明接口不支持图片。若已有可靠接口文档确认支持，可明确设置 `setup.mjs model --id=模型ID --vision=yes`，报告记录依据，不自动猜。

准备失败时看对应 runId 的 events/result，不反复扣额度。代理总请求上限默认200次、每题最多60次，均是请求次数而非价格承诺。大规模测试前先核对模型×题数×预算，不自动拉满全库。

## 常见故障

|现象|下一步|
|---|---|
|未初始化|运行init；已有配置不覆盖|
|找不到Claude/不支持必需参数|doctor核对路径/版本，依官方安装方式处理|
|401|当前Key无效或过期；停止重试，本人重启connect输入自己的Key|
|403/404或model错误|核对Agent Plan专用Key、模型ID与套餐权限；不悄悄换模型|
|429|额度/请求次数上限；记录并等待，不无限重试|
|本地连接拒绝|终端A可能退出；重新connect并做准备检查|
|connection.lock存在但进程已异常退出|确认旧连接确实退出后，仅移除自己的connection.lock再启动；不按不明PID杀进程|
|isolation-check失败|保留检查文件；不能关隔离；缺依赖/系统适配问题先处理|
|超时|保留文件和timeout；需要加预算时显式 --seconds=1200 并单列新轮次|
|Skill移动位置后题库不存在|preferences --bank指向新位置的assets/demo/bank.json|
|后台电脑睡眠/断网|恢复后核对进程和原始日志，不把断线写成测试完成|

Agent Plan 专属上游为 `https://ark.cn-beijing.volces.com/api/plan`；配置入口见[火山配置文档](https://docs.volcengine.com/docs/82379/2373740)。实际模型ID与套餐权限以使用者自己的控制台为准。
