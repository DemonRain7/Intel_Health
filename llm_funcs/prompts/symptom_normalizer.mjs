import { SystemMessage, HumanMessage } from "@langchain/core/messages";

export function buildSymptomNormalizerPrompt(diagnosisData) {
  const symptoms = Array.isArray(diagnosisData.symptoms) ? diagnosisData.symptoms.join("，") : "";
  const otherSymptoms = diagnosisData.other_symptoms || "无";
  return [
    new SystemMessage(
      "你是医学助理，请将用户口语症状整理为专业、结构化描述，并提取更具体的RAG关键词（必须包含身体部位+症状+关键修饰，如“腰部外伤疼痛”“腰椎间盘突出放射痛”）。只输出JSON。"
    ),
    new HumanMessage(
      `用户ID: ${diagnosisData.user_id}\n` +
      `身体部位: ${diagnosisData.body_part}\n` +
      `主要症状: ${symptoms}\n` +
      `其他症状: ${otherSymptoms}\n` +
      `严重程度(1-5): ${diagnosisData.severity}\n` +
      `持续时间: ${diagnosisData.duration}\n\n` +
      `输出格式：\n{\n  "optimized_symptoms": "...",\n  "rag_keywords": ["..."]\n}`
    ),
  ];
}
