import { SystemMessage, HumanMessage } from "@langchain/core/messages";

export function buildDrugEvidencePrompt(diagnosisData, ragDocs) {
  return [
    new SystemMessage(
      "你是用药证据评审员，请根据诊断结果与药物检索摘要给出0-5评分。只输出JSON。评分标准：0=无关/矛盾；1=几乎无关；2=弱相关；3=部分相关；4=高度相关；5=极高相关且包含关键禁忌/安全提示。"
    ),
    new HumanMessage(
      `诊断：${JSON.stringify(diagnosisData, null, 2)}\n` +
      `RAG摘要：${JSON.stringify(ragDocs, null, 2)}\n\n` +
      `输出格式：\n{\n  "diagnosisScore": 0-5,\n  "diagnosisComment": "..."\n}`
    ),
  ];
}
