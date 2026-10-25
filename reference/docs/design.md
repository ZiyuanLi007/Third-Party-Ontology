# 设计与整合

## Foundation
RegulatoryObligation、PolicyRequirement、ProcedureStep、Control、Risk 共用 SourceDocumentVersion、SourcePassage 和 MappingAssertion。TPR 作为场景，不复制这些类。ReviewRecord/ReportRun 预留为类型；本版实际审核状态在断言上，运行来源记录在 manifest 中，未实施审批工作流。
每条 MappingAssertion 是判断而非默认真理，包含双端证据、关系类型、理由、要素标签和审核状态。采用 example.org 命名空间，生产接入应替换为企业 URI。
## 诊断
材料未提供优先输出 MATERIAL_MISSING；材料提供但不能沿非拒绝关系到达控制则 LINK_NOT_FOUND；到达控制后，有冲突输出 CONFLICT，否则缺要素输出 PARTIAL_SUPPORT，否则 DOCUMENTARY_SUPPORT。任何结果均不等同于合规结论。unreviewed 的路径用于候选报告，须显式标记；rejected 不用于可达性。
本版两个要素为 classification / before_contract，聚焦一条窄义务。通用扩展应增加主体、条件、例外、范围与多控制联合支撑规则。当前通过可达控制的策划标签核对端到端要素，不具备一般法律推理能力。
## Semantic / Kinetic
Semantic 为对象、原文、来源及映射断言。Kinetic 仅包含读取样例、检查引用、计算可达性和要素诊断、导出报告；无整改、发布、任务分派和外部写回。
## 接入已有系统
1. 用已有政策/程序对象 ID 替换样例 ID，保留对照表；不要重新提取已验证图谱。
2. 使用既有 DI 导出 paragraph ID、原文、页码、版本和上下文；RAG 仅在批准的文档清单中检索。
3. 输出候选 MappingAssertion；旧图谱缺证据的关系也应标记未审核。
4. Compliance 核实监管解释；Policy/Process Owner 核实中间映射；Control Owner 核实控制材料。
5. 扩展现有报告模板展示这些数据，本包 HTML 只是参考输出。
## 数据字典
nodes.id 为稳定业务标识；source 指向版本化文件；locator 为文件章节；text 是来源片段；plain_english 是改写；bank_interpretation 独立且本版均为虚构草案。elements 是策划者的证据判断，conflicts 是明确矛盾判断。映射 evidence 使用 node ID，导出时对应其 SourcePassage。cases.expected 仅测试使用，不参与诊断计算。
## 风险和限制
资料不完整采用开放世界假设：未找到不等于不存在。DORA 适用性在此为演示假设。版本升级需重新审核断言，不能覆盖原文后沿用已审核标签。当前仅静态文件，无并发、认证、敏感信息权限或生产审计保证。
