-- =====================================================
-- ATTRIBUTES SCHEMA - 用户属性/爱好
-- =====================================================
-- 将hobby概念重构为更通用的"属性"概念
-- 支持多级分类的层级结构
-- 预定义所有用户可选择的属性范围和分类层级
-- =====================================================

-- Create attributes schema
CREATE SCHEMA IF NOT EXISTS attributes;

-- =====================================================
-- ATTRIBUTE CATEGORIES - 属性分类表（支持多级层级）
-- =====================================================

-- 属性分类表（支持无限层级嵌套）
CREATE TABLE attributes.categories (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    code VARCHAR(50) NOT NULL,                           -- 分类代码
    name VARCHAR(100) NOT NULL,                          -- 分类名称
    name_en VARCHAR(100),                                -- 英文名称
    description TEXT,                                    -- 分类描述
    parent_id UUID REFERENCES attributes.categories(id), -- 父分类ID（支持层级结构）
    level INTEGER NOT NULL DEFAULT 1,                    -- 层级：1=一级分类，2=二级分类，以此类推
    path TEXT,                                           -- 层级路径（如：/运动/球类/足球）
    icon_name VARCHAR(50),                               -- 图标名称
    color_code VARCHAR(7),                               -- 颜色代码（十六进制）
    sort_order INTEGER DEFAULT 0,                        -- 排序顺序
    is_active BOOLEAN DEFAULT true,                      -- 是否激活
    is_system BOOLEAN DEFAULT true,                      -- 是否系统预定义（false表示用户自定义）
    created_by UUID REFERENCES auth.users(id),           -- 创建者（用户自定义分类时使用）
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    
    -- 确保同一父分类下代码唯一
    UNIQUE(parent_id, code),
    -- 确保同一父分类下名称唯一
    UNIQUE(parent_id, name)
);

-- =====================================================
-- ATTRIBUTES - 具体属性表
-- =====================================================

-- 具体属性表
CREATE TABLE attributes.attributes (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    code VARCHAR(50) NOT NULL,                           -- 属性代码
    name VARCHAR(100) NOT NULL,                          -- 属性名称
    name_en VARCHAR(100),                                -- 英文名称
    description TEXT,                                    -- 属性描述
    category_id UUID NOT NULL REFERENCES attributes.categories(id), -- 所属分类
    
    -- 属性元数据
    tags TEXT[],                                         -- 标签数组（用于搜索和分类）
    difficulty_level VARCHAR(20) DEFAULT 'any' CHECK (difficulty_level IN ('any', 'beginner', 'intermediate', 'advanced', 'expert')), -- 难度等级
    time_commitment VARCHAR(20) DEFAULT 'medium' CHECK (time_commitment IN ('low', 'medium', 'high')), -- 时间投入
    cost_level VARCHAR(20) DEFAULT 'medium' CHECK (cost_level IN ('free', 'low', 'medium', 'high')), -- 成本水平
    physical_intensity VARCHAR(20) DEFAULT 'medium' CHECK (physical_intensity IN ('none', 'low', 'medium', 'high')), -- 体力强度
    social_aspect VARCHAR(20) DEFAULT 'mixed' CHECK (social_aspect IN ('solo', 'small_group', 'large_group', 'mixed')), -- 社交属性
    indoor_outdoor VARCHAR(20) DEFAULT 'both' CHECK (indoor_outdoor IN ('indoor', 'outdoor', 'both')), -- 室内外属性
    
    -- 推荐信息
    recommended_age_min INTEGER,                         -- 推荐最小年龄
    recommended_age_max INTEGER,                         -- 推荐最大年龄
    equipment_required BOOLEAN DEFAULT false,            -- 是否需要设备
    equipment_description TEXT,                          -- 设备描述
    
    -- 系统字段
    popularity_score INTEGER DEFAULT 0,                  -- 受欢迎程度分数
    is_active BOOLEAN DEFAULT true,                      -- 是否激活
    is_system BOOLEAN DEFAULT true,                      -- 是否系统预定义
    created_by UUID REFERENCES auth.users(id),           -- 创建者（用户自定义属性时使用）
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    
    -- 确保同一分类下代码唯一
    UNIQUE(category_id, code),
    -- 确保同一分类下名称唯一
    UNIQUE(category_id, name)
);

-- =====================================================
-- USER ATTRIBUTES - 用户属性关联表
-- =====================================================

