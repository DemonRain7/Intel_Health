/**
 * test_pipeline.mjs — IntelHealth 端到端流水线测试
 *
 * 用法:
 *   # 1) 先启动本地推理服务器
 *   python inference/local_server.py --port 8000
 *
 *   # 2a) 无 RAG 模式（不需要 Supabase）
 *   SKIP_RAG=true node test/test_pipeline.mjs
 *
 *   # 2b) 有 RAG 模式（需要 Supabase 配置）
 *   node test/test_pipeline.mjs
 */

import { app as diagnosisApp } from "../llm_funcs/diagnosis-graph.mjs";

// ── 测试用例 ────────────────────────────────────────

const TEST_CASES = [
  {
    name: "头痛 + 发热",
    input: {
      body_part: "头部",
      symptoms: ["头痛", "发热"],
      other_symptoms: "伴有轻微恶心，持续两天",
      severity: 3,
      duration: "1To3Days",
      model_profile_id: "local_test",
    },
  },
  {
    name: "腹痛 + 腹泻",
    input: {
      body_part: "腹部",
      symptoms: ["腹痛", "腹泻"],
      other_symptoms: "饭后加重，有时伴有恶心",
      severity: 4,
      duration: "4To7Days",
      model_profile_id: "local_test",
    },
  },
];

// ── 验证函数 ────────────────────────────────────────

function validateFinalOutput(output, caseName) {
  const errors = [];

  if (!output || typeof output !== "object") {
    errors.push("finalOutput 为空或不是对象");
    return errors;
  }

  // results
  if (!Array.isArray(output.results)) {
    errors.push("results 不是数组");
  } else {
    if (output.results.length < 3) {
      errors.push(`results 数量不足: ${output.results.length} < 3`);
    }
    for (const [i, r] of output.results.entries()) {
      if (!r.condition || typeof r.condition !== "string") {
        errors.push(`results[${i}].condition 无效`);
      }
      if (typeof r.probability !== "number" || r.probability < 0) {
        errors.push(`results[${i}].probability 无效: ${r.probability}`);
      }
      if (!r.description || typeof r.description !== "string") {
        errors.push(`results[${i}].description 无效`);
      }
    }
  }

  // recommendations
  if (!Array.isArray(output.recommendations)) {
    errors.push("recommendations 不是数组");
  } else if (output.recommendations.length < 3) {
    errors.push(
      `recommendations 数量不足: ${output.recommendations.length} < 3`
    );
  }

  // recomm_short
  if (!Array.isArray(output.recomm_short)) {
    errors.push("recomm_short 不是数组");
  } else if (output.recomm_short.length < 3) {
    errors.push(`recomm_short 数量不足: ${output.recomm_short.length} < 3`);
  }

  return errors;
}

// ── 运行测试 ────────────────────────────────────────

async function runTest(testCase) {
  const { name, input } = testCase;
  console.log(`\n${"=".repeat(60)}`);
  console.log(`TEST: ${name}`);
  console.log(`${"=".repeat(60)}`);
  console.log("Input:", JSON.stringify(input, null, 2));

  const t0 = Date.now();

  try {
    const result = await diagnosisApp.invoke({
      diagnosisData: input,
    });

    const elapsed = ((Date.now() - t0) / 1000).toFixed(1);
    console.log(`\n⏱️  完成用时: ${elapsed}s`);

    // 检查各 state channel
    console.log("\n── State Channels ──");
    console.log("modelType:", result.modelType);
    console.log(
      "optimizedSymptoms:",
      result.optimizedSymptoms?.slice(0, 100) + "..."
    );
    console.log("ragKeywords:", result.ragKeywords);
    console.log("ragDocs count:", result.ragDocs?.length ?? 0);
    console.log("ragScore:", result.ragScore);
    console.log("ragComment:", result.ragComment?.slice(0, 80));
    console.log("diagnosisScore:", result.diagnosisScore);
    console.log("diagnosisComment:", result.diagnosisComment?.slice(0, 80));

    // 验证 finalOutput
    const output = result.finalOutput;
    console.log("\n── Final Output ──");
    console.log(JSON.stringify(output, null, 2));

    const errors = validateFinalOutput(output, name);
    if (errors.length > 0) {
      console.error(`\n❌ FAIL: ${name}`);
      for (const err of errors) {
        console.error(`   - ${err}`);
      }
      return false;
    }

    console.log(`\n✅ PASS: ${name}`);
    return true;
  } catch (error) {
    const elapsed = ((Date.now() - t0) / 1000).toFixed(1);
    console.error(`\n❌ ERROR after ${elapsed}s: ${name}`);
    console.error(error);
    return false;
  }
}

// ── Main ────────────────────────────────────────────

async function main() {
  console.log("IntelHealth Pipeline E2E Test");
  console.log(`SKIP_RAG=${process.env.SKIP_RAG || "false"}`);
  console.log(`Test cases: ${TEST_CASES.length}`);

  let passed = 0;
  let failed = 0;

  for (const tc of TEST_CASES) {
    const ok = await runTest(tc);
    if (ok) passed++;
    else failed++;
  }

  console.log(`\n${"=".repeat(60)}`);
  console.log(`RESULTS: ${passed} passed, ${failed} failed, ${TEST_CASES.length} total`);
  console.log(`${"=".repeat(60)}`);

  process.exit(failed > 0 ? 1 : 0);
}

main();
