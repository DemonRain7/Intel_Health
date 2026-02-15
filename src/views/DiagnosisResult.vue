<template>
  <div class="diagnostic-container">
    <!-- 返回按钮 -->
    <div class="back-to-history mb-4">
      <router-link to="/history" class="btn btn-secondary">
        <i class="fas fa-arrow-left"></i> 返回历史
      </router-link>
    </div>

    <!-- 头部 -->
    <div class="diagnostic-header">
      <h1 class="text-center mb-4">诊断结果详情</h1>
    </div>

    <!-- 加载状态 -->
    <div v-if="loading" class="text-center py-12">
      <div class="spinner"></div>
      <p class="mt-4">加载诊断结果中...</p>
    </div>

    <!-- 错误显示 -->
    <div v-else-if="error" class="alert alert-danger">
      {{ error }}
    </div>

    <!-- 诊断结果 -->
    <div v-else-if="diagnosis" class="diagnostic-content">
      <div class="result-content step4-content">
        <div class="result-header">
          <h2 class="mb-2">诊断结果分析</h2>
          <p class="result-time">生成时间: {{ formatDate(diagnosis.created_at) }}</p>
        </div>
        
        <!-- 症状概述 -->
        <div class="diagnosis-overview mb-4">
          <div class="card">
            <div class="card-body">
              <h3 class="card-title mb-3">症状概述</h3>
              <div class="overview-details">
                <div class="overview-item">
                  <span class="label">部位:</span>
                  <span class="value">{{ getBodyPartName(diagnosis.body_part) }}</span>
                </div>
                <div class="overview-item">
                  <span class="label">严重程度:</span>
                  <span class="value" :class="getSeverityClass(diagnosis.severity)">
                    {{ SEVERITY_LEVELS[diagnosis.severity] || `${diagnosis.severity}/5` }}
                  </span>
                </div>
                <div class="overview-item">
                  <span class="label">持续时间:</span>
                  <span class="value">{{ diagnosis.duration || '未指定' }}</span>
                </div>
                <div class="overview-item symptoms-list">
                  <span class="label">症状:</span>
                  <div class="value">
                    <span v-for="symptom in getSymptomNames(diagnosis.symptoms)" :key="symptom" class="symptom-tag">
                      {{ symptom }}
                    </span>
                    <span class="symptom-tag" v-if="diagnosis.other_symptoms">
                    {{ diagnosis.other_symptoms }}
                  </span>
                  </div>
                </div>
                <div v-if="diagnosis.description" class="overview-item full-width">
                  <span class="label">描述:</span>
                  <span class="value">{{ diagnosis.description }}</span>
                </div>
              </div>
            </div>
          </div>
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
            <div v-for="(result, index) in diagnosis.results" :key="index" class="result-card">
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
        
                <!-- 结果图表 -->
                <div class="result-chart mb-5">
          <h3 class="mb-3">AI小建议:</h3>
          <div ref="wordCloudContainer" class="word-cloud-container"></div>
        </div>

        <!-- 建议 -->
        <div class="recommendations mb-5">
          <ul class="recommendation-list">
            <li v-for="(rec, index) in diagnosis.recommendations" :key="index">
              {{ rec }}
            </li>
          </ul>
        </div>
        
        <!-- 导航按钮 -->
        <div class="step-navigation">
          <router-link to="/history" class="btn btn-secondary">
            <i class="fas fa-arrow-left"></i> 返回历史记录
          </router-link>
          <router-link to="/diagnostic" class="btn btn-primary">
            <i class="fas fa-sync"></i> 开始新的诊断
          </router-link>
        </div>
      </div>
    </div>

    <!-- 未找到结果 -->
    <div v-else class="text-center py-8">
      <div class="alert alert-warning">
        未找到诊断结果或结果已被删除
      </div>
      <div class="mt-4">
        <router-link to="/history" class="btn btn-primary">
          返回历史记录
        </router-link>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, nextTick, watch  } from 'vue';
import { useRoute } from 'vue-router';
import { diagnosesApi } from '../utils/api';
import { COMMON_BODY_PARTS, COMMON_SYMPTOMS, SEVERITY_LEVELS } from '../utils/constants';
import * as echarts from 'echarts';
import cloud from 'd3-cloud';
import * as d3 from 'd3';



