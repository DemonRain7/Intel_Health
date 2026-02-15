<template>
  <div class="home-container">
    <!-- 英雄区域 -->
    <section class="bg-gradient-to-r from-blue-600 to-indigo-600 text-white py-20">
      <div class="container mx-auto px-4">
        <div class="flex flex-col md:flex-row items-center">
          <div class="md:w-1/2 mb-10 md:mb-0">
            <h1 class="text-4xl md:text-5xl font-bold mb-4 text-gray-900 opacity-90 drop-shadow-lg">
              把健康掌握在你的手中！
            </h1>
            <p class="text-xl mb-8 text-blue-100">
              MediCheck AI比你更了解你的身体症状，还会提供初步诊断意见，包能随时随地守护你的健康！
            </p>
            <div>
              <router-link to="/diagnostic" class="btn btn-primary bg-white text-blue-600 hover:bg-blue-50 mr-4">
                开始诊断
              </router-link>
              <a href="#how-it-works" class="btn border-2 border-white text-white bg-transparent hover:bg-blue-500">
                了解更多
              </a>
            </div>
          </div>
          <div class="md:w-1/2 flex justify-center">
            <div class="rounded-lg bg-white p-2 shadow-lg max-w-md w-full">
              <n-carousel autoplay :interval="3500" draggable show-arrow show-dots dot-type="line" effect="slide" style="height: 240px; border-radius: 8px; overflow: hidden;">
                <!-- Slide 1: 品牌 -->
                <div class="carousel-slide slide-brand">
                  <div class="brand-row">
                    <div class="brand-logo-circle">
                      <svg viewBox="0 0 24 24" fill="none" stroke="#fff" stroke-width="1.5" class="brand-logo-svg">
                        <path d="M12 21a9 9 0 1 0 0-18 9 9 0 0 0 0 18Z"/>
                        <path d="M12 6v6l4 2"/>
                        <path d="M8 12h8" stroke-linecap="round"/>
                        <path d="M12 8v8" stroke-linecap="round"/>
                      </svg>
                    </div>
                    <div class="brand-text">
                      <div class="brand-name">MediCheck AI</div>
                      <div class="brand-tagline">9-Agent Pipeline 智能诊断系统</div>
                    </div>
                  </div>
                  <div class="brand-stats">
                    <div class="brand-stat-item"><span class="brand-stat-num">9</span><span class="brand-stat-label">AI Agents</span></div>
                    <div class="brand-stat-divider"></div>
                    <div class="brand-stat-item"><span class="brand-stat-num">5</span><span class="brand-stat-label">SFT 微调</span></div>
                    <div class="brand-stat-divider"></div>
                    <div class="brand-stat-item"><span class="brand-stat-num">RAG</span><span class="brand-stat-label">知识增强</span></div>
                  </div>
                </div>
                <!-- Slide 2: Pipeline (严格按 diagnosis-graph.mjs 顺序) -->
                <div class="carousel-slide slide-pipeline">
                  <div class="pipeline-header">
                    <span class="pipeline-badge">LangGraph</span>
                    <span class="pipeline-title-text">9-Agent Diagnosis Pipeline</span>
                  </div>
                  <div class="pipeline-grid">
                    <div class="pipe-group">
                      <span class="pipe-num">1</span><span class="pipe-label">症状标准化</span>
                    </div>
                    <span class="pipe-connector"></span>
                    <div class="pipe-group">
                      <span class="pipe-num">2</span><span class="pipe-label">质量评分</span>
                    </div>
                    <span class="pipe-connector"></span>
                    <div class="pipe-group">
                      <span class="pipe-num">3</span><span class="pipe-label">RAG 检索</span>
                    </div>
                    <span class="pipe-connector"></span>
                    <div class="pipe-group">
                      <span class="pipe-num">4</span><span class="pipe-label">相关度评分</span>
                    </div>
                    <span class="pipe-connector"></span>
                    <div class="pipe-group pipe-group-highlight">
                      <span class="pipe-num">5</span><span class="pipe-label">诊断生成</span>
                    </div>
                  </div>
                  <div class="pipeline-grid" style="margin-top: 6px;">
                    <div class="pipe-group">
                      <span class="pipe-num">6</span><span class="pipe-label">证据评分</span>
                    </div>
                    <span class="pipe-connector"></span>
                    <div class="pipe-group">
                      <span class="pipe-num">7</span><span class="pipe-label">用药推荐</span>
                    </div>
                    <span class="pipe-connector"></span>
                    <div class="pipe-group">
                      <span class="pipe-num">8</span><span class="pipe-label">概率校验</span>
                    </div>
                    <span class="pipe-connector"></span>
                    <div class="pipe-group">
                      <span class="pipe-num">9</span><span class="pipe-label">输出格式化</span>
                    </div>
                  </div>
                </div>
                <!-- Slide 3: 混合模型 -->
                <div class="carousel-slide slide-hybrid">
                  <div class="slide-title" style="font-size:18px;">Qwen3 + GPT 混合模式</div>
                  <div class="hybrid-badges">
                    <span class="badge-local">Qwen3-0.6B / 1.7B</span>
                    <span class="badge-plus">+</span>
                    <span class="badge-gpt">GPT-5-mini</span>
                  </div>
                  <div class="slide-subtitle" style="margin-top:12px;">本地推理 + 云端增强，灵活切换</div>
                </div>
              </n-carousel>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- 特点部分 -->
    <section class="py-16 bg-gray-50">
      <div class="container mx-auto px-4">
        <div class="text-center mb-16">
          <h2 class="text-3xl font-bold mb-4">为什么选择 MediCheck AI</h2>
          <p class="text-xl text-gray-600 max-w-3xl mx-auto">
            没什么原因，就是方便！
          </p>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-3 gap-8">
          <div class="bg-white rounded-lg shadow-md p-6 text-center">
            <div class="text-blue-600 mx-auto mb-4">
              <svg class="w-12 h-12 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-3 7h3m-3 4h3m-6-4h.01M9 16h.01"></path>
              </svg>
            </div>
            <h3 class="text-xl font-bold mb-2">智能症状分析</h3>
            <p class="text-gray-600">
              耗时数日打造AI诊断pipeline，让AI诊断流程更为明晰，杜绝LLM幻觉问题的产生！
            </p>
          </div>

          <div class="bg-white rounded-lg shadow-md p-6 text-center">
            <div class="text-blue-600 mx-auto mb-4">
              <svg class="w-12 h-12 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"></path>
              </svg>
            </div>
            <h3 class="text-xl font-bold mb-2">诊断历史跟踪</h3>
            <p class="text-gray-600">
              记录您的健康历史，跟踪症状变化，让您更清晰地了解自己的健康趋势。
            </p>
          </div>

          <div class="bg-white rounded-lg shadow-md p-6 text-center">
            <div class="text-blue-600 mx-auto mb-4">
              <svg class="w-12 h-12 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 18h.01M8 21h8a2 2 0 002-2V5a2 2 0 00-2-2H8a2 2 0 00-2 2v14a2 2 0 002 2z"></path>
              </svg>
            </div>
            <h3 class="text-xl font-bold mb-2">自定义知识检索库</h3>
            <p class="text-gray-600">
              基于无敌的MediCheck AI，无论您是什么科目的医生，都可以自定义医学知识检索库并完美适配诊断流程。
            </p>
          </div>
        </div>
      </div>
    </section>

    <!-- 实际对话案例展示 -->
    <section class="py-16 bg-white">
      <div class="container mx-auto px-4">
        <div class="text-center mb-12">
          <h2 class="text-3xl font-bold mb-4">真实诊断案例</h2>
          <p class="text-xl text-gray-600 max-w-3xl mx-auto">
            看看 MediCheck AI 是如何为用户提供精准诊断的
          </p>
        </div>

        <!-- 案例 1 -->
        <div class="case-card mb-8">
          <div class="case-header">
            <span class="case-badge case-badge-head">头部</span>
            <span class="case-severity severity-medium">中等</span>
            <span class="case-duration">持续 2-3 天</span>
          </div>
          <div class="case-chat">
            <div class="chat-bubble user-bubble">
              <div class="chat-role">用户输入</div>
              <p>最近两天持续头痛，太阳穴两侧胀痛，伴有轻微恶心。平时用电脑比较多，睡眠不太好。</p>
            </div>
            <div class="chat-bubble ai-bubble">
              <div class="chat-role">MediCheck AI Pipeline</div>
              <div class="pipeline-steps-display">
                <span class="mini-step done">症状标准化</span>
                <span class="mini-step done">RAG 检索</span>
                <span class="mini-step done">诊断生成</span>
                <span class="mini-step done">概率校验</span>
                <span class="mini-step done">用药推荐</span>
              </div>
            </div>
            <div class="chat-bubble result-bubble">
              <div class="chat-role">诊断结果</div>
              <div class="result-items">
                <div class="result-item">
                  <div class="result-bar" style="width: 55%"></div>
                  <span class="result-condition">紧张型头痛</span>
                  <span class="result-prob">55.0%</span>
                </div>
                <div class="result-item">
                  <div class="result-bar" style="width: 30%"></div>
                  <span class="result-condition">偏头痛</span>
                  <span class="result-prob">30.0%</span>
                </div>
                <div class="result-item">
                  <div class="result-bar" style="width: 15%"></div>
                  <span class="result-condition">颈源性头痛</span>
                  <span class="result-prob">15.0%</span>
                </div>
              </div>
              <div class="result-advice">
                <strong>建议：</strong>减少屏幕使用时间，保证充足睡眠，必要时服用布洛芬缓解疼痛。如症状持续超过一周请就医。
              </div>
            </div>
          </div>
        </div>

        <!-- 案例 2 -->
        <div class="case-card">
          <div class="case-header">
            <span class="case-badge case-badge-chest">胸部</span>
            <span class="case-severity severity-high">较重</span>
            <span class="case-duration">持续 1 天内</span>
          </div>
          <div class="case-chat">
            <div class="chat-bubble user-bubble">
              <div class="chat-role">用户输入</div>
              <p>今天突然感到胸口闷痛，呼吸的时候有点费劲，偶尔会心悸。最近工作压力比较大，没怎么运动。</p>
            </div>
            <div class="chat-bubble ai-bubble">
              <div class="chat-role">MediCheck AI Pipeline</div>
              <div class="pipeline-steps-display">
                <span class="mini-step done">症状标准化</span>
                <span class="mini-step done">RAG 检索 (3 篇文档)</span>
                <span class="mini-step done">诊断生成</span>
                <span class="mini-step done">概率校验</span>
                <span class="mini-step done">用药推荐</span>
              </div>
            </div>
            <div class="chat-bubble result-bubble">
              <div class="chat-role">诊断结果</div>
              <div class="result-items">
                <div class="result-item">
                  <div class="result-bar" style="width: 45%"></div>
                  <span class="result-condition">焦虑相关胸闷</span>
                  <span class="result-prob">45.0%</span>
                </div>
                <div class="result-item">
                  <div class="result-bar" style="width: 35%"></div>
                  <span class="result-condition">肋间神经痛</span>
                  <span class="result-prob">35.0%</span>
                </div>
                <div class="result-item">
                  <div class="result-bar" style="width: 20%"></div>
                  <span class="result-condition">心肌炎早期</span>
                  <span class="result-prob">20.0%</span>
                </div>
              </div>
              <div class="result-advice">
                <strong>建议：</strong>适当休息，减轻压力。鉴于存在心肌炎可能，建议尽快前往心内科进行心电图和心肌酶检查排除器质性心脏病变。
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- 全站统计数据 -->
    <section class="py-16 bg-gray-50">
      <div class="container mx-auto px-4">
        <div class="text-center mb-12">
          <h2 class="text-3xl font-bold mb-4">全站诊断数据</h2>
          <p class="text-xl text-gray-600 max-w-3xl mx-auto">
            实时统计全平台诊断趋势与症状分布
          </p>
        </div>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-8">
          <div class="stat-chart-card">
            <h3 class="stat-chart-title">近 30 天诊断趋势</h3>
            <div v-if="statsLoading" class="stat-loading">加载中...</div>
            <div v-else-if="statsError" class="stat-error">{{ statsError }}</div>
            <div v-else ref="diagnosisTrendChart" class="stat-chart"></div>
          </div>
          <div class="stat-chart-card">
            <h3 class="stat-chart-title">症状身体部位分布</h3>
            <div v-if="statsLoading" class="stat-loading">加载中...</div>
            <div v-else-if="statsError" class="stat-error">{{ statsError }}</div>
            <div v-else ref="bodyPartsChart" class="stat-chart"></div>
          </div>
        </div>
      </div>
    </section>

    <!-- 工作原理 -->
    <section id="how-it-works" class="py-16 bg-white">
      <div class="container mx-auto px-4">
        <div class="text-center mb-16">
          <h2 class="text-3xl font-bold mb-4">想知道怎么使用 MediCheck AI?</h2>
          <p class="text-xl text-gray-600 max-w-3xl mx-auto">
            别急，Rain来教你！
          </p>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-4 gap-8">
          <div class="text-center">
            <div class="w-16 h-16 bg-blue-600 text-white rounded-full flex items-center justify-center text-2xl font-bold mx-auto mb-4">1</div>
            <h3 class="text-xl font-bold mb-2">选择身体部位</h3>
            <p class="text-gray-600">
              点击您感到不适的身体部位，帮助系统更准确地进行分析。
            </p>
          </div>

          <div class="text-center">
            <div class="w-16 h-16 bg-blue-600 text-white rounded-full flex items-center justify-center text-2xl font-bold mx-auto mb-4">2</div>
            <h3 class="text-xl font-bold mb-2">描述您的症状</h3>
            <p class="text-gray-600">
              选择您正在经历的症状，并评估疼痛程度和持续时间。
            </p>
          </div>

          <div class="text-center">
            <div class="w-16 h-16 bg-blue-600 text-white rounded-full flex items-center justify-center text-2xl font-bold mx-auto mb-4">3</div>
            <h3 class="text-xl font-bold mb-2">AI分析</h3>
            <p class="text-gray-600">
              我优化的AI系统会严谨得分析您的症状，匹配可能的健康状况。
            </p>
          </div>

          <div class="text-center">
            <div class="w-16 h-16 bg-blue-600 text-white rounded-full flex items-center justify-center text-2xl font-bold mx-auto mb-4">4</div>
            <h3 class="text-xl font-bold mb-2">获取结果</h3>
            <p class="text-gray-600">
              查看详细的诊断报告，包括可能的病症和建议的后续步骤。
            </p>
          </div>
        </div>
      </div>
    </section>

    <!-- 免责声明 -->
    <section class="py-16 bg-white">
      <div class="container mx-auto px-4">
        <div class="max-w-3xl mx-auto bg-white rounded-lg shadow-md p-8 border border-gray-100">
          <h2 class="text-2xl font-bold mb-4 text-center">重要免责声明</h2>
          <div class="text-gray-700 whitespace-pre-line">
            {{ disclaimerText }}
          </div>
          <div class="mt-6 text-center">
            <router-link to="/diagnostic" class="btn btn-primary">
              我已了解并开始使用
            </router-link>
          </div>
        </div>
      </div>
    </section>

    <!-- 开始使用 CTA -->
    <section class="py-16 bg-gradient-to-r from-blue-600 to-indigo-600 text-white">
      <div class="container mx-auto px-4 text-center">
        <h2 class="text-3xl font-bold mb-6">快来尝试吧！</h2>
        <p class="text-xl mb-8 max-w-2xl mx-auto">
          我的MediCheck AI可随时为您提供健康分析和建议，帮助您更好地了解自己的身体状况。
        </p>
        <router-link to="/diagnostic" class="btn btn-primary bg-white text-blue-600 hover:bg-blue-50 text-lg px-8 py-3">
          开始免费诊断
        </router-link>
      </div>
    </section>
  </div>
