CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS vector;


-- ============================================================
-- USERS
-- ============================================================

CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

    external_id VARCHAR(255) UNIQUE,

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);


-- ============================================================
-- CONVERSATIONS
-- ============================================================

CREATE TABLE IF NOT EXISTS conversations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

    user_id UUID NOT NULL
        REFERENCES users(id)
        ON DELETE CASCADE,

    title VARCHAR(255),

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);


CREATE INDEX IF NOT EXISTS idx_conversations_user_id
    ON conversations(user_id);


-- ============================================================
-- MESSAGES
-- ============================================================

CREATE TABLE IF NOT EXISTS messages (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

    conversation_id UUID NOT NULL
        REFERENCES conversations(id)
        ON DELETE CASCADE,

    role VARCHAR(20) NOT NULL
        CHECK (
            role IN (
                'user',
                'assistant',
                'system',
                'tool'
            )
        ),

    content TEXT NOT NULL,

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);


CREATE INDEX IF NOT EXISTS idx_messages_conversation_id
    ON messages(conversation_id);

CREATE INDEX IF NOT EXISTS idx_messages_created_at
    ON messages(created_at);


-- ============================================================
-- MEMORY FACTS
-- ============================================================

CREATE TABLE IF NOT EXISTS memory_facts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

    user_id UUID NOT NULL
        REFERENCES users(id)
        ON DELETE CASCADE,

    predicate VARCHAR(255) NOT NULL,

    value TEXT NOT NULL,

    confidence DOUBLE PRECISION NOT NULL DEFAULT 1.0
        CHECK (
            confidence >= 0.0
            AND confidence <= 1.0
        ),

    source VARCHAR(50) NOT NULL DEFAULT 'conversation',

    source_message_id UUID
        REFERENCES messages(id)
        ON DELETE SET NULL,

    valid_from TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    valid_to TIMESTAMPTZ,

    is_active BOOLEAN NOT NULL DEFAULT TRUE,

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    embedding VECTOR(384)
);


CREATE INDEX IF NOT EXISTS idx_memory_facts_user_id
    ON memory_facts(user_id);

CREATE INDEX IF NOT EXISTS idx_memory_facts_active
    ON memory_facts(user_id, is_active);

CREATE INDEX IF NOT EXISTS idx_memory_facts_predicate
    ON memory_facts(predicate);


-- ============================================================
-- VECTOR INDEX
-- ============================================================

CREATE INDEX IF NOT EXISTS idx_memory_facts_embedding
    ON memory_facts
    USING hnsw (embedding vector_cosine_ops);


-- ============================================================
-- MEMORY HISTORY
-- ============================================================

CREATE TABLE IF NOT EXISTS memory_history (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

    memory_fact_id UUID NOT NULL
        REFERENCES memory_facts(id)
        ON DELETE CASCADE,

    user_id UUID NOT NULL
        REFERENCES users(id)
        ON DELETE CASCADE,

    action VARCHAR(30) NOT NULL
        CHECK (
            action IN (
                'created',
                'updated',
                'superseded',
                'deactivated',
                'deleted'
            )
        ),

    old_value TEXT,

    new_value TEXT,

    reason TEXT,

    source_message_id UUID
        REFERENCES messages(id)
        ON DELETE SET NULL,

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);


CREATE INDEX IF NOT EXISTS idx_memory_history_user_id
    ON memory_history(user_id);

CREATE INDEX IF NOT EXISTS idx_memory_history_fact_id
    ON memory_history(memory_fact_id);

CREATE INDEX IF NOT EXISTS idx_memory_history_created_at
    ON memory_history(created_at);