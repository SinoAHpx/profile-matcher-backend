-- =====================================================
-- PROFILE SCHEMA - 用户画像总览
-- =====================================================
-- 专注于用户的基本档案信息和静态属性
-- 包含预定义的用户基本信息列和对应的字典表
-- =====================================================

-- Enable necessary extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create profile schema
CREATE SCHEMA IF NOT EXISTS profile;

-- =====================================================
-- DICTIONARY TABLES - 字典表
-- =====================================================

-- 地区字典表
CREATE TABLE profile.regions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    code VARCHAR(10) NOT NULL UNIQUE,                    -- 地区代码（如：CN-BJ, US-CA）
    name VARCHAR(100) NOT NULL,                          -- 地区名称
    name_en VARCHAR(100),                                -- 英文名称
    parent_id UUID REFERENCES profile.regions(id),       -- 父级地区（支持省市区层级）
    level INTEGER NOT NULL DEFAULT 1,                    -- 层级：1=国家，2=省/州，3=市，4=区
    sort_order INTEGER DEFAULT 0,                        -- 排序
    is_active BOOLEAN DEFAULT true,                      -- 是否激活
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 职业字典表
CREATE TABLE profile.occupations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    code VARCHAR(20) NOT NULL UNIQUE,                    -- 职业代码
    name VARCHAR(100) NOT NULL,                          -- 职业名称
    name_en VARCHAR(100),                                -- 英文名称
    category_id UUID REFERENCES profile.occupation_categories(id), -- 职业分类
    description TEXT,                                    -- 职业描述
    sort_order INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 职业分类表
