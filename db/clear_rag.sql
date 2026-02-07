-- Clear RAG vectors (pgvector)
-- Option A: full truncate (fast)
truncate table public.rag_documents;

-- Option B: delete by corpus (diagnosis / drug)
-- delete from public.rag_documents where metadata->>'corpus' = 'diagnosis';
-- delete from public.rag_documents where metadata->>'corpus' = 'drug';