-- 用户属性关联表
CREATE TABLE attributes.user_attributes (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE, -- 用户ID
    attribute_id UUID NOT NULL REFERENCES attributes.attributes(id),    -- 属性ID
    
    -- 用户对该属性的评价和参与度
    interest_level INTEGER NOT NULL CHECK (interest_level >= 1 AND interest_level <= 10), -- 兴趣等级（1-10）
    skill_level VARCHAR(20) DEFAULT 'beginner' CHECK (skill_level IN ('beginner', 'intermediate', 'advanced', 'expert')), -- 技能水平
    experience_years INTEGER CHECK (experience_years >= 0), -- 经验年数
    
    -- 参与频率和时间投入
    frequency VARCHAR(20) CHECK (frequency IN ('daily', 'weekly', 'monthly', 'occasionally', 'rarely')), -- 参与频率
    time_spent_weekly INTEGER CHECK (time_spent_weekly >= 0), -- 每周花费时间（小时）
    
    -- 个人评价
    enjoyment_rating INTEGER CHECK (enjoyment_rating >= 1 AND enjoyment_rating <= 10), -- 享受程度评分
    difficulty_rating INTEGER CHECK (difficulty_rating >= 1 AND difficulty_rating <= 10), -- 难度评分
    social_rating INTEGER CHECK (social_rating >= 1 AND social_rating <= 10), -- 社交性评分
    
    -- 状态和时间
    status VARCHAR(20) DEFAULT 'active' CHECK (status IN ('active', 'inactive', 'interested', 'completed')), -- 状态
    started_at TIMESTAMPTZ,                              -- 开始时间
    last_activity_at TIMESTAMPTZ,                        -- 最后活动时间
    
    -- 个人备注和隐私
    notes TEXT,                                          -- 个人备注
    is_public BOOLEAN DEFAULT true,                      -- 是否公开
    is_featured BOOLEAN DEFAULT false,                   -- 是否在个人档案中突出显示
    
    -- 审计字段
    added_at TIMESTAMPTZ DEFAULT NOW(),                  -- 添加时间
    updated_at TIMESTAMPTZ DEFAULT NOW(),                -- 更新时间
    
    -- 确保用户+属性唯一
    UNIQUE(user_id, attribute_id)
);

-- =====================================================
-- ATTRIBUTE RELATIONSHIPS - 属性关系表
-- =====================================================

-- 属性关系表（用于表示属性之间的关联）
CREATE TABLE attributes.attribute_relationships (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    source_attribute_id UUID NOT NULL REFERENCES attributes.attributes(id), -- 源属性
    target_attribute_id UUID NOT NULL REFERENCES attributes.attributes(id), -- 目标属性
    relationship_type VARCHAR(50) NOT NULL,              -- 关系类型：similar, prerequisite, alternative, complementary
    strength DECIMAL(3,2) DEFAULT 0.5 CHECK (strength >= 0 AND strength <= 1), -- 关系强度
    description TEXT,                                    -- 关系描述
    is_bidirectional BOOLEAN DEFAULT false,              -- 是否双向关系
    created_at TIMESTAMPTZ DEFAULT NOW(),
    
    -- 确保不能自己关联自己
    CHECK (source_attribute_id != target_attribute_id),
    -- 确保关系唯一
    UNIQUE(source_attribute_id, target_attribute_id, relationship_type)
);

-- =====================================================
-- INDEXES - 索引
-- =====================================================

-- 分类表索引
CREATE INDEX idx_categories_code ON attributes.categories(code);
CREATE INDEX idx_categories_parent ON attributes.categories(parent_id);
CREATE INDEX idx_categories_level ON attributes.categories(level);
CREATE INDEX idx_categories_path ON attributes.categories(path);
CREATE INDEX idx_categories_active ON attributes.categories(is_active) WHERE is_active = true;

-- 属性表索引
CREATE INDEX idx_attributes_code ON attributes.attributes(code);
CREATE INDEX idx_attributes_category ON attributes.attributes(category_id);
CREATE INDEX idx_attributes_tags ON attributes.attributes USING GIN(tags);
CREATE INDEX idx_attributes_difficulty ON attributes.attributes(difficulty_level);
CREATE INDEX idx_attributes_popularity ON attributes.attributes(popularity_score DESC);
CREATE INDEX idx_attributes_active ON attributes.attributes(is_active) WHERE is_active = true;

