// diagnosis-graph.mjs
console.log('Starting module load...');

import { ChatOpenAI, OpenAIEmbeddings } from "@langchain/openai";
import { HumanMessage, SystemMessage, AIMessage } from "@langchain/core/messages";
import { StateGraph, MessagesAnnotation } from "@langchain/langgraph";
import { createClient } from "@supabase/supabase-js";
import Ajv from "ajv";
import addFormats from "ajv-formats";
import crypto from "crypto";
import fs from "fs";
import path from "path";
import { fileURLToPath } from "url";

import { buildSymptomNormalizerPrompt } from "./prompts/symptom_normalizer.mjs";
import { buildSymptomQualityPrompt } from "./prompts/symptom_quality_grader.mjs";
import { buildRagRelevancePrompt } from "./prompts/rag_relevance_grader.mjs";
import { buildDiagnosisPrompt } from "./prompts/diagnosis_generator.mjs";
import { buildDrugEvidencePrompt } from "./prompts/drug_evidence_grader.mjs";
import { buildDrugRecommendPrompt } from "./prompts/drug_recommender.mjs";

const DEFAULT_GPT_MODEL = process.env.OPENAI_MODEL_NAME || "gpt-4.1";
const DEFAULT_LOCAL_MODEL = process.env.LOCAL_MODEL_NAME || "Qwen/Qwen3-0.5B-Instruct";
const DEFAULT_LOCAL_URL = process.env.LOCAL_MODEL_URL || "http://localhost:8000/v1";
const RAG_BACKEND = process.env.RAG_BACKEND || "pgvector";
const RAG_EMBEDDING_MODEL = process.env.RAG_EMBEDDING_MODEL || "text-embedding-3-small";
const RAG_CORPUS_DIAGNOSIS = process.env.RAG_CORPUS_DIAGNOSIS || "";
const RAG_CORPUS_DRUG = process.env.RAG_CORPUS_DRUG || "";
const SUPABASE_URL = process.env.SUPABASE_URL;
const SUPABASE_ANON_KEY = process.env.SUPABASE_ANON_KEY;
const SUPABASE_SERVICE_ROLE_KEY = process.env.SUPABASE_SERVICE_ROLE_KEY;

const supabaseClient = SUPABASE_URL && (SUPABASE_SERVICE_ROLE_KEY || SUPABASE_ANON_KEY)
  ? createClient(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY || SUPABASE_ANON_KEY, {
      auth: { persistSession: false }
    })
  : null;

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const PROJECT_ROOT = path.resolve(__dirname, "..");
const LOCAL_MODELS_ROOT = process.env.LOCAL_MODELS_ROOT || path.resolve(PROJECT_ROOT, "models");
const MODEL_PROFILES_PATH = path.resolve(__dirname, "../config/model_profiles.json");
const SCHEMA_DIR = path.resolve(__dirname, "../src/assets/schemas");

let MODEL_PROFILES = {};
try {
  MODEL_PROFILES = JSON.parse(fs.readFileSync(MODEL_PROFILES_PATH, "utf-8"));
} catch (error) {
  console.warn("⚠️ 无法加载 model_profiles.json，使用默认配置:", error.message);
}

const ajv = new Ajv({ allErrors: true, allowUnionTypes: true });
addFormats(ajv);
const SCHEMA_CACHE = new Map();

function getSchemaValidator(schemaName) {
  if (SCHEMA_CACHE.has(schemaName)) {
    return SCHEMA_CACHE.get(schemaName);
  }
  const schemaPath = path.resolve(SCHEMA_DIR, `${schemaName}.json`);
  if (!fs.existsSync(schemaPath)) {
    console.warn(`⚠️ schema 文件不存在: ${schemaPath}`);
    SCHEMA_CACHE.set(schemaName, null);
    return null;
  }
  const schema = JSON.parse(fs.readFileSync(schemaPath, "utf-8"));
  const validate = ajv.compile(schema);
  SCHEMA_CACHE.set(schemaName, validate);
  return validate;
}

function validateSchema(schemaName, data) {
  if (!schemaName) return true;
  const validate = getSchemaValidator(schemaName);
  if (!validate) return true;
  const ok = validate(data);
  if (!ok) {
    console.warn("⚠️ schema 校验失败:", schemaName, validate.errors);
  }
  return ok;
}

// 初始化 GPT LLM (默认) - 使用官方 OpenAI API
const llmGPT = new ChatOpenAI({
  model: DEFAULT_GPT_MODEL,  // GPT-4.1
  temperature: 0.2,  // 控制随机性，0.2 适合医学诊断
  max_tokens: 1000,   // 限制回复长度，防止过长响应导致超时
  openAIApiKey: process.env.OPENAI_API_KEY,
});

// 初始化本地模型 LLM
const llmLocal = new ChatOpenAI({
  model: DEFAULT_LOCAL_MODEL,
  temperature: 0.2,
  maxTokens: 1000,
  openAIApiKey: "not-needed",  // vLLM 本地服务不需要 API Key
  configuration: {
    baseURL: DEFAULT_LOCAL_URL,
  },
});

const LLM_CACHE = new Map();
const AGENT_MODEL_PREFIX = {
  symptom_normalizer: "SYMPTOM_NORMALIZER",
  symptom_quality_grader: "SYMPTOM_QUALITY_GRADER",
  rag_relevance_grader: "RAG_RELEVANCE_GRADER",
  diagnosis_generator: "DIAGNOSIS_GENERATOR",
  drug_evidence_grader: "DRUG_EVIDENCE_GRADER",
  drug_recommender: "DRUG_RECOMMENDER",
  output_formatter: "OUTPUT_FORMATTER",
};

