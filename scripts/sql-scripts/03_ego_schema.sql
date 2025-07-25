-- =====================================================
-- EGO SCHEMA - 人格特质/认知功能
-- =====================================================
-- 专注于用户的心理特质、人格类型、认知模式等内在属性
-- 包含荣格认知功能和可扩展的人格特质系统
-- =====================================================

-- Create ego schema
CREATE SCHEMA IF NOT EXISTS ego;

-- =====================================================
-- COGNITIVE FUNCTIONS - 认知功能（荣格8种认知功能）
-- =====================================================

-- 荣格8种认知功能主表
CREATE TABLE ego.cognitive_functions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    code VARCHAR(2) NOT NULL UNIQUE,                     -- 功能代码：Ni, Ne, Si, Se, Ti, Te, Fi, Fe
    name VARCHAR(50) NOT NULL,                           -- 功能名称
    full_name VARCHAR(100) NOT NULL,                     -- 完整名称
    description TEXT,                                    -- 功能描述
    function_type VARCHAR(20) NOT NULL CHECK (function_type IN ('thinking', 'feeling', 'sensing', 'intuition')), -- 功能类型
    attitude VARCHAR(20) NOT NULL CHECK (attitude IN ('introverted', 'extraverted')), -- 态度：内向/外向
    is_active BOOLEAN DEFAULT true,                      -- 是否激活
    created_at TIMESTAMPTZ DEFAULT NOW()                 -- 创建时间
);

-- 用户认知功能评分和排名
CREATE TABLE ego.user_cognitive_functions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE, -- 用户ID
    cognitive_function_id UUID NOT NULL REFERENCES ego.cognitive_functions(id), -- 认知功能ID
    raw_score INTEGER CHECK (raw_score >= 0 AND raw_score <= 100), -- 原始分数（0-100）
    normalized_score DECIMAL(5,2) CHECK (normalized_score >= 0 AND normalized_score <= 100), -- 标准化分数
    function_rank INTEGER CHECK (function_rank >= 1 AND function_rank <= 8), -- 功能排名（1-8）
    confidence_level DECIMAL(3,2) DEFAULT 0.5 CHECK (confidence_level >= 0 AND confidence_level <= 1), -- 置信度（0-1）
    assessment_source VARCHAR(50) DEFAULT 'self_assessment', -- 评估来源
    notes TEXT,                                          -- 备注
    assessed_at TIMESTAMPTZ DEFAULT NOW(),               -- 评估时间
    created_at TIMESTAMPTZ DEFAULT NOW(),                -- 创建时间
    updated_at TIMESTAMPTZ DEFAULT NOW(),                -- 更新时间
    UNIQUE(user_id, cognitive_function_id)               -- 用户+认知功能唯一约束
);

-- 认知功能评估历史记录
CREATE TABLE ego.cognitive_function_assessments (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE, -- 用户ID
    assessment_type VARCHAR(50) NOT NULL,               -- 评估类型：initial, periodic, ai_analysis, peer_feedback
    assessment_method VARCHAR(50),                      -- 评估方法：questionnaire, behavioral_analysis, interview
    total_score INTEGER,                                -- 总分
    assessment_data JSONB DEFAULT '{}',                 -- 评估数据（JSON格式）
    confidence_score DECIMAL(3,2) CHECK (confidence_score >= 0 AND confidence_score <= 1), -- 置信度分数
    assessor_id UUID REFERENCES auth.users(id),         -- 评估者ID
    notes TEXT,                                         -- 备注
    completed_at TIMESTAMPTZ DEFAULT NOW(),             -- 完成时间
    created_at TIMESTAMPTZ DEFAULT NOW()                -- 创建时间
);

-- =====================================================
-- PERSONALITY TRAITS - 人格特质系统
-- =====================================================

-- 特质分类表（支持不同人格框架）
CREATE TABLE ego.trait_categories (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(100) NOT NULL UNIQUE,                  -- 分类名称
    slug VARCHAR(50) NOT NULL UNIQUE,                   -- URL友好标识符
    description TEXT,                                   -- 分类描述
    framework VARCHAR(50),                              -- 框架类型：big_five, enneagram, disc, custom
    version VARCHAR(20) DEFAULT '1.0',                  -- 版本号
    is_active BOOLEAN DEFAULT true,                     -- 是否激活
    created_at TIMESTAMPTZ DEFAULT NOW(),               -- 创建时间
    updated_at TIMESTAMPTZ DEFAULT NOW()                -- 更新时间
);

