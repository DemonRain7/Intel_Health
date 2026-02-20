import { SystemMessage, HumanMessage } from "@langchain/core/messages";

export function buildSymptomQualityPrompt(optimizedSymptoms, ragKeywords) {
  return [
    new SystemMessage(
      "你是医学结构化质量评分员，请为结构化症状描述评分(0-5)，并给出改进建议。只输出JSON。评分标准可以参考这几项：1. 是否有无中生有、添加用户未提及的症状； 2. 是否符合用户描述； 3. 是否保持客观中立的医学描述语气； 4. 是否符合逻辑； 5. 是否夸大或缩小了病情程度；"
    ),
    new HumanMessage(
      `请对以下症状结构化结果进行评分：\n` +
      `optimized_symptoms: ${optimizedSymptoms}\n` +
      `rag_keywords: ${JSON.stringify(ragKeywords)}\n\n` +
      `请输出 JSON 格式：{"score": 0-5, "comment": "...", "isValid": true/false}`
    ),
  ];
}