function resolveAgentModelConfig(agentName, diagnosisData = {}) {
  const profileId = diagnosisData.model_profile_id || "fast";
  const profile = MODEL_PROFILES[profileId] || MODEL_PROFILES.fast || {};
  const profileAgent = profile?.agents?.[agentName] || {};
  const override = diagnosisData?.agent_overrides?.[agentName] || {};
  return {
    model_type: override.model_type || profileAgent.model_type,
    model_name: override.model_name || profileAgent.model_name,
    model_path: override.model_path || profileAgent.model_path,
    base_url: override.base_url || profileAgent.base_url,
  };
}

function resolveModelPath(modelPathValue) {
  if (!modelPathValue || typeof modelPathValue !== "string") return null;
  const normalized = modelPathValue.trim();
  if (!normalized) return null;

  if (path.isAbsolute(normalized)) {
    return normalized;
  }

  // Support paths like "models/merged/diagnosis_generator"
  if (normalized.startsWith("models/") || normalized.startsWith("models\\")) {
    return path.resolve(PROJECT_ROOT, normalized);
  }

  // Support short relative paths inside LOCAL_MODELS_ROOT
  return path.resolve(LOCAL_MODELS_ROOT, normalized);
}

function buildLLM({ modelType, modelName, baseURL }) {
  if (modelType === "local") {
    return new ChatOpenAI({
      model: modelName || DEFAULT_LOCAL_MODEL,
      temperature: 0.2,
      maxTokens: 1000,
      openAIApiKey: "not-needed",
      configuration: {
        baseURL: baseURL || DEFAULT_LOCAL_URL,
      },
    });
  }
  return new ChatOpenAI({
    model: modelName || DEFAULT_GPT_MODEL,
    temperature: 0.2,
    max_tokens: 1000,
    openAIApiKey: process.env.OPENAI_API_KEY,
  });
}

// 根据模型类型选择 LLM（支持按 Agent 独立配置）
function getLLM(agentName, modelTypeOverride, diagnosisData) {
  const prefix = AGENT_MODEL_PREFIX[agentName];
  const envModelType = prefix ? process.env[`${prefix}_MODEL_TYPE`] : null;
  const envGptModel = prefix ? process.env[`${prefix}_GPT_MODEL`] : null;
  const envLocalModel = prefix ? process.env[`${prefix}_LOCAL_MODEL`] : null;
  const envLocalModelPath = prefix ? process.env[`${prefix}_LOCAL_MODEL_PATH`] : null;
  const envLocalUrl = prefix ? process.env[`${prefix}_LOCAL_URL`] : null;

  const profileConfig = resolveAgentModelConfig(agentName, diagnosisData);

  const resolvedModelType =
    profileConfig.model_type ||
    envModelType ||
    modelTypeOverride ||
    diagnosisData?.model_type ||
    "local";

  let resolvedModelName =
    resolvedModelType === "local"
      ? (profileConfig.model_name || envLocalModel || DEFAULT_LOCAL_MODEL)
      : (profileConfig.model_name || envGptModel || DEFAULT_GPT_MODEL);

  if (resolvedModelType === "local") {
    const localModelPath = resolveModelPath(
      profileConfig.model_path || envLocalModelPath
    );
    if (localModelPath) {
      if (fs.existsSync(localModelPath)) {
        resolvedModelName = localModelPath;
      } else {
        console.warn(`Local model path not found for ${agentName}: ${localModelPath}. Falling back to model_name.`);
      }
    }
  }
  const resolvedBaseURL =
    resolvedModelType === "local" ? (profileConfig.base_url || envLocalUrl || DEFAULT_LOCAL_URL) : null;

  const cacheKey = `${resolvedModelType}|${resolvedModelName}|${resolvedBaseURL || ""}`;
  if (cacheKey === `gpt|${DEFAULT_GPT_MODEL}|`) {
    console.log("使用 GPT 模型:", DEFAULT_GPT_MODEL);
    return llmGPT;
  }
  if (cacheKey === `local|${DEFAULT_LOCAL_MODEL}|${DEFAULT_LOCAL_URL}`) {
    console.log("使用本地模型:", DEFAULT_LOCAL_MODEL);
    return llmLocal;
  }

  if (!LLM_CACHE.has(cacheKey)) {
    LLM_CACHE.set(
      cacheKey,
      buildLLM({
        modelType: resolvedModelType,
        modelName: resolvedModelName,
        baseURL: resolvedBaseURL,
      })
    );
  }
  console.log("使用定制模型:", cacheKey);
  return LLM_CACHE.get(cacheKey);
}

// 兼容旧代码的默认 llm
const llm = llmGPT;

/**
 * 安全的 JSON 解析函数 - 适用于小模型可能不严格输出 JSON 的情况
 * @param {string} content - LLM 返回的内容
 * @param {object} defaultValue - 解析失败时的默认值
 * @returns {object} 解析后的对象或默认值
 */
