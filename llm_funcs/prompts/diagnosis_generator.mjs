import { SystemMessage, HumanMessage } from "@langchain/core/messages";

export function buildDiagnosisPrompt(optimizedSymptoms, ragDocs) {
  return [
    new SystemMessage(
      "你是医学推理助手，请根据症状和RAG文档推理出3组疾病可能性，并输出JSON。"
    ),
    new HumanMessage(
      `症状：${optimizedSymptoms}\n` +
      `RAG文档：${JSON.stringify(ragDocs, null, 2)}\n\n` +
      `输出格式：\n{\n  "results": [\n    {"condition": "...", "probability": 0.xx, "description": "..."}\n  ],\n  "recommendations": ["...","...","..."],\n  "recomm_short": ["..."x10]\n}`
    ),
  ];
}
