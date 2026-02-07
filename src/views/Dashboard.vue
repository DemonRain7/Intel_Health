<template>
  <div class="bg-gray-50 min-h-screen py-8">
    <div class="container mx-auto px-4">
      <h1 class="text-3xl font-bold text-gray-900 mb-8 text-center">个人健康仪表盘</h1>
      
      <!-- 加载状态 -->
      <div v-if="loading" class="text-center py-12">
        <svg class="animate-spin w-12 h-12 mx-auto text-blue-600" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
          <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
          <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
        </svg>
        <p class="mt-4 text-gray-600">加载您的健康数据...</p>
      </div>
      
      <!-- 仪表盘内容 -->
      <div v-else class="max-w-6xl mx-auto">
        <!-- 欢迎卡片 -->
        <div class="bg-gradient-to-r from-blue-600 to-indigo-600 rounded-lg shadow-md text-white p-6 mb-8">
          <div class="flex flex-col md:flex-row items-center">
            <div class="mb-4 md:mb-0 md:mr-6">
              <div class="w-20 h-20 bg-white rounded-full text-blue-600 flex items-center justify-center text-2xl font-bold">
                {{ userInitials }}
              </div>
            </div>
            <div>
              <h2 class="text-2xl font-bold mb-2">欢迎回来，{{ userStore.username }}</h2>
              <p>您的个人健康数据一目了然，让健康管理更简单。</p>
              
              <div class="mt-4">
                <router-link to="/diagnostic" class="inline-block bg-white text-blue-600 hover:bg-blue-50 px-4 py-2 rounded-md font-medium mr-3">
                  新诊断
                </router-link>
                <router-link to="/history" class="inline-block text-white border border-white hover:bg-blue-700 px-4 py-2 rounded-md font-medium">
                  查看历史
                </router-link>
              </div>
            </div>
          </div>
        </div>
        
        <!-- 没有数据时显示 -->
        <div v-if="diagnoses.length === 0" class="bg-white rounded-lg shadow-md p-8 text-center">
          <div class="text-blue-600 mb-4">
            <svg class="w-16 h-16 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"></path>
            </svg>
          </div>
          <h2 class="text-xl font-semibold mb-2">开始您的健康跟踪</h2>
          <p class="text-gray-600 mb-6">您还没有任何诊断记录。使用我们的AI诊断工具来开始追踪您的健康情况。</p>
          <router-link to="/diagnostic" class="btn btn-primary">
            立即开始诊断
          </router-link>
        </div>
        
        <!-- 有数据时的仪表盘内容 -->
        <div v-else>
          <!-- 统计信息卡片 -->
          <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
            <div class="bg-white rounded-lg shadow-md p-6">
              <div class="flex items-center justify-between mb-4">
                <h3 class="text-lg font-semibold text-gray-700">总诊断次数</h3>
                <div class="text-blue-600">
                  <svg class="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-3 7h3m-3 4h3m-6-4h.01M9 16h.01"></path>
                  </svg>
                </div>
              </div>
              <div class="text-3xl font-bold text-gray-900">{{ diagnoses.length }}</div>
              <p class="text-sm text-gray-500 mt-2">
                <span class="text-green-600">+{{ recentDiagnosesCount }}</span> 在过去7天
              </p>
            </div>
            
            <div class="bg-white rounded-lg shadow-md p-6">
              <div class="flex items-center justify-between mb-4">
                <h3 class="text-lg font-semibold text-gray-700">最常见症状</h3>
                <div class="text-blue-600">
                  <svg class="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 8v8m-4-5v5m-4-2v2m-2 4h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"></path>
                  </svg>
                </div>
              </div>
              <div class="text-xl font-bold text-gray-900">{{ mostCommonSymptom || '无数据' }}</div>
              <p class="text-sm text-gray-500 mt-2">基于您的所有诊断记录</p>
            </div>
            
            <div class="bg-white rounded-lg shadow-md p-6">
              <div class="flex items-center justify-between mb-4">
                <h3 class="text-lg font-semibold text-gray-700">最常见诊断结果</h3>
                <div class="text-blue-600">
                  <svg class="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                  </svg>
                </div>
              </div>
              <div class="text-xl font-bold text-gray-900">{{ mostCommonCondition || '无数据' }}</div>
              <p class="text-sm text-gray-500 mt-2">
                {{ commonConditionCount }} 次诊断中出现
              </p>
            </div>
          </div>
          
          <!-- 图表区域 -->
          <div class="grid grid-cols-1 md:grid-cols-2 gap-8 mb-8">
            <!-- 诊断趋势图 -->
            <div class="bg-white rounded-lg shadow-md p-6">
              <h3 class="text-lg font-semibold text-gray-700 mb-4">诊断趋势</h3>
              <div class="h-64" ref="trendsChartContainer"></div>
            </div>
            
            <!-- 出现症状的身体部位分布图 -->
            <div class="bg-white rounded-lg shadow-md p-6">
              <h3 class="text-lg font-semibold text-gray-700 mb-4">出现症状的身体部位分布</h3>
              <div class="h-64" ref="bodyPartsChartContainer"></div>
            </div>
          </div>
          
          <!-- 最近诊断记录 -->
          <div class="bg-white rounded-lg shadow-md p-6">
            <div class="flex items-center justify-between mb-6">
              <h3 class="text-lg font-semibold text-gray-700">最近诊断记录</h3>
              <router-link to="/history" class="text-blue-600 hover:text-blue-800 text-sm font-medium">
                查看全部
              </router-link>
            </div>
            
            <div class="overflow-x-auto">
              <table class="min-w-full divide-y divide-gray-200">
                <thead class="bg-gray-50">
                  <tr>
                    <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      日期
                    </th>
                    <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      身体部位
                    </th>
                    <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      症状
                    </th>
                    <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      可能的病症
                    </th>
                    <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      操作
                    </th>
                  </tr>
                </thead>
                <tbody class="bg-white divide-y divide-gray-200">
                  <tr v-for="diagnosis in recentDiagnoses" :key="diagnosis.id">
                    <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {{ formatDate(diagnosis.created_at) }}
                    </td>
                    <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                      {{ getBodyPartName(diagnosis.body_part) }}
                    </td>
                    <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      <div class="flex flex-wrap gap-1">
                        <span 
                          v-for="(symptom, index) in getSymptomNames(diagnosis.symptoms).slice(0, 2)" 
                          :key="index"
                          class="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-blue-100 text-blue-800"
                        >
                          {{ symptom }}
                        </span>
                        <span 
                          v-if="getSymptomNames(diagnosis.symptoms).length > 2" 
                          class="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-gray-100 text-gray-800"
                        >
                          +{{ getSymptomNames(diagnosis.symptoms).length - 2 }}
                        </span>
                        <!-- 其他症状 -->
                        <span 
  v-if="diagnosis.other_symptoms && diagnosis.other_symptoms.length > 0" 
  class="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-yellow-100 text-yellow-800"
