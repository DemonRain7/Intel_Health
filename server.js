import express from "express";
import cors from "cors";
import bodyParser from "body-parser";
import path from "path";
import fs from "fs";
import jwt from "jsonwebtoken";
import crypto from "crypto";
import dotenv from "dotenv";
import { fileURLToPath } from "url";
import { createClient } from "@supabase/supabase-js";
import { app as diagnosisApp } from "./llm_funcs/diagnosis-graph.mjs";

dotenv.config();

const app = express();
const port = process.env.PORT || 8081;

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const SUPABASE_URL = process.env.SUPABASE_URL;
const SUPABASE_ANON_KEY = process.env.SUPABASE_ANON_KEY;
const SUPABASE_JWT_SECRET = process.env.SUPABASE_JWT_SECRET;
const SUPABASE_SERVICE_ROLE_KEY = process.env.SUPABASE_SERVICE_ROLE_KEY;
const CACHE_TTL_HOURS = Number(process.env.DIAGNOSIS_CACHE_TTL_HOURS || 24);

const hasSupabase = Boolean(SUPABASE_URL && SUPABASE_ANON_KEY);

const supabasePublic = hasSupabase
  ? createClient(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY || SUPABASE_ANON_KEY, {
      auth: { persistSession: false }
    })
  : null;

const createUserClient = (accessToken) =>
  createClient(SUPABASE_URL, SUPABASE_ANON_KEY, {
    global: { headers: { Authorization: `Bearer ${accessToken}` } },
    auth: { persistSession: false }
  });

const getBeijingDateStr = (utcDateStr) => {
  const utcDate = new Date(utcDateStr);
  const beijingTime = new Date(utcDate.getTime() + 8 * 60 * 60 * 1000);
  return `${beijingTime.getFullYear()}-${String(beijingTime.getMonth() + 1).padStart(2, '0')}-${String(beijingTime.getDate()).padStart(2, '0')}`;
};

app.use(cors());
app.use(bodyParser.json());

const requireSupabase = (res) => {
  if (!hasSupabase) {
    res.status(500).json({ message: 'Supabase is not configured. Please set SUPABASE_URL and SUPABASE_ANON_KEY.' });
    return false;
  }
  return true;
};

const verifySupabaseToken = async (token) => {
  if (SUPABASE_JWT_SECRET) {
    try {
      const decoded = jwt.verify(token, SUPABASE_JWT_SECRET, { algorithms: ['HS256'] });
      return {
        id: decoded.sub,
        email: decoded.email,
        role: decoded.role
      };
    } catch (err) {
      console.warn('JWT verify failed, falling back to Supabase auth:', err.message);
    }
  }

  if (!supabasePublic) {
    throw new Error('Supabase client not available');
  }

  const { data, error } = await supabasePublic.auth.getUser(token);
  if (error || !data?.user) {
    throw new Error('Invalid token');
  }

  return {
    id: data.user.id,
    email: data.user.email,
    role: data.user.role
  };
};

const authenticateToken = async (req, res, next) => {
  if (!hasSupabase) {
    return res.status(500).json({ message: 'Supabase is not configured. Please set SUPABASE_URL and SUPABASE_ANON_KEY.' });
  }
  const authHeader = req.headers['authorization'];
  const token = authHeader && authHeader.split(' ')[1];

  if (!token) {
    return res.status(401).json({ message: 'Missing authorization token' });
  }

  try {
    const user = await verifySupabaseToken(token);
    req.user = user;
    req.accessToken = token;
    req.supabase = createUserClient(token);
    next();
  } catch (err) {
    return res.status(403).json({ message: 'Invalid or expired token' });
  }
};

const hashInput = (payload) =>
  crypto.createHash('sha256').update(JSON.stringify(payload)).digest('hex');

const isCacheFresh = (createdAt) => {
  if (!createdAt) return false;
  const created = new Date(createdAt).getTime();
  const ageHours = (Date.now() - created) / (1000 * 60 * 60);
  return ageHours <= CACHE_TTL_HOURS;
};

// Model profiles
app.get('/api/model-profiles', async (req, res) => {
  try {
    const profilesPath = path.join(__dirname, 'config', 'model_profiles.json');
    const profiles = JSON.parse(fs.readFileSync(profilesPath, 'utf-8'));
    res.json(profiles);
  } catch (error) {
    console.error('Failed to load model profiles:', error);
    res.status(500).json({ message: 'Failed to load model profiles' });
  }
});