-- 特质值类型定义
CREATE TABLE ego.trait_value_types (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(50) NOT NULL UNIQUE,                   -- 类型名称
    data_type VARCHAR(20) NOT NULL CHECK (data_type IN ('integer', 'decimal', 'boolean', 'text', 'enum')), -- 数据类型
    min_value DECIMAL,                                  -- 最小值
    max_value DECIMAL,                                  -- 最大值
    enum_values TEXT[],                                 -- 枚举值（用于枚举类型）
    validation_rules JSONB DEFAULT '{}',                -- 验证规则（JSON格式）
    description TEXT,                                   -- 描述
    created_at TIMESTAMPTZ DEFAULT NOW()                -- 创建时间
);

-- 人格特质主表
CREATE TABLE ego.personality_traits (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(100) NOT NULL,                         -- 特质名称
    slug VARCHAR(50) NOT NULL,                          -- URL友好标识符
    description TEXT,                                   -- 特质描述
    category_id UUID REFERENCES ego.trait_categories(id), -- 所属分类ID
    value_type_id UUID NOT NULL REFERENCES ego.trait_value_types(id), -- 数值类型ID
    is_reverse_scored BOOLEAN DEFAULT false,            -- 是否反向计分
    display_order INTEGER DEFAULT 0,                    -- 显示顺序
    tags TEXT[],                                        -- 标签数组
    is_active BOOLEAN DEFAULT true,                     -- 是否激活
    created_at TIMESTAMPTZ DEFAULT NOW(),               -- 创建时间
    updated_at TIMESTAMPTZ DEFAULT NOW(),               -- 更新时间
    UNIQUE(category_id, slug)                           -- 分类+标识符唯一约束
);

-- 用户人格特质值
CREATE TABLE ego.user_personality_traits (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE, -- 用户ID
    trait_id UUID NOT NULL REFERENCES ego.personality_traits(id), -- 特质ID
    value_numeric DECIMAL,                              -- 数值型值
    value_text TEXT,                                    -- 文本型值
    value_boolean BOOLEAN,                              -- 布尔型值
    confidence_level DECIMAL(3,2) DEFAULT 0.5 CHECK (confidence_level >= 0 AND confidence_level <= 1), -- 置信度
    assessment_source VARCHAR(50) DEFAULT 'self_assessment', -- 评估来源
    assessment_date TIMESTAMPTZ DEFAULT NOW(),          -- 评估日期
    notes TEXT,                                         -- 备注
    is_public BOOLEAN DEFAULT true,                     -- 是否公开
    created_at TIMESTAMPTZ DEFAULT NOW(),               -- 创建时间
    updated_at TIMESTAMPTZ DEFAULT NOW(),               -- 更新时间
    UNIQUE(user_id, trait_id)                           -- 用户+特质唯一约束
);

-- 特质评估历史和来源
CREATE TABLE ego.trait_assessments (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE, -- 用户ID
    assessment_name VARCHAR(100) NOT NULL,              -- 评估名称
    assessment_type VARCHAR(50) NOT NULL,               -- 评估类型：questionnaire, ai_analysis, peer_feedback, professional
    category_id UUID REFERENCES ego.trait_categories(id), -- 分类ID
    total_questions INTEGER,                            -- 总题数
    completed_questions INTEGER,                        -- 已完成题数
    overall_confidence DECIMAL(3,2) CHECK (overall_confidence >= 0 AND overall_confidence <= 1), -- 整体置信度
    assessment_data JSONB DEFAULT '{}',                 -- 评估数据（JSON格式）
    assessor_id UUID REFERENCES auth.users(id),         -- 评估者ID
    started_at TIMESTAMPTZ DEFAULT NOW(),               -- 开始时间
    completed_at TIMESTAMPTZ,                           -- 完成时间
    created_at TIMESTAMPTZ DEFAULT NOW()                -- 创建时间
);

-- =====================================================
-- INDEXES - 索引
-- =====================================================

