import { SystemMessage, HumanMessage } from "@langchain/core/messages";

export function buildDrugEvidencePrompt(diagnosisData, ragDocs) {
  return [
    new SystemMessage(
      "你是医学用药证据质量评审员。你的评分将直接影响后续药物推荐Agent对这批检索文档的引用权重：" +
      "分数越低，推荐Agent越依赖通用药学知识而非这批文档；分数越高，越优先引用文档内容。" +
      "请严格、诚实地打分——低分同样有参考价值，切勿为了「让流程顺利」而虚高打分。" +
      "只输出JSON，不要加任何说明文字或Markdown标签。\n\n" +
      "评分标准（0-5整数）：\n" +
      "0 = 文档内容与诊断疾病无关或存在明显矛盾，不应引用\n" +
      "1 = 文档涉及相关用药领域，但与具体诊断几乎无交叉\n" +
      "2 = 文档有弱相关性，可提供少量背景参考，但药物推荐针对性不足\n" +
      "3 = 文档与诊断有部分匹配，提供一定用药参考价值\n" +
      "4 = 文档高度相关，包含与诊断疾病直接对应的用药方案或循证依据\n" +
      "5 = 文档极高相关，包含精准的用药指导、重要禁忌提示或关键药物相互作用信息"
    ),
    new HumanMessage(
      `诊断结果：\n${JSON.stringify(diagnosisData, null, 2)}\n\n` +
      `检索到的RAG文档摘要：\n${JSON.stringify(ragDocs, null, 2)}\n\n` +
      `请评估以上文档对该诊断结果的用药参考价值，给出评分和简短理由。\n\n` +
      `输出格式（严格JSON，不含Markdown标签）：\n` +
      `{\n  "diagnosisScore": <0-5整数>,\n  "diagnosisComment": "<评分理由，不超过50字>"\n}`
    ),
  ];
}
