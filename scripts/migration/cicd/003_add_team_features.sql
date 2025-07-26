-- 创建小队发帖信息表
CREATE TABLE public.team_posts (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    team_id UUID NOT NULL REFERENCES public.teams(id) ON DELETE CASCADE,
    author_email VARCHAR(255) NOT NULL,
    title VARCHAR(200) NOT NULL,
    content TEXT NOT NULL,
    is_active BOOLEAN DEFAULT true NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, NOW()) NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, NOW()) NOT NULL
);

-- 创建小队推荐通知表
CREATE TABLE public.team_recommendations (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    team_id UUID NOT NULL REFERENCES public.teams(id) ON DELETE CASCADE,
    target_user_email VARCHAR(255) NOT NULL,
    recommendation_reason TEXT, -- 推荐理由
    algorithm_score NUMERIC(5,2), -- 算法匹配分数
    status VARCHAR(20) NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'accepted', 'rejected')),
    is_active BOOLEAN DEFAULT true NOT NULL, -- 控制是否显示
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL, -- 推荐有效期
    created_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, NOW()) NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, NOW()) NOT NULL,
    UNIQUE(team_id, target_user_email, created_at) -- 防止重复推荐
);

-- 添加触发器自动更新updated_at
CREATE TRIGGER update_team_posts_updated_at BEFORE UPDATE
    ON public.team_posts FOR EACH ROW EXECUTE FUNCTION
    update_updated_at_column();

CREATE TRIGGER update_team_recommendations_updated_at BEFORE UPDATE
    ON public.team_recommendations FOR EACH ROW EXECUTE FUNCTION
    update_updated_at_column();

-- 启用行级安全
ALTER TABLE public.team_posts ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.team_recommendations ENABLE ROW LEVEL SECURITY;

-- 小队发帖表RLS策略
CREATE POLICY "所有人都可以查看小队发帖" ON public.team_posts
    FOR SELECT USING (is_active = true);

CREATE POLICY "小队成员可以发帖" ON public.team_posts
    FOR INSERT WITH CHECK (
        auth.email() IN (
            SELECT unnest(member_emails) 
            FROM public.teams 
            WHERE id = team_id
        )
    );

CREATE POLICY "发帖作者可以更新自己的帖子" ON public.team_posts
    FOR UPDATE USING (auth.email() = author_email);

CREATE POLICY "发帖作者可以删除自己的帖子" ON public.team_posts
    FOR DELETE USING (auth.email() = author_email);

-- 小队推荐表RLS策略
CREATE POLICY "用户只能查看发给自己的推荐" ON public.team_recommendations
    FOR SELECT USING (
        auth.email() = target_user_email 
        AND is_active = true 
        AND expires_at > NOW()
    );

CREATE POLICY "用户可以更新发给自己的推荐状态" ON public.team_recommendations
    FOR UPDATE USING (auth.email() = target_user_email)
    WITH CHECK (auth.email() = target_user_email);

-- 创建索引
CREATE INDEX idx_team_posts_team_id ON public.team_posts(team_id);
CREATE INDEX idx_team_posts_author_email ON public.team_posts(author_email);
CREATE INDEX idx_team_posts_is_active ON public.team_posts(is_active);

CREATE INDEX idx_team_recommendations_team_id ON public.team_recommendations(team_id);
CREATE INDEX idx_team_recommendations_target_user_email ON public.team_recommendations(target_user_email);
CREATE INDEX idx_team_recommendations_status ON public.team_recommendations(status);
CREATE INDEX idx_team_recommendations_expires_at ON public.team_recommendations(expires_at);
CREATE INDEX idx_team_recommendations_is_active ON public.team_recommendations(is_active);

-- 创建清理过期推荐的函数
CREATE OR REPLACE FUNCTION cleanup_expired_recommendations()
RETURNS void AS $$
BEGIN
    UPDATE public.team_recommendations 
    SET is_active = false 
    WHERE expires_at < NOW() AND is_active = true;
END;
$$ LANGUAGE plpgsql;

-- 创建定时清理任务（需要pg_cron扩展）
-- SELECT cron.schedule('cleanup-expired-recommendations', '0 0 * * *', 'SELECT cleanup_expired_recommendations();');