-- 认知功能索引
CREATE INDEX idx_cognitive_functions_code ON ego.cognitive_functions(code);
CREATE INDEX idx_cognitive_functions_type ON ego.cognitive_functions(function_type);
CREATE INDEX idx_user_cognitive_functions_user ON ego.user_cognitive_functions(user_id);
CREATE INDEX idx_user_cognitive_functions_rank ON ego.user_cognitive_functions(function_rank);
CREATE INDEX idx_user_cognitive_functions_score ON ego.user_cognitive_functions(normalized_score DESC);

-- 人格特质索引
CREATE INDEX idx_trait_categories_slug ON ego.trait_categories(slug);
CREATE INDEX idx_trait_categories_framework ON ego.trait_categories(framework);
CREATE INDEX idx_personality_traits_category ON ego.personality_traits(category_id);
CREATE INDEX idx_personality_traits_slug ON ego.personality_traits(slug);
CREATE INDEX idx_user_personality_traits_user ON ego.user_personality_traits(user_id);
CREATE INDEX idx_user_personality_traits_public ON ego.user_personality_traits(is_public) WHERE is_public = true;

-- 评估历史索引
CREATE INDEX idx_cognitive_assessments_user ON ego.cognitive_function_assessments(user_id);
CREATE INDEX idx_cognitive_assessments_type ON ego.cognitive_function_assessments(assessment_type);
CREATE INDEX idx_trait_assessments_user ON ego.trait_assessments(user_id);
CREATE INDEX idx_trait_assessments_category ON ego.trait_assessments(category_id);

-- =====================================================
-- TRIGGERS AND FUNCTIONS - 触发器和函数
-- =====================================================

-- 自动更新updated_at时间戳的函数
CREATE OR REPLACE FUNCTION ego.update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- 应用更新触发器
CREATE TRIGGER update_user_cognitive_functions_updated_at 
    BEFORE UPDATE ON ego.user_cognitive_functions
    FOR EACH ROW EXECUTE FUNCTION ego.update_updated_at_column();

CREATE TRIGGER update_trait_categories_updated_at 
    BEFORE UPDATE ON ego.trait_categories
    FOR EACH ROW EXECUTE FUNCTION ego.update_updated_at_column();

CREATE TRIGGER update_personality_traits_updated_at 
    BEFORE UPDATE ON ego.personality_traits
    FOR EACH ROW EXECUTE FUNCTION ego.update_updated_at_column();

CREATE TRIGGER update_user_personality_traits_updated_at 
    BEFORE UPDATE ON ego.user_personality_traits
    FOR EACH ROW EXECUTE FUNCTION ego.update_updated_at_column();

-- =====================================================
-- ROW LEVEL SECURITY - 行级安全策略
-- =====================================================

-- 启用RLS
ALTER TABLE ego.cognitive_functions ENABLE ROW LEVEL SECURITY;
ALTER TABLE ego.user_cognitive_functions ENABLE ROW LEVEL SECURITY;
ALTER TABLE ego.cognitive_function_assessments ENABLE ROW LEVEL SECURITY;
ALTER TABLE ego.trait_categories ENABLE ROW LEVEL SECURITY;
ALTER TABLE ego.trait_value_types ENABLE ROW LEVEL SECURITY;
ALTER TABLE ego.personality_traits ENABLE ROW LEVEL SECURITY;
ALTER TABLE ego.user_personality_traits ENABLE ROW LEVEL SECURITY;
ALTER TABLE ego.trait_assessments ENABLE ROW LEVEL SECURITY;

-- 认知功能策略
CREATE POLICY "Anyone can view cognitive functions" ON ego.cognitive_functions
    FOR SELECT USING (true);

CREATE POLICY "Users can view public cognitive function data" ON ego.user_cognitive_functions
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM profile.user_profiles
            WHERE id = ego.user_cognitive_functions.user_id
            AND (profile_visibility = 'public' OR id = auth.uid())
        )
    );

CREATE POLICY "Users can manage their own cognitive functions" ON ego.user_cognitive_functions
    FOR ALL USING (user_id = auth.uid());

-- 人格特质策略
CREATE POLICY "Anyone can view trait categories" ON ego.trait_categories FOR SELECT USING (true);
CREATE POLICY "Anyone can view trait value types" ON ego.trait_value_types FOR SELECT USING (true);
CREATE POLICY "Anyone can view personality traits" ON ego.personality_traits FOR SELECT USING (true);

CREATE POLICY "Users can view public personality traits data" ON ego.user_personality_traits
    FOR SELECT USING (is_public = true OR user_id = auth.uid());

