-- Supabase schema + RLS policies for IntelHealth
-- Run in Supabase SQL editor

-- Enable pgvector
create extension if not exists vector;

-- Profiles (extends auth.users)
create table if not exists public.profiles (
  user_id uuid primary key references auth.users(id) on delete cascade,
  created_at timestamp with time zone default now()
);

-- Symptoms (public read)
create table if not exists public.symptoms (
  id text primary key,
  name text not null,
  body_part text not null,
  description text
);

-- Diagnoses (user scoped)
create table if not exists public.diagnoses (
  id bigserial primary key,
  user_id uuid references auth.users(id) on delete cascade,
  body_part text,
  symptoms text[] not null,
  severity text not null,
  duration text,
  other_symptoms text,
  results jsonb not null,
  recommendations text[],
  recomm_short text[],
  created_at timestamp with time zone default now()
);

-- Diagnosis cache (user scoped)
create table if not exists public.diagnosis_cache (
  id bigserial primary key,
  user_id uuid references auth.users(id) on delete cascade,
  input_hash text not null,
  response_json jsonb not null,
  model_profile_id text,
  created_at timestamp with time zone default now()
);

create index if not exists diagnosis_cache_input_hash_idx
  on public.diagnosis_cache (input_hash);

-- RAG documents (pgvector)
create table if not exists public.rag_documents (
  id bigserial primary key,
  content text not null,
  metadata jsonb,
  embedding vector(1536) not null,
  created_at timestamp with time zone default now()
);

create index if not exists rag_documents_embedding_idx
  on public.rag_documents using ivfflat (embedding vector_cosine_ops)
  with (lists = 100);

-- Enable RLS
alter table public.profiles enable row level security;
alter table public.diagnoses enable row level security;
alter table public.diagnosis_cache enable row level security;
alter table public.symptoms enable row level security;
alter table public.rag_documents enable row level security;

-- Profiles policies
drop policy if exists "profiles_select_own" on public.profiles;
drop policy if exists "profiles_insert_own" on public.profiles;
drop policy if exists "profiles_update_own" on public.profiles;
create policy "profiles_select_own"
  on public.profiles for select
  using (auth.uid() = user_id);

create policy "profiles_insert_own"
  on public.profiles for insert
  with check (auth.uid() = user_id);

create policy "profiles_update_own"
  on public.profiles for update
  using (auth.uid() = user_id);

-- Diagnoses policies
drop policy if exists "diagnoses_select_own" on public.diagnoses;
drop policy if exists "diagnoses_insert_own" on public.diagnoses;
drop policy if exists "diagnoses_update_own" on public.diagnoses;
drop policy if exists "diagnoses_delete_own" on public.diagnoses;
create policy "diagnoses_select_own"
  on public.diagnoses for select
  using (auth.uid() = user_id);

create policy "diagnoses_insert_own"
  on public.diagnoses for insert
  with check (auth.uid() = user_id);

create policy "diagnoses_update_own"
  on public.diagnoses for update
  using (auth.uid() = user_id);

create policy "diagnoses_delete_own"
  on public.diagnoses for delete
  using (auth.uid() = user_id);

-- Diagnosis cache policies
drop policy if exists "cache_select_own" on public.diagnosis_cache;
drop policy if exists "cache_insert_own" on public.diagnosis_cache;
create policy "cache_select_own"
  on public.diagnosis_cache for select
  using (auth.uid() = user_id);

create policy "cache_insert_own"
  on public.diagnosis_cache for insert
  with check (auth.uid() = user_id);

-- Symptoms policies (public read)
drop policy if exists "symptoms_select_public" on public.symptoms;
create policy "symptoms_select_public"
  on public.symptoms for select
  using (true);

-- RAG documents policies (public read)
drop policy if exists "rag_documents_select_public" on public.rag_documents;
create policy "rag_documents_select_public"
  on public.rag_documents for select
  using (true);

-- Vector search RPC
create or replace function public.match_rag_documents(
  query_embedding vector(1536),
  match_count int default 5,
  filter jsonb default null
)
returns table(
  id bigint,
  content text,
  metadata jsonb,
  similarity float
)
language sql
stable
as $$
  select
    id,
    content,
    metadata,
    1 - (embedding <=> query_embedding) as similarity
  from public.rag_documents
  where (filter is null or metadata @> filter)
  order by embedding <=> query_embedding
  limit match_count;
$$;