</template>

<script>
import { ref, nextTick, onMounted, onBeforeUnmount } from 'vue';
import { DISCLAIMER_TEXT, COMMON_BODY_PARTS } from '../utils/constants';
import { statisticsApi } from '../utils/api';
import * as echarts from 'echarts';

const BODY_PART_MAP = Object.fromEntries(COMMON_BODY_PARTS.map(p => [p.id, p.name]));

export default {
  name: 'HomePage',
  setup() {
    const disclaimerText = ref(DISCLAIMER_TEXT);

    // 统计数据
    const diagnosisTrendChart = ref(null);
    const bodyPartsChart = ref(null);
    const statsLoading = ref(true);
    const statsError = ref('');
    let trendChartInstance = null;
    let bodyPartsChartInstance = null;

    const fetchAndRenderStats = async () => {
      statsLoading.value = true;
      statsError.value = '';
      try {
        const [trendRes, bodyRes] = await Promise.all([
          statisticsApi.getDiagnosesStats(),
          statisticsApi.getBodyPartsStats(),
        ]);

        // 先关闭 loading 让 chart div 渲染出来，再等 DOM 更新
        statsLoading.value = false;
        await nextTick();

        // 诊断趋势折线图
        if (diagnosisTrendChart.value) {
          trendChartInstance = echarts.init(diagnosisTrendChart.value);
          trendChartInstance.setOption({
            tooltip: { trigger: 'axis' },
            grid: { left: '8%', right: '5%', bottom: '12%', top: '10%', containLabel: true },
            xAxis: {
              type: 'category',
              data: trendRes.data.dates || [],
              axisLabel: { fontSize: 11, interval: 4 },
              boundaryGap: false,
            },
            yAxis: {
              type: 'value',
              minInterval: 1,
              axisLabel: { fontSize: 11 },
            },
            series: [{
              type: 'line',
              data: trendRes.data.counts || [],
              smooth: true,
              symbol: 'circle',
              symbolSize: 6,
              lineStyle: { width: 3, color: '#3b82f6' },
              areaStyle: {
                color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
                  { offset: 0, color: 'rgba(59,130,246,0.25)' },
                  { offset: 1, color: 'rgba(59,130,246,0.02)' },
                ]),
              },
              itemStyle: { color: '#3b82f6' },
            }],
          });
        }

        // 身体部位饼图
        if (bodyPartsChart.value) {
          const pieData = (bodyRes.data || []).map(item => ({
            name: BODY_PART_MAP[item.name] || item.name,
            value: item.value,
          }));
          bodyPartsChartInstance = echarts.init(bodyPartsChart.value);
          bodyPartsChartInstance.setOption({
            tooltip: { trigger: 'item', formatter: '{b}: {c} ({d}%)' },
            legend: {
              orient: 'vertical',
              right: '5%',
              top: 'center',
              textStyle: { fontSize: 12 },
            },
            color: ['#3b82f6', '#ef4444', '#f59e0b', '#10b981', '#8b5cf6', '#ec4899', '#06b6d4', '#64748b'],
            series: [{
              type: 'pie',
              radius: ['40%', '70%'],
              center: ['40%', '50%'],
              avoidLabelOverlap: true,
              label: { show: false },
              emphasis: {
                label: { show: true, fontSize: 14, fontWeight: 'bold' },
              },
              data: pieData,
            }],
          });
        }
      } catch (e) {
        console.error('统计数据加载失败:', e);
        statsError.value = '统计数据加载失败，请稍后刷新';
      } finally {
        statsLoading.value = false;
      }
    };

    const handleResize = () => {
      trendChartInstance?.resize();
      bodyPartsChartInstance?.resize();
    };

    onMounted(() => {
      fetchAndRenderStats();
      window.addEventListener('resize', handleResize);
    });

    onBeforeUnmount(() => {
      window.removeEventListener('resize', handleResize);
      trendChartInstance?.dispose();
      bodyPartsChartInstance?.dispose();
      trendChartInstance = null;
      bodyPartsChartInstance = null;
    });

    return {
      disclaimerText,
      diagnosisTrendChart,
      bodyPartsChart,
      statsLoading,
      statsError,
    };
  }
};
</script>

