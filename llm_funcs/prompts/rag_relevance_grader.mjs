import { SystemMessage, HumanMessage } from "@langchain/core/messages";

export function buildRagRelevancePrompt(optimizedSymptoms, ragDocs) {
  return [
    new SystemMessage(
      "你是医学RAG内容质量评审员。你的评分将直接影响后续诊断Agent对这批检索文档的引用权重：" +
      "分数越低，诊断Agent越依赖自身医学知识而非这批文档；分数越高，越优先引用文档内容。" +
      "请严格、诚实地打分——低分同样有参考价值，切勿为了「让流程顺利」而虚高打分。" +
      "只输出JSON，不要加任何说明文字或Markdown标签。\n\n" +
      "评分标准（0-5整数）：\n" +
      "0 = 文档与患者症状无关或存在明显矛盾，不应引用\n" +
      "1 = 文档涉及相关器官/系统，但与具体症状几乎无交叉\n" +
      "2 = 文档有弱相关性，可提供少量背景参考，但核心内容不匹配\n" +
      "3 = 文档与症状有部分匹配，能提供一定诊断参考价值\n" +
      "4 = 文档高度相关，包含与症状直接对应的诊断信息或鉴别要点\n" +
      "5 = 文档极高相关，包含精准的症状-疾病映射、关键诊断标准或重要鉴别诊断提示"
    ),
    new HumanMessage(
      `患者症状：\n${optimizedSymptoms}\n\n` +
      `检索到的RAG文档摘要：\n${JSON.stringify(ragDocs, null, 2)}\n\n` +
      `请评估以上文档对诊断该患者症状的参考价值，给出评分和简短理由。\n\n` +
      `输出格式（严格JSON，不含Markdown标签）：\n` +
      `{\n  "ragScore": <0-5整数>,\n  "ragComment": "<评分理由，不超过50字>"\n}`
    ),
  ];
}
