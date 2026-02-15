<template>
  <div class="diagnostic-container">
    <!-- 返回首页按钮 -->
    <div class="back-to-home mb-4">
      <router-link to="/" class="btn btn-secondary">
        <i class="fas fa-arrow-left"></i> 返回首页
      </router-link>
    </div>

    <!-- 头部 -->
    <div class="diagnostic-header">
      <h1 class="text-center mb-4">AI 智能诊断工具</h1>
      <p class="text-center mb-5">
        请提供您的症状信息，我们的AI系统将为您分析可能的健康状况。
        <strong>注意：这只是初步参考，严重症状请立即就医。</strong>
      </p>
    </div>

    <!-- 步骤指示器 -->
    <div class="steps-container mb-5">
      <div class="step" :class="{ active: step >= 1, completed: step > 1 }">
        <div class="step-number">1</div>
        <div class="step-label">选择身体部位</div>
      </div>
      <div class="step-line"></div>
      <div class="step" :class="{ active: step >= 2, completed: step > 2 }">
        <div class="step-number">2</div>
        <div class="step-label">描述症状</div>
      </div>
      <div class="step-line"></div>
      <div class="step" :class="{ active: step >= 3, completed: step > 3 }">
        <div class="step-number">3</div>
        <div class="step-label">确认预处理</div>
      </div>
      <div class="step-line"></div>
      <div class="step" :class="{ active: step >= 4, completed: step > 4 }">
        <div class="step-number">4</div>
        <div class="step-label">分析中</div>
      </div>
      <div class="step-line"></div>
      <div class="step" :class="{ active: step >= 5 }">
        <div class="step-number">5</div>
        <div class="step-label">诊断结果</div>
      </div>
    </div>
    
    <!-- 主内容区域 -->
    <div class="diagnostic-content">
      <!-- 步骤1: 选择身体部位 -->
      <div v-if="step === 1" class="step-content step1-content">
        <h2 class="mb-4">请选择您感到不适的身体部位</h2>
        
        <div class="body-parts-grid">
          <!-- 头部 -->
          <div class="body-part-card" 
               :class="{ active: selectedBodyPart === 'head' }"
               @click="selectBodyPart('head')">
            <i class="fas fa-brain fa-3x"></i>
            <div class="body-part-name">头部</div>
          </div>
          
          <!-- 胸部 -->
          <div class="body-part-card" 
               :class="{ active: selectedBodyPart === 'chest' }"
               @click="selectBodyPart('chest')">
            <i class="fas fa-heartbeat fa-3x"></i>
            <div class="body-part-name">胸部</div>
          </div>
          
          <!-- 腹部 -->
          <div class="body-part-card" 
               :class="{ active: selectedBodyPart === 'abdomen' }"
               @click="selectBodyPart('abdomen')">
            <i class="fas fa-apple-alt fa-3x"></i>
            <div class="body-part-name">腹部</div>
          </div>
          
          <!-- 背部 -->
          <div class="body-part-card" 
               :class="{ active: selectedBodyPart === 'back' }"
               @click="selectBodyPart('back')">
            <i class="fas fa-child fa-3x"></i>
            <div class="body-part-name">背部</div>
          </div>
          
          <!-- 手臂 -->
          <div class="body-part-card" 
               :class="{ active: selectedBodyPart === 'arms' }"
               @click="selectBodyPart('arms')">
            <i class="fas fa-hand fa-3x"></i>
            <div class="body-part-name">手臂</div>
          </div>
          
          <!-- 腿部 -->
          <div class="body-part-card" 
               :class="{ active: selectedBodyPart === 'legs' }"
               @click="selectBodyPart('legs')">
            <i class="fas fa-socks fa-3x"></i>
            <div class="body-part-name">腿部</div>
          </div>
          
          <!-- 皮肤 -->
          <div class="body-part-card" 
               :class="{ active: selectedBodyPart === 'skin' }"
               @click="selectBodyPart('skin')">
            <i class="fas fa-allergies fa-3x"></i>
            <div class="body-part-name">皮肤</div>
          </div>
          
          <!-- 全身 -->
          <div class="body-part-card" 
               :class="{ active: selectedBodyPart === 'general' }"
               @click="selectBodyPart('general')">
            <i class="fas fa-user fa-3x"></i>
            <div class="body-part-name">全身症状</div>
          </div>
        </div>
        
        <!-- 下一步按钮 -->
        <div class="mt-5 text-center">
          <button class="btn btn-primary" @click="nextStep" :disabled="!selectedBodyPart">
            下一步 <i class="fas fa-arrow-right"></i>
          </button>
        </div>
      </div>

      <!-- 步骤2: 描述症状 -->
      <div v-if="step === 2" class="step-content step2-content">
        <h2 class="mb-4">请描述您的症状</h2>
        
        <!-- 常见症状选择 -->
        <div class="symptoms-section mb-4">
          <h3 class="mb-3">{{ selectedBodyPart }}部位常见症状:</h3>
          <div class="error-message" v-if="errors.symptoms">{{ errors.symptoms }}</div>
          
          <div class="symptoms-grid">
            <div v-for="symptom in filteredSymptoms" :key="symptom.id"
                 class="symptom-card" 
                 :class="{ active: selectedSymptoms.includes(symptom.id) }"
                 @click="toggleSymptom(symptom.id)">
              <div class="symptom-name">{{ symptom.name }}</div>
              <div class="symptom-desc" v-if="symptom.description">{{ symptom.description }}</div>
              <!-- <div class="symptom-desc" v-else>{{ getDefaultDescription(symptom.name) }}</div> -->
              <div class="symptom-desc" v-else>{{null}}</div>
            </div>
          </div>
        </div>
        
        <!-- 其他症状 -->
        <div class="other-symptoms-section mb-4">
          <h3 class="mb-3">其他症状或细节 (选填):</h3>
          <div class="textarea-container">
            <textarea v-model="otherSymptoms" class="form-control custom-textarea" 
                      placeholder="请描述其他症状或提供更多细节..."></textarea>
          </div>
        </div>
        
        <!-- 症状信息区域 -->
        <div class="symptoms-details-container">
          <!-- 症状严重程度 -->
          <div class="severity-section mb-5">
            <h3 class="mb-4 section-heading">症状严重程度:</h3>
            <div class="severity-slider">
              <input type="range" min="1" max="5" v-model.number="severityLevel" class="slider">
              <div class="severity-labels">
                <span>轻微</span>
                <span>一般</span>
                <span>严重</span>
              </div>
            </div>
          </div>
          
          <!-- 持续时间 -->
          <div class="duration-section mb-5" style="margin-top: 60px;">
            <h3 class="mb-4 section-heading">症状持续时间:</h3>
            <div class="error-message" v-if="errors.duration">{{ errors.duration }}</div>
            
            <div class="custom-select">
              <select v-model="duration" class="select-dropdown">
                <option value="" disabled selected>请选择持续时间</option>
                <option v-for="option in durationOptions" :key="option.id" :value="option.id">
                  {{ option.label }}
                </option>
              </select>
            </div>
          </div>
          
          <!-- 模型档位与高级覆盖 -->
          <div class="model-section mb-5" style="margin-top: 60px;">
            <h3 class="mb-4 section-heading">选择模型档位:</h3>

            <div class="custom-select">
              <select v-model="selectedProfileId" class="select-dropdown">
                <option v-for="profile in modelProfiles" :key="profile.id" :value="profile.id">
                  {{ profile.name }} - {{ profile.description }}
                </option>
              </select>
            </div>
            <div class="text-sm text-gray-500 mt-2">
              当前档位将决定各 Agent 的默认模型配置。
            </div>

            <!-- 混合系列才显示 GPT 覆盖选项 -->
            <div v-if="selectedProfileId === 'hybrid'" class="mt-4 space-y-4">
              <div class="bg-blue-50 rounded-lg p-4">
                <div class="font-medium text-gray-700 mb-3">选择要使用 GPT 云端模型的 Agent：</div>
                <div v-for="agent in overrideAgents" :key="agent.id" class="flex items-center gap-3 mb-3">
                  <label class="flex items-center gap-2 min-w-[120px]">
                    <input type="checkbox" v-model="agentOverrides[agent.id].useGpt" class="form-checkbox" />
                    <span class="text-gray-700">{{ agent.name }}</span>
                  </label>
                  <select v-if="agentOverrides[agent.id].useGpt" v-model="agentOverrides[agent.id].model_name" class="select-dropdown" style="max-width: 200px;">
                    <option value="gpt-5-mini">gpt-5-mini（快速）</option>
                    <option value="gpt-5.1">gpt-5.1（高质量）</option>
                    <option value="gpt-4.1">gpt-4.1（经典）</option>
                  </select>
                </div>
                <p class="text-xs text-gray-500 mt-2">未勾选的 Agent 将继续使用本地 Qwen 模型。</p>
              </div>
            </div>
          </div>
        </div>
        
        <!-- 导航按钮 -->
        <div class="step-navigation">
          <button class="btn btn-secondary" @click="step = 1">
            <i class="fas fa-arrow-left"></i> 上一步
          </button>
          <button @click="proceedToAnalysis" class="btn btn-primary">
            开始分析 <i class="fas fa-arrow-right"></i>
          </button>
        </div>
      </div>

      <!-- 步骤3: 确认 AI 预处理结果 -->
      <div v-if="step === 3" class="step-content step3-review">
        <h2 class="mb-2">确认 AI 预处理结果</h2>
        <p class="text-gray-500 mb-4">
          AI 已将您的症状描述标准化，并提取了用于医学文献检索的关键词。请检查是否准确，如有不符可直接修改。
        </p>

        <!-- 预处理加载中 -->
        <div v-if="preprocessLoading" class="text-center py-8">
          <div class="spinner"></div>
          <p class="mt-4 text-gray-500">AI 正在整理您的症状描述...</p>
        </div>

        <div v-else>
          <!-- optimized_symptoms -->
          <div class="review-field mb-5">
            <label class="review-label">
              标准化症状描述
              <span class="review-hint">（AI 将您的口语描述转换为结构化的医学描述，后续所有诊断环节都基于此文本）</span>
            </label>
            <textarea v-model="reviewOptimizedSymptoms" class="review-textarea" rows="4"></textarea>
          </div>

          <!-- rag_keywords -->
          <div class="review-field mb-5">
            <label class="review-label">
              检索关键词
              <span class="review-hint">（系统将用这些关键词在医学知识库中查找相关资料，辅助诊断判断）</span>
            </label>
            <div class="review-keywords">
              <div v-for="(kw, idx) in reviewRagKeywords" :key="idx" class="keyword-chip">
                <input v-model="reviewRagKeywords[idx]" class="keyword-input" />
                <button class="keyword-remove" @click="reviewRagKeywords.splice(idx, 1)">&times;</button>
              </div>
              <button class="keyword-add" @click="reviewRagKeywords.push('')">+ 添加关键词</button>
            </div>
          </div>
        </div>

        <!-- 导航按钮 -->
        <div class="step-navigation">
          <button class="btn btn-secondary" @click="step = 2">
            <i class="fas fa-arrow-left"></i> 返回修改
          </button>
          <button class="btn btn-primary" @click="confirmAndStartAnalysis" :disabled="preprocessLoading">
            确认并开始诊断 <i class="fas fa-arrow-right"></i>
          </button>
        </div>
      </div>

      <!-- 步骤4: 分析中（实时进度） -->
      <div v-if="step === 4" class="step-content step4-analysis">
        <div class="analysis-loading text-center">
          <div class="spinner"></div>
          <h2 class="mt-4">AI诊断系统正在分析您的症状...</h2>
          <p class="text-gray-500 mb-6">Pipeline 实时进度</p>
        </div>
        <!-- 进度条 -->
        <div class="pipeline-progress">
          <div class="progress-bar-container mb-4">
            <div class="progress-bar-bg">
              <div class="progress-bar-fill" :style="{ width: progressPercent + '%' }"></div>
            </div>
            <span class="progress-text">{{ progressPercent }}%</span>
          </div>
          <!-- 步骤列表 -->
          <div class="progress-steps">
            <div v-for="(pStep, idx) in progressSteps" :key="idx"
                 class="progress-step"
                 :class="{ done: true }">
              <div class="step-icon">&#10003;</div>
              <div class="step-info">
                <div class="step-label">{{ pStep.label }}</div>
                <div class="step-detail" v-if="pStep.detail">{{ pStep.detail }}</div>
              </div>
            </div>
            <!-- 当前执行中的步骤 -->
            <div v-if="currentStepLabel" class="progress-step active">
              <div class="step-icon spinning">&#9881;</div>
              <div class="step-info">
                <div class="step-label">{{ currentStepLabel }}</div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 步骤5: 诊断结果 -->
      <div v-if="step === 5" class="step-content step5-content">
        <div class="result-header">
          <h2 class="mb-2">诊断结果分析</h2>
          <p class="result-time">生成时间: {{ formattedDate }}</p>
        </div>
        
        <!-- 免责声明 -->
        <div class="disclaimer mb-4">
          <i class="fas fa-exclamation-triangle"></i>
          <span>
            免责声明: 此结果仅供参考，不构成医疗建议。如有严重症状，请立即就医。
          </span>
        </div>
        
        <!-- 结果图表 -->
        <div class="result-chart mb-5">
          <h3 class="mb-3">可能的病症分析:</h3>
          <div ref="chartContainer" class="chart-container"></div>
        </div>
        
        <!-- 详细结果 -->
        <div class="detailed-results mb-5">
          <h3 class="mb-3">详细分析:</h3>
          
          <div class="results-grid">
            <div v-for="(result, index) in diagnosisResults" :key="index" class="result-card">
              <div class="result-header">
                <h4>{{ result.condition }}</h4>
                <div class="probability">
                  概率: {{ (result.probability * 100).toFixed(1) }}%
                </div>
              </div>
              <div class="result-description">
                {{ result.description }}
              </div>
            </div>
          </div>
        </div>
        
        <!-- AI建议词云 -->
        <div class="ai-recommendations mb-5" v-if="diagnosisRecomm_short.length > 0">
          <h3 class="mb-3">AI健康建议:</h3>
          <div ref="wordCloudContainer" class="word-cloud-container"></div>
        </div>
        
        <!-- 建议 -->
        <div class="recommendations mb-5">
          <h3 class="mb-3">建议:</h3>
          <ul class="recommendation-list">
            <li v-for="(item, index) in diagnosisRecomm" :key="index">{{ item }}</li>
          </ul>
        </div>

        <!-- 各 Agent 使用的模型 -->
        <div v-if="agentModelsMap && Object.keys(agentModelsMap).length > 0" class="agent-models-section mb-5">
          <h3 class="mb-3">Pipeline 模型配置:</h3>
          <div class="agent-models-grid">
            <div v-for="(info, agent) in agentModelsMap" :key="agent" class="agent-model-tag">
              <span class="agent-name">{{ AGENT_LABELS[agent] || agent }}</span>
              <span class="model-badge" :class="info.type === 'gpt' ? 'badge-gpt' : 'badge-local'">
                {{ info.model }}
              </span>
            </div>
          </div>
        </div>

        <!-- 导航按钮 -->
        <div class="step-navigation">
          <button class="btn btn-secondary" @click="step = 2">
            <i class="fas fa-arrow-left"></i> 返回修改
          </button>
          <button class="btn btn-primary" @click="startNewDiagnosis">
            <i class="fas fa-sync"></i> 开始新的诊断
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, reactive, computed, onMounted, watch } from 'vue';
import { useRouter } from 'vue-router';
import { symptomsApi, diagnosesApi } from '@/utils/api';
import { COMMON_SYMPTOMS, SEVERITY_LEVELS, DURATION_OPTIONS, MODEL_PROFILES } from '@/utils/constants';
import { useUserStore } from '@/store/userStore';
import * as echarts from 'echarts';
import cloud from 'd3-cloud';
import * as d3 from 'd3';