// Metrics (for Home charts)
app.get('/api/metrics', async (req, res) => {
  try {
    const metricsPath = path.join(__dirname, 'src', 'assets', 'metrics', 'training_metrics.json');
    if (!fs.existsSync(metricsPath)) {
      return res.json({ labels: [], json_valid_rate: [], keyword_coverage: [] });
    }
    const metrics = JSON.parse(fs.readFileSync(metricsPath, 'utf-8'));
    res.json(metrics);
  } catch (error) {
    console.error('Failed to load metrics:', error);
    res.status(500).json({ message: 'Failed to load metrics' });
  }
});

// Deprecated local auth endpoints (Supabase Auth should be used from frontend)
app.post('/api/users/login', (req, res) => {
  res.status(410).json({ message: 'Use Supabase Auth on the client instead.' });
});

app.post('/api/users', (req, res) => {
  res.status(410).json({ message: 'Use Supabase Auth on the client instead.' });
});

app.get('/api/users/profile', authenticateToken, async (req, res) => {
  if (!requireSupabase(res)) return;
  try {
    const { data, error } = await req.supabase
      .from('profiles')
      .select('*')
      .eq('user_id', req.user.id)
      .single();

    if (error) {
      return res.status(404).json({ message: 'Profile not found' });
    }

    res.json(data);
  } catch (error) {
    console.error('Failed to fetch profile:', error);
    res.status(500).json({ message: 'Server error' });
  }
});

// Symptoms
app.get('/api/symptoms', async (req, res) => {
  if (!requireSupabase(res)) return;
  try {
    const { data, error } = await supabasePublic.from('symptoms').select('*');
    if (error) throw error;
    res.json(data);
  } catch (error) {
    console.error('Failed to fetch symptoms:', error);
    res.status(500).json({ message: 'Server error' });
  }
});

app.get('/api/symptoms/bodyPart/:bodyPart', async (req, res) => {
  if (!requireSupabase(res)) return;
  try {
    const { bodyPart } = req.params;
    const { data, error } = await supabasePublic
      .from('symptoms')
      .select('*')
      .eq('body_part', bodyPart);
    if (error) throw error;
    res.json(data);
  } catch (error) {
    console.error('Failed to fetch symptoms by body part:', error);
    res.status(500).json({ message: 'Server error' });
  }
});

app.post('/api/symptoms', authenticateToken, async (req, res) => {
  if (!requireSupabase(res)) return;
  try {
    const symptomData = req.body;
    const { data, error } = await req.supabase
      .from('symptoms')
      .insert(symptomData)
      .select()
      .single();

    if (error) throw error;
    res.status(201).json(data);
  } catch (error) {
    console.error('Failed to create symptom:', error);
    res.status(500).json({ message: 'Server error' });
  }
});

// Diagnoses
app.get('/api/diagnoses', authenticateToken, async (req, res) => {
  if (!requireSupabase(res)) return;
  try {
    const { data, error } = await req.supabase
      .from('diagnoses')
      .select('*')
      .eq('user_id', req.user.id)
      .order('created_at');
    if (error) throw error;
    res.json(data || []);
  } catch (error) {
    console.error('Failed to fetch diagnoses:', error);
    res.status(500).json({ message: 'Server error' });
  }
});

app.get('/api/diagnoses/:id', authenticateToken, async (req, res) => {
  if (!requireSupabase(res)) return;
  try {
    const { id } = req.params;
    const { data, error } = await req.supabase
      .from('diagnoses')
      .select('*')
      .eq('id', id)
      .eq('user_id', req.user.id)
      .single();

    if (error || !data) {
      return res.status(404).json({ message: 'Diagnosis not found' });
    }

    res.json(data);
  } catch (error) {
    console.error('Failed to fetch diagnosis:', error);
    res.status(500).json({ message: 'Server error' });
  }
});

