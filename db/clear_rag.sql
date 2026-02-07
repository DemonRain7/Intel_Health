-- Clear RAG vectors (pgvector)
-- Option A: full truncate (fast)
-- 清空表并重置 ID
TRUNCATE TABLE rag_documents RESTART IDENTITY;


-- Option B: delete by corpus (diagnosis / drug)
-- delete from public.rag_documents where metadata->>'corpus' = 'diagnosis';
-- delete from public.rag_documents where metadata->>'corpus' = 'drug';
