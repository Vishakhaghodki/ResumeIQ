PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS users (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    name       TEXT NOT NULL,
    email      TEXT UNIQUE,
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS resumes (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id     INTEGER NOT NULL DEFAULT 1 REFERENCES users(id),
    filename    TEXT NOT NULL,
    raw_text    TEXT NOT NULL,
    uploaded_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS extracted_info (
    id             INTEGER PRIMARY KEY AUTOINCREMENT,
    resume_id      INTEGER NOT NULL REFERENCES resumes(id) ON DELETE CASCADE,
    name           TEXT,
    email          TEXT,
    phone          TEXT,
    skills         TEXT,   -- JSON list
    education      TEXT,   -- JSON list
    experience     TEXT,   -- JSON list
    projects       TEXT,   -- JSON list
    certifications TEXT    -- JSON list
);

CREATE TABLE IF NOT EXISTS job_descriptions (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id     INTEGER NOT NULL DEFAULT 1 REFERENCES users(id),
    title       TEXT NOT NULL,
    description TEXT NOT NULL,
    created_at  TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS analyses (
    id               INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id          INTEGER NOT NULL DEFAULT 1 REFERENCES users(id),
    resume_id        INTEGER NOT NULL REFERENCES resumes(id) ON DELETE CASCADE,
    job_id           INTEGER NOT NULL REFERENCES job_descriptions(id) ON DELETE CASCADE,
    match_score      REAL NOT NULL,
    ats_score        REAL NOT NULL,
    skill_score      REAL,
    keyword_score    REAL,
    similarity_score REAL,
    matched_skills   TEXT,  -- JSON list of strings
    missing_skills   TEXT,  -- JSON list of {skill, mentions}
    missing_keywords TEXT,  -- JSON list of strings
    suggestions      TEXT,  -- JSON list of {priority, text}
    ats_details      TEXT,  -- JSON {checks, word_count, pages}
    ai_feedback      TEXT,
    ai_mode          TEXT,  -- 'live' or 'demo'
    ai_provider      TEXT,
    created_at       TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS analysis_history (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    analysis_id INTEGER NOT NULL REFERENCES analyses(id) ON DELETE CASCADE,
    event       TEXT NOT NULL,          -- created | report_downloaded
    match_score REAL,
    ats_score   REAL,
    created_at  TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_analyses_created ON analyses(created_at);
CREATE INDEX IF NOT EXISTS idx_history_analysis ON analysis_history(analysis_id);

INSERT OR IGNORE INTO users (id, name, email) VALUES (1, 'Guest', NULL);
