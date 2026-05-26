# ResearchDraft Agent Harness 质量报告

## 项目摘要
- 项目名称：ResearchDraft Agent Harness
- 版本：MVP v5 Web Search Provider 与候选文献元数据增强
- 架构意图：Manager 负责任务调度，Specialist Agent 分别负责访谈、规划、写作、搜索、来源审查、人工确认、引用检查、Word 排版和验证。
- 约束：不做 RAG，不做向量库，不新增 LaTeX、GUI 或数据库。
- 文献原则：搜索结果仅作为 candidate_literature，未经人工确认不得进入正式参考文献。
- 内容原则：禁止编造论文、作者、DOI、期刊、实验结果、指标或数据集规模。
- 论文标题：DeepScholar Agent：多智能体深度研究与可信论文交付 Harness
- Markdown 草稿：examples\demo_run\draft.md
- Word 文档：examples\demo_run\paper.docx

## Draft Context 摘要
- 研究背景：HR 需要快速理解一个可运行的研究 Agent MVP，系统需要留下证据、Trace 和 Word 交付物。
- 研究问题：如何在论文草稿生成过程中降低无依据结论，并保留可审计交付链路？
- 方法模块：任务规划；候选文献检索；来源审查；引用检查；Word 交付
- 数据集或材料：公开网页与用户上传材料的结构化摘要
- 实验指标：引用覆盖率；无依据结论率；文档交付成功率
- 创新点：Evidence Cards；Trace Evaluation；Human Review Gate
- 参考文献：[待补充：参考文献]
- Draft Context 缺失字段：references

## 结构检查
- 标题: 通过；检测到一级标题
- 摘要: 通过；检测到章节标题
- 关键词: 通过；检测到章节标题
- 引言: 通过；检测到章节标题
- 相关工作: 通过；检测到章节标题
- 方法: 通过；检测到章节标题
- 实验与结果分析: 通过；检测到章节标题
- 结论: 通过；检测到章节标题
- 参考文献: 通过；检测到章节标题

## 内容缺失
- 待补充标记数量：3
- 待确认标记数量：0
- 原则：缺失内容必须保留 [待补充：...] 或 [待确认：...]，不得替换为猜测内容。

## 待补充项
- [待补充：参考文献]
- [待补充：引用来源]
- [待补充：相关工作引用]

## 待确认项
- [待确认：参考文献真实性、完整性与引用位置]
- [待确认：参考文献真实性与引用位置]
- [待确认：近三年文献覆盖是否足够]

## 引用与文献质量检查
- 参考文献总数：0
- 正文引用数量：0
- 未在正文引用的参考文献：无
- 正文引用但参考文献缺失的问题：无
- 重复参考文献：无
- 文献格式风险：无
- 人工确认项：[待补充：引用来源]
- 近三年文献数量：0
- 近三年文献占比：0%
- 是否缺少相关工作支撑：是
- 文献需求分析：[待补充：参考文献]；相关工作支撑不足，需要补充同主题、同方法或同应用场景文献。
- 建议补充的文献方向：围绕“任务规划”补充近三年方法对比或系统实现类文献；围绕“候选文献检索”补充近三年方法对比或系统实现类文献；围绕“来源审查”补充近三年方法对比或系统实现类文献；围绕“Evidence Cards”补充可验证性、可追踪性或质量评估类文献；围绕“Trace Evaluation”补充可验证性、可追踪性或质量评估类文献
- 人工确认项：[待确认：参考文献真实性、完整性与引用位置]；[待确认：近三年文献覆盖是否足够]

## 联网文献搜索与人工确认
- 搜索 provider：fallback_mock
- 搜索 query 列表：DeepScholar Agent：多智能体深度研究与可信论文交付 Harness literature review paper；如何在论文草稿生成过程中降低无依据结论，并保留可审计交付链路？ literature review paper；公开网页与用户上传材料的结构化摘要 literature review paper；任务规划 literature review paper；候选文献检索 literature review paper
- 是否使用缓存：True
- 候选去重前数量：5
- 候选去重后数量：5
- 候选文献数量：5
- 高置信候选数量：0
- 低置信候选数量：3
- 已确认文献数量：0
- 未确认候选数量：5
- 来源类型分布：paper:5
- 高风险候选：C001；C002；C003；C004；C005
- 人工确认结果：skip/无确认
- 搜索失败与 fallback 情况：fallback_used=True；failure_reason=
- 未进入正式参考文献的候选说明：pending_review 候选仅保留在 candidate_literature.json，不写入 draft.md 参考文献章节。

