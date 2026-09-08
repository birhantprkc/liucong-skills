# 兼容旧入口的说明

v2不再依赖作者电脑的绝对路径、旧临时代理或历史results目录。

- 第一次运行看 [初始化](initialization.md)。
- 随包入口为 `scripts/runner.mjs`，从本Skill目录执行。
- 执行配置使用每个使用者自己的 `LIUCONG_EVAL_HOME`，默认 `~/.local/share/liucong-model-eval`。
- 历史演示工程保留原样，不用新版初始化去覆盖或重建旧轮次；需要复现旧题时固定对应原始Prompt、素材和预算。
- 本包保留board_redesign/orbit_audio两条演示题。board_redesign明确是固定种子的第二次改版；完整题面以 `assets/demo/bank.json` 为准，旧visual-prompts为便于阅读的参考副本。
