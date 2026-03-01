-- ============================================
-- Government Job Notification System Schema
-- Run this in Supabase SQL Editor
-- ============================================

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================
-- USERS (extends Supabase Auth)
-- ============================================
CREATE TABLE IF NOT EXISTS public.users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    telegram_username TEXT,
    telegram_chat_id BIGINT,
    is_premium BOOLEAN DEFAULT FALSE,
    is_active BOOLEAN DEFAULT TRUE,
    role TEXT CHECK (role IN ('user', 'admin')) DEFAULT 'user',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================
-- USER PROFILES (eligibility details)
-- ============================================
CREATE TABLE IF NOT EXISTS public.user_profiles (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID UNIQUE NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
    dob DATE,
    gender TEXT CHECK (gender IN ('M', 'F', 'Other')),
    education_level TEXT CHECK (education_level IN ('10th', '12th', 'Diploma', 'Graduation', 'Post Graduation', 'PhD')),
    education_stream TEXT,
    category TEXT CHECK (category IN ('General', 'OBC', 'SC', 'ST', 'EWS')),
    state TEXT,
    exam_interests TEXT[] DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================
-- TELEGRAM CHANNELS (monitored sources)
-- ============================================
CREATE TABLE IF NOT EXISTS public.telegram_channels (
    id SERIAL PRIMARY KEY,
    channel_username TEXT UNIQUE NOT NULL,
    channel_name TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    last_scraped_id BIGINT DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================
-- NOTIFICATIONS (scraped job posts)
-- ============================================
CREATE TABLE IF NOT EXISTS public.notifications (
    id SERIAL PRIMARY KEY,
    title TEXT NOT NULL,
    organization TEXT,
    exam_type TEXT CHECK (exam_type IN ('Central', 'State', 'Banking', 'Railway', 'Defence', 'PSU', 'Other')),
    original_pdf_url TEXT,
    official_website_url TEXT,
    last_date DATE,
    min_age INTEGER,
    max_age INTEGER,
    age_relaxation JSONB DEFAULT '{}',
    education_required TEXT,
    total_vacancies INTEGER,
    vacancy_by_category JSONB DEFAULT '{}',
    source_channel TEXT,
    source_message_id BIGINT,
    raw_text TEXT,
    is_processed BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Unique constraint to prevent duplicate scraping
CREATE UNIQUE INDEX IF NOT EXISTS idx_notif_source 
ON public.notifications(source_channel, source_message_id);

-- ============================================
-- NOTIFICATION DELIVERIES (tracking)
-- ============================================
CREATE TABLE IF NOT EXISTS public.notification_deliveries (
    id SERIAL PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
    notification_id INTEGER NOT NULL REFERENCES public.notifications(id) ON DELETE CASCADE,
    delivered_at TIMESTAMPTZ DEFAULT NOW(),
    delivery_type TEXT CHECK (delivery_type IN ('auto', 'manual')) DEFAULT 'manual',
    UNIQUE(user_id, notification_id)
);

-- ============================================
-- USER SELECTIONS (free user checkbox picks)
-- ============================================
CREATE TABLE IF NOT EXISTS public.user_selections (
    id SERIAL PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
    notification_id INTEGER NOT NULL REFERENCES public.notifications(id) ON DELETE CASCADE,
    selected_at TIMESTAMPTZ DEFAULT NOW(),
    is_delivered BOOLEAN DEFAULT FALSE,
    UNIQUE(user_id, notification_id)
);

-- ============================================
-- INDEXES for performance
-- ============================================
CREATE INDEX IF NOT EXISTS idx_notifications_created ON public.notifications(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_notifications_exam_type ON public.notifications(exam_type);
CREATE INDEX IF NOT EXISTS idx_notifications_last_date ON public.notifications(last_date);
CREATE INDEX IF NOT EXISTS idx_user_profiles_category ON public.user_profiles(category);
CREATE INDEX IF NOT EXISTS idx_user_profiles_education ON public.user_profiles(education_level);
CREATE INDEX IF NOT EXISTS idx_deliveries_user ON public.notification_deliveries(user_id);
CREATE INDEX IF NOT EXISTS idx_selections_user ON public.user_selections(user_id);

-- ============================================
-- ROW LEVEL SECURITY
-- ============================================
ALTER TABLE public.users ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.user_profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.notifications ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.notification_deliveries ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.user_selections ENABLE ROW LEVEL SECURITY;

-- Public read access to notifications
CREATE POLICY "Anyone can read notifications" ON public.notifications
    FOR SELECT USING (true);

-- Service role has full access (for backend)
CREATE POLICY "Service role full access users" ON public.users
    FOR ALL USING (true);
CREATE POLICY "Service role full access profiles" ON public.user_profiles
    FOR ALL USING (true);
CREATE POLICY "Service role full access notifications" ON public.notifications
    FOR ALL USING (true);
CREATE POLICY "Service role full access deliveries" ON public.notification_deliveries
    FOR ALL USING (true);
CREATE POLICY "Service role full access selections" ON public.user_selections
    FOR ALL USING (true);
