import { SystemMessage, HumanMessage } from "@langchain/core/messages";

/**
 * @param {string} condition        - 疾病名称
 * @param {string} drugRagContext   - 药物 RAG 检索内容
 * @param {number|null} diagnosisScore   - drug_evidence_grader 的评分（0-5），null 表示未知
 * @param {string} diagnosisComment      - 评分理由
 */
export function buildDrugRecommendPrompt(condition, drugRagContext, diagnosisScore = null, diagnosisComment = "") {
  let ragInstruction;
  if (diagnosisScore === null || diagnosisScore >= 4) {
    ragInstruction =
      "当前药物知识文档与该诊断高度相关，请优先参考以下文档内容给出推荐方案。";
  } else if (diagnosisScore >= 2) {
    ragInstruction =
      `当前药物知识文档相关度一般（评分 ${diagnosisScore}/5${diagnosisComment ? `，原因：${diagnosisComment}` : ""}）。` +
      "请综合文档内容与你的药学知识给出推荐，不要过度依赖文档，以通用药学知识为主要依据。";
  } else {
    ragInstruction =
      `当前药物知识文档相关度较低（评分 ${diagnosisScore}/5${diagnosisComment ? `，原因：${diagnosisComment}` : ""}）。` +
      "请主要依靠你的药学知识给出推荐，以下文档仅作辅助背景参考，不要强行从中提取用药方案。";
  }

  return [
    new SystemMessage(
      "你是临床药物推荐助手，请根据疾病和药物知识为患者推荐用药方案。" +
      "只输出JSON，不要加任何说明文字或Markdown标签。"
    ),
    new HumanMessage(
      `疾病：${condition}\n\n` +
      `【药物文档使用说明】${ragInstruction}\n\n` +
      `药物知识：\n${drugRagContext}\n\n` +
      `输出格式：\n` +
      `{\n` +
      `  "drugs": [{\n` +
      `    "condition": "疾病名称",\n` +
      `    "recommended_drugs": [\n` +
      `      {"name": "药物名", "usage": "用法用量", "notes": "注意事项"}\n` +
      `    ]\n` +
      `  }]\n` +
      `}`
    ),
  ];
}
