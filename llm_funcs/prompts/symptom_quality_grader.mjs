import { SystemMessage, HumanMessage } from "@langchain/core/messages";

export function buildSymptomQualityPrompt(optimizedSymptoms, ragKeywords) {
  return [
    new SystemMessage(
      "你是医学结构化质检助手，请为结构化症状输出评分(0-5)，并给出简短建议。只输出JSON。"
    ),
    new HumanMessage(
      `输入：\noptimized_symptoms: ${optimizedSymptoms}\n` +
      `rag_keywords: ${JSON.stringify(ragKeywords)}\n\n` +
      `输出格式：\n{\n  "score": 0-5,\n  "comment": "...",\n  "isValid": true/false\n}`
    ),
  ];
}
