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
            
            <div class="rounded-lg bg-white p-2 shadow-lg max-w-md">
              <n-carousel 
  autoplay 
  :interval="3000" 
  :mousewheel="true" 
  :draggable="true" 
  @update:current="handleSlideChange"
>
  <img class="carousel-img" src="https://placehold.co/600x400/ffffff/1976d2.png?text=MediCheck+AI" alt="MediCheck AI界面预览"/>
  <div class="carousel-img chart-slide">
    <div ref="diagnosisChartContainer" class="chart-container">
      <div v-if="!hasInitializedChart" class="chart-loading">
        <div class="loading-spinner"></div>
        <div class="loading-text">正在加载诊断统计数据...</div>
      </div>
    </div>
  </div>
  <img class="carousel-img" src="https://placehold.co/600x400/ffffff/1976d2.png?text=MediCheck+AI" alt="MediCheck AI界面预览"/>
  <div class="carousel-img chart-slide">
    <div ref="bodyPartsChartContainer" class="chart-container">
      <div v-if="!hasInitializedBodyPartsChart" class="chart-loading">
        <div class="loading-spinner"></div>
        <div class="loading-text">正在加载身体部位统计数据...</div>
      </div>
    </div>
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
    
    <!-- 模型训练提升 -->
    <section class="py-16 bg-white">
      <div class="container mx-auto px-4">
        <div class="text-center mb-12">
          <h2 class="text-3xl font-bold mb-4">模型训练提升</h2>
          <p class="text-xl text-gray-600 max-w-3xl mx-auto">
            训练前后输出稳定性对比（JSON 合法率与关键词覆盖率）
          </p>
        </div>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-8">
          <div class="bg-white rounded-lg shadow-md p-4">
            <h3 class="text-lg font-semibold mb-3 text-gray-700">JSON 合法率</h3>
            <div ref="trainingJsonChartContainer" class="metrics-chart"></div>
          </div>
          <div class="bg-white rounded-lg shadow-md p-4">
            <h3 class="text-lg font-semibold mb-3 text-gray-700">关键词覆盖率</h3>
            <div ref="trainingKeywordChartContainer" class="metrics-chart"></div>
          </div>
        </div>
      </div>
    </section>

    <!-- 工作原理 -->
    <section id="how-it-works" class="py-16">
      <div class="container mx-auto px-4">
        <div class="text-center mb-16">
          <h2 class="text-3xl font-bold mb-4">想知道怎么使用 MediCheck AI?</h2>
          <p class="text-xl text-gray-600 max-w-3xl mx-auto">
            别急，西园7舍2单元301A邱宇来教你！
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
    <section class="py-16 bg-gray-50">
      <div class="container mx-auto px-4">
        <div class="max-w-3xl mx-auto bg-white rounded-lg shadow-md p-8">
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
import { ref, onMounted, onBeforeUnmount } from 'vue';
import { DISCLAIMER_TEXT } from '../utils/constants';
import trainingMetrics from '../assets/metrics/training_metrics.json';
import * as echarts from 'echarts';
import axios from 'axios';

