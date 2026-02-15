import axios from 'axios';
import { supabase } from './supabase';

// 创建axios实例 - 确保使用正确的baseURL
const api = axios.create({
  baseURL: '/api',  // 使用相对路径，让Vite的代理能正确转发
  headers: {
    'Content-Type': 'application/json'
  },
  // 增加超时设置，OpenAI API调用可能需要更长的时间
  timeout: 1200000  // 120秒
});

// 创建单独的统计API实例 - 避免凭证和token干扰
const statsApi = axios.create({
  baseURL: '/api/statistics',  // 统计API的基本URL
  headers: {
    'Content-Type': 'application/json',
    'X-Requested-With': 'XMLHttpRequest'
  },
  // 添加超时设置 - 与诊断API保持一致
  timeout: 50000 // 50秒，确保有足够的时间处理大数据集
});

// 添加调试信息用于请求拦截
statsApi.interceptors.request.use(config => {
  console.log('统计API请求:', config.method.toUpperCase(), config.url);
  return config;
}, error => {
  console.error('统计API请求错误:', error);
  return Promise.reject(error);
});

// 添加调试信息用于响应拦截
statsApi.interceptors.response.use(response => {
  console.log('统计API响应状态:', response.status);
  return response;
}, error => {
  console.error('统计API响应错误:', error.response?.status || '未知错误');
  return Promise.reject(error);
});

// 请求拦截器 - 添加授权token
api.interceptors.request.use(async config => {
  const { data } = await supabase.auth.getSession();
  const token = data?.session?.access_token;
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
}, error => {
  return Promise.reject(error);
});

// 症状相关API
export const symptomsApi = {
  // 获取所有症状
  getAll() {
    return api.get('/symptoms');
  },
  
  // 根据身体部位获取症状
  getByBodyPart(bodyPart) {
    return api.get(`/symptoms/bodyPart/${bodyPart}`);
  },
  
  // 创建新症状
  create(symptomData) {
    return api.post('/symptoms', symptomData);
  }
};

// 诊断相关API
export const diagnosesApi = {
  // 获取所有诊断
  getAll() {
    return api.get('/diagnoses');
  },
  
  // 根据ID获取诊断
  getById(id) {
    return api.get(`/diagnoses/${id}`);
  },
  
  // 创建新诊断
  create(diagnosisData) {
    return api.post('/diagnoses', diagnosisData);
  },

  // 预处理: 只运行 symptom_normalizer，返回 optimized_symptoms + rag_keywords
  preprocess(diagnosisData) {
    return api.post('/diagnoses/preprocess', diagnosisData);
  },

  /**
   * 创建诊断 (SSE 流式)
   * @param {object} diagnosisData
   * @param {function} onProgress - (progressEvent) => void
   * @returns {Promise<object>} 最终诊断结果
   */
  async createWithSSE(diagnosisData, onProgress) {
    // 获取 auth token
    const { data: sessionData } = await supabase.auth.getSession();
    const token = sessionData?.session?.access_token;

    const response = await fetch('/api/diagnoses', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Accept: 'text/event-stream',
        ...(token ? { Authorization: `Bearer ${token}` } : {}),
      },
      body: JSON.stringify(diagnosisData),
    });

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }

    return new Promise((resolve, reject) => {
      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let buffer = '';
      let finalResult = null;

      function processLines(text) {
        buffer += text;
        const lines = buffer.split('\n');
        buffer = lines.pop(); // 保留不完整的最后一行

        let currentEvent = '';
        for (const line of lines) {
          if (line.startsWith('event: ')) {
            currentEvent = line.slice(7).trim();
          } else if (line.startsWith('data: ')) {
            const dataStr = line.slice(6);
            try {
              const data = JSON.parse(dataStr);
              if (currentEvent === 'progress' && onProgress) {
                onProgress(data);
              } else if (currentEvent === 'result') {
                finalResult = data;
              } else if (currentEvent === 'error') {
                reject(new Error(data.message || 'Pipeline error'));
              }
            } catch (e) {
              // ignore parse errors in SSE
            }
          }
        }
      }

      (async () => {
        try {
          for (;;) {
            const { done, value } = await reader.read();
            if (done) break;
            processLines(decoder.decode(value, { stream: true }));
          }
          // 处理 buffer 中剩余内容
          if (buffer.trim()) processLines(buffer + '\n');
          if (finalResult) {
            resolve({ data: finalResult });
          } else {
            reject(new Error('No result received from SSE stream'));
          }
        } catch (err) {
          reject(err);
        }
      })();
    });
  }
};

// 用户相关API
export const usersApi = {
  // 用户登录
  login(userData) {
    return api.post('/users/login', userData);
  },
  
  // 用户注册
  register(userData) {
    return api.post('/users', userData);
  },
  
  // 获取用户资料
  getProfile() {
    return api.get('/users/profile');
  }
};

// 统计相关API
export const statisticsApi = {
  // 获取诊断统计数据
  getDiagnosesStats() {
    return statsApi.get('/diagnoses');
  },
  
  // 获取身体部位统计数据
  getBodyPartsStats() {
    return statsApi.get('/bodyparts');
  }
};

// 模型档位
export const modelProfilesApi = {
  getAll() {
    return api.get('/model-profiles');
  }
};

// 训练评测指标
export const metricsApi = {
  getMetrics() {
    return api.get('/metrics');
  }
};

export default {
  symptoms: symptomsApi,
  diagnoses: diagnosesApi,
  users: usersApi,
  statistics: statisticsApi,
  modelProfiles: modelProfilesApi,
  metrics: metricsApi
};