function safeJSONParse(content, defaultValue = null, schemaName = null) {
  // 策略1: 直接解析
  try {
    const parsed = JSON.parse(content);
    if (schemaName && !validateSchema(schemaName, parsed)) {
      return defaultValue;
    }
    return parsed;
  } catch (e) {
    // 继续尝试其他策略
  }

  // 策略2: 尝试提取 JSON 对象 {...}
  const jsonObjectMatch = content.match(/\{[\s\S]*\}/);
  if (jsonObjectMatch) {
    try {
      const parsed = JSON.parse(jsonObjectMatch[0]);
      if (schemaName && !validateSchema(schemaName, parsed)) {
        return defaultValue;
      }
      return parsed;
    } catch (e) {
      // 继续尝试
    }
  }

  // 策略3: 尝试提取 JSON 数组 [...]
  const jsonArrayMatch = content.match(/\[[\s\S]*\]/);
  if (jsonArrayMatch) {
    try {
      const parsed = JSON.parse(jsonArrayMatch[0]);
      if (schemaName && !validateSchema(schemaName, parsed)) {
        return defaultValue;
      }
      return parsed;
    } catch (e) {
      // 继续尝试
    }
  }

  // 策略4: 清理常见的格式问题后重试
  const cleaned = content
    .replace(/```json\s*/g, '')
    .replace(/```\s*/g, '')
    .replace(/^\s*[\r\n]+/, '')
    .replace(/[\r\n]+\s*$/, '')
    .trim();

  try {
    const parsed = JSON.parse(cleaned);
    if (schemaName && !validateSchema(schemaName, parsed)) {
      return defaultValue;
    }
    return parsed;
  } catch (e) {
    // 全部失败
  }

  console.warn("⚠️ safeJSONParse: 所有解析策略均失败，返回默认值");
  return defaultValue;
}

function isNonEmptyString(value) {
  return typeof value === "string" && value.trim().length > 0;
}

function isStringArray(value) {
  return Array.isArray(value) && value.every(item => typeof item === "string" && item.trim().length > 0);
}

function normalizePreprocessOutput(parsed) {
  if (!parsed || !isNonEmptyString(parsed.optimized_symptoms) || !isStringArray(parsed.rag_keywords)) {
    return null;
  }
  return {
    optimized_symptoms: parsed.optimized_symptoms.trim(),
    rag_keywords: parsed.rag_keywords.map(k => k.trim()).filter(Boolean),
  };
}

function normalizeCriticOutput(parsed) {
  if (!parsed || typeof parsed.score !== "number") {
    return null;
  }
  return {
    score: Math.min(5, Math.max(0, Math.round(parsed.score))),
    comment: isNonEmptyString(parsed.comment) ? parsed.comment.trim() : "",
    isValid: typeof parsed.isValid === "boolean" ? parsed.isValid : parsed.score >= 3,
  };
}

function normalizeRagCheckOutput(parsed) {
  if (!parsed || typeof parsed.ragScore !== "number") {
    return null;
  }
  return {
    ragScore: Math.min(5, Math.max(0, Math.round(parsed.ragScore))),
    ragComment: isNonEmptyString(parsed.ragComment) ? parsed.ragComment.trim() : "",
  };
}

function normalizeDiagnosisOutput(parsed, options = {}) {
  const { allowExtraRecommendations = false } = options;
  if (!parsed || !Array.isArray(parsed.results)) {
    return null;
  }
  const results = parsed.results
    .filter(r => r && isNonEmptyString(r.condition) && typeof r.probability === "number" && isNonEmptyString(r.description))
    .map(r => ({
      condition: r.condition.trim(),
      probability: Math.max(0, r.probability),
      description: r.description.trim(),
    }));
  if (results.length < 3) {
    return null;
  }
  const totalProb = results.reduce((sum, r) => sum + r.probability, 0);
  const normalizedResults = totalProb > 0
    ? results.map(r => ({ ...r, probability: Number((r.probability / totalProb).toFixed(2)) }))
    : results.map(r => ({ ...r, probability: Number((1 / results.length).toFixed(2)) }));

  const recommendations = Array.isArray(parsed.recommendations)
    ? parsed.recommendations.filter(isNonEmptyString).map(r => r.trim())
    : [];
  const recommShort = Array.isArray(parsed.recomm_short)
    ? parsed.recomm_short.filter(isNonEmptyString).map(r => r.trim())
    : [];

  if (recommendations.length < 3 || recommShort.length < 3) {
    return null;
  }

  return {
    results: normalizedResults.slice(0, 3),
    recommendations: allowExtraRecommendations ? recommendations : recommendations.slice(0, 3),
    recomm_short: recommShort.slice(0, 10),
  };
}

function normalizeDrugOutput(parsed) {
  if (!parsed || !Array.isArray(parsed.drugs)) {
    return null;
  }
  const drugs = parsed.drugs
    .filter(d => d && isNonEmptyString(d.condition) && Array.isArray(d.recommended_drugs))
    .map(d => ({
      condition: d.condition.trim(),
      recommended_drugs: d.recommended_drugs
        .filter(r => r && isNonEmptyString(r.name) && isNonEmptyString(r.usage) && isNonEmptyString(r.notes))
        .map(r => ({
          name: r.name.trim(),
          usage: r.usage.trim(),
          notes: r.notes.trim(),
        })),
    }))
    .filter(d => d.recommended_drugs.length > 0);
  if (drugs.length === 0) {
    return null;
  }
  return { drugs };
}

function normalizeDiagnosisScoreOutput(parsed) {
  if (!parsed || typeof parsed.diagnosisScore !== "number") {
    return null;
  }
  return {
    diagnosisScore: Math.min(5, Math.max(0, Math.round(parsed.diagnosisScore))),
    diagnosisComment: isNonEmptyString(parsed.diagnosisComment) ? parsed.diagnosisComment.trim() : "",
  };
}

