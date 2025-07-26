-- 创建用户资料表
CREATE TABLE public.user_profiles (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    nickname VARCHAR(50) NOT NULL,
    avatar_url TEXT,
    mbti VARCHAR(4) CHECK (mbti IN ('INTJ','INTP','ENTJ','ENTP','INFJ','INFP','ENFJ','ENFP','ISTJ','ISFJ','ESTJ','ESFJ','ISTP','ISFP','ESTP','ESFP')),
    hobbies INTEGER[] DEFAULT '{}',
    skills INTEGER[] DEFAULT '{}',
    motto TEXT,
    self_description TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, NOW()) NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, NOW()) NOT NULL,
    UNIQUE(user_id)
);

-- 添加触发器自动更新updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = TIMEZONE('utc'::text, NOW());
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_user_profiles_updated_at BEFORE UPDATE
    ON public.user_profiles FOR EACH ROW EXECUTE FUNCTION
    update_updated_at_column();

-- 创建技能常量表
CREATE TABLE public.skills_reference (
    id INTEGER PRIMARY KEY,
    name VARCHAR(50) NOT NULL,
    category VARCHAR(10) NOT NULL CHECK (category IN ('软件','硬件','设计','产品'))
);

-- 插入技能数据
INSERT INTO public.skills_reference (id, name, category) VALUES
-- 软件类别
(1, 'Web 前端开发', '软件'),
(2, '服务器后端开发', '软件'),
(3, 'iOS 原生开发', '软件'),
(4, 'Android 原生开发', '软件'),
(5, '跨端 / 小程序开发', '软件'),
(6, '算法 / AI / 机器学习', '软件'),
(7, '数据工程 / 大数据', '软件'),
(8, 'DevOps / 云原生', '软件'),
(9, '自动化测试 / QA', '软件'),
-- 硬件类别
(10, '嵌入式固件 (C/C++)', '硬件'),
(11, '物联网 (IoT) 设备开发', '硬件'),
(12, '单片机 / MCU 开发', '硬件'),
(13, 'FPGA / CPLD 设计', '硬件'),
(14, '机器人控制', '硬件'),
(15, '传感器集成与调试', '硬件'),
(16, 'PCB 设计与打样', '硬件'),
(17, '硬件驱动开发', '硬件'),
(18, '硬件测试与可靠性', '硬件'),
-- 设计类别
(19, 'UX 研究 / 用户访谈', '设计'),
(20, 'UI 视觉设计', '设计'),
(21, '交互设计 (IxD)', '设计'),
(22, '平面 / 海报设计', '设计'),
(23, '动效 / 微交互', '设计'),
(24, '品牌 VI / Logo', '设计'),
(25, '原型制作 (Figma/Sketch)', '设计'),
(26, '3D 建模 / 渲染', '设计'),
(27, '游戏美术 / 像素风', '设计'),
-- 产品类别
(28, '产品经理 / PRD 编写', '产品'),
(29, '需求分析 / 优先级划分', '产品'),
(30, '市场 & 竞品调研', '产品'),
(31, '增长黑客 / 运营', '产品'),
(32, '数据分析 / 指标体系', '产品'),
(33, '商业策划 / 商业模型', '产品'),
(34, '用户体验 (UX) 评审', '产品'),
(35, '文案 / Storytelling', '产品'),
(36, '项目管理 / Scrum', '产品');

-- 创建爱好常量表
CREATE TABLE public.hobbies_reference (
    id INTEGER PRIMARY KEY,
    name VARCHAR(20) NOT NULL,
    category VARCHAR(10) NOT NULL CHECK (category IN ('body','mind','heart','hands'))
);

-- 插入爱好数据
INSERT INTO public.hobbies_reference (id, name, category) VALUES
-- body 类别
(1, '瑜伽', 'body'),
(2, '游泳', 'body'),
(3, '跑步', 'body'),
(4, '健身', 'body'),
(5, '舞蹈', 'body'),
(6, '篮球', 'body'),
(7, '足球', 'body'),
(8, '网球', 'body'),
(9, '乒乓球', 'body'),
(10, '羽毛球', 'body'),
(11, '滑板', 'body'),
(12, '攀岩', 'body'),
(13, '武术', 'body'),
(14, '骑行', 'body'),
(15, '徒步', 'body'),
(16, '滑雪', 'body'),
(17, '高尔夫', 'body'),
(18, '排球', 'body'),
-- mind 类别
(19, '写作', 'mind'),
(20, '阅读', 'mind'),
(21, '摄影', 'mind'),
(22, '绘画', 'mind'),
(23, '下棋', 'mind'),
(24, '冥想', 'mind'),
(25, '学习语言', 'mind'),
(26, '解谜', 'mind'),
(27, '数独', 'mind'),
(28, '记忆训练', 'mind'),
(29, '辩论', 'mind'),
(30, '哲学思考', 'mind'),
(31, '科普研究', 'mind'),
(32, '历史探索', 'mind'),
(33, '创意写作', 'mind'),
(34, '战略游戏', 'mind'),
-- heart 类别
(35, '志愿服务', 'heart'),
(36, '音乐欣赏', 'heart'),
(37, '园艺', 'heart'),
(38, '宠物饲养', 'heart'),
(39, '烹饪', 'heart'),
(40, '茶艺', 'heart'),
(41, '手帐', 'heart'),
(42, '剧本杀', 'heart'),
(43, '收藏', 'heart'),
(44, '占星', 'heart'),
(45, '冥想', 'heart'),
(46, '心理学', 'heart'),
(47, '社交', 'heart'),
(48, '旅行', 'heart'),
(49, '摄影', 'heart'),
(50, '艺术鉴赏', 'heart'),
-- hands 类别
(51, '绘画', 'hands'),
(52, '书法', 'hands'),
(53, '编程', 'hands'),
(54, '手工艺', 'hands'),
(55, '木工', 'hands'),
(56, '陶艺', 'hands'),
(57, '编织', 'hands'),
(58, '折纸', 'hands'),
(59, '缝纫', 'hands'),
(60, '烘焙', 'hands'),
(61, '园艺', 'hands'),
(62, '乐器演奏', 'hands'),
(63, '模型制作', 'hands'),
(64, '首饰制作', 'hands'),
(65, '皮革工艺', 'hands'),
(66, '雕刻', 'hands');

-- 启用行级安全
ALTER TABLE public.user_profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.hobbies_reference ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.skills_reference ENABLE ROW LEVEL SECURITY;

-- 用户资料表RLS策略
CREATE POLICY "用户只能查看自己的资料" ON public.user_profiles
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "用户只能插入自己的资料" ON public.user_profiles
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "用户只能更新自己的资料" ON public.user_profiles
    FOR UPDATE USING (auth.uid() = user_id);

CREATE POLICY "用户只能删除自己的资料" ON public.user_profiles
    FOR DELETE USING (auth.uid() = user_id);

-- 爱好参考表RLS策略（公开只读）
CREATE POLICY "所有人都可以读取爱好参考" ON public.hobbies_reference
    FOR SELECT USING (true);

-- 技能参考表RLS策略（公开只读）
CREATE POLICY "所有人都可以读取技能参考" ON public.skills_reference
    FOR SELECT USING (true);

-- 创建索引
CREATE INDEX idx_user_profiles_user_id ON public.user_profiles(user_id);
CREATE INDEX idx_user_profiles_nickname ON public.user_profiles(nickname);
CREATE INDEX idx_hobbies_reference_category ON public.hobbies_reference(category);
CREATE INDEX idx_skills_reference_category ON public.skills_reference(category);