<style scoped>
.home-container {
  margin: 0;
  padding: 0;
}

/* ---- 轮播图 Slide 样式 ---- */
.carousel-slide {
  height: 240px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 20px;
  border-radius: 8px;
  user-select: none;
}

.slide-brand {
  background: linear-gradient(135deg, #1e3a5f 0%, #1e40af 50%, #3b82f6 100%);
}
.slide-pipeline {
  background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
}
.slide-hybrid {
  background: linear-gradient(135deg, #ede9fe 0%, #c4b5fd 50%, #dbeafe 100%);
}

/* ---- Slide 1: Brand ---- */
.brand-row {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 20px;
}

.brand-logo-circle {
  width: 52px;
  height: 52px;
  border-radius: 50%;
  background: rgba(255,255,255,0.15);
  backdrop-filter: blur(4px);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  border: 2px solid rgba(255,255,255,0.3);
}

.brand-logo-svg {
  width: 28px;
  height: 28px;
}

.brand-text {
  text-align: left;
}

.brand-name {
  font-size: 26px;
  font-weight: 800;
  color: #fff;
  letter-spacing: -0.5px;
  line-height: 1.1;
}

.brand-tagline {
  font-size: 13px;
  color: rgba(255,255,255,0.7);
  margin-top: 4px;
}

.brand-stats {
  display: flex;
  align-items: center;
  gap: 16px;
  background: rgba(255,255,255,0.1);
  border-radius: 12px;
  padding: 10px 20px;
  backdrop-filter: blur(4px);
}

.brand-stat-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 2px;
}

.brand-stat-num {
  font-size: 18px;
  font-weight: 800;
  color: #fff;
}

.brand-stat-label {
  font-size: 11px;
  color: rgba(255,255,255,0.65);
}

.brand-stat-divider {
  width: 1px;
  height: 28px;
  background: rgba(255,255,255,0.2);
}

/* ---- Slide 2: Pipeline ---- */
.pipeline-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 14px;
}