function buildFallbackDiagnosis() {
  return {
    results: [
      { condition: "需要进一步检查", probability: 0.5, description: "基于当前症状描述，建议进行专业医学检查以确定具体病因。" },
      { condition: "一般性不适", probability: 0.3, description: "可能是轻微的身体不适，建议观察症状变化。" },
      { condition: "心理因素", probability: 0.2, description: "部分症状可能与心理状态相关，建议保持良好心态。" }
    ],
    recommendations: [
      "建议尽快前往正规医院进行详细检查",
      "保持良好的作息和饮食习惯",
      "如症状加重请立即就医"
    ],
    recomm_short: ["及时就医", "保持休息", "健康饮食", "多喝水", "避免劳累", "保持心情", "定期复查", "遵医嘱", "适当运动", "规律作息"]
  };
}



// -------- 各节点定义 --------

// 1. 预处理和初步推测
async function symptom_normalizer(messages) {
  // 1. 获取用户发来的结构化诊断数据
  const lastMessage = messages.messages[messages.messages.length - 1];  // 获取最后一个 HumanMessage 对象
  // console.log(lastMessage);
  const diagnosisData = lastMessage ? lastMessage.content : null;
  // console.log("第一步input的message：",diagnosisData);  // 打印出来确认

  // 获取模型选择（默认使用 GPT）
  const modelType = diagnosisData?.model_type || "local";
  const currentLLM = getLLM("symptom_normalizer", modelType, diagnosisData);

  // 2. 安全性检查
  if (typeof diagnosisData !== "object" || diagnosisData === null) {
    throw new Error("Invalid diagnosis input: expected an object.");
  }
  if (!validateSchema("symptom_normalizer.input", diagnosisData)) {
    throw new Error("Invalid diagnosis input: schema validation failed.");
  }

  // 3. 构建诊断 prompt
  const symptoms = diagnosisData.symptoms?.length > 0
    ? diagnosisData.symptoms.join(",")
    : "无症状";

  const otherSymptoms = diagnosisData.other_symptoms || "无其他症状";

  const prompt = buildSymptomNormalizerPrompt(diagnosisData);

  // 4. LLM 推理
  const response = await currentLLM.invoke(prompt);

  // 5. 解析 LLM 返回内容
  let parsed;
  try {
    parsed = JSON.parse(response.content);
    console.log("第一步预处理输出成功：", parsed);
  } catch (e) {
    console.warn("⚠️ JSON 直接解析失败，尝试从响应中提取 JSON...");

    // 尝试从响应中提取 JSON（有时模型会在 JSON 前后加文字）
    const jsonMatch = response.content.match(/\{[\s\S]*?"optimized_symptoms"[\s\S]*?"rag_keywords"[\s\S]*?\}/);
    if (jsonMatch) {
      try {
        parsed = JSON.parse(jsonMatch[0]);
        console.log("✅ 从响应中提取 JSON 成功：", parsed);
      } catch (e2) {
        console.warn("⚠️ 提取的 JSON 仍然无法解析");
      }
    }

    // 如果仍然失败，构造一个基础的回退结果
    if (!parsed) {
      console.warn("⚠️ 使用回退模式，基于原始输入构造结果");
      const fallbackSymptoms = diagnosisData.symptoms?.length > 0
        ? diagnosisData.symptoms.join("、")
        : "";
      const fallbackOther = diagnosisData.other_symptoms || "";
      const bodyPart = diagnosisData.body_part || "全身";
      const severity = ["轻微", "较轻", "中等", "较重", "严重"][Math.min(Math.max((diagnosisData.severity || 3) - 1, 0), 4)];
      const durationMap = {
        "lessThan24Hours": "24小时内",
        "1To3Days": "1至3天",
        "4To7Days": "4至7天",
        "1To2Weeks": "1至2周",
        "moreThan2Weeks": "超过2周"
      };
      const duration = durationMap[diagnosisData.duration] || diagnosisData.duration || "不详";

      const combinedSymptoms = [fallbackSymptoms, fallbackOther].filter(s => s).join("，");

      parsed = {
        optimized_symptoms: `患者${bodyPart}部位出现${combinedSymptoms || "不适症状"}，症状程度${severity}，持续时间${duration}。`,
        rag_keywords: [
          bodyPart,
          ...diagnosisData.symptoms || [],
          ...(diagnosisData.other_symptoms ? diagnosisData.other_symptoms.split(/[,，、\s]+/).filter(s => s.length > 1) : []),
          severity,
          duration
        ].filter(k => k && k.length > 0)
      };
      console.log("📋 回退结果：", parsed);
    }
  }

  if (parsed && !validateSchema("symptom_normalizer.output", parsed)) { parsed = null; }
  parsed = normalizePreprocessOutput(parsed);
  if (!parsed) {
    console.warn("⚠️ 结构化预处理输出不符合格式，使用回退结果");
    const fallbackSymptoms = diagnosisData.symptoms?.length > 0
      ? diagnosisData.symptoms.join("、")
      : "";
    const fallbackOther = diagnosisData.other_symptoms || "";
    const bodyPart = diagnosisData.body_part || "全身";
    const severity = ["轻微", "较轻", "中等", "较重", "严重"][Math.min(Math.max((diagnosisData.severity || 3) - 1, 0), 4)];
    const durationMap = {
      "lessThan24Hours": "24小时内",
      "1To3Days": "1至3天",
      "4To7Days": "4至7天",
      "1To2Weeks": "1至2周",
      "moreThan2Weeks": "超过2周"
    };
    const duration = durationMap[diagnosisData.duration] || diagnosisData.duration || "不详";

    const combinedSymptoms = [fallbackSymptoms, fallbackOther].filter(s => s).join("，");

    parsed = {
      optimized_symptoms: `患者${bodyPart}部位出现${combinedSymptoms || "不适症状"}，症状程度${severity}，持续时间${duration}。`,
      rag_keywords: [
        bodyPart,
        ...diagnosisData.symptoms || [],
        ...(diagnosisData.other_symptoms ? diagnosisData.other_symptoms.split(/[,，、\s]+/).filter(s => s.length > 1) : []),
        severity,
        duration
      ].filter(k => k && k.length > 0)
    };
  }

  // 6. 返回给 LangGraph 的下一个节点（传递 modelType）
  return {
    messages: [
      new AIMessage({
        content: {
          diagnosisData: diagnosisData,
          optimizedSymptoms: parsed.optimized_symptoms,
          rag_keywords: parsed.rag_keywords,
          modelType: modelType,  // 传递模型选择到下一步
        }
      })
    ]
  };

}


