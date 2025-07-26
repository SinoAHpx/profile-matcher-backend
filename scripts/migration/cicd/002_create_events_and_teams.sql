-- 创建活动大类表
CREATE TABLE public.events (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT NOT NULL,
    poster_url TEXT,
    start_time TIMESTAMP WITH TIME ZONE NOT NULL,
    end_time TIMESTAMP WITH TIME ZONE NOT NULL,
    location VARCHAR(200) NOT NULL,
    is_active BOOLEAN DEFAULT true NOT NULL,
    max_participants INTEGER NOT NULL,
    all_participants_emails TEXT[] DEFAULT '{}',
    teamed_participants_emails TEXT[] DEFAULT '{}',
    unteamed_participants_emails TEXT[] DEFAULT '{}',
    team_ids UUID[] DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, NOW()) NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, NOW()) NOT NULL
);

-- 创建小队表
CREATE TABLE public.teams (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    event_id UUID NOT NULL REFERENCES public.events(id) ON DELETE CASCADE,
    name VARCHAR(100) NOT NULL,
    say_something TEXT,
    member_emails TEXT[] DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, NOW()) NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, NOW()) NOT NULL
);

-- 创建用户参与活动表
CREATE TABLE public.event_participants (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    event_id UUID NOT NULL REFERENCES public.events(id) ON DELETE CASCADE,
    user_email VARCHAR(255) NOT NULL,
    team_id UUID REFERENCES public.teams(id) ON DELETE SET NULL,
    joined_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, NOW()) NOT NULL,
    UNIQUE(event_id, user_email)
);

-- 创建用户在小队中承担的技能角色表
CREATE TABLE public.team_member_skills (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    team_id UUID NOT NULL REFERENCES public.teams(id) ON DELETE CASCADE,
    user_email VARCHAR(255) NOT NULL,
    skill_ids INTEGER[] NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, NOW()) NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, NOW()) NOT NULL,
    UNIQUE(team_id, user_email)
);

-- 添加触发器自动更新updated_at
CREATE TRIGGER update_events_updated_at BEFORE UPDATE
    ON public.events FOR EACH ROW EXECUTE FUNCTION
    update_updated_at_column();

CREATE TRIGGER update_teams_updated_at BEFORE UPDATE
    ON public.teams FOR EACH ROW EXECUTE FUNCTION
    update_updated_at_column();

CREATE TRIGGER update_team_member_skills_updated_at BEFORE UPDATE
    ON public.team_member_skills FOR EACH ROW EXECUTE FUNCTION
    update_updated_at_column();

-- 插入 AdventureX 2025 活动数据
INSERT INTO public.events (
    name, 
    description, 
    start_time, 
    end_time, 
    location, 
    is_active, 
    max_participants
) VALUES (
    'AdventureX 2025',
    '从今日起，我们将招募 800 名具有编程、设计、或其他能力的"当代嬉皮士"，那些有勇气去创造的青年，并邀请他们在今年7月23日至27日来到中国杭州参与AdventureX 2025 线下黑客松。

在这五天，我们将提供中国最好的创造场所之一，无限的算力、硬件，五天的餐饮和住宿，深度的技术讲座，有趣的「蓝调」活动，而所有的"创造者"们则需要组成小组，并从0到1制作一个硬件或者软件项目，或者是进行技术创新。更重要的是，这将是五天，没有任何限制和现实引力的逃逸，你可以将最疯狂的想法变为现实。

同时，我们也欢迎所有对 Adventurex 2025 感兴趣的朋友来到现场，亲眼见证中国年轻人可以创造，可以有潜力开创下一个新的时代。',
    '2025-07-23 00:00:00+00:00',
    '2025-07-26 23:59:59+00:00',
    '浙江·杭州',
    true,
    800
);

-- 启用行级安全
ALTER TABLE public.events ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.teams ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.event_participants ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.team_member_skills ENABLE ROW LEVEL SECURITY;

-- 活动表RLS策略（公开只读，管理员可写）
CREATE POLICY "所有人都可以查看活动" ON public.events
    FOR SELECT USING (true);

-- 小队表RLS策略
CREATE POLICY "所有人都可以查看小队" ON public.teams
    FOR SELECT USING (true);

CREATE POLICY "认证用户可以创建小队" ON public.teams
    FOR INSERT WITH CHECK (auth.uid() IS NOT NULL);

CREATE POLICY "小队成员可以更新小队信息" ON public.teams
    FOR UPDATE USING (
        auth.email() = ANY(member_emails)
    );

-- 参与者表RLS策略
CREATE POLICY "所有人都可以查看参与者信息" ON public.event_participants
    FOR SELECT USING (true);

CREATE POLICY "认证用户可以参与活动" ON public.event_participants
    FOR INSERT WITH CHECK (auth.email() = user_email);

CREATE POLICY "用户可以更新自己的参与信息" ON public.event_participants
    FOR UPDATE USING (auth.email() = user_email);

CREATE POLICY "用户可以取消参与" ON public.event_participants
    FOR DELETE USING (auth.email() = user_email);

-- 小队成员技能表RLS策略
CREATE POLICY "所有人都可以查看小队成员技能" ON public.team_member_skills
    FOR SELECT USING (true);

CREATE POLICY "用户可以设置自己的技能角色" ON public.team_member_skills
    FOR INSERT WITH CHECK (auth.email() = user_email);

CREATE POLICY "用户可以更新自己的技能角色" ON public.team_member_skills
    FOR UPDATE USING (auth.email() = user_email);

CREATE POLICY "用户可以删除自己的技能角色" ON public.team_member_skills
    FOR DELETE USING (auth.email() = user_email);

-- 创建索引
CREATE INDEX idx_events_is_active ON public.events(is_active);
CREATE INDEX idx_events_start_time ON public.events(start_time);
CREATE INDEX idx_teams_event_id ON public.teams(event_id);
CREATE INDEX idx_event_participants_event_id ON public.event_participants(event_id);
CREATE INDEX idx_event_participants_user_email ON public.event_participants(user_email);
CREATE INDEX idx_event_participants_team_id ON public.event_participants(team_id);
CREATE INDEX idx_team_member_skills_team_id ON public.team_member_skills(team_id);
CREATE INDEX idx_team_member_skills_user_email ON public.team_member_skills(user_email);