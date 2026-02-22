import { SystemMessage, HumanMessage } from "@langchain/core/messages";

/**
 * @param {string} optimizedSymptoms
 * @param {Array}  ragDocs
 * @param {number|null} ragScore   - rag_relevance_grader 的评分（0-5），null 表示未知
 * @param {string} ragComment      - 评分理由
 */
export function buildDiagnosisPrompt(optimizedSymptoms, ragDocs, ragScore = null, ragComment = "") {
  let ragInstruction;
  if (ragScore === null || ragScore >= 4) {
    ragInstruction =
      "当前RAG文档与患者症状高度相关，请优先结合以下文档内容进行推理，文档可作为主要参考依据。";
  } else if (ragScore >= 2) {
    ragInstruction =
      `当前RAG文档相关度一般（评分 ${ragScore}/5${ragComment ? `，原因：${ragComment}` : ""}）。` +
      "请综合文档内容与你的医学知识进行推理，不要过度依赖文档，必要时以你的知识为主。";
  } else {
    ragInstruction =
      `当前RAG文档相关度较低（评分 ${ragScore}/5${ragComment ? `，原因：${ragComment}` : ""}）。` +
      "请主要依靠你的医学知识进行推理，将以下文档仅作辅助背景参考，不要强行从中提取诊断依据。";
  }

  return [
    new SystemMessage(
      "你是医学推理助手，请根据患者症状推理出3种可能的疾病，结合RAG文档和你的医学知识综合判断。" +
      "输出JSON：results（3个疾病，probability之和为1.0）、recommendations（3条就医建议）、recomm_short（10条简短提示）。" +
      "只输出JSON，不要加任何说明文字或Markdown标签。"
    ),
    new HumanMessage(
      `患者症状：\n${optimizedSymptoms}\n\n` +
      `【RAG文档使用说明】${ragInstruction}\n\n` +
      `RAG文档：\n${JSON.stringify(ragDocs, null, 2)}\n\n` +
      `输出格式：\n` +
      `{\n` +
      `  "results": [\n` +
      `    {"condition": "疾病名称", "probability": 0.xx, "description": "简要描述"}\n` +
      `  ],\n` +
      `  "recommendations": ["建议1", "建议2", "建议3"],\n` +
      `  "recomm_short": ["提示1", "提示2", "提示3", "提示4", "提示5", "提示6", "提示7", "提示8", "提示9", "提示10"]\n` +
      `}`
    ),
  ];
}
