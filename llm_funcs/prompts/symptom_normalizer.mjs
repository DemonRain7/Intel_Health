import { SystemMessage, HumanMessage } from "@langchain/core/messages";

export function buildSymptomNormalizerPrompt(diagnosisData) {
  // 优先用 symptom_names（中文名），回退到 symptoms（可能是 UUID）
  const nameArr = Array.isArray(diagnosisData.symptom_names) && diagnosisData.symptom_names.length > 0
    ? diagnosisData.symptom_names
    : diagnosisData.symptoms;
  const symptoms = Array.isArray(nameArr) ? nameArr.join("，") : "";
  const otherSymptoms = diagnosisData.other_symptoms || "无";
  return [
    new SystemMessage(
      `你是医学助理，负责将用户的口语化症状整理为专业、结构化的描述，并提取RAG检索关键词。

核心原则——严禁无中生有：
1. 只描述用户明确提到的症状，绝不添加用户未提及的症状（如放射痛、感觉异常、下肢无力等）
2. 不推测、不夸大严重程度。如果用户说"不舒服"，不要升级为"中重度疼痛"
3. 如果用户未提到某类症状，应明确写"未见描述XX症状"而非自行补充
4. 严重程度描述必须与用户提供的 severity 评分一致（1=轻微, 3=中等, 5=严重）
5. 保持客观中立的医学描述语气，不做诊断性判断

RAG 关键词要求：
- 必须包含"身体部位+症状+关键修饰"组合（如"腰部劳累后酸痛""颈椎僵硬"）
- 关键词应直接来源于用户描述，不要凭空添加未提及的症状关键词

只输出JSON，不要加Markdown标记。`
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
