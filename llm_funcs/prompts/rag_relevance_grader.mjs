import { SystemMessage, HumanMessage } from "@langchain/core/messages";

export function buildRagRelevancePrompt(optimizedSymptoms, ragDocs) {
  return [
    new SystemMessage(
      "你是RAG内容评审员，请根据检索摘要判断与症状的相关性，并给出0-5评分。只输出JSON。评分标准：0=无关或矛盾；1=几乎无关；2=弱相关；3=部分相关；4=高度相关；5=极高相关且包含关键诊断提示/鉴别要点。"
    ),
    new HumanMessage(
      `症状：${optimizedSymptoms}\n` +
      `RAG摘要：${JSON.stringify(ragDocs, null, 2)}\n\n` +
      `输出格式：\n{\n  "ragScore": 0-5,\n  "ragComment": "..."\n}`
    ),
  ];
}
