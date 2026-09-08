# 权威题源与可复现导入

核对日期：2026-09-08。只从论文作者/官方组织的项目页、仓库或数据集卡定位题目；不把媒体截图、搜索摘要或二次转述当题库。先看用户想测什么，再选择题源，不以“权威”替代任务相关性。

|题源|适合测什么|官方入口|数据集卡许可与注意|
|---|---|---|---|
|MMMU|跨学科图文理解、图表与推理|[项目仓库](https://github.com/MMMU-Benchmark/MMMU)、[官方数据集](https://huggingface.co/datasets/MMMU/MMMU)|数据卡标Apache-2.0；原题可能含教材/第三方图，公开素材逐项检查|
|BLINK|空间关系、深度、多视角、视觉对应等感知|[作者仓库](https://github.com/zeyofu/BLINK_Benchmark)、[官方数据集](https://huggingface.co/datasets/BLINK-Benchmark/BLINK)|数据卡标Apache-2.0；保留子任务、图像顺序和choices|
|RealWorldQA|真实场景理解与空间问题|[xAI官方数据集](https://huggingface.co/datasets/xai-org/RealworldQA)|数据卡标CC BY-ND 4.0；保留署名，原图原题不裁切/翻译后当原版再发布|

这三类题各自针对不同能力；简单的自制钟表/错觉仅作回归和演示，不能自动冠上上述benchmark名。

## 可执行的获取方式

导入脚本使用官方Hugging Face数据查看器，默认只取3题，避免首次就下载整库。不请求Agent Plan Key，不调用模型。参数为source/config/split/offset/count：

```sh
uv run --python 3.11 scripts/import-benchmark.py --source=mmmu --config=Math --split=validation --count=3 --out="/自己的题库/mmmu-math-v1"
uv run --python 3.11 scripts/import-benchmark.py --source=blink --config=Spatial_Relation --split=val --count=3 --out="/自己的题库/blink-spatial-v1"
uv run --python 3.11 scripts/import-benchmark.py --source=realworldqa --count=3 --out="/自己的题库/realworldqa-v1"
node scripts/bank.mjs validate --file="/自己的题库/mmmu-math-v1/bank.json"
```

这些目录由使用者选择，须为不存在的新目录。下载失败不生成假的题目。没有网络或数据查看器不可用时，保留URL与错误，可用官方数据集下载快照后转成通用题库；不从别的网站找一张相似图代替。

脚本保留：
- 来源URL、官方原题号、子任务、split、取样offset/count、抓取时间。
- 当时仓库head作为观察信息；数据查看器的题面快照哈希、图片缓存版本分别记录。**不把查看器缓存版本冒充仓库commit**。正式复现实验使用已导出的本地冻结题库。
- 每张原始查看器图片的SHA-256和顺序，不重绘、不裁切。
- bank.json供执行；source-records.json留原题/答案/解析，ATTRIBUTION.md留署名。答案/解析只在评测侧，不能送入被测目录。

## 题面与评分适配边界

- BLINK使用数据行自带的prompt和多图顺序，严格识别单选字母。
- MMMU保留原问题，附原options与统一“只答选项”的格式要求；记录为题面格式适配。开放题标manual，使用官方开放题评分器复核；不是随便做字符串匹配。
- RealWorldQA保留原问题，默认对原答案严格trim匹配；解释型回复可能被严格判错，人工复核要单列规则与结果，不隐瞒这个口径。
- 本导入器用于**小样本、可追溯的同题对照**，protocol记作subset-strict-v1。它不是三套官方评估框架的完整复刻。
- 要报官方benchmark成绩：固定官方release/commit、完整规定split、官方prompt/预处理/解码与答案提取规则，用对应官方评分器；记录缺题、排除理由和所有样本。缺任一条件就改称子集测试。
- 标注未公开的答案不得猜；不要拿测试集样本先给模型调提示词，再把同组样本当独立评估。
- 上传/开源Skill默认只带题库结构、来源说明与下载器，不带用户私有题、Key或第三方研究截图。