export default {
  name: 'DiagnosisResult',
  
  setup() {
    const route = useRoute();
    const diagnosis = ref(null);
    const loading = ref(true);
    const error = ref(null);
    const wordCloudContainer = ref(null);
    const chartContainer = ref(null);
    const diagnosisResults = ref([]);
    const diagnosisRecomm_short = ref([]);

    let chart = null;
    
    // 获取诊断详情
    const fetchDiagnosis = async () => {
      loading.value = true;
      error.value = null;
      
      try {
        const diagnosisId = route.params.id;
        const response = await diagnosesApi.getById(diagnosisId);
        diagnosis.value = response.data;
        diagnosisResults.value = response.data.results || [];
        diagnosisRecomm_short.value = response.data.recomm_short || [];
        
        // 渲染图表（在下一个DOM更新周期）
        nextTick(() => {
          initChart();
          initWordCloud();
        });
      } catch (err) {
        console.error('获取诊断详情失败:', err);
        error.value = '获取诊断详情失败，请稍后再试或返回历史页面。';
      } finally {
        loading.value = false;
      }
    };

    //初始化pie chart
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

    
    // 格式化日期
    const formatDate = (dateStr) => {
      if (!dateStr) return '';
      
      const date = new Date(dateStr);
      return new Intl.DateTimeFormat('zh-CN', {
        year: 'numeric',
        month: 'long',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      }).format(date);
    };
    
    // 获取身体部位名称
    const getBodyPartName = (partId) => {
      if (!partId) return '未指定';
      
      const part = COMMON_BODY_PARTS.find(p => p.id === partId);
      return part ? part.name : partId;
    };
    
    // 获取症状名称列表
    const getSymptomNames = (symptomIds) => {
      if (!symptomIds || !Array.isArray(symptomIds)) return [];
      // 优先使用存储的 symptom_names（解决 UUID 显示问题）
      if (diagnosis.value && Array.isArray(diagnosis.value.symptom_names) && diagnosis.value.symptom_names.length > 0) {
        return diagnosis.value.symptom_names;
      }
      return symptomIds.map(id => {
        const symptom = COMMON_SYMPTOMS.find(s => s.id === id);
        return symptom ? symptom.name : '';
      }).filter(Boolean);
    };
    
    // 获取严重程度样式类
    const getSeverityClass = (severity) => {
      if (!severity) return '';
      
      const level = parseInt(severity);
      if (level <= 2) return 'severity-low';
      if (level === 3) return 'severity-medium';
      return 'severity-high';
    };
    
    // 组件挂载时获取数据
    onMounted(() => {
      fetchDiagnosis();
      // initWordCloud();
    });
    
    watch(diagnosisRecomm_short, () => {
      initChart();
  initWordCloud();
});

    return {
      diagnosis,
      loading,
      error,
      SEVERITY_LEVELS,
      formatDate,
      getBodyPartName,
      getSymptomNames,
      chartContainer,
      wordCloudContainer, 
      getSeverityClass,
      diagnosisResults
    };
  }
};
</script>

<style scoped>
.diagnostic-container {
  max-width: 1000px;
  margin: 0 auto;
  padding: 2rem 1rem;
}

.diagnostic-header {
  margin-bottom: 2rem;
}

.result-header {
  display: flex;
  flex-direction: column;
  align-items: center;
  margin-bottom: 1.5rem;
}

.result-time {
  color: #718096;
  font-size: 0.9rem;
}

.disclaimer {
  background-color: #fff5f5;
  border-left: 4px solid #f56565;
  padding: 1rem;
  display: flex;
  align-items: center;
  border-radius: 0.375rem;
}

.disclaimer i {
  font-size: 1.25rem;
  color: #f56565;
  margin-right: 0.75rem;
}

.chart-container {
  height: 350px;
  width: 100%;
  background-color: #fff;
  border-radius: 0.5rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

.results-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 1rem;
}

.result-card {
  background-color: #fff;
  border-radius: 0.5rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  padding: 1.25rem;
}

.result-card .result-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.75rem;
}

.result-card h4 {
  font-size: 1.125rem;
  font-weight: 600;
  margin: 0;
  color: #2d3748;
}

.probability {
  font-size: 0.875rem;
  font-weight: 500;
  color: #4299e1;
}

.result-description {
  color: #4a5568;
  font-size: 0.9375rem;
  line-height: 1.5;
}

.recommendations {
  background-color: #ebf8ff;
  border-radius: 0.5rem;
  padding: 1.5rem;
}

.recommendation-list {
  list-style-type: none;
  padding-left: 0;
  margin-bottom: 0;
}

.word-cloud-container {
  width: 100%;
  height: 300px;
  background-color: #f8fafe;
  border-radius: 10px;
  padding: 10px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
  position: relative;
  overflow: hidden;
}


.recommendation-list li {
  padding: 0.5rem 0;
  padding-left: 1.75rem;
  position: relative;
}

.recommendation-list li:before {
  content: '✓';
  color: #4299e1;
  position: absolute;
  left: 0;
  font-weight: bold;
}

.step-navigation {
  display: flex;
  justify-content: space-between;
  margin-top: 2rem;
}

.card {
  background-color: #fff;
  border-radius: 0.5rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

.card-body {
  padding: 1.5rem;
}

.card-title {
  font-size: 1.25rem;
  font-weight: 600;
  color: #2d3748;
}

.overview-details {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  gap: 1rem;
}

.overview-item {
  margin-bottom: 0.75rem;
}

.overview-item.full-width {
  grid-column: 1 / -1;
}

.overview-item .label {
  font-weight: 600;
  color: #4a5568;
  margin-right: 0.5rem;
}

.overview-item .value {
  color: #2d3748;
}

.symptoms-list .value {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  margin-top: 0.5rem;
}

.symptom-tag {
  background-color: #ebf8ff;
  color: #4299e1;
  padding: 0.25rem 0.75rem;
  border-radius: 9999px;
  font-size: 0.875rem;
  white-space: nowrap;
}

.severity-low {
  color: #38a169;
}

.severity-medium {
  color: #d69e2e;
}

.severity-high {
  color: #e53e3e;
}

.spinner {
  width: 3rem;
  height: 3rem;
  border: 4px solid rgba(66, 153, 225, 0.25);
  border-left-color: #4299e1;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

@media (max-width: 768px) {
  .overview-details {
    grid-template-columns: 1fr;
  }
  
  .results-grid {
    grid-template-columns: 1fr;
  }
  
  .step-navigation {
    flex-direction: column;
    gap: 1rem;
  }
  
  .step-navigation button, .step-navigation a {
    width: 100%;
  }
}
</style>
