import { SystemMessage, HumanMessage } from "@langchain/core/messages";

export function buildSymptomQualityPrompt(optimizedSymptoms, ragKeywords) {
  return [
    new SystemMessage(
      "你是医学结构化质量评分员，请为结构化症状描述评分(0-5)，并给出改进建议。只输出JSON。"
    ),
    new HumanMessage(
      `请对以下症状结构化结果进行评分：\n` +
      `optimized_symptoms: ${optimizedSymptoms}\n` +
      `rag_keywords: ${JSON.stringify(ragKeywords)}\n\n` +
      `请输出 JSON 格式：{"score": 0-5, "comment": "...", "isValid": true/false}`
    ),
  ];
}