app.post('/api/diagnoses', authenticateToken, async (req, res) => {
  if (!requireSupabase(res)) return;

  try {
    const diagnosisData = req.body || {};

    const cachePayload = {
      user_id: req.user.id,
      body_part: diagnosisData.body_part,
      symptoms: diagnosisData.symptoms,
      other_symptoms: diagnosisData.other_symptoms,
      severity: diagnosisData.severity,
      duration: diagnosisData.duration,
      model_profile_id: diagnosisData.model_profile_id,
      agent_overrides: diagnosisData.agent_overrides
    };
    const inputHash = hashInput(cachePayload);

    let diagnosisResult = null;
    let usedCache = false;

    const { data: cacheRows } = await req.supabase
      .from('diagnosis_cache')
      .select('*')
      .eq('input_hash', inputHash)
      .order('created_at', { ascending: false })
      .limit(1);

    if (cacheRows && cacheRows.length > 0 && isCacheFresh(cacheRows[0].created_at)) {
      diagnosisResult = cacheRows[0].response_json;
      usedCache = true;
    }

    if (!diagnosisResult) {
      const result = await diagnosisApp.invoke({
        diagnosisData: { ...diagnosisData, user_id: req.user.id },
      });
      diagnosisResult = result.finalOutput;

      await req.supabase.from('diagnosis_cache').insert({
        user_id: req.user.id,
        input_hash: inputHash,
        response_json: diagnosisResult,
        model_profile_id: diagnosisData.model_profile_id || null
      });
    }

    const newDiagnosisData = {
      user_id: req.user.id,
      body_part: diagnosisData.body_part,
      symptoms: Array.isArray(diagnosisData.symptoms) ? diagnosisData.symptoms : [],
      severity: String(diagnosisData.severity || 3),
      duration: diagnosisData.duration,
      other_symptoms: diagnosisData.other_symptoms,
      results: diagnosisResult.results,
      recommendations: diagnosisResult.recommendations,
      recomm_short: diagnosisResult.recomm_short
    };

    const { data, error } = await req.supabase
      .from('diagnoses')
      .insert(newDiagnosisData)
      .select()
      .single();

    if (error) throw error;

    res.status(201).json({ ...data, cached: usedCache });
  } catch (error) {
    console.error('Failed to create diagnosis:', error);
    res.status(500).json({ message: 'Server error' });
  }
});

// Statistics (public)
app.get('/api/statistics/diagnoses', async (req, res) => {
  if (!requireSupabase(res)) return;
  try {
    const { data: allDiagnoses, error } = await supabasePublic
      .from('diagnoses')
      .select('*');
    if (error) throw error;

    const now = new Date();
    const beijingNow = new Date(now.getTime() + 8 * 60 * 60 * 1000);
    const today = new Date(beijingNow.getFullYear(), beijingNow.getMonth(), beijingNow.getDate());

    const twentyNineDaysAgo = new Date(today);
    twentyNineDaysAgo.setDate(today.getDate() - 29);

    const dateMap = {};
    const dateLabels = [];

    for (let i = 0; i < 30; i++) {
      const date = new Date(twentyNineDaysAgo);
      date.setDate(twentyNineDaysAgo.getDate() + i);
      const dateStr = `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')}`;
      const label = `${parseInt(date.getMonth() + 1)}/${parseInt(date.getDate())}`;

      dateMap[dateStr] = 0;
      dateLabels.push(label);
    }

    allDiagnoses.forEach(diagnosis => {
      if (!diagnosis.created_at) return;
      const dateStr = getBeijingDateStr(diagnosis.created_at);
      if (dateMap[dateStr] !== undefined) {
        dateMap[dateStr]++;
      }
    });

    const counts = [];
    for (let i = 0; i < dateLabels.length; i++) {
      const date = new Date(twentyNineDaysAgo);
      date.setDate(twentyNineDaysAgo.getDate() + i);
      const dateStr = `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')}`;
      counts.push(dateMap[dateStr] || 0);
    }

    res.json({ dates: dateLabels, counts });
  } catch (error) {
    console.error('Failed to fetch diagnosis statistics:', error);
    res.status(500).json({ message: 'Server error' });
  }
});

app.get('/api/statistics/bodyparts', async (req, res) => {
  if (!requireSupabase(res)) return;
  try {
    const { data: allDiagnoses, error } = await supabasePublic
      .from('diagnoses')
      .select('*');
    if (error) throw error;

    const bodyPartCounts = {};

    allDiagnoses.forEach(diagnosis => {
      const bodyPart = diagnosis.body_part || 'unknown';
      bodyPartCounts[bodyPart] = (bodyPartCounts[bodyPart] || 0) + 1;
    });

    const result = Object.entries(bodyPartCounts)
      .map(([bodyPart, count]) => ({ name: bodyPart, value: count }))
      .sort((a, b) => b.value - a.value);

    res.json(result);
  } catch (error) {
    console.error('Failed to fetch body part statistics:', error);
    res.status(500).json({ message: 'Server error' });
  }
});

if (process.env.NODE_ENV === 'production') {
  app.use(express.static(path.join(__dirname, 'dist')));
  app.get('*', (req, res) => {
    res.sendFile(path.join(__dirname, 'dist', 'index.html'));
  });
}

app.listen(port, '0.0.0.0', () => {
  console.log(`Server running on port ${port}`);
});
