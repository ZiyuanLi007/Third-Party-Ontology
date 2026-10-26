# TRACE — Regulatory Intelligence Workbench

## 运行（本地应用，不是双击 HTML）
需要 Python 3.10 或以上。解压并在本目录运行：

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python app.py
```
Windows 激活命令：`.venv\Scripts\activate`，其余相同。浏览器打开 http://127.0.0.1:8765 。端口被占用时：`python app.py --port 8766`。
也可在安装依赖后运行 start.command（macOS/Linux）或 start.bat（Windows）。不要直接双击 static/index.html：上传、解析和模型调用需要 Python 后端。

## 五分钟演示
1. 监管要求评估页点击 A/B/C/D：查看完整支撑、部分支撑、缺材料和冲突。点击四个层级卡片展开原文与定位；映射依据中检查双端证据。
2. 本体浏览器切换 Foundation / TPR 场景视图 / Kinetic 能力。点节点看解释，导入自己的 TTL 或导出 Foundation。自定义 TTL 仅浏览，不自动改写业务诊断逻辑。
3. 文档工作台按 regulation、policy、procedure、control 类型分别上传 samples/ 中四个文件。版本填 v1.0。加载即解析原文；点击结构化可生成段落级条目。
4. 返回评估页，选中文档，输入监管要求，运行本地候选检索。此时只有候选证据，不会假装完成语义覆盖评估。
5. 配置获准使用的模型，测试连接。可再做模型结构化、切换模型评估。查看引用与诊断，导出 JSON 或独立 HTML 报告。
6. 评估记录保留上传材料评估的证据快照；预设演示不写入记录。

## 模型配置
支持 **OpenAI-compatible Chat Completions**，不是任意厂商原生协议。填写完整 endpoint，例如 `https://your-gateway/v1/chat/completions`、model、key。默认认证 Header 为 Authorization，前缀 `Bearer `（末尾空格有意义）。Azure 兼容接口填写带部署和 api-version 的完整地址，Header 为 api-key，前缀留空。本地兼容服务可填写 localhost HTTP，无需 Key。其他非本地地址要求 HTTPS；拒绝重定向以免凭据被转发。
请求为 messages + model + temperature，响应从 choices[0].message.content 读取 JSON。Responses-only / Anthropic 原生接口不支持，需在 provider() 中添加适配器。模型必须支持 JSON 输出；畸形输出或无效引文会报错/降级，不静默回退成成功。
Key 只在 Python 进程内存中，留空保留已配置 Key；“清除”会清空配置。重启需要重新填写。连接测试发送最小请求，无文档内容。

## 功能与数据
- 文档：TXT/MD/JSON/CSV 按文本段落处理；PDF 提取文本；DOCX 提取段落。JSON/CSV 并非自动按企业 schema 映射。
- 原文保留段落/页面定位及块内字符范围，模型 quote 必须是原文子串。
- 本地结构化仅拆段；模型结构化产生单位、原文引用、plain English、银行解释草案，均未审核。
- 评估按每层最多 6 个候选段落进行关键词检索，再由模型完成层级分析和相邻层链接。中文跨语言检索、复杂表格、扫描 PDF、脚注和法律依赖解析有限。扫描 PDF 先做 OCR；替换为银行既有 DI/RAG 接口是后续接入点。
- 评估目前直接检索原文段落；结构化条目是可检查、可导出的独立产物，不自动成为已认可知识。
- 缺少某类型文档 = material_missing；有文档但无支撑 = not_found；引用失效 = uncertain。supported/partial/conflict 必须有有效原文引用。相邻映射需双端证据。精确引用验证不等于语义或法律判断正确。
- Model summary 是模型草案，必须结合经校验的层级状态和警告阅读，未经过 SME 签署。
- 单文件 10MB、单文件解析文本 300k 字符；单次模型抽取 60k 字符。长文本拒绝并提示拆分，不静默截断。

## 范围与事实边界
样例只用 DORA 原始 OJ Article 28(4)(a)；上位引言的签约前条件为标记清晰的改写。银行材料全为合成；没有真实 SME 审核。TPR 是 Foundation 的场景视图，不是另一套重复 ontology。所有报告不认证合规，不评估控制运行有效性，不生成整改方案或任务。
这是独立本地 POC，尚未连接银行现有图谱/pipeline；reference/ 保留前版模型、结构化样例和设计文档。没有正式身份认证或多租户隔离，请保持默认 127.0.0.1 运行，不用于生产或公网部署。

## 存储与清理
`workspace/state.json` 保存解析文本、结构化条目、导入 ontology 与评估快照，不包含模型配置或 key。删除文档不删除历史报告证据；彻底清除本地数据可停止服务后删除 workspace/state.json。原文件未复制保存，请自行保留。分发给他人前不要打包 workspace 内容。

## 文件
app.py 后端；static/ 前端；samples/ 可上传样例；reference/ 上一版数据和 TTL；test_app.py 核心与接口测试；TEST_RESULTS.txt 验证结果。

## 接入企业能力
parse_file() → Document Intelligence；retrieve() → Group AI Platform RAG；provider() → 企业模型网关；ontology() / state → 现有知识图谱服务。保留企业对象 ID、文档版本、原文位置和审核状态。不可将本地候选映射直接升级为已审核关系。

## 测试
`python -m unittest -v test_app.py`
已验证 mock 模型协议、伪造引用拦截、缺材料判定、结构化引用和 TTL 解析。未使用真实模型 Key，因此真实模型服务的网络、配额和输出质量需在你的环境通过“测试连接”核实。当前托管预览环境没有可用 Python 后端运行时，浏览器视觉验收未完成；本地 HTTP 接口和 JavaScript 语法单独检查。

## 真实样本测试与 TPR 视图
参见 [REAL_SAMPLE_GUIDE.md](REAL_SAMPLE_GUIDE.md)。TPR 页现为四种预置实例场景，导出实例 TTL；Foundation 页为通用类型定义。上传材料尚不自动进入预置图。