-- 用户属性索引
CREATE INDEX idx_user_attributes_user ON attributes.user_attributes(user_id);
CREATE INDEX idx_user_attributes_attribute ON attributes.user_attributes(attribute_id);
CREATE INDEX idx_user_attributes_interest ON attributes.user_attributes(interest_level DESC);
CREATE INDEX idx_user_attributes_skill ON attributes.user_attributes(skill_level);
CREATE INDEX idx_user_attributes_public ON attributes.user_attributes(is_public) WHERE is_public = true;
CREATE INDEX idx_user_attributes_featured ON attributes.user_attributes(is_featured) WHERE is_featured = true;
CREATE INDEX idx_user_attributes_status ON attributes.user_attributes(status);

-- 属性关系索引
CREATE INDEX idx_attribute_relationships_source ON attributes.attribute_relationships(source_attribute_id);
CREATE INDEX idx_attribute_relationships_target ON attributes.attribute_relationships(target_attribute_id);
CREATE INDEX idx_attribute_relationships_type ON attributes.attribute_relationships(relationship_type);

-- =====================================================
-- TRIGGERS AND FUNCTIONS - 触发器和函数
-- =====================================================

-- 自动更新updated_at时间戳的函数
CREATE OR REPLACE FUNCTION attributes.update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- 应用更新触发器
CREATE TRIGGER update_categories_updated_at 
    BEFORE UPDATE ON attributes.categories
    FOR EACH ROW EXECUTE FUNCTION attributes.update_updated_at_column();

CREATE TRIGGER update_attributes_updated_at 
    BEFORE UPDATE ON attributes.attributes
    FOR EACH ROW EXECUTE FUNCTION attributes.update_updated_at_column();

CREATE TRIGGER update_user_attributes_updated_at 
    BEFORE UPDATE ON attributes.user_attributes
    FOR EACH ROW EXECUTE FUNCTION attributes.update_updated_at_column();

-- 自动更新分类路径的函数
CREATE OR REPLACE FUNCTION attributes.update_category_path()
RETURNS TRIGGER AS $$
DECLARE
    parent_path TEXT;
BEGIN
    IF NEW.parent_id IS NULL THEN
        NEW.path = '/' || NEW.name;
        NEW.level = 1;
    ELSE
        SELECT path, level INTO parent_path, NEW.level 
        FROM attributes.categories 
        WHERE id = NEW.parent_id;
        
        NEW.path = parent_path || '/' || NEW.name;
        NEW.level = NEW.level + 1;
    END IF;
    
    RETURN NEW;
END;
$$ language 'plpgsql';

-- 分类路径更新触发器
CREATE TRIGGER update_category_path_trigger
    BEFORE INSERT OR UPDATE ON attributes.categories
    FOR EACH ROW EXECUTE FUNCTION attributes.update_category_path();

-- 更新属性受欢迎程度的函数
CREATE OR REPLACE FUNCTION attributes.update_popularity_score()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE attributes.attributes
    SET popularity_score = (
        SELECT COUNT(*)
        FROM attributes.user_attributes
        WHERE attribute_id = NEW.attribute_id
        AND status = 'active'
    )
    WHERE id = NEW.attribute_id;
    
    RETURN NEW;
END;
$$ language 'plpgsql';

-- 受欢迎程度更新触发器
CREATE TRIGGER update_popularity_score_trigger
    AFTER INSERT OR UPDATE OR DELETE ON attributes.user_attributes
    FOR EACH ROW EXECUTE FUNCTION attributes.update_popularity_score();

-- =====================================================
-- ROW LEVEL SECURITY - 行级安全策略
-- =====================================================

-- 启用RLS
ALTER TABLE attributes.categories ENABLE ROW LEVEL SECURITY;
ALTER TABLE attributes.attributes ENABLE ROW LEVEL SECURITY;
ALTER TABLE attributes.user_attributes ENABLE ROW LEVEL SECURITY;
ALTER TABLE attributes.attribute_relationships ENABLE ROW LEVEL SECURITY;

-- 分类和属性表策略（所有人可读）
CREATE POLICY "Anyone can view categories" ON attributes.categories
    FOR SELECT USING (true);

CREATE POLICY "Users can create custom categories" ON attributes.categories
    FOR INSERT WITH CHECK (is_system = false AND created_by = auth.uid());

CREATE POLICY "Users can manage their own custom categories" ON attributes.categories
    FOR UPDATE USING (is_system = false AND created_by = auth.uid());

