import { SystemMessage, HumanMessage } from "@langchain/core/messages";

export function buildDiagnosisReviewerPrompt(
  originalSymptoms,
  optimizedSymptoms,
  diagnosisResults
) {
  const resultsText = diagnosisResults
    .map(
      (r) =>
        `- ${r.condition}: 概率 ${(r.probability * 100).toFixed(1)}%, 描述: ${r.description || "无"}`
    )
    .join("\n");

  return [
    new SystemMessage(
      `你是一名资深临床医学审查专家。你的任务是审查AI诊断模型给出的疾病概率分布，判断其是否合理。

审查要点：
1. 对比用户原始症状描述和优化后的症状，确认预处理是否准确
2. 检查每种疾病的概率是否与症状严重程度和常见程度匹配
3. 常见病（如感冒、颈椎病、肌肉劳损等）在模糊症状下应有更高概率
4. 罕见病（如肿瘤、脊柱炎等）在没有明确指征时概率应较低
5. 重新分配概率使其更符合临床实际，三个概率之和必须为1.0

输出严格JSON格式，不要加任何Markdown标记：
{
  "review_comment": "对诊断结果的整体评价和调整理由",
  "preprocess_accurate": true/false,
  "results": [
    {"condition": "疾病名", "probability": 0.xx, "description": "调整后的描述"},
    ...
  ]
}`
    ),
    new HumanMessage(
      `用户原始症状输入摘要：${originalSymptoms}\n\n` +
        `AI优化后的症状描述：${optimizedSymptoms}\n\n` +
        `AI诊断模型输出的结果：\n${resultsText}\n\n` +
        `请审查以上诊断结果，重新分配概率使其更合理。`
    ),
  ];
}
