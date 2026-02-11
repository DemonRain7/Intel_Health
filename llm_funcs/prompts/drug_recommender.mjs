import { SystemMessage, HumanMessage } from "@langchain/core/messages";

export function buildDrugRecommendPrompt(condition, drugRagContext) {
  return [
    new SystemMessage(
      "你是临床药物推荐助手，请根据疾病和药物知识推荐用药，输出JSON。"
    ),
    new HumanMessage(
      `疾病：${condition}\n` +
      `药物知识：${drugRagContext}\n\n` +
      `输出格式：\n{\n  "drugs": [{\n    "condition": "...",\n    "recommended_drugs": [\n      {"name": "...", "usage": "...", "notes": "..."}\n    ]\n  }]\n}`
    ),
  ];
}
