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
        <div class="step-label">分析中</div>
      </div>
      <div class="step-line"></div>
      <div class="step" :class="{ active: step >= 4 }">
        <div class="step-number">4</div>
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
            <div class="flex items-center justify-between">
              <h3 class="mb-4 section-heading">选择模型档位:</h3>
              <button
                type="button"
                class="text-sm text-blue-600 hover:text-blue-500"
                @click="showAdvanced = !showAdvanced"
              >
                {{ showAdvanced ? '收起高级覆盖' : '高级覆盖' }}
              </button>
            </div>

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

            <div v-if="showAdvanced" class="mt-4 space-y-4">
              <div v-for="agent in overrideAgents" :key="agent.id" class="bg-gray-50 rounded-lg p-4">
                <div class="font-medium text-gray-700 mb-2">{{ agent.name }}</div>
                <div class="grid grid-cols-1 md:grid-cols-3 gap-3">
                  <select v-model="agentOverrides[agent.id].model_type" class="select-dropdown">
                    <option value="">跟随档位</option>
                    <option value="local">本地 Qwen</option>
                    <option value="gpt">云端 GPT</option>
                  </select>
                  <input v-model="agentOverrides[agent.id].model_name" class="form-input" placeholder="模型名称 (可选)" />
                  <input v-model="agentOverrides[agent.id].base_url" class="form-input" placeholder="本地 API Base URL (可选)" />
                </div>
                <p class="text-xs text-gray-500 mt-2">未填写的字段将沿用档位配置。</p>
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

      <!-- 步骤3: 分析中 -->
      <div v-if="step === 3" class="step-content step3-content text-center">
        <div class="analysis-loading">
          <div class="spinner"></div>
          <h2 class="mt-4">AI诊断系统正在分析您的症状...</h2>
          <p>这可能需要几十秒钟时间，请耐心等待。</p>
        </div>
      </div>

      <!-- 步骤4: 诊断结果 -->
      <div v-if="step === 4" class="step-content step4-content">
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
    const selectedProfileId = ref(modelProfiles[0]?.id || 'fast');
    const showAdvanced = ref(false);
    const overrideAgents = [
      { id: 'symptom_normalizer', name: '症状规范化' },
      { id: 'diagnosis_generator', name: '诊断生成' },
      { id: 'drug_recommender', name: '用药推荐' }
    ];
    const agentOverrides = reactive({
      symptom_normalizer: { model_type: '', model_name: '', base_url: '' },
      diagnosis_generator: { model_type: '', model_name: '', base_url: '' },
      drug_recommender: { model_type: '', model_name: '', base_url: '' }
    });
    
    // 错误信息
    const errors = ref({
      symptoms: '',
      duration: ''
    });
    
    // 诊断结果
    const diagnosisResults = ref([]);
    const diagnosisRecomm = ref([]);
    const diagnosisRecomm_short = ref([]);
    const formattedDate = ref('');
    
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
  });;
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
      const payload = {};
      overrideAgents.forEach(agent => {
        const cfg = agentOverrides[agent.id];
        if (!cfg) return;
        const hasValue = [cfg.model_type, cfg.model_name, cfg.base_url]
          .some(v => v && String(v).trim().length > 0);
        if (hasValue) {
          payload[agent.id] = {
            ...(cfg.model_type ? { model_type: cfg.model_type } : {}),
            ...(cfg.model_name ? { model_name: cfg.model_name } : {}),
            ...(cfg.base_url ? { base_url: cfg.base_url } : {})
          };
        }
      });
      return payload;
    };

    // 进行分析
    const proceedToAnalysis = async () => {
      if (!validateForm()) return;
      
      // 检查用户是否已登录
      if (!userStore.isAuthenticated) {
        alert('请先登录，未登录用户无法保存诊断记录！');
        // 可以选择跳转到登录页面
        router.push('/login');
        return;
      }
      
      // 转到分析中状态
      step.value = 3;
      
      try {
        // 组装诊断数据 - 使用snake_case匹配后端期望的格式
        const overridePayload = buildAgentOverridesPayload();
        const diagnosisData = {
          user_id: userStore.userId,
          body_part: selectedBodyPart.value,
          symptoms: selectedSymptoms.value,
          other_symptoms: otherSymptoms.value,
          severity: severityLevel.value,
          duration: duration.value,
          model_profile_id: selectedProfileId.value,
          agent_overrides: overridePayload
        };
        
        console.log('发送诊断数据:', diagnosisData);
        
        // 发送诊断请求到后端
        const response = await diagnosesApi.create(diagnosisData);
        console.log('收到诊断响应:', response.data);
        
        // 设置结果
        diagnosisResults.value = response.data.results || [];
        diagnosisRecomm_short.value = response.data.recomm_short || [];
        diagnosisRecomm.value = response.data.recommendations || [];
        
        // 格式化日期
        const date = new Date(response.data.created_at || new Date());
        formattedDate.value = new Intl.DateTimeFormat('zh-CN', {
          year: 'numeric',
          month: 'long',
          day: 'numeric',
          hour: '2-digit',
          minute: '2-digit'
        }).format(date);
        
        // 等待一点时间模拟 AI 分析过程
        setTimeout(() => {
          step.value = 4;
          // 在下一轮事件循环中初始化图表，确保DOM已经渲染
          setTimeout(() => {
            initChart();
            initWordCloud(); // 初始化词云图
          }, 0);
        }, 1500);
      } catch (error) {
        console.error('分析错误:', error);
        alert('分析过程中出现错误，请稍后再试');
        step.value = 2;
      }
    };
    
    // 开始新的诊断
    const startNewDiagnosis = () => {
      selectedBodyPart.value = '';
      selectedSymptoms.value = [];
      otherSymptoms.value = '';
      severityLevel.value = 3;
      duration.value = '';
      selectedProfileId.value = modelProfiles[0]?.id || 'fast';
      showAdvanced.value = false;
      Object.keys(agentOverrides).forEach(key => {
        agentOverrides[key].model_type = '';
        agentOverrides[key].model_name = '';
        agentOverrides[key].base_url = '';
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
      showAdvanced,
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
      getDefaultDescription
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
</style>