CREATE POLICY "Users can manage their own personality traits" ON ego.user_personality_traits
    FOR ALL USING (user_id = auth.uid());

-- 评估策略
CREATE POLICY "Users can view their own cognitive assessments" ON ego.cognitive_function_assessments
    FOR SELECT USING (user_id = auth.uid() OR assessor_id = auth.uid());

CREATE POLICY "Users can manage their own cognitive assessments" ON ego.cognitive_function_assessments
    FOR ALL USING (user_id = auth.uid());

CREATE POLICY "Users can view their own trait assessments" ON ego.trait_assessments
    FOR SELECT USING (user_id = auth.uid() OR assessor_id = auth.uid());

CREATE POLICY "Users can manage their own trait assessments" ON ego.trait_assessments
    FOR ALL USING (user_id = auth.uid());

-- =====================================================
-- SEED DATA - 种子数据
-- =====================================================

-- 插入荣格8种认知功能数据
INSERT INTO ego.cognitive_functions (code, name, full_name, description, function_type, attitude) VALUES
('Ni', 'Introverted Intuition', 'Introverted Intuition', 'Focuses on internal patterns, insights, and future possibilities. Seeks to understand the underlying meaning and connections. 专注于内在模式、洞察力和未来可能性。', 'intuition', 'introverted'),
('Ne', 'Extraverted Intuition', 'Extraverted Intuition', 'Explores external possibilities and connections. Generates ideas and sees potential in the outside world. 探索外部可能性和联系。', 'intuition', 'extraverted'),
('Si', 'Introverted Sensing', 'Introverted Sensing', 'Focuses on internal sensory experiences and past memories. Values tradition and detailed recall. 专注于内在感官体验和过去记忆。', 'sensing', 'introverted'),
('Se', 'Extraverted Sensing', 'Extraverted Sensing', 'Engages with immediate sensory experiences in the external world. Lives in the present moment. 参与外部世界的即时感官体验。', 'sensing', 'extraverted'),
('Ti', 'Introverted Thinking', 'Introverted Thinking', 'Analyzes and categorizes information internally. Seeks logical consistency and understanding. 内部分析和分类信息。', 'thinking', 'introverted'),
('Te', 'Extraverted Thinking', 'Extraverted Thinking', 'Organizes and structures the external world. Focuses on efficiency and objective results. 组织和构建外部世界。', 'thinking', 'extraverted'),
('Fi', 'Introverted Feeling', 'Introverted Feeling', 'Evaluates based on internal values and personal significance. Seeks authenticity and harmony. 基于内在价值观进行评估。', 'feeling', 'introverted'),
('Fe', 'Extraverted Feeling', 'Extraverted Feeling', 'Considers the feelings and needs of others. Seeks group harmony and social connection. 考虑他人的感受和需求。', 'feeling', 'extraverted');

-- 插入特质值类型
INSERT INTO ego.trait_value_types (name, data_type, min_value, max_value, description) VALUES
('percentage_score', 'integer', 0, 100, 'Percentage score from 0 to 100 百分比分数0-100'),
('likert_5', 'integer', 1, 5, '5-point Likert scale 5点李克特量表'),
('likert_7', 'integer', 1, 7, '7-point Likert scale 7点李克特量表'),
('preference_level', 'integer', 1, 10, 'Preference level from 1 to 10 偏好等级1-10'),
('boolean_choice', 'boolean', NULL, NULL, 'True/false choice 是/否选择'),
('text_description', 'text', NULL, NULL, 'Free text description 自由文本描述');

-- 插入特质分类
INSERT INTO ego.trait_categories (name, slug, description, framework) VALUES
('Big Five Personality Traits', 'big_five', 'The five-factor model of personality 大五人格模型', 'big_five'),
('Enneagram Types', 'enneagram', 'Nine personality types based on core motivations 基于核心动机的九型人格', 'enneagram'),
('DISC Assessment', 'disc', 'Behavioral assessment tool measuring Dominance, Influence, Steadiness, and Conscientiousness DISC行为评估工具', 'disc'),
('Values and Motivations', 'values', 'Core values and motivational drivers 核心价值观和动机驱动因素', 'custom'),
('Communication Style', 'communication', 'Preferred communication patterns and styles 偏好的沟通模式和风格', 'custom');