.pipeline-badge {
  background: #3b82f6;
  color: #fff;
  padding: 3px 10px;
  border-radius: 10px;
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.5px;
}

.pipeline-title-text {
  font-size: 16px;
  font-weight: 700;
  color: #e2e8f0;
}

.pipeline-grid {
  display: flex;
  align-items: center;
  gap: 3px;
  flex-wrap: wrap;
  justify-content: center;
}

.pipe-group {
  display: flex;
  align-items: center;
  gap: 4px;
  background: rgba(255,255,255,0.08);
  border: 1px solid rgba(255,255,255,0.12);
  border-radius: 8px;
  padding: 4px 8px;
}

.pipe-group-highlight {
  background: rgba(59,130,246,0.25);
  border-color: rgba(59,130,246,0.5);
}

.pipe-num {
  font-size: 10px;
  font-weight: 800;
  color: #60a5fa;
  background: rgba(59,130,246,0.2);
  width: 18px;
  height: 18px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.pipe-label {
  font-size: 11px;
  font-weight: 500;
  color: #cbd5e1;
  white-space: nowrap;
}

.pipe-connector {
  width: 10px;
  height: 2px;
  background: rgba(96,165,250,0.4);
  border-radius: 1px;
}

/* ---- Slide 3 (unchanged) ---- */
.slide-title {
  font-size: 24px;
  font-weight: 700;
  color: #1e40af;
  margin-bottom: 4px;
}

.slide-subtitle {
  font-size: 14px;
  color: #64748b;
}

.hybrid-badges {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-top: 16px;
}

.badge-local {
  background: #1e40af;
  color: #fff;
  padding: 6px 14px;
  border-radius: 20px;
  font-size: 13px;
  font-weight: 600;
}

.badge-gpt {
  background: #059669;
  color: #fff;
  padding: 6px 14px;
  border-radius: 20px;
  font-size: 13px;
  font-weight: 600;
}

.badge-plus {
  font-size: 20px;
  font-weight: 700;
  color: #94a3b8;
}

/* ---- 案例展示样式 ---- */
.case-card {
  max-width: 800px;
  margin: 0 auto;
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 16px;
  overflow: hidden;
}

.case-header {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 14px 20px;
  background: #f1f5f9;
  border-bottom: 1px solid #e2e8f0;
}

.case-badge {
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 13px;
  font-weight: 600;
  color: #fff;
}

.case-badge-head { background: #3b82f6; }
.case-badge-chest { background: #ef4444; }
.case-badge-abdomen { background: #f59e0b; }

.case-severity {
  padding: 3px 10px;
  border-radius: 10px;
  font-size: 12px;
  font-weight: 500;
}
.severity-medium { background: #fef3c7; color: #92400e; }
.severity-high { background: #fee2e2; color: #991b1b; }

.case-duration {
  font-size: 13px;
  color: #64748b;
  margin-left: auto;
}

.case-chat {
  padding: 16px 20px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.chat-bubble {
  padding: 12px 16px;
  border-radius: 12px;
  max-width: 90%;
}

.chat-role {
  font-size: 11px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  margin-bottom: 6px;
}

.user-bubble {
  background: #dbeafe;
  align-self: flex-end;
  border-bottom-right-radius: 4px;
}
.user-bubble .chat-role { color: #1e40af; }
.user-bubble p { color: #1e3a5f; font-size: 14px; margin: 0; line-height: 1.6; }

.ai-bubble {
  background: #f0fdf4;
  border: 1px solid #bbf7d0;
  align-self: flex-start;
  border-bottom-left-radius: 4px;
}
.ai-bubble .chat-role { color: #166534; }

.pipeline-steps-display {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.mini-step {
  padding: 3px 10px;
  border-radius: 10px;
  font-size: 11px;
  font-weight: 500;
  background: #dcfce7;
  color: #166534;
  border: 1px solid #bbf7d0;
}

.mini-step.done::before {
  content: '\2713 ';
}

.result-bubble {
  background: #fff;
  border: 1px solid #e2e8f0;
  align-self: flex-start;
  width: 100%;
  max-width: 100%;
  border-bottom-left-radius: 4px;
}
.result-bubble .chat-role { color: #1e40af; }

.result-items {
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin-bottom: 12px;
}

.result-item {
  display: flex;
  align-items: center;
  gap: 8px;
  position: relative;
  height: 28px;
  background: #f1f5f9;
  border-radius: 6px;
  overflow: hidden;
}

.result-bar {
  position: absolute;
  left: 0;
  top: 0;
  height: 100%;
  background: linear-gradient(90deg, #3b82f6, #60a5fa);
  border-radius: 6px;
  opacity: 0.2;
}

.result-condition {
  position: relative;
  z-index: 1;
  font-size: 13px;
  font-weight: 600;
  color: #1e293b;
  padding-left: 10px;
}

.result-prob {
  position: relative;
  z-index: 1;
  margin-left: auto;
  font-size: 13px;
  font-weight: 700;
  color: #3b82f6;
  padding-right: 10px;
}

.result-advice {
  font-size: 13px;
  color: #475569;
  line-height: 1.6;
  padding: 10px 12px;
  background: #fffbeb;
  border-radius: 8px;
  border-left: 3px solid #f59e0b;
}

/* ---- 统计图表卡片 ---- */
.stat-chart-card {
  background: #fff;
  border: 1px solid #e2e8f0;
  border-radius: 16px;
  padding: 20px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.06);
}

.stat-chart-title {
  font-size: 16px;
  font-weight: 700;
  color: #1e293b;
  margin-bottom: 16px;
  padding-bottom: 10px;
  border-bottom: 2px solid #3b82f6;
  display: inline-block;
}

.stat-chart {
  width: 100%;
  height: 280px;
}

.stat-loading,
.stat-error {
  height: 280px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #94a3b8;
  font-size: 14px;
}

.stat-error {
  color: #ef4444;
}
</style>