>
  {{ Array.isArray(diagnosis.other_symptoms) ? diagnosis.other_symptoms.join('，') : diagnosis.other_symptoms }}
</span>

                      </div>
                    </td>
                    <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {{ getTopCondition(diagnosis.results) }}
                    </td>
                    <td class="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                      <router-link :to="`/diagnostic/result/${diagnosis.id}`" class="text-blue-600 hover:text-blue-900">
                        查看
                      </router-link>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
            
            <div v-if="recentDiagnoses.length === 0" class="text-center py-8 text-gray-500">
              暂无最近记录
            </div>
          </div>
        </div>
        
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted, watch } from 'vue';
import { useRouter } from 'vue-router';
import { useUserStore } from '../store/userStore';
import { diagnosesApi } from '../utils/api';
import { COMMON_BODY_PARTS, COMMON_SYMPTOMS } from '../utils/constants';
import * as echarts from 'echarts/core';
import { BarChart, PieChart, LineChart } from 'echarts/charts';
import { TitleComponent, TooltipComponent, LegendComponent, GridComponent } from 'echarts/components';
import { LabelLayout } from 'echarts/features';
import { CanvasRenderer } from 'echarts/renderers';

// 注册 ECharts 组件
echarts.use([
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  GridComponent,
  BarChart,
  PieChart,
  LineChart,
  CanvasRenderer,
  LabelLayout
]);