-- =====================================================
-- VIEWS - 视图
-- =====================================================

-- 用户认知功能排名视图
CREATE VIEW ego.user_cognitive_function_rankings AS
SELECT
    ucf.user_id,                    -- 用户ID
    cf.code,                        -- 功能代码
    cf.name,                        -- 功能名称
    cf.function_type,               -- 功能类型
    cf.attitude,                    -- 态度（内向/外向）
    ucf.normalized_score,           -- 标准化分数
    ucf.function_rank,              -- 功能排名
    ucf.confidence_level,           -- 置信度
    ucf.assessed_at                 -- 评估时间
FROM ego.user_cognitive_functions ucf
JOIN ego.cognitive_functions cf ON ucf.cognitive_function_id = cf.id
ORDER BY ucf.user_id, ucf.function_rank;

-- 用户人格特质摘要视图
CREATE VIEW ego.user_personality_summary AS
SELECT
    upt.user_id,
    pt.name AS trait_name,
    tc.name AS category_name,
    tc.framework,
    CASE
        WHEN tvt.data_type = 'integer' THEN upt.value_numeric::text
        WHEN tvt.data_type = 'decimal' THEN upt.value_numeric::text
        WHEN tvt.data_type = 'boolean' THEN upt.value_boolean::text
        WHEN tvt.data_type = 'text' THEN upt.value_text
        ELSE NULL
    END AS trait_value,
    upt.confidence_level,
    upt.assessment_date,
    upt.is_public
FROM ego.user_personality_traits upt
JOIN ego.personality_traits pt ON upt.trait_id = pt.id
JOIN ego.trait_categories tc ON pt.category_id = tc.id
JOIN ego.trait_value_types tvt ON pt.value_type_id = tvt.id
WHERE upt.is_public = true OR upt.user_id = auth.uid();

-- 认知功能类型分布视图
CREATE VIEW ego.cognitive_function_distribution AS
SELECT
    user_id,
    SUM(CASE WHEN cf.function_type = 'thinking' THEN ucf.normalized_score ELSE 0 END) /
    COUNT(CASE WHEN cf.function_type = 'thinking' THEN 1 END) AS thinking_avg,
    SUM(CASE WHEN cf.function_type = 'feeling' THEN ucf.normalized_score ELSE 0 END) /
    COUNT(CASE WHEN cf.function_type = 'feeling' THEN 1 END) AS feeling_avg,
    SUM(CASE WHEN cf.function_type = 'sensing' THEN ucf.normalized_score ELSE 0 END) /
    COUNT(CASE WHEN cf.function_type = 'sensing' THEN 1 END) AS sensing_avg,
    SUM(CASE WHEN cf.function_type = 'intuition' THEN ucf.normalized_score ELSE 0 END) /
    COUNT(CASE WHEN cf.function_type = 'intuition' THEN 1 END) AS intuition_avg,
    SUM(CASE WHEN cf.attitude = 'introverted' THEN ucf.normalized_score ELSE 0 END) /
    COUNT(CASE WHEN cf.attitude = 'introverted' THEN 1 END) AS introverted_avg,
    SUM(CASE WHEN cf.attitude = 'extraverted' THEN ucf.normalized_score ELSE 0 END) /
    COUNT(CASE WHEN cf.attitude = 'extraverted' THEN 1 END) AS extraverted_avg
FROM ego.user_cognitive_functions ucf
JOIN ego.cognitive_functions cf ON ucf.cognitive_function_id = cf.id
GROUP BY user_id;

-- =====================================================
-- COMMENTS - 表注释
-- =====================================================

COMMENT ON SCHEMA ego IS 'Ego schema for personality traits and cognitive functions 人格特质和认知功能架构';
COMMENT ON TABLE ego.cognitive_functions IS 'Jung''s 8 cognitive functions for personality typing 荣格8种认知功能，用于人格类型分析';
COMMENT ON TABLE ego.user_cognitive_functions IS 'User-specific cognitive function scores and rankings 用户特定的认知功能评分和排名';
COMMENT ON TABLE ego.personality_traits IS 'Extensible personality traits supporting multiple frameworks 可扩展人格特质，支持多种框架';
COMMENT ON TABLE ego.user_personality_traits IS 'User-specific personality trait values with confidence scoring 用户特定的人格特质值，包含置信度评分';