CREATE POLICY "Anyone can view attributes" ON attributes.attributes
    FOR SELECT USING (true);

CREATE POLICY "Users can create custom attributes" ON attributes.attributes
    FOR INSERT WITH CHECK (is_system = false AND created_by = auth.uid());

CREATE POLICY "Users can manage their own custom attributes" ON attributes.attributes
    FOR UPDATE USING (is_system = false AND created_by = auth.uid());

-- 用户属性关联策略
CREATE POLICY "Users can view public user attributes" ON attributes.user_attributes
    FOR SELECT USING (is_public = true OR user_id = auth.uid());

CREATE POLICY "Users can manage their own attributes" ON attributes.user_attributes
    FOR ALL USING (user_id = auth.uid());

-- 属性关系策略
CREATE POLICY "Anyone can view attribute relationships" ON attributes.attribute_relationships
    FOR SELECT USING (true);

-- =====================================================
-- SEED DATA - 种子数据
-- =====================================================

-- 一级分类数据
INSERT INTO attributes.categories (code, name, name_en, description, level, path, icon_name, color_code, sort_order) VALUES
('sports', '运动', 'Sports', '各类体育运动和身体活动', 1, '/运动', 'sports', '#10B981', 1),
('arts', '艺术', 'Arts', '创意和艺术表达形式', 1, '/艺术', 'palette', '#EC4899', 2),
('music', '音乐', 'Music', '音乐相关活动和技能', 1, '/音乐', 'music', '#8B5CF6', 3),
('reading', '阅读', 'Reading', '阅读和文学相关活动', 1, '/阅读', 'book', '#3B82F6', 4),
('tech', '科技', 'Technology', '技术和数字相关活动', 1, '/科技', 'computer', '#6366F1', 5),
('cooking', '烹饪', 'Cooking', '烹饪和美食相关活动', 1, '/烹饪', 'chef-hat', '#F59E0B', 6),
('travel', '旅行', 'Travel', '旅行和探索相关活动', 1, '/旅行', 'globe', '#EF4444', 7),
('games', '游戏', 'Games', '各类游戏活动', 1, '/游戏', 'gamepad', '#2563EB', 8),
('crafts', '手工', 'Crafts', '手工和DIY活动', 1, '/手工', 'hammer', '#D97706', 9),
('social', '社交', 'Social', '社交和社区活动', 1, '/社交', 'users', '#14B8A6', 10);

-- 二级分类数据（运动分类下）
INSERT INTO attributes.categories (code, name, name_en, description, parent_id, icon_name, color_code, sort_order)
SELECT 'ball_sports', '球类运动', 'Ball Sports', '各类球类运动', id, 'ball', '#10B981', 1
FROM attributes.categories WHERE code = 'sports'
UNION ALL
SELECT 'water_sports', '水上运动', 'Water Sports', '各类水上运动', id, 'water', '#0EA5E9', 2
FROM attributes.categories WHERE code = 'sports'
UNION ALL
SELECT 'outdoor_sports', '户外运动', 'Outdoor Sports', '各类户外运动', id, 'mountain', '#F59E0B', 3
FROM attributes.categories WHERE code = 'sports'
UNION ALL
SELECT 'fitness', '健身', 'Fitness', '健身和体能训练', id, 'dumbbell', '#EF4444', 4
FROM attributes.categories WHERE code = 'sports';

-- 二级分类数据（音乐分类下）
INSERT INTO attributes.categories (code, name, name_en, description, parent_id, icon_name, color_code, sort_order)
SELECT 'instruments', '乐器', 'Instruments', '各类乐器演奏', id, 'guitar', '#8B5CF6', 1
FROM attributes.categories WHERE code = 'music'
UNION ALL
SELECT 'vocal', '声乐', 'Vocal', '唱歌和声乐', id, 'microphone', '#EC4899', 2
FROM attributes.categories WHERE code = 'music'
UNION ALL
SELECT 'music_production', '音乐制作', 'Music Production', '音乐创作和制作', id, 'sliders', '#6366F1', 3
FROM attributes.categories WHERE code = 'music';