export default {
  name: 'DiagnosticTool',
  
  setup() {
    // 用户数据
    const userStore = useUserStore();
    const router = useRouter();
    
    // 身体部位选择
    const selectedBodyPart = ref('');
    
    // 症状相关
    const symptoms = ref([]);
    const filteredSymptoms = ref([]);
    const selectedSymptoms = ref([]);
    const otherSymptoms = ref('');
    const severityLevel = ref(3);
    const duration = ref('');
    const durationOptions = DURATION_OPTIONS;
    
    // 模型档位与高级覆盖
    const modelProfiles = MODEL_PROFILES;
    const selectedProfileId = ref(modelProfiles[0]?.id || 'balanced');
    const overrideAgents = [
      { id: 'symptom_normalizer', name: '症状规范化' },
      { id: 'symptom_quality_grader', name: '症状质量评分' },
      { id: 'rag_relevance_grader', name: 'RAG 相关度评分' },
      { id: 'diagnosis_generator', name: '诊断生成' },
      { id: 'drug_evidence_grader', name: '用药证据评分' },
      { id: 'drug_recommender', name: '用药推荐' },
      { id: 'diagnosis_reviewer', name: '诊断概率校验' },
      { id: 'output_formatter', name: '输出格式化' },
    ];
    const agentOverrides = reactive({
      symptom_normalizer: { useGpt: false, model_name: 'gpt-5-mini' },
      symptom_quality_grader: { useGpt: false, model_name: 'gpt-5-mini' },
      rag_relevance_grader: { useGpt: false, model_name: 'gpt-5-mini' },
      diagnosis_generator: { useGpt: false, model_name: 'gpt-5-mini' },
      drug_evidence_grader: { useGpt: false, model_name: 'gpt-5-mini' },
      drug_recommender: { useGpt: false, model_name: 'gpt-5-mini' },
      diagnosis_reviewer: { useGpt: false, model_name: 'gpt-5-mini' },
      output_formatter: { useGpt: false, model_name: 'gpt-5-mini' },
    });
    
    // 错误信息
    const errors = ref({
      symptoms: '',
      duration: ''
    });
    
    // Agent 中文名映射
    const AGENT_LABELS = {
      symptom_normalizer: '症状规范化',
      symptom_quality_grader: '质量评分',
      rag_retriever: 'RAG 检索',
      rag_relevance_grader: '相关度评分',
      diagnosis_generator: '诊断生成',
      drug_evidence_grader: '用药证据评分',
      drug_recommender: '用药推荐',
      diagnosis_reviewer: '概率校验',
      output_formatter: '输出格式化',
    };

    // 诊断结果
    const diagnosisResults = ref([]);
    const diagnosisRecomm = ref([]);
    const diagnosisRecomm_short = ref([]);
    const formattedDate = ref('');
    const agentModelsMap = ref({});

    // 预处理确认步骤（step 3）
    const preprocessLoading = ref(false);
    const reviewOptimizedSymptoms = ref('');
    const reviewRagKeywords = ref([]);

    // Pipeline 实时进度
    const progressSteps = ref([]);   // 已完成的步骤 [{ label, detail }]
    const currentStepLabel = ref(''); // 当前正在执行的步骤名
    const progressPercent = computed(() => {
      const total = 9; // pipeline 总节点数
      const done = progressSteps.value.length;
      return Math.min(Math.round((done / total) * 100), 100);
    });
    
    // 步骤控制
    const step = ref(1);
    
    // 获取症状数据
    const fetchSymptoms = async () => {
      try {
        const response = await symptomsApi.getAll();
        symptoms.value = response.data;
      } catch (error) {
        console.error('获取症状数据错误:', error);
      }
    };
    
    // 获取特定身体部位的症状
    const fetchBodyPartSymptoms = async (bodyPart) => {
      try {
        const response = await symptomsApi.getByBodyPart(bodyPart);
        console.log(response.data);
        filteredSymptoms.value = response.data;
      } catch (error) {
        console.error('获取身体部位症状错误:', error);
        // 回退到前端筛选
        filteredSymptoms.value = symptoms.value.filter(
          s => s.body_part === bodyPart
        );
      }
    };
    
    // 监听选择的身体部位变化
    watch(selectedBodyPart, (newValue) => {
      if (newValue) {
        fetchBodyPartSymptoms(newValue);
      }
    });
    
    // 初始化图表
    const initChart = () => {
      if (!diagnosisResults.value.length) return;
      
      const chartDom = chartContainer.value;
      if (!chartDom) return;
      
      const myChart = echarts.init(chartDom);
      const option = {
        tooltip: {
          trigger: 'item',
          formatter: '{b}: {c} ({d}%)'
        },
        legend: {
          orient: 'vertical',
          left: 'left',
          data: diagnosisResults.value.map(r => r.condition)
        },
        series: [
          {
            name: '可能性',
            type: 'pie',
            radius: '50%',
            data: diagnosisResults.value.map(r => ({
              value: (r.probability * 100).toFixed(1),
              name: r.condition
            })),
            emphasis: {
              itemStyle: {
                shadowBlur: 10,
                shadowOffsetX: 0,
                shadowColor: 'rgba(0, 0, 0, 0.5)'
              }
            }
          }
        ]
      };
      
      option && myChart.setOption(option);
      
      chart = myChart;
    };
    
     // 初始化词云图图表
    const initWordCloud = () => {
  const container = wordCloudContainer.value;
  if (!container || !diagnosisRecomm_short.value.length) return;

  container.innerHTML = ''; // 清空原词云

  const width = container.clientWidth;
  const height = 300;

  const svg = d3.select(container)
    .append('svg')
    .attr('width', width)
    .attr('height', height)
    .append('g')
    .attr('transform', `translate(${width / 2}, ${height / 2})`);

  const colors = ['#3273dc', '#00d1b2', '#48bb78', '#4c51bf', '#f56565'];

  cloud()
    .size([width, height])
    .words(diagnosisRecomm_short.value.map((text, i) => ({
      text,
      size: 16 + Math.random() * 14,
      color: colors[i % colors.length]
    })))
    .padding(8)
    .rotate(() => [-30, -15, 0, 15, 30][Math.floor(Math.random() * 5)])
    .spiral('rectangular')
    .font('sans-serif')
    .fontWeight('bold')
    .fontSize(d => d.size)
    .on('end', words => {
      svg.selectAll('text')
        .data(words)
        .enter()
        .append('text')
        .style('font-size', d => `${d.size}px`)
        .style('fill', d => d.color)
        .style('font-weight', 'bold')
        .attr('text-anchor', 'middle')
        .attr('transform', d => `translate(${d.x}, ${d.y}) rotate(${d.rotate})`)
        .text(d => d.text)
        // hover 效果
  .on('mouseover', function (event, d) {
    d3.select(this)
      .transition()
      .duration(200)
      .style('fill', '#ff6b6b')
      .style('font-size', `${d.size * 1.2}px`)
      .style('filter', 'drop-shadow(0 0 2px #999)');
  })
  .on('mouseout', function (event, d) {
    d3.select(this)
      .transition()
      .duration(200)
      .style('fill', d.color)
      .style('font-size', `${d.size}px`)
      .style('filter', 'none');
  });
    })

    .start();
};
    
    let chart = null;
    let wordCloud = null;
    const chartContainer = ref(null);
    const wordCloudContainer = ref(null);
    
    // 选择身体部位
    const selectBodyPart = (partId) => {
      selectedBodyPart.value = partId;
      // 清除之前选择的症状
      selectedSymptoms.value = [];
    };
    
    // 切换症状选择
    const toggleSymptom = (symptomId) => {
      const index = selectedSymptoms.value.indexOf(symptomId);
      if (index === -1) {
        selectedSymptoms.value.push(symptomId);
      } else {
        selectedSymptoms.value.splice(index, 1);
      }
    };
    
    // 验证表单
    const validateForm = () => {
      let isValid = true;
      errors.value.symptoms = '';
      errors.value.duration = '';
      
      if (selectedSymptoms.value.length === 0 && otherSymptoms.value.length === 0) {
        errors.value.symptoms = '请至少选择一个症状';
        isValid = false;
      }
      
      if (!duration.value) {
        errors.value.duration = '请选择症状持续时间';
        isValid = false;
      }
      
      return isValid;
    };
    
    // 下一步
    const nextStep = () => {
      step.value++;
    };
    
    const buildAgentOverridesPayload = () => {
      if (selectedProfileId.value !== 'hybrid') return {};
      const payload = {};
      overrideAgents.forEach(agent => {
        const cfg = agentOverrides[agent.id];
        if (!cfg || !cfg.useGpt) return;
        payload[agent.id] = {
          model_type: 'gpt',
          model_name: cfg.model_name || 'gpt-5-mini'
        };
      });
      return payload;
    };

    // 构建通用诊断数据
    const buildDiagnosisPayload = () => {
      const overridePayload = buildAgentOverridesPayload();
      const symptomNames = selectedSymptoms.value.map(id => {
        const s = symptoms.value.find(sym => sym.id === id);
        return s ? s.name : id;
      });
      return {
        user_id: userStore.userId,
        body_part: selectedBodyPart.value,
        symptoms: selectedSymptoms.value,
        symptom_names: symptomNames,
        other_symptoms: otherSymptoms.value,
        severity: severityLevel.value,
        duration: duration.value,
        model_profile_id: selectedProfileId.value,
        agent_overrides: overridePayload
      };
    };

    // 步骤 2 → 3：预处理（只运行 symptom_normalizer）
    const proceedToAnalysis = async () => {
      if (!validateForm()) return;

      if (!userStore.isAuthenticated) {
        alert('请先登录，未登录用户无法保存诊断记录！');
        router.push('/login');
        return;
      }

      step.value = 3;
      preprocessLoading.value = true;

      try {
        const payload = buildDiagnosisPayload();
        console.log('发送预处理请求:', payload);
        const res = await diagnosesApi.preprocess(payload);
        reviewOptimizedSymptoms.value = res.data.optimized_symptoms || '';
        reviewRagKeywords.value = res.data.rag_keywords || [];
      } catch (error) {
        console.error('预处理失败:', error);
        const msg = error.message || error.response?.data?.message || '';
        if (msg.includes('ECONNREFUSED') || msg.includes('Connection error')) {
          alert('本地模型服务未启动（127.0.0.1:8000 连接失败）。\n\n请先启动本地推理服务器，或切换到「混合系列」档位并开启 GPT 覆盖。');
        } else {
          alert(`预处理出错：${msg || '未知错误'}`);
        }
        step.value = 2;
      } finally {
        preprocessLoading.value = false;
      }
    };

    // 步骤 3 → 4 → 5：用户确认后启动完整 pipeline
    const confirmAndStartAnalysis = async () => {
      step.value = 4;
      progressSteps.value = [];
      currentStepLabel.value = '正在启动诊断 Pipeline...';

      try {
        const payload = buildDiagnosisPayload();
        // 注入用户确认/修改后的预处理结果
        payload._confirmed_optimized_symptoms = reviewOptimizedSymptoms.value;
        payload._confirmed_rag_keywords = reviewRagKeywords.value.filter(k => k.trim());

        console.log('发送诊断数据（含用户确认预处理）:', payload);

        const response = await diagnosesApi.createWithSSE(payload, (progress) => {
          const detail = formatProgressDetail(progress);
          progressSteps.value.push({ label: progress.label, detail });
          currentStepLabel.value = progress.step < progress.total
            ? '准备下一步...'
            : '正在保存结果...';
        });
        console.log('收到诊断响应:', response.data);
        currentStepLabel.value = '';

        diagnosisResults.value = response.data.results || [];
        diagnosisRecomm_short.value = response.data.recomm_short || [];
        diagnosisRecomm.value = response.data.recommendations || [];
        agentModelsMap.value = response.data.agent_models || {};

        const date = new Date(response.data.created_at || new Date());
        formattedDate.value = new Intl.DateTimeFormat('zh-CN', {
          year: 'numeric',
          month: 'long',
          day: 'numeric',
          hour: '2-digit',
          minute: '2-digit'
        }).format(date);

        setTimeout(() => {
          step.value = 5;
          setTimeout(() => {
            initChart();
            initWordCloud();
          }, 0);
        }, 500);
      } catch (error) {
        console.error('分析错误:', error);
        const msg = error.message || '';
        if (msg.includes('ECONNREFUSED') || msg.includes('Connection error')) {
          alert('本地模型服务未启动（127.0.0.1:8000 连接失败）。\n\n请先启动本地推理服务器，或切换到「混合系列」档位并开启 GPT 覆盖。');
        } else {
          alert(`诊断 Pipeline 出错：${msg || '未知错误，请稍后再试'}`);
        }
        currentStepLabel.value = '';
        step.value = 3;
      }
    };
    
    // 开始新的诊断
    const startNewDiagnosis = () => {
      selectedBodyPart.value = '';
      selectedSymptoms.value = [];
      otherSymptoms.value = '';
      severityLevel.value = 3;
      duration.value = '';
      selectedProfileId.value = modelProfiles[0]?.id || 'balanced';
      Object.keys(agentOverrides).forEach(key => {
        agentOverrides[key].useGpt = false;
        agentOverrides[key].model_name = 'gpt-5-mini';
      });
      step.value = 1;
      
      // 清除图表
      if (chart) {
        chart.dispose();
        chart = null;
      }
      
      // 清除词云图
      if (wordCloud) {
        wordCloud.dispose();
        wordCloud = null;
      }
    };
    
    // 格式化进度详情摘要
    const formatProgressDetail = (progress) => {
      const d = progress.data || {};
      switch (progress.node) {
        case 'symptom_normalizer':
          return d.optimized_symptoms
            ? `优化后: ${d.optimized_symptoms.slice(0, 60)}...`
            : '';
        case 'symptom_quality_grader':
          return d.score != null ? `评分: ${d.score}/5 — ${d.comment || ''}` : '';
        case 'rag_retriever':
          return d.doc_count != null ? `检索到 ${d.doc_count} 篇文档` : '';
        case 'rag_relevance_grader':
          return d.rag_score != null ? `相关度: ${d.rag_score}/5` : '';
        case 'diagnosis_generator':
          return d.conditions
            ? d.conditions.map(c => `${c.condition} ${(c.probability * 100).toFixed(0)}%`).join(', ')
            : '';
        case 'diagnosis_reviewer':
          return d.adjusted
            ? '概率已校验: ' + d.adjusted.map(c => `${c.condition} ${(c.probability * 100).toFixed(0)}%`).join(', ')
            : '';
        case 'drug_recommender':
          return d.drug_count != null ? `生成 ${d.drug_count} 条建议` : '';
        default:
          return '';
      }
    };

    // 获取默认症状描述
    const getDefaultDescription = (symptomName) => {
      // 根据症状名称提供默认描述
      const descriptionMap = {
        '头痛': '头部疼痛，可能伴有压迫感、跳痛或钝痛。',
        '头晕': '眩晕感或失去平衡感，可能伴有旋转感。',
        '发热': '体温升高，通常超过37.5°C，可能伴有出汗或寒战。',
        '疲劳': '全身无力、乏力或精力不足，无法完成日常活动。',
        '咳嗽': '突然或持续的咳嗽，可能是干咳或有痰。',
        '喉咙痛': '吞咽时喉咙疼痛、干燥或灼热感。',
        '胸痛': '胸部不适、压迫感或疼痛，可能向手臂、颈部或背部放射。',
        '呼吸困难': '呼吸急促、费力或感到无法获取足够的空气。',
        '心悸': '心跳加速、不规则或感到心脏跳动明显。',
        '腹痛': '腹部各区域的不适或疼痛，可能是钝痛、尖锐痛或绞痛。',
        '恶心': '想吐的感觉，可能伴有头晕、出汗或唾液增多。',
        '呕吐': '胃内容物通过口腔强制排出。',
        '腹泻': '排便次数增加，粪便稀薄或含水量高。',
        '便秘': '排便困难、不规则或频率减少。',
        '背痛': '背部任何区域的疼痛，可能是突然发作或长期存在。',
        '关节痛': '关节区域疼痛、僵硬或肿胀，可能影响活动。',
        '肌肉痛': '肌肉疼痛、酸痛或紧张，可能是由于过度使用或炎症。',
        '皮疹': '皮肤上的异常变化，如红斑、肿胀、瘙痒或脱皮。',
        '瘙痒': '皮肤上引起抓挠欲望的不适感。',
        '水肿': '身体某部位肿胀，通常是由于体液积聚。',
        '体重减轻': '非故意的体重下降，通常在短时间内。',
        '体重增加': '明显的体重增加，可能伴有水肿或食欲增加。',
        '睡眠问题': '难以入睡、保持睡眠或早醒，影响日常功能。'
      };
      
      return descriptionMap[symptomName] || '请选择此症状并描述您的具体感受。';
    };
    
    // 在组件挂载时获取症状数据
    onMounted(() => {
      fetchSymptoms();
    });
    
    return {
      userStore,
      selectedBodyPart,
      symptoms,
      filteredSymptoms,
      selectedSymptoms,
      otherSymptoms,
      severityLevel,
      duration,
      durationOptions,
      modelProfiles,
      selectedProfileId,
      overrideAgents,
      agentOverrides,
      errors,
      diagnosisResults,
      diagnosisRecomm_short,
      diagnosisRecomm,
      formattedDate,
      step,
      selectBodyPart,
      toggleSymptom,
      nextStep,
      proceedToAnalysis,
      startNewDiagnosis,
      chartContainer,
      wordCloudContainer,
      validateForm,
      getDefaultDescription,
      progressSteps,
      currentStepLabel,
      progressPercent,
      agentModelsMap,
      AGENT_LABELS,
      preprocessLoading,
      reviewOptimizedSymptoms,
      reviewRagKeywords,
      confirmAndStartAnalysis,
    };
  }
};
</script>