CREATE TABLE profile.occupation_categories (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    code VARCHAR(20) NOT NULL UNIQUE,                    -- 分类代码
    name VARCHAR(100) NOT NULL,                          -- 分类名称
    name_en VARCHAR(100),                                -- 英文名称
    parent_id UUID REFERENCES profile.occupation_categories(id), -- 支持层级分类
    description TEXT,                                    -- 分类描述
    sort_order INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 教育程度字典表
CREATE TABLE profile.education_levels (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    code VARCHAR(20) NOT NULL UNIQUE,                    -- 教育程度代码
    name VARCHAR(100) NOT NULL,                          -- 教育程度名称
    name_en VARCHAR(100),                                -- 英文名称
    level_order INTEGER NOT NULL,                        -- 教育程度排序（数字越大程度越高）
    description TEXT,                                    -- 描述
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 关系状态字典表
CREATE TABLE profile.relationship_statuses (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    code VARCHAR(20) NOT NULL UNIQUE,                    -- 状态代码
    name VARCHAR(50) NOT NULL,                           -- 状态名称
    name_en VARCHAR(50),                                 -- 英文名称
    description TEXT,                                    -- 描述
    sort_order INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 性别字典表
CREATE TABLE profile.genders (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    code VARCHAR(20) NOT NULL UNIQUE,                    -- 性别代码
    name VARCHAR(50) NOT NULL,                           -- 性别名称
    name_en VARCHAR(50),                                 -- 英文名称
    sort_order INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- =====================================================
-- CORE USER PROFILE TABLE - 核心用户档案表
-- =====================================================

-- 主用户档案表 (优化版本 - 移除与auth.users重复的字段)
-- Optimized user profiles table - removed fields that duplicate auth.users
CREATE TABLE profile.user_profiles (
    id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,  -- 用户ID，关联认证用户表

    -- 基本信息 (Basic Information)
    -- Note: email, phone, created_at, updated_at are available in auth.users
    -- Note: custom metadata should use auth.users.raw_user_meta_data instead of separate metadata field
    display_name VARCHAR(100),                           -- 显示名称
    first_name VARCHAR(50),                              -- 名
    last_name VARCHAR(50),                               -- 姓
    bio TEXT,                                            -- 个人简介
    avatar_url TEXT,                                     -- 头像URL

    -- 人口统计信息 (Demographics)
    birth_date DATE,                                     -- 出生日期
    gender_id UUID REFERENCES profile.genders(id),       -- 性别
    region_id UUID REFERENCES profile.regions(id),       -- 地区
    timezone VARCHAR(50),                                -- 时区

    -- 职业和教育 (Career & Education)
    occupation_id UUID REFERENCES profile.occupations(id), -- 职业
    education_level_id UUID REFERENCES profile.education_levels(id), -- 教育程度
    company VARCHAR(100),                                -- 公司名称
    school VARCHAR(100),                                 -- 学校名称

    -- 个人状态 (Personal Status)
    relationship_status_id UUID REFERENCES profile.relationship_statuses(id), -- 关系状态

    -- 联系信息 (Contact Information)
    -- Note: phone is available in auth.users.phone
    website_url TEXT,                                    -- 个人网站

    -- 系统字段 (System Fields)
    profile_visibility VARCHAR(20) DEFAULT 'public' CHECK (profile_visibility IN ('public', 'friends', 'private')), -- 档案可见性
    profile_completion_percentage INTEGER DEFAULT 0 CHECK (profile_completion_percentage >= 0 AND profile_completion_percentage <= 100), -- 档案完成度
    last_active_at TIMESTAMPTZ,                          -- 最后活跃时间

    -- 审计字段 (Audit Fields)
    -- Note: created_at and updated_at are available in auth.users
    is_active BOOLEAN DEFAULT true,                      -- 是否激活
    is_verified BOOLEAN DEFAULT false                    -- 是否已验证
    -- Removed: phone (use auth.users.phone)
    -- Removed: metadata (use auth.users.raw_user_meta_data)
    -- Removed: created_at, updated_at (use auth.users.created_at, updated_at)
);

-- 档案完成度跟踪表
CREATE TABLE profile.completion_status (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES profile.user_profiles(id) ON DELETE CASCADE,
    section_name VARCHAR(50) NOT NULL,                   -- 档案部分名称
    is_completed BOOLEAN DEFAULT false,                  -- 是否完成
    completion_date TIMESTAMPTZ,                         -- 完成日期
    completion_percentage INTEGER DEFAULT 0 CHECK (completion_percentage >= 0 AND completion_percentage <= 100),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(user_id, section_name)
);

-- 档案版本历史表
CREATE TABLE profile.profile_versions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES profile.user_profiles(id) ON DELETE CASCADE,
    version_number INTEGER NOT NULL,                     -- 版本号
    changes_summary TEXT,                                -- 变更摘要
    profile_data JSONB NOT NULL,                         -- 档案数据快照
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(user_id, version_number)
);

-- =====================================================
-- INDEXES - 索引
-- =====================================================

-- 字典表索引
CREATE INDEX idx_regions_code ON profile.regions(code);
CREATE INDEX idx_regions_parent ON profile.regions(parent_id);
CREATE INDEX idx_regions_level ON profile.regions(level);
CREATE INDEX idx_occupations_code ON profile.occupations(code);
CREATE INDEX idx_occupations_category ON profile.occupations(category_id);
CREATE INDEX idx_occupation_categories_parent ON profile.occupation_categories(parent_id);

-- 用户档案索引
CREATE INDEX idx_user_profiles_display_name ON profile.user_profiles(display_name);
CREATE INDEX idx_user_profiles_region ON profile.user_profiles(region_id);
CREATE INDEX idx_user_profiles_occupation ON profile.user_profiles(occupation_id);
CREATE INDEX idx_user_profiles_education ON profile.user_profiles(education_level_id);
CREATE INDEX idx_user_profiles_gender ON profile.user_profiles(gender_id);
CREATE INDEX idx_user_profiles_active ON profile.user_profiles(is_active) WHERE is_active = true;
CREATE INDEX idx_user_profiles_visibility ON profile.user_profiles(profile_visibility);
CREATE INDEX idx_user_profiles_completion ON profile.user_profiles(profile_completion_percentage);

-- =====================================================
-- TRIGGERS AND FUNCTIONS - 触发器和函数
-- =====================================================

-- 自动更新updated_at时间戳的函数
CREATE OR REPLACE FUNCTION profile.update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- 应用更新触发器
CREATE TRIGGER update_user_profiles_updated_at 
    BEFORE UPDATE ON profile.user_profiles
    FOR EACH ROW EXECUTE FUNCTION profile.update_updated_at_column();

CREATE TRIGGER update_completion_status_updated_at 
    BEFORE UPDATE ON profile.completion_status
    FOR EACH ROW EXECUTE FUNCTION profile.update_updated_at_column();

-- 档案完成度计算函数
CREATE OR REPLACE FUNCTION profile.update_profile_completion()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE profile.user_profiles
    SET profile_completion_percentage = (
        SELECT COALESCE(AVG(completion_percentage), 0)
        FROM profile.completion_status
        WHERE user_id = NEW.user_id
    )
    WHERE id = NEW.user_id;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- 档案完成度更新触发器
CREATE TRIGGER update_profile_completion_trigger
    AFTER INSERT OR UPDATE ON profile.completion_status
    FOR EACH ROW EXECUTE FUNCTION profile.update_profile_completion();

-- =====================================================
-- ROW LEVEL SECURITY - 行级安全策略
-- =====================================================

-- 启用RLS
ALTER TABLE profile.user_profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE profile.completion_status ENABLE ROW LEVEL SECURITY;
ALTER TABLE profile.profile_versions ENABLE ROW LEVEL SECURITY;

-- 字典表RLS（只读）
ALTER TABLE profile.regions ENABLE ROW LEVEL SECURITY;
ALTER TABLE profile.occupations ENABLE ROW LEVEL SECURITY;
ALTER TABLE profile.occupation_categories ENABLE ROW LEVEL SECURITY;
ALTER TABLE profile.education_levels ENABLE ROW LEVEL SECURITY;
ALTER TABLE profile.relationship_statuses ENABLE ROW LEVEL SECURITY;
ALTER TABLE profile.genders ENABLE ROW LEVEL SECURITY;

-- 用户档案策略
CREATE POLICY "Users can view public profiles" ON profile.user_profiles
    FOR SELECT USING (profile_visibility = 'public' OR id = auth.uid());

CREATE POLICY "Users can manage their own profile" ON profile.user_profiles
    FOR ALL USING (id = auth.uid());

-- 完成状态策略
CREATE POLICY "Users can view their own completion status" ON profile.completion_status
    FOR SELECT USING (user_id = auth.uid());

CREATE POLICY "Users can manage their own completion status" ON profile.completion_status
    FOR ALL USING (user_id = auth.uid());

-- 字典表策略（所有人可读）
CREATE POLICY "Anyone can view regions" ON profile.regions FOR SELECT USING (true);
CREATE POLICY "Anyone can view occupations" ON profile.occupations FOR SELECT USING (true);
CREATE POLICY "Anyone can view occupation categories" ON profile.occupation_categories FOR SELECT USING (true);
CREATE POLICY "Anyone can view education levels" ON profile.education_levels FOR SELECT USING (true);
CREATE POLICY "Anyone can view relationship statuses" ON profile.relationship_statuses FOR SELECT USING (true);
CREATE POLICY "Anyone can view genders" ON profile.genders FOR SELECT USING (true);

-- =====================================================
-- SEED DATA - 种子数据
-- =====================================================

-- 性别数据
INSERT INTO profile.genders (code, name, name_en, sort_order) VALUES
('male', '男性', 'Male', 1),
('female', '女性', 'Female', 2),
('non_binary', '非二元性别', 'Non-binary', 3),
('prefer_not_to_say', '不愿透露', 'Prefer not to say', 4);

-- 教育程度数据
INSERT INTO profile.education_levels (code, name, name_en, level_order) VALUES
('elementary', '小学', 'Elementary School', 1),
('middle_school', '初中', 'Middle School', 2),
('high_school', '高中', 'High School', 3),
('associate', '专科', 'Associate Degree', 4),
('bachelor', '本科', 'Bachelor Degree', 5),
('master', '硕士', 'Master Degree', 6),
('doctorate', '博士', 'Doctorate', 7);

-- 关系状态数据
INSERT INTO profile.relationship_statuses (code, name, name_en, sort_order) VALUES
('single', '单身', 'Single', 1),
('dating', '恋爱中', 'Dating', 2),
('engaged', '已订婚', 'Engaged', 3),
('married', '已婚', 'Married', 4),
('divorced', '离异', 'Divorced', 5),
('widowed', '丧偶', 'Widowed', 6),
('complicated', '复杂', 'It''s Complicated', 7);

-- 职业分类数据（一级分类）
INSERT INTO profile.occupation_categories (code, name, name_en, sort_order) VALUES
('tech', '技术', 'Technology', 1),
('business', '商业', 'Business', 2),
('education', '教育', 'Education', 3),
('healthcare', '医疗', 'Healthcare', 4),
('arts', '艺术', 'Arts & Entertainment', 5),
('service', '服务业', 'Service Industry', 6),
('government', '政府', 'Government', 7),
('other', '其他', 'Other', 8);

-- 地区数据（示例：中国主要城市）
INSERT INTO profile.regions (code, name, name_en, level, sort_order) VALUES
('CN', '中国', 'China', 1, 1),
('US', '美国', 'United States', 1, 2);

-- 中国省份
INSERT INTO profile.regions (code, name, name_en, parent_id, level, sort_order)
SELECT 'CN-BJ', '北京市', 'Beijing', id, 2, 1 FROM profile.regions WHERE code = 'CN'
UNION ALL
SELECT 'CN-SH', '上海市', 'Shanghai', id, 2, 2 FROM profile.regions WHERE code = 'CN'
UNION ALL
SELECT 'CN-GD', '广东省', 'Guangdong', id, 2, 3 FROM profile.regions WHERE code = 'CN';

-- =====================================================
-- VIEWS - 视图
-- =====================================================

-- 用户档案摘要视图 (优化版本 - 包含auth.users字段)
-- Optimized user profile summary view - includes auth.users fields
CREATE VIEW profile.user_profile_summary AS
SELECT
    up.id,
    up.display_name,
    up.first_name,
    up.last_name,
    up.bio,
    up.avatar_url,
    up.birth_date,
    EXTRACT(YEAR FROM AGE(up.birth_date)) as age,
    g.name as gender,
    r.name as region,
    o.name as occupation,
    el.name as education_level,
    rs.name as relationship_status,
    up.profile_completion_percentage,
    up.last_active_at,
    -- Fields from auth.users
    au.email,
    au.phone,
    au.created_at,
    au.updated_at,
    au.raw_user_meta_data as user_metadata,
    au.email_confirmed_at,
    au.last_sign_in_at
FROM profile.user_profiles up
LEFT JOIN auth.users au ON up.id = au.id
LEFT JOIN profile.genders g ON up.gender_id = g.id
LEFT JOIN profile.regions r ON up.region_id = r.id
LEFT JOIN profile.occupations o ON up.occupation_id = o.id
LEFT JOIN profile.education_levels el ON up.education_level_id = el.id
LEFT JOIN profile.relationship_statuses rs ON up.relationship_status_id = rs.id
WHERE up.is_active = true;

-- =====================================================
-- COMMENTS - 表注释
-- =====================================================

COMMENT ON SCHEMA profile IS 'Profile schema for user basic information and demographics 用户基本信息和人口统计数据架构';
COMMENT ON TABLE profile.user_profiles IS 'Main user profile table with basic demographic information 主用户档案表，包含基本人口统计信息';
COMMENT ON TABLE profile.regions IS 'Geographic regions dictionary with hierarchical structure 地理区域字典表，支持层级结构';
COMMENT ON TABLE profile.occupations IS 'Occupations dictionary table 职业字典表';
COMMENT ON TABLE profile.education_levels IS 'Education levels dictionary table 教育程度字典表';