export default {
  name: 'DashboardPage',
  setup() {
    const router = useRouter();
    const userStore = useUserStore();
    
    // 状态
    const diagnoses = ref([]);
    const loading = ref(true);
    const error = ref(null);
    
    // 图表容器引用
    const trendsChartContainer = ref(null);
    const bodyPartsChartContainer = ref(null);
    
    // 图表实例
    let trendsChart = null;
    let bodyPartsChart = null;
    
    // 计算属性：用户首字母
    const userInitials = computed(() => {
      const username = userStore.username || '';
      return username.substring(0, 1).toUpperCase();
    });
    
    // 计算属性：最近7天的诊断数量
    const recentDiagnosesCount = computed(() => {
      return diagnoses.value.filter(d => {
        const diagnosisDate = new Date(d.created_at);
        const now = new Date();
        const diffTime = Math.abs(now - diagnosisDate);
        const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
        return diffDays <= 7;
      }).length;
    });
    
    // 计算属性：最常见的症状
    const mostCommonSymptom = computed(() => {
      const symptomCounts = {};
      
      // 统计所有症状的出现次数
      diagnoses.value.forEach(diagnosis => {
        diagnosis.symptoms.forEach(symptomId => {
          if (!symptomCounts[symptomId]) {
            symptomCounts[symptomId] = 0;
          }
          symptomCounts[symptomId]++;
        });
      });
      
      // 找出出现次数最多的症状
      let maxCount = 0;
      let mostCommonSymptomId = null;
      
      Object.entries(symptomCounts).forEach(([symptomId, count]) => {
        if (count > maxCount) {
          maxCount = count;
          mostCommonSymptomId = symptomId;
        }
      });
      
      // 获取症状名称
      if (mostCommonSymptomId) {
        const symptom = COMMON_SYMPTOMS.find(s => s.id === mostCommonSymptomId);
        return symptom ? symptom.name : null;
      }
      
      return null;
    });
    
    // 计算属性：最常见的诊断结果
    const mostCommonCondition = computed(() => {
      const conditionCounts = {};
      
      // 统计所有诊断结果的出现次数
      diagnoses.value.forEach(diagnosis => {
        if (diagnosis.results && diagnosis.results.length > 0) {
          // 获取概率最高的诊断结果
          const topResult = [...diagnosis.results].sort((a, b) => b.probability - a.probability)[0];
          if (topResult) {
            if (!conditionCounts[topResult.condition]) {
              conditionCounts[topResult.condition] = 0;
            }
            conditionCounts[topResult.condition]++;
          }
        }
      });
      
      // 找出出现次数最多的诊断结果
      let maxCount = 0;
      let mostCommonCondition = null;
      
      Object.entries(conditionCounts).forEach(([condition, count]) => {
        if (count > maxCount) {
          maxCount = count;
          mostCommonCondition = condition;
        }
      });
      
      return mostCommonCondition;
    });
    
    // 计算属性：最常见诊断结果的出现次数
    const commonConditionCount = computed(() => {
      if (!mostCommonCondition.value) return 0;
      
      let count = 0;
      diagnoses.value.forEach(diagnosis => {
        if (diagnosis.results && diagnosis.results.length > 0) {
          const topResult = [...diagnosis.results].sort((a, b) => b.probability - a.probability)[0];
          if (topResult && topResult.condition === mostCommonCondition.value) {
            count++;
          }
        }
      });
      
      return count;
    });
    
    // 计算属性：最近的诊断记录（最多5条）
    const recentDiagnoses = computed(() => {
      return [...diagnoses.value]
        .sort((a, b) => new Date(b.created_at) - new Date(a.created_at))
        .slice(0, 5);
    });
    
    // 获取诊断历史数据
    const fetchDiagnoses = async () => {
      loading.value = true;
      error.value = null;
      
      try {
        const response = await diagnosesApi.getAll();
        diagnoses.value = response.data || [];
      } catch (err) {
        console.error('获取诊断历史失败:', err);
        error.value = '获取诊断历史失败，请稍后再试。';
      } finally {
        loading.value = false;
      }
    };
    
    // 初始化趋势图表
    const initTrendsChart = () => {
      if (!trendsChartContainer.value || diagnoses.value.length === 0) return;
      
      if (trendsChart) {
        trendsChart.dispose();
      }
      
      trendsChart = echarts.init(trendsChartContainer.value);
      
      // 生成图表数据（近30天的诊断数量趋势）
      const chartData = generateChartData(diagnoses.value, 30);
      
      const option = {
        tooltip: {
          trigger: 'axis',
          formatter: '{b}: {c} 次诊断'
        },
        xAxis: {
          type: 'category',
          data: chartData.dates,
          axisLine: {
            lineStyle: {
              color: '#ddd'
            }
          },
          axisLabel: {
            color: '#666',
            fontSize: 10,
            interval: 5
          }
        },
        yAxis: {
          type: 'value',
          minInterval: 1,
          axisLine: {
            show: false
          },
          axisTick: {
            show: false
          },
          axisLabel: {
            color: '#666'
          },
          splitLine: {
            lineStyle: {
              color: '#eee'
            }
          }
        },
        series: [
          {
            data: chartData.counts,
            type: 'line',
            smooth: true,
            symbolSize: 6,
            lineStyle: {
              width: 3,
              color: '#1976d2'
            },
            itemStyle: {
              color: '#1976d2'
            },
            areaStyle: {
              color: {
                type: 'linear',
                x: 0,
                y: 0,
                x2: 0,
                y2: 1,
                colorStops: [
                  { offset: 0, color: 'rgba(25, 118, 210, 0.3)' },
                  { offset: 1, color: 'rgba(25, 118, 210, 0.05)' }
                ]
              }
            }
          }
        ],
        grid: {
          left: '3%',
          right: '4%',
          bottom: '3%',
          top: '3%',
          containLabel: true
        }
      };
      
      trendsChart.setOption(option);
      
      window.addEventListener('resize', () => {
        if (trendsChart) {
          trendsChart.resize();
        }
      });
    };
    
    // 初始化身体部位分布图表
    const initBodyPartsChart = () => {
      if (!bodyPartsChartContainer.value || diagnoses.value.length === 0) return;
      
      if (bodyPartsChart) {
        bodyPartsChart.dispose();
      }
      
      bodyPartsChart = echarts.init(bodyPartsChartContainer.value);
      
      // 统计各身体部位的诊断次数
      const bodyPartCounts = {};
      diagnoses.value.forEach(diagnosis => {
        const bodyPart = diagnosis.body_part || 'unknown';
        if (!bodyPartCounts[bodyPart]) {
          bodyPartCounts[bodyPart] = 0;
        }
        bodyPartCounts[bodyPart]++;
      });
      
      // 准备图表数据
      const chartData = Object.entries(bodyPartCounts).map(([bodyPart, count]) => {
        const partName = getBodyPartName(bodyPart);
        return {
          name: partName,
          value: count
        };
      });
      
      const option = {
        tooltip: {
          trigger: 'item',
          formatter: '{b}: {c} 次 ({d}%)'
        },
        legend: {
          orient: 'vertical',
          right: '5%',
          top: 'center',
          itemWidth: 10,
          itemHeight: 10,
          textStyle: {
            fontSize: 10
          }
        },
        series: [
          {
            type: 'pie',
            radius: ['40%', '70%'],
            center: ['40%', '50%'],
            avoidLabelOverlap: false,
            itemStyle: {
              borderRadius: 6,
              borderColor: '#fff',
              borderWidth: 2
            },
            label: {
              show: false
            },
            emphasis: {
              label: {
                show: true,
                fontSize: 12
              }
            },
            labelLine: {
              show: false
            },
            data: chartData
          }
        ]
      };
      
      bodyPartsChart.setOption(option);
      
      window.addEventListener('resize', () => {
        if (bodyPartsChart) {
          bodyPartsChart.resize();
        }
      });
    };
    
    // 生成趋势图表数据
    const generateChartData = (diagnoses, days) => {
      const dates = [];
      const counts = [];
      
      // 生成最近n天的日期数组
      const endDate = new Date();
      for (let i = days - 1; i >= 0; i--) {
        const date = new Date();
        date.setDate(endDate.getDate() - i);
        dates.push(formatDate(date));
        counts.push(0);
      }
      
      // 统计每天的诊断次数
      diagnoses.forEach(diagnosis => {
        const diagnosisDate = new Date(diagnosis.created_at);
        const diffTime = Math.abs(endDate - diagnosisDate);
        const diffDays = Math.floor(diffTime / (1000 * 60 * 60 * 24));
        
        if (diffDays < days) {
          counts[counts.length - 1 - diffDays]++;
        }
      });
      
      return { dates, counts };
    };
    
    // 格式化日期为月/日格式
    const formatDate = (date) => {
      return `${date.getMonth() + 1}/${date.getDate()}`;
    };
    
    // 格式化完整日期时间
    const formatFullDate = (dateStr) => {
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
      const part = COMMON_BODY_PARTS.find(p => p.id === partId);
      return part ? part.name : '未指定部位';
    };
    
    // 获取症状名称列表
    const getSymptomNames = (symptomIds) => {
      return symptomIds.map(id => {
        const symptom = COMMON_SYMPTOMS.find(s => s.id === id);
        return symptom ? symptom.name : '';
      }).filter(Boolean);
    };
    
    // 获取最高概率的诊断结果
    const getTopCondition = (results) => {
      if (!results || results.length === 0) return '无数据';
      
      const sorted = [...results].sort((a, b) => b.probability - a.probability);
      return sorted[0].condition;
    };
    
    // 监听诊断数据变化，更新图表
    watch(diagnoses, () => {
      if (diagnoses.value.length > 0) {
        // 在下一轮事件循环中初始化图表，确保DOM已经渲染
        setTimeout(() => {
          initTrendsChart();
          initBodyPartsChart();
        }, 0);
      }
    });
    
    // 在组件挂载时获取数据
    onMounted(() => {
      fetchDiagnoses();
    });
    
    return {
      userStore,
      diagnoses,
      loading,
      error,
      userInitials,
      recentDiagnosesCount,
      mostCommonSymptom,
      mostCommonCondition,
      commonConditionCount,
      recentDiagnoses,
      trendsChartContainer,
      bodyPartsChartContainer,
      getBodyPartName,
      getSymptomNames,
      getTopCondition,
      formatDate: formatFullDate
    };
  }
};
</script>