<style scoped>
.diagnostic-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.diagnostic-header h1 {
  color: #3273dc;
  font-weight: 700;
}

/* 步骤指示器样式 */
.steps-container {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin: 30px 0;
}

.step {
  display: flex;
  flex-direction: column;
  align-items: center;
  position: relative;
  flex: 1;
}

.step-number {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background-color: #ddd;
  display: flex;
  justify-content: center;
  align-items: center;
  font-weight: bold;
  margin-bottom: 10px;
  transition: all 0.3s ease;
}

.step-label {
  font-size: 14px;
  color: #666;
  transition: all 0.3s ease;
}

.step.active .step-number {
  background-color: #3273dc;
  color: white;
}

.step.active .step-label {
  color: #333;
  font-weight: bold;
}

.step.completed .step-number {
  background-color: #22c55e;
  color: white;
}

.step-line {
  flex-grow: 1;
  height: 3px;
  background-color: #ddd;
  margin: 0 10px;
  margin-bottom: 30px;
}

/* 身体部位选择样式 */
.body-parts-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 20px;
  margin-top: 30px;
}

.body-part-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 20px;
  background-color: #f5f5f5;
  border-radius: 10px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.body-part-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
}

.body-part-card.active {
  background-color: #3273dc;
  color: white;
}

.body-part-name {
  margin-top: 15px;
  font-weight: 600;
}

