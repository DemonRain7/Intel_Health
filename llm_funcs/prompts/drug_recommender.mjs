import { SystemMessage, HumanMessage } from "@langchain/core/messages";

export function buildDrugRecommendPrompt(condition, drugRagContext) {
  return [
    new SystemMessage(
      "你是用药建议助手，请基于疾病与药物知识输出用药建议JSON。"
    ),
    new HumanMessage(
      `疾病：${condition}\n` +
      `药物知识：${drugRagContext}\n\n` +
      `输出格式：\n{\n  "drugs": [{\n    "condition": "...",\n    "recommended_drugs": [\n      {"name": "...", "usage": "...", "notes": "..."}\n    ]\n  }]\n}`
    ),
  ];
}