-- 三级分类数据（球类运动下）
INSERT INTO attributes.categories (code, name, name_en, description, parent_id, icon_name, color_code, sort_order)
SELECT 'basketball', '篮球', 'Basketball', '篮球运动', id, 'basketball', '#F97316', 1
FROM attributes.categories WHERE code = 'ball_sports'
UNION ALL
SELECT 'football', '足球', 'Football', '足球运动', id, 'football', '#22C55E', 2
FROM attributes.categories WHERE code = 'ball_sports'
UNION ALL
SELECT 'tennis', '网球', 'Tennis', '网球运动', id, 'tennis', '#FACC15', 3
FROM attributes.categories WHERE code = 'ball_sports'
UNION ALL
SELECT 'badminton', '羽毛球', 'Badminton', '羽毛球运动', id, 'badminton', '#A3E635', 4
FROM attributes.categories WHERE code = 'ball_sports';

-- 具体属性数据（篮球相关）
INSERT INTO attributes.attributes (code, name, name_en, description, category_id, difficulty_level, time_commitment, physical_intensity, social_aspect, indoor_outdoor, tags)
SELECT 'basketball_playing', '打篮球', 'Playing Basketball', '参与篮球比赛或休闲打球', id, 'intermediate', 'medium', 'high', 'small_group', 'both', ARRAY['team sport', 'ball game', 'cardio']
FROM attributes.categories WHERE code = 'basketball'
UNION ALL
SELECT 'basketball_watching', '看篮球比赛', 'Watching Basketball', '观看篮球比赛', id, 'any', 'low', 'none', 'large_group', 'both', ARRAY['spectator', 'sports fan', 'entertainment']
FROM attributes.categories WHERE code = 'basketball'
UNION ALL
SELECT 'basketball_coaching', '篮球教练', 'Basketball Coaching', '担任篮球教练', id, 'expert', 'high', 'medium', 'small_group', 'both', ARRAY['teaching', 'leadership', 'sports']
FROM attributes.categories WHERE code = 'basketball';

-- =====================================================
-- VIEWS - 视图
-- =====================================================

-- 属性分类树视图
CREATE VIEW attributes.category_tree AS
WITH RECURSIVE category_tree AS (
    -- 基础查询：获取所有一级分类
    SELECT
        id, code, name, name_en, description, parent_id, level, path,
        icon_name, color_code, sort_order, is_active, is_system,
        ARRAY[id] AS ancestry,
        ARRAY[name] AS ancestry_names,
        ARRAY[sort_order] AS ancestry_orders
    FROM attributes.categories
    WHERE parent_id IS NULL

    UNION ALL

    -- 递归查询：获取所有子分类
    SELECT
        c.id, c.code, c.name, c.name_en, c.description, c.parent_id, c.level, c.path,
        c.icon_name, c.color_code, c.sort_order, c.is_active, c.is_system,
        ct.ancestry || c.id,
        ct.ancestry_names || c.name,
        ct.ancestry_orders || c.sort_order
    FROM attributes.categories c
    JOIN category_tree ct ON c.parent_id = ct.id
)
SELECT * FROM category_tree
ORDER BY ancestry_orders;

-- 用户属性摘要视图
CREATE VIEW attributes.user_attribute_summary AS
SELECT
    ua.user_id,
    a.id AS attribute_id,
    a.name AS attribute_name,
    a.name_en AS attribute_name_en,
    c.name AS category_name,
    c.path AS category_path,
    ua.interest_level,
    ua.skill_level,
    ua.experience_years,
    ua.status,
    ua.is_featured,
    ua.is_public
FROM attributes.user_attributes ua
JOIN attributes.attributes a ON ua.attribute_id = a.id
JOIN attributes.categories c ON a.category_id = c.id
WHERE ua.is_public = true OR ua.user_id = auth.uid();

-- =====================================================
-- COMMENTS - 表注释
-- =====================================================

COMMENT ON SCHEMA attributes IS 'Attributes schema for user interests, hobbies and activities 用户兴趣、爱好和活动属性架构';
COMMENT ON TABLE attributes.categories IS 'Hierarchical categories for attributes with unlimited nesting 属性分类表，支持无限层级嵌套';
COMMENT ON TABLE attributes.attributes IS 'Specific attributes that users can associate with their profiles 用户可以关联到档案的具体属性';
COMMENT ON TABLE attributes.user_attributes IS 'User-attribute associations with preference levels and experience 用户-属性关联表，包含偏好等级和经验';
COMMENT ON TABLE attributes.attribute_relationships IS 'Relationships between attributes (similar, prerequisite, etc.) 属性之间的关系（相似、前置条件等）';