/* 症状选择样式 */
.symptoms-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  gap: 15px;
}

.symptom-card {
  padding: 15px;
  background-color: #f5f5f5;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s ease;
  height: 100%;
  display: flex;
  flex-direction: column;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  border: 1px solid #e5e7eb;
}

.symptom-card:hover {
  background-color: #eaeaea;
  box-shadow: 0 3px 6px rgba(0, 0, 0, 0.15);
  transform: translateY(-2px);
}

.symptom-card.active {
  background-color: #3273dc;
  color: white;
  border-color: #3273dc;
}

.symptom-name {
  font-weight: 600;
  margin-bottom: 8px;
  font-size: 16px;
  line-height: 1.4;
}

.symptom-desc {
  font-size: 14px;
  color: #555;
  line-height: 1.5;
  flex-grow: 1;
}

.symptom-card.active .symptom-desc {
  color: rgba(255, 255, 255, 0.8);
}

/* 严重程度滑块 */
.severity-slider {
  width: 100%;
  max-width: 500px;
  margin: 0 auto;
}

.slider {
  width: 100%;
  height: 10px;
  -webkit-appearance: none;
  appearance: none;
  background: linear-gradient(to right, #22c55e, #eab308, #ef4444);
  outline: none;
  border-radius: 5px;
}

.slider::-webkit-slider-thumb {
  -webkit-appearance: none;
  appearance: none;
  width: 25px;
  height: 25px;
  border-radius: 50%;
  background: #3273dc;
  cursor: pointer;
}

.severity-labels {
  display: flex;
  justify-content: space-between;
  margin-top: 10px;
  color: #666;
}

/* 症状信息区域容器 */
.symptoms-details-container {
  margin: 0 auto;
  max-width: 800px;
  padding: 20px 0;
}

/* 持续时间选择 */
.duration-section {
  margin: 30px auto;
  max-width: 800px;
}

.section-heading {
  display: inline-block;
  min-width: 120px;
}

.custom-select {
  max-width: 500px;
  margin-top: 10px;
}

.select-dropdown {
  width: 100%;
  padding: 12px 15px;
  border: 1px solid #d1d5db;
  border-radius: 8px;
  font-size: 16px;
  color: #333;
  background-color: #fff;
  appearance: none;
  background-image: url("data:image/svg+xml;charset=UTF-8,%3csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='currentColor' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3e%3cpolyline points='6 9 12 15 18 9'%3e%3c/polyline%3e%3c/svg%3e");
  background-repeat: no-repeat;
  background-position: right 15px center;
  background-size: 16px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.select-dropdown:focus {
  border-color: #3273dc;
  box-shadow: 0 0 0 3px rgba(50, 115, 220, 0.2);
  outline: none;
}

/* 文本区域样式 */
.textarea-container {
  width: 100%;
  max-width: 800px;
  margin: 0 auto;
}

.custom-textarea {
  width: 100%;
  min-height: 120px;
  padding: 15px;
  border: 1px solid #d1d5db;
  border-radius: 8px;
  font-size: 16px;
  line-height: 1.6;
  color: #333;
  resize: vertical;
  transition: all 0.3s ease;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
}

.custom-textarea:focus {
  border-color: #3273dc;
  box-shadow: 0 0 0 3px rgba(50, 115, 220, 0.2);
  outline: none;
}

/* 导航按钮 */
.step-navigation {
  display: flex;
  justify-content: space-between;
  margin-top: 30px;
}

/* 错误信息 */
.error-message {
  color: #ef4444;
  margin-bottom: 10px;
}

/* 加载动画 */
.analysis-loading {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 300px;
}

.spinner {
  width: 70px;
  height: 70px;
  border: 8px solid #f3f3f3;
  border-top: 8px solid #3273dc;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

/* 结果页样式 */
.result-header {
  margin-bottom: 20px;
}

.result-time {
  color: #666;
  font-style: italic;
}

.disclaimer {
  background-color: #fff9db;
  border-left: 4px solid #f59f00;
  padding: 15px;
  border-radius: 4px;
  display: flex;
  align-items: center;
  gap: 10px;
}

.disclaimer i {
  color: #f59f00;
  font-size: 20px;
}

.chart-container {
  width: 100%;
  height: 400px;
  margin: 0 auto;
}

.word-cloud-container {
  width: 100%;
  height: 350px;
  margin: 0 auto;
  background-color: #f8fafe;
  border-radius: 10px;
  padding: 15px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
  position: relative;
  overflow: hidden;
}

.cloud-title {
  text-align: center;
  font-size: 18px;
  font-weight: bold;
  color: #3273dc;
  margin-bottom: 15px;
}

.cloud-container {
  position: relative;
  width: 100%;
  height: calc(100% - 30px);
}

.cloud-word {
  white-space: nowrap;
  padding: 5px 8px;
  border-radius: 3px;
}

.results-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 20px;
}

.result-card {
  background-color: #f8f9fa;
  border-radius: 10px;
  padding: 20px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
}

.result-card .result-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}

.result-card h4 {
  margin: 0;
  color: #3273dc;
}

.probability {
  background-color: #3273dc;
  color: white;
  padding: 5px 10px;
  border-radius: 20px;
  font-size: 14px;
}

.result-description {
  line-height: 1.6;
  color: #444;
}

.recommendation-list {
  background-color: #f0f7ff;
  padding: 20px 20px 20px 40px;
  border-radius: 10px;
}

.recommendation-list li {
  margin-bottom: 10px;
  line-height: 1.6;
}

/* 响应式调整 */
@media (max-width: 768px) {
  .body-parts-grid,
  .symptoms-grid,
  .results-grid {
    grid-template-columns: 1fr;
  }
  
  .step-navigation {
    flex-direction: column;
    gap: 15px;
  }
  
  .step-navigation button {
    width: 100%;
  }
  
  .step-label {
    display: none;
  }
}

/* Pipeline 实时进度 */
.pipeline-progress {
  max-width: 600px;
  margin: 0 auto;
}

.progress-bar-container {
  display: flex;
  align-items: center;
  gap: 12px;
}

.progress-bar-bg {
  flex: 1;
  height: 8px;
  background: #e5e7eb;
  border-radius: 4px;
  overflow: hidden;
}

.progress-bar-fill {
  height: 100%;
  background: linear-gradient(90deg, #3273dc, #22c55e);
  border-radius: 4px;
  transition: width 0.4s ease;
}

.progress-text {
  font-size: 14px;
  font-weight: 600;
  color: #3273dc;
  min-width: 40px;
  text-align: right;
}

.progress-steps {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.progress-step {
  display: flex;
  align-items: flex-start;
  gap: 10px;
  padding: 8px 12px;
  border-radius: 8px;
  background: #f0fdf4;
  border: 1px solid #bbf7d0;
}

.progress-step.active {
  background: #eff6ff;
  border-color: #bfdbfe;
}

.progress-step .step-icon {
  font-size: 14px;
  color: #22c55e;
  flex-shrink: 0;
  margin-top: 2px;
}

.progress-step.active .step-icon {
  color: #3273dc;
}

.progress-step.active .step-icon.spinning {
  animation: spin 1.5s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.progress-step .step-info {
  flex: 1;
  min-width: 0;
}

.progress-step .step-label {
  font-size: 14px;
  font-weight: 600;
  color: #333;
  display: block;
}

.progress-step .step-detail {
  font-size: 12px;
  color: #666;
  margin-top: 2px;
  word-break: break-all;
}

/* 预处理确认步骤 */
.step3-review {
  max-width: 800px;
  margin: 0 auto;
}
.review-field {
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  padding: 16px 20px;
}
.review-label {
  display: block;
  font-weight: 600;
  color: #1e293b;
  margin-bottom: 8px;
  font-size: 15px;
}
.review-hint {
  font-weight: 400;
  color: #64748b;
  font-size: 13px;
}
.review-textarea {
  width: 100%;
  border: 1px solid #cbd5e1;
  border-radius: 8px;
  padding: 10px 12px;
  font-size: 14px;
  line-height: 1.6;
  resize: vertical;
  font-family: inherit;
}
.review-textarea:focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.15);
}
.review-keywords {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  align-items: center;
}
.keyword-chip {
  display: flex;
  align-items: center;
  gap: 4px;
  background: #dbeafe;
  border-radius: 6px;
  padding: 4px 6px;
}
.keyword-input {
  border: none;
  background: transparent;
  font-size: 13px;
  color: #1d4ed8;
  width: auto;
  min-width: 60px;
  max-width: 200px;
  outline: none;
}
.keyword-remove {
  background: none;
  border: none;
  color: #93c5fd;
  font-size: 16px;
  cursor: pointer;
  padding: 0 2px;
  line-height: 1;
}
.keyword-remove:hover {
  color: #dc2626;
}
.keyword-add {
  background: none;
  border: 1px dashed #94a3b8;
  border-radius: 6px;
  padding: 4px 10px;
  font-size: 13px;
  color: #64748b;
  cursor: pointer;
}
.keyword-add:hover {
  border-color: #3b82f6;
  color: #3b82f6;
}

/* Agent 模型信息 */
.agent-models-section h3 {
  color: #1e293b;
}
.agent-models-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}
.agent-model-tag {
  display: flex;
  align-items: center;
  gap: 6px;
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  padding: 6px 12px;
  font-size: 13px;
}
.agent-model-tag .agent-name {
  color: #475569;
  font-weight: 500;
}
.model-badge {
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 600;
}
.model-badge.badge-local {
  background: #dbeafe;
  color: #1d4ed8;
}
.model-badge.badge-gpt {
  background: #dcfce7;
  color: #166534;
}
</style>
