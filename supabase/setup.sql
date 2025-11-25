-- Supabase Database Setup for منهج AI
-- قاعدة البيانات الكاملة لبوت منهج AI

-- Enable necessary extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- جدول الطلاب الرئيسي
CREATE TABLE IF NOT EXISTS students (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    telegram_id BIGINT UNIQUE NOT NULL,
    name TEXT NOT NULL,
    education_stage TEXT NOT NULL,
    country TEXT DEFAULT 'المملكة العربية السعودية',
    verification_code TEXT UNIQUE NOT NULL,
    
    -- نظام النقاط والمدفوعات
    points INTEGER DEFAULT 50, -- مكافأة ترحيب
    riyal INTEGER DEFAULT 0,
    
    -- حالات العضوية
    is_premium BOOLEAN DEFAULT FALSE,
    is_gift_premium BOOLEAN DEFAULT FALSE,
    is_manager BOOLEAN DEFAULT FALSE,
    
    -- نظام الإحالة
    successful_referrals INTEGER DEFAULT 0,
    referral_code TEXT, -- رمز الإحالة المستخدم عند التسجيل
    
    -- إحصائيات النشاط
    questions_count INTEGER DEFAULT 0,
    ads_response_count INTEGER DEFAULT 0,
    last_activity TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- تواريخ
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- جدول الأسئلة
CREATE TABLE IF NOT EXISTS questions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id BIGINT NOT NULL REFERENCES students(telegram_id) ON DELETE CASCADE,
    question TEXT NOT NULL,
    question_type TEXT DEFAULT 'general',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- جدول المهام
CREATE TABLE IF NOT EXISTS tasks (
    id SERIAL PRIMARY KEY,
    link TEXT NOT NULL,
    description TEXT NOT NULL,
    points INTEGER DEFAULT 10,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- جدول المهام المكتملة
CREATE TABLE IF NOT EXISTS completed_tasks (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id BIGINT NOT NULL REFERENCES students(telegram_id) ON DELETE CASCADE,
    task_id INTEGER NOT NULL REFERENCES tasks(id) ON DELETE CASCADE,
    completed_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(user_id, task_id)
);

-- جدول التحويلات
CREATE TABLE IF NOT EXISTS transfers (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    sender_id BIGINT NOT NULL REFERENCES students(telegram_id) ON DELETE CASCADE,
    receiver_id BIGINT NOT NULL REFERENCES students(telegram_id) ON DELETE CASCADE,
    amount INTEGER NOT NULL,
    transfer_type TEXT NOT NULL CHECK (transfer_type IN ('riyal', 'points')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- جدول الدعم
CREATE TABLE IF NOT EXISTS support_messages (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id BIGINT NOT NULL REFERENCES students(telegram_id) ON DELETE CASCADE,
    message TEXT NOT NULL,
    reply TEXT,
    is_answered BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    replied_at TIMESTAMP WITH TIME ZONE
);

-- جدول المديرين
CREATE TABLE IF NOT EXISTS admins (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    telegram_id BIGINT UNIQUE NOT NULL REFERENCES students(telegram_id) ON DELETE CASCADE,
    permissions TEXT[] DEFAULT ARRAY['basic'],
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- جدول الإعدادات العامة
CREATE TABLE IF NOT EXISTS app_settings (
    id SERIAL PRIMARY KEY,
    setting_key TEXT UNIQUE NOT NULL,
    setting_value TEXT NOT NULL,
    description TEXT,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- إدراج الإعدادات الافتراضية
INSERT INTO app_settings (setting_key, setting_value, description) VALUES
('premium_price', '10 ريال سعودي', 'سعر البريميم'),
('contact_email', 'mosapadn@gmail.com', 'ايميل التواصل'),
('contact_instagram', 'mos_adn', 'حساب الانستجرام'),
('ad_link', 'https://otieu.com/4/10160934', 'رابط الإعلان'),
('ad_response_limit', '2', 'حد الردود قبل الإعلان'),
('welcome_points', '50', 'نقاط الترحيب للمستخدم الجديد'),
('referral_points', '100', 'نقاط الإحالة'),
('app_version', '2.0', 'إصدار التطبيق')
ON CONFLICT (setting_key) DO NOTHING;

-- Functions & Triggers

-- دالة تحديث updated_at تلقائياً
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Triggers لتحديث updated_at
CREATE TRIGGER update_students_updated_at 
    BEFORE UPDATE ON students 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_app_settings_updated_at 
    BEFORE UPDATE ON app_settings 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- دالة منح نقاط الإحالة
CREATE OR REPLACE FUNCTION grant_referral_points()
RETURNS TRIGGER AS $$
DECLARE
    referrer_user_id BIGINT;
BEGIN
    -- البحث عن المحيل بناءً على رمز الإحالة
    IF NEW.referral_code IS NOT NULL THEN
        SELECT telegram_id INTO referrer_user_id
        FROM students 
        WHERE verification_code = NEW.referral_code;
        
        -- إضافة النقاط للمحيل
        IF referrer_user_id IS NOT NULL THEN
            UPDATE students 
            SET points = points + 100,
                successful_referrals = successful_referrals + 1
            WHERE telegram_id = referrer_user_id;
        END IF;
    END IF;
    
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Trigger لمنح نقاط الإحالة عند التسجيل
CREATE TRIGGER grant_referral_points_trigger
    AFTER INSERT ON students
    FOR EACH ROW EXECUTE FUNCTION grant_referral_points();

-- دالة تحديث آخر نشاط
CREATE OR REPLACE FUNCTION update_last_activity()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE students 
    SET last_activity = NOW() 
    WHERE telegram_id = NEW.user_id;
    
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Trigger لتحديث آخر نشاط عند إرسال سؤال
CREATE TRIGGER update_last_activity_trigger
    AFTER INSERT ON questions
    FOR EACH ROW EXECUTE FUNCTION update_last_activity();

-- Views للإحصائيات

-- عرض أفضل المستخدمين بالنقاط
CREATE OR REPLACE VIEW top_users_by_points AS
SELECT 
    name,
    points,
    riyal,
    successful_referrals,
    questions_count,
    created_at,
    ROW_NUMBER() OVER (ORDER BY points DESC) as rank
FROM students
ORDER BY points DESC
LIMIT 100;

-- عرض إحصائيات عامة
CREATE OR REPLACE VIEW app_statistics AS
SELECT 
    (SELECT COUNT(*) FROM students) as total_users,
    (SELECT COUNT(*) FROM students WHERE is_premium = TRUE) as premium_users,
    (SELECT COUNT(*) FROM students WHERE created_at >= CURRENT_DATE) as new_users_today,
    (SELECT SUM(points) FROM students) as total_points,
    (SELECT SUM(riyal) FROM students) as total_riyal,
    (SELECT COUNT(*) FROM questions) as total_questions,
    (SELECT COUNT(*) FROM completed_tasks) as total_completed_tasks;

-- عرض المهام المتاحة مع عدد المكملين
CREATE OR REPLACE VIEW tasks_with_completion_count AS
SELECT 
    t.id,
    t.description,
    t.points,
    t.link,
    t.is_active,
    COUNT(ct.id) as completion_count,
    t.created_at
FROM tasks t
LEFT JOIN completed_tasks ct ON t.id = ct.task_id
GROUP BY t.id, t.description, t.points, t.link, t.is_active, t.created_at
ORDER BY t.created_at DESC;

-- Indexes لتحسين الأداء
CREATE INDEX IF NOT EXISTS idx_students_telegram_id ON students(telegram_id);
CREATE INDEX IF NOT EXISTS idx_students_verification_code ON students(verification_code);
CREATE INDEX IF NOT EXISTS idx_students_referral_code ON students(referral_code);
CREATE INDEX IF NOT EXISTS idx_students_is_premium ON students(is_premium);
CREATE INDEX IF NOT EXISTS idx_students_created_at ON students(created_at);
CREATE INDEX IF NOT EXISTS idx_questions_user_id ON questions(user_id);
CREATE INDEX IF NOT EXISTS idx_questions_created_at ON questions(created_at);
CREATE INDEX IF NOT EXISTS idx_completed_tasks_user_id ON completed_tasks(user_id);
CREATE INDEX IF NOT EXISTS idx_completed_tasks_task_id ON completed_tasks(task_id);
CREATE INDEX IF NOT EXISTS idx_transfers_sender_id ON transfers(sender_id);
CREATE INDEX IF NOT EXISTS idx_transfers_receiver_id ON transfers(receiver_id);
CREATE INDEX IF NOT EXISTS idx_support_messages_user_id ON support_messages(user_id);
CREATE INDEX IF NOT EXISTS idx_support_messages_is_answered ON support_messages(is_answered);

-- Row Level Security (RLS) - اختياري للأمان الإضافي
-- ALTER TABLE students ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE questions ENABLE ROW LEVEL SECURITY;

-- بيانات تجريبية للمديرين (اختياري)
-- INSERT INTO students (telegram_id, name, education_stage, country, verification_code, is_manager, points, riyal)
-- VALUES (123456789, 'مصعب فهد', 'الجامعة/التعليم العالي', 'المملكة العربية السعودية', 'ADMIN001', TRUE, 1000, 100)
-- ON CONFLICT (telegram_id) DO UPDATE SET is_manager = TRUE;

-- إضافة المدير للجدول
-- INSERT INTO admins (telegram_id, permissions)
-- VALUES (123456789, ARRAY['basic', 'advanced', 'super'])
-- ON CONFLICT (telegram_id) DO UPDATE SET permissions = ARRAY['basic', 'advanced', 'super'];

-- مهام تجريبية
INSERT INTO tasks (link, description, points) VALUES
('https://t.me/manhaj_ai_channel', 'انضم لقناة منهج AI', 20),
('https://instagram.com/mos_adn', 'تابعنا على الانستجرام', 15),
('https://twitter.com/manhaj_ai', 'تابعنا على تويتر', 15),
('https://youtube.com/@manhaj_ai', 'اشترك في قناة اليوتيوب', 25)
ON CONFLICT DO NOTHING;

-- إشعارات إنجاز الإعداد
SELECT 'منهج AI Database Setup Complete! 🎉' as status;