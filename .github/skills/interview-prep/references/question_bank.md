# 模拟面试题库

## FAST

1. 用 60 秒介绍 DeepScholar-Agent。
2. 这个项目和普通论文生成器有什么区别？
3. 你最想展示给 HR 的三个文件是什么？
4. 当前 MVP 的能力边界是什么？

## CODE

1. `researchdraft/core/langgraph_harness.py` 里 StateGraph 的节点顺序是什么？为什么这样设计？
2. `researchdraft/workspace/manager.py` 怎么生成 Evidence Cards 和 Claim Map？
3. `app/main.py` 哪些端点最适合 demo？返回了什么？
4. `researchdraft/evaluation/deep_research_eval.py` 的指标如何计算？
5. `researchdraft/tools/word_tools.py` 负责哪些 DOCX 结构？

## HARD

1. 你说“多智能体”，但真正的 LLM agent 在哪里？如果面试官质疑你只是流程编排，你怎么回答？
2. 你说“可信论文交付”，如果 evidence 本身是错的怎么办？
3. 为什么没有先做 pgvector / PostgreSQL？
4. 这个项目和 Open Deep Research 的差异是什么？
5. 如果 HR 要现场运行 demo，最可能失败在哪里？你怎么兜底？

## HR

1. 这个项目为什么值得放进简历？
2. 你在项目里最有技术判断力的设计是什么？
3. 如果再给两周，你会补什么？
4. 这个项目有没有夸大？哪些地方你会主动说明边界？
