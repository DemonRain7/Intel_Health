// 常见身体部位
export const COMMON_BODY_PARTS = [
  { id: 'head', name: '头部', icon: 'head-icon' },
  { id: 'chest', name: '胸部', icon: 'chest-icon' },
  { id: 'abdomen', name: '腹部', icon: 'abdomen-icon' },
  { id: 'back', name: '背部', icon: 'back-icon' },
  { id: 'arms', name: '手臂', icon: 'arms-icon' },
  { id: 'legs', name: '腿部', icon: 'legs-icon' },
  { id: 'skin', name: '皮肤', icon: 'skin-icon' },
  { id: 'general', name: '全身', icon: 'general-icon' }
];

// 常见症状列表
export const COMMON_SYMPTOMS = [
  { id: 'headache', name: '头痛', bodyPart: 'head' },
  { id: 'dizziness', name: '头晕', bodyPart: 'head' },
  { id: 'fever', name: '发热', bodyPart: 'general' },
  { id: 'fatigue', name: '疲劳', bodyPart: 'general' },
  { id: 'cough', name: '咳嗽', bodyPart: 'chest' },
  { id: 'shortnessOfBreath', name: '呼吸短促', bodyPart: 'chest' },
  { id: 'chestPain', name: '胸痛', bodyPart: 'chest' },
  { id: 'stomachPain', name: '腹痛', bodyPart: 'abdomen' },
  { id: 'nausea', name: '恶心', bodyPart: 'abdomen' },
  { id: 'vomiting', name: '呕吐', bodyPart: 'abdomen' },
  { id: 'diarrhea', name: '腹泻', bodyPart: 'abdomen' },
  { id: 'constipation', name: '便秘', bodyPart: 'abdomen' },
  { id: 'backPain', name: '背痛', bodyPart: 'back' },
  { id: 'jointPain', name: '关节痛', bodyPart: 'arms' },
  { id: 'musclePain', name: '肌肉痛', bodyPart: 'general' },
  { id: 'rash', name: '皮疹', bodyPart: 'skin' },
  { id: 'itching', name: '瘙痒', bodyPart: 'skin' }
];

// 严重程度等级
export const SEVERITY_LEVELS = {
  1: '轻微',
  2: '轻度',
  3: '中等',
  4: '严重',
  5: '极度严重'
};

// 症状持续时间选项
export const DURATION_OPTIONS = [
  { id: 'lessThan1Day', label: '少于1天' },
  { id: '1To3Days', label: '1-3天' },
  { id: '4To7Days', label: '4-7天' },
  { id: '1To2Weeks', label: '1-2周' },
  { id: '2To4Weeks', label: '2-4周' },
  { id: 'moreThan4Weeks', label: '超过4周' }
];

// 免责声明文本
export const DISCLAIMER_TEXT = `
请注意！我做的这个MediCheck AI 提供的信息仅供参考，不构成实际完整无误的医疗建议、诊断或治疗！

本系统只是一个辅助工具，不能替代专业医疗咨询。如果您有健康问题，请立即就医或寻求专业医疗帮助。

使用本系统即表示您理解并接受这些条款。
`;

// ģ�͵�λ
export const MODEL_PROFILES = [
  {
    id: 'fast',
    name: 'fast',
    description: 'ȫ�� Agent ʹ�� Qwen3-0.5B',
  },
  {
    id: 'balanced',
    name: 'balanced',
    description: '���/��ҩʹ�� Qwen3-1.8B������ 0.5B',
  }
];
