---
name: liucong-model-eval
description: 初始化并执行可追溯的模型对照测评，支持权威视觉 benchmark 子集、用户自有题库和前后端真实任务；固定题面、隔离工具、保留首轮产物并验收。用于从零搭建测评环境、按个人题库跑测、同题比较模型或整理测评报告。
metadata:
  version: "2.0.0"
---

# 刘聪模型测评

用固定题目测试真实接入的模型，区分模型回答、生成状态和实际验收。调度 Agent 不替被测模型答题，也不把自己修好的页面记成模型首轮成绩。本包按刘聪式实测方法组织，内置题是原创演示题，不是刘聪完整私有题库或官方榜单。

## 先识别当前情况

- **第一次使用 / 缺软件 / 缺 Key**：读 [初始化](references/initialization.md)，从环境检查开始。不要假设别人的电脑已经配置好；不要沿用演示机路径。随包执行器支持 macOS，其他系统未提供已验证适配器，不降级为无隔离执行。
- **用户已经有题库或偏好**：先用用户指定的题面、图片和评分方式，读 [自有题库与偏好](references/question-bank.md)。不擅自改题，不用演示题顶替。
- **用户要找权威题 / benchmark**：读 [题源目录](references/benchmark-sources.md)，从作者/机构官方渠道获取原题，冻结版本、题号、图片和答案。少量抽测称“某 benchmark 子集”，不得标成完整 benchmark 分数。
- **只说“简单测一下”**：沿用已保存偏好；没有偏好时用内置简单演示题，默认最多3题、先1个模型。手机指令不自动扩大成长任务。

所有下列命令从本 Skill 文件夹执行；路径有空格时用双引号引用，或使用程序参数数组。脚本路径相对 Skill，自定义题库路径相对该题库。

## 初始化与凭据

1. 运行 `node scripts/setup.mjs doctor`。未初始化则按初始化文档补软件、运行 init；已有配置保留，不清空用户的 Claude Code 全局配置。
2. 用户在终端执行 `node scripts/connect.mjs`，由本人隐藏输入自己的 Agent Plan Key。Key 只在连接进程内存里；配置、Skill、题库、报告和截图均不得含真实 Key。不能安全输入时给用户这一步，不让其把 Key 发到聊天。
3. 运行 `node scripts/runner.mjs isolation-check`。越界读写、外网必须拒绝，目录内写、Node、Claude CLI 启动必须通过；失败则停在具体错误，不换成无隔离方式。
4. 对每个模型先跑 connection；要用图片再跑 visioncheck，要做代码题再跑 toolscheck。准备检查不计正式测评。工具检查核对真实 tool_result，模型自述不算证据。视觉探针失败不直接断言模型不支持视觉，先检查接口错误与原始回答。
5. 连接关闭或重启后重新输入 Key，并重新做该连接的准备检查。更换模型名单后重启连接。接口拒绝、模型名错误或额度不足不自动切模型。

## 冻结题目，再执行

- 先用 bank validate 检查题库；用 run --dry-run 列出本轮题号、模型、预算，不调用模型。
- 模型对照使用同题面、同图片字节/顺序、同初始工程、同工具、同预算。固定 seed 和题号；保留全部选中题，不看结果后换题。不同题库、工具条件或预算分组报告。
- 支持一次 run --models=模型A,模型B 顺序执行，避免抢同一本地服务端口。默认不自动重跑已有同条件任务；补跑需明确理由并加 --repeat --reason="原因"，保留失败记录。
- 简单问答禁用全部工具；代码题限 Read、Write、Edit、Bash，默认无外网。每题新工作目录与 Claude 配置，禁用全局 Skill/MCP/记忆/历史发现。不能使用跳过权限或关闭隔离参数。
- 题库答案、解析、评分脚本不复制进被测模型目录。图片作为真实 image 内容传入，按 Image 1…顺序记录；不能用调度者的图像描述替代视觉输入。
- 隔离连接给每题单独的短期令牌，绑定单个模型；被测进程不接触真实上游 Key。系统运行库仍可读，本适配器是进程沙箱，不宣称是虚拟机。
- 生成的命令和网页视为待验收产物；后端在同样的受限环境跑测试，不能直接在宿主机执行不受限代码。

常用流程：

```sh
node scripts/runner.mjs run --cases=connection,visioncheck,toolscheck --model=glm-5.3-flash
node scripts/runner.mjs run --dry-run --tier=simple --count=3
node scripts/runner.mjs run --tier=simple --count=3
node scripts/runner.mjs run --cases=orbit_audio --model=glm-5.3-flash --seconds=1200
node scripts/runner.mjs status
node scripts/runner.mjs export
```

自有/权威题库加 `--bank="/题库目录/bank.json"`；如果配置了非内置题库，准备检查显式传本 Skill 的 `assets/demo/bank.json`。参数细节和个人偏好见题库文档。

## 验收与交付

读 [方法与验收](references/methodology.md)。每条结论能追溯到 runId、题面/图片哈希、原始回答和实际操作。

- complete 只表示会话结束，不等于答案正确或页面通过。文件缺失、超时但有产物、接口错误、人工复核、未测分别记录。
- 选择题仅自动认单个选项；解释很长或答案歧义需复核，不能从任意字母猜答案。开放题按官方评分器或预先约定 rubric；本包的小样本严格匹配不是官方榜单评分器。
- 前端实际打开并操作关键功能，视觉和功能分开评。手机响应式记录真实 innerWidth、scrollWidth。截图只代表当时画面；不能把按钮状态当听感、把隐藏DOM当可见弹层。
- 每个重点案例保留1张首屏和1张关键交互/问题截图即可；过程图备档，不要求全部入稿。没浏览器能力就写未做GUI验收。
- 首轮不覆盖；用户要求修复时才另存修复版，记操作者和哈希。用户说停止/不修就收敛。
- export 输出 CSV、JSON、原始 Prompt、图片、事件和产物；再组织“结论 → 同题条件 → 案例证据 → 限制/失败”。自有私密题库默认只在本地使用，不随公开 Skill 打包。
- 飞书/云电脑是可选交付：有权限才写真实文档，没权限先交本地文件；没有真实验证不宣称已自动同步或手机远控成功。文章语气可另用写作 Skill，本 Skill 执行不依赖它。