export default {
  name: 'HomePage',
  setup() {
    const disclaimerText = ref(DISCLAIMER_TEXT);
    
    // 折线图相关
    const diagnosisChartContainer = ref(null);
    let diagnosisChart = null;
    const diagnoses = ref([]);
    const hasInitializedChart = ref(false);
    
    // 饼图相关
    const bodyPartsChartContainer = ref(null);
    const trainingJsonChartContainer = ref(null);
    const trainingKeywordChartContainer = ref(null);
    let trainingJsonChart = null;
    let trainingKeywordChart = null;

    let bodyPartsChart = null;
    const bodyParts = ref([]);
    const hasInitializedBodyPartsChart = ref(false);

    const handleCarouselChange = async (index) => {
      console.log('轮播图切换到索引:', index);
      
      // 使用修改后的更通用的轮播项检测方法
      const activeSlideIndex = detectActiveSlide();
      console.log('检测到活动轮播项索引:', activeSlideIndex);
      
      if (index === 1 || activeSlideIndex === 1) {
        try {
          console.log('轮播切换到诊断图表');
          
          // 确保DOM已经更新
          await new Promise(resolve => setTimeout(resolve, 300));
          
          // 检查容器是否存在
          if (!diagnosisChartContainer.value) {
            console.error('诊断图表容器不存在，请检查引用');
          } else {
            console.log('诊断图表容器尺寸:', 
              diagnosisChartContainer.value.offsetWidth, 'x', 
              diagnosisChartContainer.value.offsetHeight);
          }
          
          // 无论是否已初始化，当切换到图表轮播项时都尝试初始化或重绘图表
          if (diagnoses.value.dates && diagnoses.value.counts) {
            console.log('已有诊断数据，初始化/更新图表');
            
            // 确保DOM容器渲染完毕后再初始化图表
            setTimeout(() => {
              // 确保容器有宽高
              if (diagnosisChartContainer.value) {
                diagnosisChartContainer.value.style.width = '100%';
                diagnosisChartContainer.value.style.height = '240px';
                diagnosisChartContainer.value.style.backgroundColor = '#ffffff';
              }
              
              initDiagnosisChart();
              hasInitializedChart.value = true;
            }, 300);
          } else {
            console.log('轮播切换到诊断图表，但数据尚未就绪，尝试获取...');
            // 尝试立即获取数据
            const success = await fetchDiagnoses();
            if (success) {
              setTimeout(() => {
                initDiagnosisChart();
                hasInitializedChart.value = true;
              }, 300);
            } else {
              console.error('获取诊断统计数据失败');
            }
          }
        } catch (error) {
          console.error('诊断图表轮播切换处理错误:', error);
        }
      } else if (index === 2 || activeSlideIndex === 2) {
        try {
          console.log('轮播切换到身体部位图表');
          
          // 确保DOM已经更新 - 增加延迟确保完全渲染
          await new Promise(resolve => setTimeout(resolve, 300));
          
          // 检查容器是否存在
          if (!bodyPartsChartContainer.value) {
            console.error('身体部位图表容器不存在，请检查引用');
          } else {
            console.log('身体部位图表容器尺寸:', 
              bodyPartsChartContainer.value.offsetWidth, 'x', 
              bodyPartsChartContainer.value.offsetHeight);
          }
          
          // 无论之前状态如何，都重新获取身体部位数据以确保最新
          console.log('重新获取身体部位数据...');
          try {
            const success = await fetchBodyParts();
            console.log('获取身体部位数据结果:', success ? '成功' : '失败');
            
            if (success && bodyParts.value && bodyParts.value.length > 0) {
              console.log('获取到有效身体部位数据，初始化图表...');
              
              // 确保DOM容器渲染完毕后再初始化图表
              setTimeout(() => {
                // 确保容器有宽高
                if (bodyPartsChartContainer.value) {
                  bodyPartsChartContainer.value.style.width = '100%';
                  bodyPartsChartContainer.value.style.height = '240px';
                  bodyPartsChartContainer.value.style.backgroundColor = '#ffffff';
                }
                
                initBodyPartsChart();
                hasInitializedBodyPartsChart.value = true;
              }, 300);
            } else {
              console.error('无法获取有效的身体部位数据');
            }
          } catch (apiError) {
            console.error('API调用失败:', apiError);
          }
        } catch (error) {
          console.error('身体部位图表轮播切换处理错误:', error);
        }
      }
    };
    
    // 检测当前激活的轮播项
    const detectActiveSlide = () => {
      const carousel = document.querySelector('.n-carousel');
      if (!carousel) return -1;
      
      // 尝试从当前激活的轮播项类名获取索引
      const activeSlide = carousel.querySelector('.n-carousel__slide--current');
      if (activeSlide) {
        const slides = Array.from(carousel.querySelectorAll('.n-carousel__slide'));
        return slides.indexOf(activeSlide);
      }
      
      // 尝试从属性获取索引
      const attrIndex = carousel.getAttribute('current');
      if (attrIndex !== null) {
        return parseInt(attrIndex);
      }
      
      // 无法确定当前轮播项
      return -1;
    };

    // 获取诊断统计数据
    const fetchDiagnoses = async () => {
      try {
        console.log('正在获取诊断统计数据...');
        
        // 使用完整的URL路径而不是相对路径
        const apiUrl = `/api/statistics/diagnoses`;
        console.log('正在请求API:', apiUrl);
        
        // 添加更多的请求信息帮助调试
        const response = await axios.get(apiUrl, {
          headers: { 'X-Requested-With': 'XMLHttpRequest' },
          timeout: 10000 // 10秒超时
        });
        
        console.log('获取到的统计数据:', response.data);
        
        if (response.data && response.data.dates && response.data.counts) {
          console.log('诊断数据有效:', 
                      '日期数量:', response.data.dates.length, 
                      '数据点数量:', response.data.counts.length);
                      
          // 使用服务器返回的统计数据
          diagnoses.value = response.data;
          
          // 详细记录轮播组件状态和属性 - 用于调试诊断图表
          const carousel = document.querySelector('.n-carousel');
          
          if (carousel) {
            console.log('诊断图表: 轮播组件找到，检查属性:');
            console.log('  - current 属性:', carousel.getAttribute('current'));
            
            // 尝试检查子元素以判断当前激活的轮播项
            const activeSlide = carousel.querySelector('.n-carousel__slide--current');
            if (activeSlide) {
              console.log('  - 发现活动轮播项索引:', 
                Array.from(carousel.querySelectorAll('.n-carousel__slide')).indexOf(activeSlide));
            }
          }
          
          return true; // 数据获取成功
        } else {
          console.error('返回的统计数据格式不正确:', response.data);
          return false;
        }
      } catch (error) {
        console.error('获取诊断统计数据失败:', error);
        
        // 如果API请求失败，使用空数据初始化图表
        console.warn('使用空数据初始化图表，等待API可用');
        diagnoses.value = {
          dates: [],
          counts: []
        };
        
        return false; // 数据获取失败
      }
    };

    // 生成图表数据
    const generateChartData = (diagnoses, days) => {
      const today = new Date();
      const dateLabels = [];
      const counts = [];
      
      // 生成过去days天的日期标签
      for (let i = days - 1; i >= 0; i--) {
        const date = new Date(today);
        date.setDate(today.getDate() - i);
        const dateStr = `${date.getMonth() + 1}/${date.getDate()}`;
        dateLabels.push(dateStr);
        counts.push(0); // 初始化计数为0
      }
      
      // 统计每天的诊断数量
      diagnoses.forEach(diagnosis => {
        const diagnosisDate = new Date(diagnosis.created_at);
        const daysDiff = Math.floor((today - diagnosisDate) / (1000 * 60 * 60 * 24));
        
        // 只统计在范围内的日期
        if (daysDiff >= 0 && daysDiff < days) {
          counts[days - 1 - daysDiff]++;
        }
      });
      
      return {
        dateLabels,
        counts
      };
    };

    // 初始化诊断数量折线图
    const initDiagnosisChart = () => {
      if (!diagnosisChartContainer.value) {
        console.error('图表容器引用不存在');
        return;
      }
      
      // 确保容器已经渲染并有尺寸
      const container = diagnosisChartContainer.value;
      
      // 强制设置容器尺寸，确保能够正确渲染
      container.style.width = '100%';
      container.style.height = '240px';
      
      if (container.offsetHeight === 0 || container.offsetWidth === 0) {
        console.log('图表容器尺寸仍为0，延迟300ms初始化');
        setTimeout(initDiagnosisChart, 300);
        return;
      }
      
      // 如果已有图表实例，先销毁
      if (diagnosisChart) {
        try {
          diagnosisChart.dispose();
        } catch (e) {
          console.error('销毁旧图表实例失败:', e);
        }
        diagnosisChart = null;
      }
      
      try {
        console.log('初始化图表容器尺寸:', container.offsetWidth, 'x', container.offsetHeight);
        diagnosisChart = echarts.init(container);
        
        // 确保诊断数据存在
        if (!diagnoses.value.dates || !diagnoses.value.counts) {
          console.warn('图表数据不完整，显示空图表');
        }
        
        const option = {
          title: {
            text: '平台诊断数量统计',
            textStyle: {
              fontSize: 14
            }
          },
          tooltip: {
            trigger: 'axis',
            formatter: '{b}: {c} 次诊断'
          },
          xAxis: {
            type: 'category',
            data: diagnoses.value.dates || [],
            axisLabel: {
              rotate: 45,
              fontSize: 10,
              interval: 'auto'
            }
          },
          yAxis: {
            type: 'value',
            minInterval: 1,
            axisLabel: {
              fontSize: 10
            }
          },
          series: [
            {
              data: diagnoses.value.counts || [],
              type: 'line',
              smooth: true,
              name: '诊断数量',
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
                    {
                      offset: 0, 
                      color: 'rgba(25, 118, 210, 0.5)'
                    },
                    {
                      offset: 1, 
                      color: 'rgba(25, 118, 210, 0.1)'
                    }
                  ]
                }
              }
            }
          ],
          grid: {
            left: '10%',
            right: '5%',
            bottom: '15%',
            containLabel: true
          }
        };
        
        diagnosisChart.setOption(option);
        console.log('图表初始化成功!');
        
        // 确保图表在轮播显示后更新大小
        setTimeout(() => {
          if (diagnosisChart) {
            diagnosisChart.resize();
            console.log('图表大小已更新');
          }
        }, 100);
        
      } catch (error) {
        console.error('初始化图表发生错误:', error);
        hasInitializedChart.value = false;
      }
    };

    // 获取身体部位统计数据
    const fetchBodyParts = async () => {
      try {
        console.log('正在获取身体部位统计数据...');
        // 使用完整的URL路径而不是相对路径
        const apiUrl = `/api/statistics/bodyparts`;
        console.log('正在请求API:', apiUrl);
        
        // 添加更多的请求信息帮助调试
        const response = await axios.get(apiUrl, {
          headers: { 'X-Requested-With': 'XMLHttpRequest' },
          timeout: 10000 // 10秒超时
        });
        
        console.log('获取到的身体部位统计数据:', response.data);
        
        if (response.data && Array.isArray(response.data) && response.data.length > 0) {
          console.log('数据有效，处理返回的', response.data.length, '条记录');
          // 将人类可读的身体部位名称添加到数据中
          bodyParts.value = response.data.map(item => {
            return {
              ...item,
              displayName: getBodyPartDisplayName(item.name)
            };
          });
          
          // 测试所有可能的属性和值，以找出正确的索引方式
          const carousel = document.querySelector('.n-carousel');
          
          // 详细记录轮播组件状态和属性
          if (carousel) {
            console.log('轮播组件找到，检查属性:');
            console.log('  - current 属性:', carousel.getAttribute('current'));
            console.log('  - data-current 属性:', carousel.getAttribute('data-current'));
            console.log('  - data-index 属性:', carousel.getAttribute('data-index'));
            
            // 尝试检查子元素以判断当前激活的轮播项
            const activeSlide = carousel.querySelector('.n-carousel__slide--current');
            if (activeSlide) {
              console.log('  - 发现活动轮播项:', activeSlide);
              console.log('  - 活动轮播项索引:', Array.from(carousel.querySelectorAll('.n-carousel__slide')).indexOf(activeSlide));
            }
            
            // 直接检查轮播项状态
            const allSlides = carousel.querySelectorAll('.n-carousel__slide');
            console.log('  - 轮播项数量:', allSlides.length);
            allSlides.forEach((slide, i) => {
              console.log(`  - 轮播项 ${i} 的类名:`, slide.className);
            });
          } else {
            console.log('轮播组件未找到');
          }
          
          // 我们现在不依赖轮播索引来初始化，采用单独的处理函数
          
          return true; // 数据获取成功
        } else {
          console.error('返回的身体部位统计数据格式不正确:', response.data);
          return false;
        }
      } catch (error) {
        console.error('获取身体部位统计数据失败:', error);
        
        // 如果API请求失败，使用空数据初始化图表
        console.warn('使用空数据初始化身体部位图表，等待API可用');
        bodyParts.value = [];
        
        return false; // 数据获取失败
      }
    };
    
    // 获取身体部位的显示名称
    const getBodyPartDisplayName = (bodyPart) => {
      // 根据我们的测试数据添加映射
      const bodyPartMap = {
        'head': '头部',
        'chest': '胸部',
        'abdomen': '腹部',
        'back': '背部',
        'limbs': '四肢',
        'throat': '喉咙',
        'skin': '皮肤',
        'general': '全身',
        'unknown': '未知部位'
      };
      
      return bodyPartMap[bodyPart] || bodyPart;
    };
    
    // 初始化身体部位饼状图
    const initBodyPartsChart = () => {
      console.log('开始初始化身体部位饼状图...');
      
      // 检查引用和数据
      if (!bodyPartsChartContainer.value) {
        console.error('身体部位图表容器引用不存在');
        return;
      }
      
      if (!bodyParts.value || !Array.isArray(bodyParts.value) || bodyParts.value.length === 0) {
        console.error('身体部位数据无效:', bodyParts.value);
        return;
      }
      
      // 确保容器已经渲染并有尺寸
      const container = bodyPartsChartContainer.value;
      
      // 强制设置容器尺寸，确保能够正确渲染
      container.style.width = '100%';
      container.style.height = '240px';
      container.style.backgroundColor = '#ffffff';
      
      console.log('设置的容器尺寸: 100% x 240px');
      console.log('容器当前实际尺寸:', container.offsetWidth, 'x', container.offsetHeight);
      
      if (container.offsetHeight === 0 || container.offsetWidth === 0) {
        console.log('身体部位图表容器尺寸仍为0，延迟500ms初始化');
        setTimeout(initBodyPartsChart, 500);
        return;
      }
      
      // 如果已有图表实例，先销毁
      if (bodyPartsChart) {
        try {
          console.log('销毁已有图表实例');
          bodyPartsChart.dispose();
        } catch (e) {
          console.error('销毁旧身体部位图表实例失败:', e);
        }
        bodyPartsChart = null;
      }
      
      try {
        console.log('初始化身体部位图表，容器尺寸:', container.offsetWidth, 'x', container.offsetHeight);
        console.log('使用数据:', JSON.stringify(bodyParts.value));
        
        // 确保容器在DOM中并且可见
        if (container.offsetParent === null) {
          console.error('容器不可见，可能未添加到DOM或被隐藏');
          // 尝试延迟重试
          setTimeout(initBodyPartsChart, 1000);
          return;
        }
        
        // 创建新实例
        bodyPartsChart = echarts.init(container);
        
        // 生成饼图的颜色列表
        const colors = [
          '#1976D2', '#2196F3', '#64B5F6', '#BBDEFB', '#42A5F5',
          '#2979FF', '#448AFF', '#82B1FF', '#0D47A1', '#1A237E'
        ];
        
        // 确保有数据可用于图表
        const chartData = bodyParts.value.map((item, index) => ({
          name: item.displayName || item.name || `未知部位${index + 1}`,
          value: item.value || 0,
          itemStyle: {
            color: colors[index % colors.length]
          }
        }));
        
        console.log('处理后的图表数据:', JSON.stringify(chartData));
        
        const option = {
          title: {
            text: '患者问诊身体部位分布',
            textStyle: {
              fontSize: 14
            }
          },
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
                show: false,
                position: 'center'
              },
              emphasis: {
                label: {
                  show: true,
                  fontSize: 12,
                  fontWeight: 'bold'
                }
              },
              labelLine: {
                show: false
              },
              data: chartData
            }
          ]
        };
        
        // 设置图表选项
        bodyPartsChart.setOption(option);
        console.log('身体部位图表初始化成功!');
        
        // 确保图表在轮播显示后更新大小
        setTimeout(() => {
          if (bodyPartsChart) {
            bodyPartsChart.resize();
            console.log('身体部位图表大小已更新');
            
            // 第二次更新以确保图表正确显示
            setTimeout(() => {
              if (bodyPartsChart) {
                bodyPartsChart.resize();
              }
            }, 200);
          }
        }, 100);
        
        // 标记初始化成功
        hasInitializedBodyPartsChart.value = true;
        
      } catch (error) {
        console.error('初始化身体部位图表发生错误:', error);
        hasInitializedBodyPartsChart.value = false;
      }
    };

    // 训练前后对比图表
    const initTrainingCharts = () => {
      if (!trainingJsonChartContainer.value || !trainingKeywordChartContainer.value) {
        return;
      }

      const labels = trainingMetrics.labels || ['base', 'finetuned'];
      const jsonValues = trainingMetrics.json_valid_rate || [0, 0];
      const keywordValues = trainingMetrics.keyword_coverage || [0, 0];

      const buildBarOption = (title, values, color) => ({
        title: {
          text: title,
          textStyle: { fontSize: 14 }
        },
        tooltip: { trigger: 'axis' },
        xAxis: { type: 'category', data: labels },
        yAxis: { type: 'value', min: 0, max: 1 },
        series: [
          {
            type: 'bar',
            data: values,
            itemStyle: { color }
          }
        ],
        grid: { left: '10%', right: '5%', bottom: '12%', containLabel: true }
      });

      if (trainingJsonChart) {
        trainingJsonChart.dispose();
      }
      if (trainingKeywordChart) {
        trainingKeywordChart.dispose();
      }

      trainingJsonChart = echarts.init(trainingJsonChartContainer.value);
      trainingJsonChart.setOption(buildBarOption('JSON 合法率', jsonValues, '#1976d2'));

      trainingKeywordChart = echarts.init(trainingKeywordChartContainer.value);
      trainingKeywordChart.setOption(buildBarOption('关键词覆盖率', keywordValues, '#42a5f5'));
    };
    
    // 窗口大小变化时重绘图表
    const handleResize = () => {
      if (diagnosisChart) {
        diagnosisChart.resize();
      }
      if (bodyPartsChart) {
        bodyPartsChart.resize();
      }
      if (trainingJsonChart) {
        trainingJsonChart.resize();
      }
      if (trainingKeywordChart) {
        trainingKeywordChart.resize();
      }
    };

    onMounted(() => {
      initTrainingCharts();
      // 获取诊断统计数据并在就绪后尝试初始化图表
      fetchDiagnoses().then(() => {
        console.log('组件挂载后诊断数据获取完成，尝试初始化图表');
        // 延迟初始化以确保DOM完全就绪
        setTimeout(() => {
          if (diagnoses.value.dates && diagnoses.value.counts) {
            console.log('在mounted hook中初始化诊断图表');
            initDiagnosisChart();
            hasInitializedChart.value = true;
          }
        }, 500);
      });
      
      // 获取身体部位统计数据
      fetchBodyParts().then(() => {
        console.log('组件挂载后身体部位数据获取完成，尝试初始化图表');
        // 延迟初始化以确保DOM完全就绪
        setTimeout(() => {
          if (bodyParts.value && bodyParts.value.length > 0) {
            console.log('在mounted hook中初始化身体部位图表');
            initBodyPartsChart();
            hasInitializedBodyPartsChart.value = true;
          }
        }, 500);
      });
      
      window.addEventListener('resize', handleResize);
    });

    onBeforeUnmount(() => {
      window.removeEventListener('resize', handleResize);
      if (diagnosisChart) {
        diagnosisChart.dispose();
        diagnosisChart = null;
      }
      if (bodyPartsChart) {
        bodyPartsChart.dispose();
        bodyPartsChart = null;
      }
      if (trainingJsonChart) {
        trainingJsonChart.dispose();
        trainingJsonChart = null;
      }
      if (trainingKeywordChart) {
        trainingKeywordChart.dispose();
        trainingKeywordChart = null;
      }
    });
    
    return {
      disclaimerText,
      diagnosisChartContainer, // 向模板暴露诊断图表容器引用
      bodyPartsChartContainer, // 向模板暴露身体部位图表容器引用
      trainingJsonChartContainer,
      trainingKeywordChartContainer,
      handleSlideChange: handleCarouselChange,
      hasInitializedChart,
      hasInitializedBodyPartsChart
    };
  }
};
</script>

<style scoped>
.home-container {
  margin: 0;
  padding: 0;
}
</style>

<style scoped>
.carousel-img {
  width: 100%;
  height: 240px;
  object-fit: cover;
  position: relative;
}

.chart-slide {
  display: flex;
  justify-content: center;
  align-items: center;
}

.chart-container {
  width: 100%;
  height: 100%;
  min-height: 240px;
  position: relative;
  background-color: #fff;
}

.metrics-chart {
  width: 100%;
  height: 260px;
}

.chart-loading {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  background-color: rgba(255, 255, 255, 0.9);
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 4px solid rgba(25, 118, 210, 0.2);
  border-top: 4px solid #1976d2;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 12px;
}

.loading-text {
  font-size: 14px;
  color: #1976d2;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}
</style>
