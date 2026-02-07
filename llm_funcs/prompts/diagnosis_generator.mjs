import { SystemMessage, HumanMessage } from "@langchain/core/messages";

export function buildDiagnosisPrompt(optimizedSymptoms, ragDocs) {
  return [
    new SystemMessage(
      "你是医学诊断助手，请基于症状与RAG背景给出3个可能诊断，并输出JSON。"
    ),
    new HumanMessage(
      `症状：${optimizedSymptoms}\n` +
      `RAG文档：${JSON.stringify(ragDocs, null, 2)}\n\n` +
      `输出格式：\n{\n  "results": [\n    {"condition": "...", "probability": 0.xx, "description": "..."}\n  ],\n  "recommendations": ["...","...","..."],\n  "recomm_short": ["..."x10]\n}`
    ),
  ];
}