## Word 输出检查
- draft_context.json: 通过；examples\demo_run\draft_context.json，大小 891 字节
- draft.md: 通过；examples\demo_run\draft.md，大小 1974 字节
- paper.docx: 通过；examples\demo_run\paper.docx，大小 38563 字节
- candidate_literature.json: 通过；examples\demo_run\candidate_literature.json，大小 5236 字节
- source_review_report.json: 通过；examples\demo_run\source_review_report.json，大小 2762 字节
- search_cache.json: 通过；examples\demo_run\search_cache.json，大小 4023 字节
- trace.json: 通过；examples\demo_run\trace.json，大小 4250 字节
- 标题居中: 通过；首页标题居中
- 标题加粗: 通过；首页标题加粗
- 标题层级: 通过；Heading 段落数 9
- 正文统一字体字号: 通过；存在正文段落，使用 Normal/正文样式
- 正文首行缩进: 通过；检测到 24pt 首行缩进
- 页码: 通过；检测到页脚段落
- 参考文献单独成节: 通过；检测到参考文献标题和独立 section
- 参考文献编号清晰: 通过；无正式参考文献条目，保留待补充占位
- 提示：Word 输出保留待补充/待确认标记，便于人工继续编辑。

## Agent 执行摘要
- InterviewAgent: 1 步
- PlanningAgent: 1 步
- WritingAgent: 2 步
- LiteratureSearchAgent: 1 步
- SourceReviewAgent: 1 步
- HumanReviewGate: 1 步
- LiteratureAgent: 1 步
- CitationAgent: 1 步
- WordFormatAgent: 1 步
- VerifierAgent: 1 步
- Trace Agent 覆盖: 通过；检测到 Agent: CitationAgent, HumanReviewGate, InterviewAgent, LiteratureAgent, LiteratureSearchAgent, PlanningAgent, SourceReviewAgent, VerifierAgent, WordFormatAgent, WritingAgent
- Trace 字段完整性: 通过；每步均包含 task_id/agent/stage/input_keys/output_keys/tool_call/status/failure_reason/timestamp

## Trace 与质量评测
- 引用覆盖率：100%
- 无依据结论率：50%
- 补检通过率：0%
- 文档交付成功率：100%
- Bad Case Replay：可通过 `/demo/replay` 或 `researchdraft.replay.bad_case_replay` 复现无依据结论场景。

## Agent 执行明细
- interview | INTERVIEWING | InterviewAgent | tool=fixed_questionnaire | status=ok | time=2026-05-26T02:26:58.588430+00:00
- planning | PLANNING | PlanningAgent | tool=paper_outline.yaml | status=ok | time=2026-05-26T02:26:58.595051+00:00
- drafting | DRAFTING | WritingAgent | tool=llm_optional_or_template | status=ok | time=2026-05-26T02:26:58.605616+00:00
- web-searching | WEB_SEARCHING | LiteratureSearchAgent | tool=web_search_provider_or_fallback provider=fallback_mock queries=5 raw_result_count=5 deduped_result_count=5 cache_hit=True fallback_used=True | status=ok | time=2026-05-26T02:26:58.629048+00:00
- source-reviewing | SOURCE_REVIEWING | SourceReviewAgent | tool=review_candidate_sources | status=ok | time=2026-05-26T02:26:58.638128+00:00
- human-reviewing | HUMAN_REVIEWING | HumanReviewGate | tool=cli_candidate_confirmation | status=skipped | time=2026-05-26T02:26:58.647249+00:00
- drafting-after-human-review | DRAFTING | WritingAgent | tool=llm_optional_or_template | status=ok | time=2026-05-26T02:26:58.657854+00:00
- literature-reviewing | LITERATURE_REVIEWING | LiteratureAgent | tool=analyze_literature_needs | status=ok | time=2026-05-26T02:26:58.660884+00:00
- citation-checking | CITATION_CHECKING | CitationAgent | tool=check_citation_consistency | status=issues_found | time=2026-05-26T02:26:58.666814+00:00
  - failure_reason: 引用来源缺失
- formatting | FORMATTING | WordFormatAgent | tool=tool_assign_heading_styles, tool_format_body, tool_setup_page_numbers, tool_format_references | status=ok | time=2026-05-26T02:26:58.924950+00:00
- verifying | VERIFYING | VerifierAgent | tool=verify_content_web_literature_citation_and_format | status=ok | time=2026-05-26T02:26:58.927090+00:00

## 版本限制
- 搜索结果只是候选文献线索，不自动写入正式参考文献。
- 没有搜索 API key 或真实搜索失败时自动 fallback 到 mock provider。
- 不自动生成 DOI、作者、期刊、实验结果、数据集规模、指标数值或对比结论。
- 不做 RAG、向量库、LaTeX、GUI 或数据库。
