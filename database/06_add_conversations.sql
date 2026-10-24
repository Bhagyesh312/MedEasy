-- Add conversations table for Phase 4 chat system

CREATE TABLE IF NOT EXISTS conversations (
    conversation_id VARCHAR(36) PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    data JSONB NOT NULL,  -- Full conversation data including messages
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE
);

-- Create indexes for conversations table
CREATE INDEX IF NOT EXISTS idx_conversations_user_id ON conversations(user_id);
CREATE INDEX IF NOT EXISTS idx_conversations_created_at ON conversations(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_conversations_active ON conversations(is_active) WHERE is_active = TRUE;

-- Add conversation summary for quick lookup
CREATE TABLE IF NOT EXISTS conversation_summaries (
    conversation_id VARCHAR(36) PRIMARY KEY REFERENCES conversations(conversation_id) ON DELETE CASCADE,
    user_id INTEGER NOT NULL,
    report_id INTEGER REFERENCES reports(id) ON DELETE SET NULL,
    summary TEXT,
    message_count INTEGER DEFAULT 0,
    total_tokens INTEGER DEFAULT 0,
    avg_verification_score DECIMAL(3,2),
    last_message_at TIMESTAMP
);

-- Create indexes for conversation_summaries table
CREATE INDEX IF NOT EXISTS idx_summaries_user_id ON conversation_summaries(user_id);
CREATE INDEX IF NOT EXISTS idx_summaries_report_id ON conversation_summaries(report_id);

-- Comments
COMMENT ON TABLE conversations IS 'Phase 4: Stores full conversation threads with messages';
COMMENT ON TABLE conversation_summaries IS 'Quick lookup table for conversation metadata';