// 对第一步的Critic评分
async function symptom_quality_grader(state) {
  const lastMessage = state.messages[state.messages.length - 1];
  const { diagnosisData, optimizedSymptoms, rag_keywords, modelType } = lastMessage.content;
  const currentLLM = getLLM("symptom_quality_grader", modelType, diagnosisData);

  const criticPrompt = buildSymptomQualityPrompt(optimizedSymptoms, rag_keywords);


  const maxTries = 5;
  let tries = 0;
  let finalOutput = {
    diagnosisData,
    optimizedSymptoms,
    rag_keywords,
  };
  // console.log("finaloutput:", finalOutput)
  let tmp_critic = {
    score: null,
    comment: null,
    isValid: null,
  }

  // 第一步：先对已有结果进行初步评分
  const firstCritic = await currentLLM.invoke(criticPrompt);

  let criticScore = normalizeCriticOutput(safeJSONParse(firstCritic.content, { score: 3, isValid: true, comment: "默认通过（小模型容错）" }, \"symptom_quality_grader.output\"));
  if (!criticScore) {
    console.warn("评分解析异常，使用默认通过:", firstCritic.content);
    criticScore = { score: 3, isValid: true, comment: "默认通过（小模型容错）" };
  }

  // console.log("critic_score_initial:", criticScore.score)
  // console.log("critic_comment_initial:", criticScore.comment)

  // criticScore.score = 2

  // 更新评分
  tmp_critic.score = criticScore.score;
  tmp_critic.comment = criticScore.comment;
  tmp_critic.isValid = criticScore.isValid;

  if (criticScore.isValid && criticScore.score >= 3) {
    console.log("第一步预处理输出审查合格、无需修改！改进建议为：", tmp_critic.comment, "改进评分为：", tmp_critic.score)
    return {
      messages: [
        new AIMessage({
          content: {
            diagnosisData,
            optimizedSymptoms,
            rag_keywords,
            modelType
          }
        })
      ]
    };
  }

  // 如果初步结果不合格，开始进行修正循环
  while (tries < maxTries) {
    tries++;

    const improvementPrompt = `
你是医学助手，请根据以下用户结构化症状信息，以及Critic给出的改进意见，重新生成优化的诊断信息（optimized_symptoms 和 rag_keywords）：
【用户结构化数据】
${JSON.stringify(diagnosisData, null, 2)}

【上一次的输出要求以及结果】
要求：
  1. 在用户提供的主要症状以及其他症状中，如果有模糊或通俗词语，请尝试优化为专业术语；此外，把你优化后的这两个症状描述融合在一起，一并存在optimized_symptoms中。
  2. 接下来我会进行RAG操作，请你挑选并提炼出关键的症状描述等关键信息短语，存在rag_keywords中。请注意至少一定要包含身体部位和症状描述这两个信息。
  3. 把1、2步骤得到的optimized_symptoms以及rag_keywords合并为一个json格式输出。

结果：
{
  "optimized_symptoms": "${finalOutput.optimizedSymptoms}",
  "rag_keywords": ${JSON.stringify(finalOutput.rag_keywords)}
}

【Critic的评分与建议】
评分：${tmp_critic.score}
建议：${tmp_critic.comment}
`;

    const improvementResponse = await currentLLM.invoke([
      new SystemMessage(
        `请重新生成诊断结果，确保满足专业性、格式规范、贴合用户症状等要求。注意请一定以如下格式输出，不能加上任何 Markdown 标签（如\`\`\`json）、提示性文字或换行符号：\n`+
        `{\n` +
        `  "optimized_symptoms": "...",\n` +
        `  "rag_keywords": ["...", "...", "...", ...]\n` +
        `}`),
      new HumanMessage(improvementPrompt)
    ]);
    // console.log("improvementResponse:", JSON.parse(improvementResponse.content))


    let parsed = normalizePreprocessOutput(safeJSONParse(improvementResponse.content, null, "symptom_normalizer.output"));
    if (!parsed) {
      console.warn("优化输出 JSON 解析失败，跳过此轮：", improvementResponse.content);
      continue;
    }
    finalOutput.optimizedSymptoms = parsed.optimized_symptoms;
    finalOutput.rag_keywords = parsed.rag_keywords || [];

    // 评分新输出
    console.log(JSON.stringify(parsed, null, 2))
    const secondCritic = await currentLLM.invoke(
      buildSymptomQualityPrompt(parsed.optimized_symptoms, parsed.rag_keywords)
    );

    // console.log("secondCritic:", secondCritic)
    let newScoreData = normalizeCriticOutput(safeJSONParse(secondCritic.content, { score: 3, isValid: true, comment: "默认通过" }, \"symptom_quality_grader.output\"));
    if (!newScoreData) {
      console.warn("二次评分解析失败，使用默认通过");
      newScoreData = { score: 3, isValid: true, comment: "默认通过" };
    }

    tmp_critic.score = newScoreData.score
    tmp_critic.comment = newScoreData.comment
    tmp_critic.isValid = newScoreData.isValid

    if (newScoreData.isValid && newScoreData.score >= 3) {
      finalOutput = {
        diagnosisData,
        optimizedSymptoms: parsed.optimized_symptoms,
        rag_keywords: parsed.rag_keywords
      };
      break;
    }
    else{
      console.log("第一步预处理诊断结果未合格，优化中...建议为：", tmp_critic.comment, "，打分为：", tmp_critic.score)
    }
  }

  if ( tmp_critic.score < 3) {
    const fallbackKeywords = [
      diagnosisData?.body_part || "",
      ...(diagnosisData?.symptoms || []),
      ...(diagnosisData?.other_symptoms ? String(diagnosisData.other_symptoms).split(/[,\s]+/).filter(Boolean) : [])
    ].filter(Boolean);
    finalOutput.optimizedSymptoms = finalOutput.optimizedSymptoms || (diagnosisData?.symptoms || []).join(", ") || "Symptom summary unavailable";
    finalOutput.rag_keywords = fallbackKeywords;
    console.log("第一步评判结果：经过多次尝试，仍未在初始第一步生成合格的诊断结构化数据。最终评分为：", tmp_critic.score );
  }
  else{
    console.log("第一步评判结果初始不合格，但经过多次尝试，已成功优化。最终评分为：", tmp_critic.score ,"最终输出为：", finalOutput);
  }

  return {
    messages: [
      new AIMessage({
        content: { ...finalOutput, modelType }
      })
    ]
  };
}


// 2. 基于检索的增强推理 (RAG - pgvector only)
async function fetchPgvectorRag(query, matchCount = 5, filter = null) {
  if (!supabaseClient) {
    throw new Error("Supabase client not configured for pgvector RAG.");
  }
  if (!process.env.OPENAI_API_KEY) {
    throw new Error("OPENAI_API_KEY missing for pgvector embeddings.");
  }

  const embeddings = new OpenAIEmbeddings({
    openAIApiKey: process.env.OPENAI_API_KEY,
    model: RAG_EMBEDDING_MODEL
  });
  const queryEmbedding = await embeddings.embedQuery(query);
  const { data, error } = await supabaseClient.rpc("match_rag_documents", {
    query_embedding: queryEmbedding,
    match_count: matchCount,
    filter
  });
  if (error) {
    throw new Error(`pgvector RPC error: ${error.message}`);
  }
  const rows = data || [];
  return rows.map((row, idx) => ({
    doc_id: row.metadata?.source || String(row.id || idx),
    score: Number(row.similarity || 0),
    snippet: String(row.content || "").slice(0, 500)
  }));
}

async function rag_retriever(state) {
  const lastMessage = state.messages[state.messages.length - 1];
  const { diagnosisData, optimizedSymptoms, rag_keywords, modelType } = lastMessage.content;

  if (!Array.isArray(rag_keywords) || rag_keywords.length === 0) {
    throw new Error("rag_keywords is empty; cannot run RAG retrieval.");
  }

  const query = rag_keywords.join(" ");
  const ragBackend = diagnosisData.rag_backend || RAG_BACKEND;
  if (ragBackend !== "pgvector") {
    throw new Error("Only pgvector RAG is supported. Set RAG_BACKEND=pgvector.");
  }

  const diagnosisCorpus = diagnosisData.rag_corpus || RAG_CORPUS_DIAGNOSIS;
  const filter = diagnosisCorpus ? { corpus: diagnosisCorpus } : null;
  const rag_docs = await fetchPgvectorRag(query, 5, filter);

  return {
    messages: [
      new SystemMessage({
        content: {
          diagnosisData,
          optimizedSymptoms,
          rag_docs,
          modelType,
        }
      })
    ]
  };
}

// 对第二步提取的RAG置信度审核
async function rag_relevance_grader(state) {
  const lastMessage = state.messages[state.messages.length - 1];
  const { diagnosisData, optimizedSymptoms, rag_docs, modelType } = lastMessage.content;
  const currentLLM = getLLM("rag_relevance_grader", modelType, diagnosisData);

  const prompt = buildRagRelevancePrompt(optimizedSymptoms, rag_docs);
  const response = await currentLLM.invoke(prompt);

  let parsed = normalizeRagCheckOutput(
    safeJSONParse(
      response.content,
      { ragScore: 3, ragComment: "default pass" },
      "rag_relevance_grader.output"
    )
  );
  if (!parsed) {
    parsed = { ragScore: 3, ragComment: "default pass" };
  }

  return {
    messages: [
      new AIMessage({
        content: {
          diagnosisData,
          optimizedSymptoms,
          rag_docs,
          ragScore: parsed.ragScore,
          ragComment: parsed.ragComment,
          modelType,
        }
      })
    ]
  };
}


// // 5. 诊断审核
// async function initialDiagnosis(state) {
//   const lastMessage = state.messages[state.messages.length - 1];
//   const { diagnosisData, optimizedSymptoms, ragContext, ragScore, ragComment } = lastMessage.content;

//   const prompt_diagnos = [
//     new SystemMessage(
//       `你是一位医学推理助手，后续用户会发给你相关的症状、症状相关医学背景等信息并给出你任务指示。请你严格按照以下JSON格式返回输出：\n` +
//       `{\n` +
//       `  "results": [\n` +
//       `    { "condition": "疾病名称1", "probability": 0.xx, "description": "描述1" },\n` +
//       `    { "condition": "疾病名称2", "probability": 0.yy, "description": "描述2" },\n` +
//       `    { "condition": "疾病名称3", "probability": 0.zz, "description": "描述3" }\n` +
//       `  ],\n` +
//       `  "recommendations": ["建议1", "建议2", "建议3"],\n` +
//       `  "recomm_short": ["简化的建议1", ..., "简化的建议10"]\n` +
//       `}`
//     ),
//     new HumanMessage(
//       `一、这是用户的患病症状以及该症状相关的背景医学知识等信息，请你记住。其中，1）【用户患病症状】给出了用户自己描述的患病症状；` +
//       ` 2）【RAG医学背景】给出了症状相关的、可能会帮助到你的医学背景知识；` +
//       ` 3）【RAG与病症相关度评分】以评分的形式给出了【RAG医学背景】中提供的RAG背景知识与用户描述病症的相关程度；` +
//       ` 4）【RAG参考建议】则是给你的RAG参考建议，你可以根据这个来判断【RAG医学背景】提供给你的信息会在多大程度上影响你的最终诊断结果输出：\n` +
//       `【用户患病症状】\n${optimizedSymptoms}\n\n` +
//       `【RAG医学背景】\n${ragContext}\n\n` +
//       `【RAG与病症相关度评分】\n${ragScore}/5\n\n` +
//       `【RAG参考建议】：${ragComment}\n\n` +
//       `二、请你根据上述信息，完成以下任务。注意：所有返回必须为中文。：\n` +
//       `在你严格参考过上述提供的【用户患病症状】以及【RAG医学背景】等信息后，缜密的分析出三组可能的疾病名称 (condition)、对应的患病概率 (probability) 以及疾病描述 (description)，` +
//       `并提供三个健康建议 (recommendations)以及十个简化版建议 (recomm_short)，其中每个健康建议至少要有15字，简化版建议不超过10个字。` 
//     )
//   ];

//   const response = await llm.invoke(prompt_diagnos);

//   let parsedResult;

async function diagnosis_generator(state) {
  const lastMessage = state.messages[state.messages.length - 1];
  const { diagnosisData, optimizedSymptoms, rag_docs, ragScore, ragComment, modelType } = lastMessage.content;
  const currentLLM = getLLM("diagnosis_generator", modelType, diagnosisData);

  if (typeof ragScore === "number" && ragScore < 2) {
    const fallback = buildFallbackDiagnosis();
    return {
      messages: [
        new AIMessage({
          content: {
            diagnosisData: fallback,
            optimizedSymptoms,
            rag_docs,
            ragScore,
            ragComment,
            modelType,
          }
        })
      ]
    };
  }

  const prompt = buildDiagnosisPrompt(optimizedSymptoms, rag_docs);
  const response = await currentLLM.invoke(prompt);

  let parsedResult = normalizeDiagnosisOutput(
    safeJSONParse(response.content, null, "diagnosis_generator.output")
  );
  if (!parsedResult) {
    parsedResult = buildFallbackDiagnosis();
  }

  return {
    messages: [
      new AIMessage({
        content: {
          diagnosisData: parsedResult,
          optimizedSymptoms,
          rag_docs,
          ragScore,
          ragComment,
          modelType,
        }
      })
    ]
  };
}


async function drug_evidence_grader(state) {
  const lastMessage = state.messages[state.messages.length - 1];
  const { diagnosisData, optimizedSymptoms, rag_docs, modelType } = lastMessage.content;
  const currentLLM = getLLM("drug_evidence_grader", modelType, diagnosisData);

  const prompt = buildDrugEvidencePrompt(diagnosisData, rag_docs);
  const response = await currentLLM.invoke(prompt);

  let scoreMeta = normalizeDiagnosisScoreOutput(
    safeJSONParse(response.content, { diagnosisScore: 3, diagnosisComment: "default pass" }, "drug_evidence_grader.output")
  );
  if (!scoreMeta) {
    scoreMeta = { diagnosisScore: 3, diagnosisComment: "default pass" };
  }

  return {
    messages: [
      new AIMessage({
        content: {
          diagnosisData,
          optimizedSymptoms,
          rag_docs,
          diagnosisScore: scoreMeta.diagnosisScore,
          diagnosisComment: scoreMeta.diagnosisComment,
          modelType,
        }
      })
    ]
  };
}



async function drug_recommender(state) {
  const lastMessage = state.messages[state.messages.length - 1];
  const { diagnosisData, optimizedSymptoms, rag_docs, modelType } = lastMessage.content;
  const currentLLM = getLLM("drug_recommender", modelType, diagnosisData);

  const drugsOutput = [];
  const drugCorpus = diagnosisData?.drug_rag_corpus || RAG_CORPUS_DRUG;
  let drug_rag_docs = null;
  try {
    const drugQuery = Array.isArray(diagnosisData?.results)
      ? diagnosisData.results.map(r => r.condition).filter(Boolean).join(" ")
      : "";
    if (drugQuery) {
      const drugFilter = drugCorpus ? { corpus: drugCorpus } : null;
      drug_rag_docs = await fetchPgvectorRag(drugQuery, 5, drugFilter);
    }
  } catch (error) {
    console.warn("drug_rag pgvector retrieval failed:", error.message);
    drug_rag_docs = null;
  }

  for (const result of diagnosisData.results) {
    const fallbackContext = rag_docs ? rag_docs.map(d => d.snippet).join("\n") : "";
    const drugContextDocs = drug_rag_docs ? drug_rag_docs.map(d => d.snippet).join("\n") : fallbackContext;
    const drugRagContext = result.drugRagContext || drugContextDocs || "";
    const drugRagScore = result.drugRagScore ?? 3;
    const drugRagComment = result.drugRagComment || "默认通过";
    const condition = result.condition;

    const drugPrompt = buildDrugRecommendPrompt(condition, drugRagContext);

    const response = await currentLLM.invoke(drugPrompt);

    let parsed = normalizeDrugOutput(safeJSONParse(response.content, null, "drug_recommender.output"));
    if (!parsed) {
      console.warn(`"${condition}" 的药物建议解析失败，使用默认建议`);
      parsed = {
        drugs: [{
          condition: condition,
          recommended_drugs: [
            { name: "请咨询医生", usage: "根据具体情况用药", notes: "需专业医生指导" }
          ]
        }]
      };
    }

    drugsOutput.push(...parsed.drugs);
  }

  // === 补充总结性建议 ===
  const summaryPrompt = [
    new SystemMessage("你是一个医学总结助手，请根据每个疾病的药物建议总结整体治疗方向，用一句中文话概括。"),
    new HumanMessage(`以下是用户每种疾病的用药推荐情况，请你总结整体建议：
${drugsOutput.map(d => `【${d.condition}】\n${d.recommended_drugs.map(r => `- ${r.name}：${r.usage}`).join("\n")}`).join("\n\n")}`)
  ];

  const summaryResp = await currentLLM.invoke(summaryPrompt);
  const summaryText = summaryResp.content.trim();

  // === 合并最终结果并插入到 diagnosisData 中 ===
  const drugRecommendations = drugsOutput.map(d =>
    `【${d.condition} 用药建议】\n` +
    d.recommended_drugs.map(drug => `- ${drug.name}：${drug.usage}（${drug.notes}）`).join("\n")
  );

  // 添加用药建议
  diagnosisData.recommendations.push(...drugRecommendations);
  diagnosisData.recommendations.push(`【总结建议】\n${summaryText}`);

  console.log("第四步加入用药推荐后的最终诊断建议为:", diagnosisData.recommendations)
  return {
    messages: [
      new AIMessage({
        content: {
          diagnosisData: diagnosisData,
          optimizedSymptoms,
          modelType,
        }
      })
    ]
  };
}


async function output_formatter(state) {
  const lastMessage = state.messages[state.messages.length - 1];
  const { diagnosisData, optimizedSymptoms, modelType } = lastMessage.content;

  const normalized = normalizeDiagnosisOutput(diagnosisData, { allowExtraRecommendations: true }) || buildFallbackDiagnosis();

  return {
    messages: [
      new AIMessage({
        content: {
          diagnosisData: normalized,
          optimizedSymptoms,
          modelType,
        }
      })
    ]
  };
}


// -------- 创建图 --------

// 使用 StateGraph 创建工作流图
const diagnosisGraph = new StateGraph(MessagesAnnotation)
  .addNode("symptom_normalizer", symptom_normalizer)  // 第一步：预处理和初步推测
  .addEdge("__start__", "symptom_normalizer")
  .addNode("symptom_quality_grader", symptom_quality_grader)  
  .addEdge("symptom_normalizer", "symptom_quality_grader") 
  .addNode("rag_retriever", rag_retriever)  
  .addEdge("symptom_quality_grader", "rag_retriever")
  .addNode("rag_relevance_grader", rag_relevance_grader)  
  .addEdge("rag_retriever", "rag_relevance_grader")
  .addNode("diagnosis_generator", diagnosis_generator)
  .addEdge("rag_relevance_grader", "diagnosis_generator")
  .addNode("drug_evidence_grader", drug_evidence_grader)
  .addEdge("diagnosis_generator", "drug_evidence_grader")
  .addNode("drug_recommender", drug_recommender)
  .addEdge("drug_evidence_grader", "drug_recommender")
  .addNode("output_formatter", output_formatter)  
  .addEdge("drug_recommender", "output_formatter")
  .addEdge("output_formatter", "__end__"); // 最终返回结果，结束节点

// // 编译并输出最终工作流
const app = await diagnosisGraph.compile();

export { app };


// // 示例：调用图并输出结果
// const initialState = {
//   messages: [new HumanMessage("我有些头痛，持续了三天")],
//   diagnosisData: {
//     user_id: "12345",
//     body_part: "head",
//     symptoms: ["headache"],
//     other_symptoms: "nausea",
//     severity: 3,
//     duration: "3 days",
//   },
// };

// const finalState = await app.invoke(initialState);
// console.log(finalState.result);
