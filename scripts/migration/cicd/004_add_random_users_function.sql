-- 创建获取随机用户资料的函数
CREATE OR REPLACE FUNCTION get_random_user_profiles()
RETURNS TABLE(
    id UUID,
    user_id UUID,
    nickname VARCHAR(50),
    avatar_url TEXT,
    mbti VARCHAR(4),
    hobbies INTEGER[],
    skills INTEGER[],
    motto TEXT,
    self_description TEXT,
    created_at TIMESTAMP WITH TIME ZONE,
    updated_at TIMESTAMP WITH TIME ZONE
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        up.id,
        up.user_id,
        up.nickname,
        up.avatar_url,
        up.mbti,
        up.hobbies,
        up.skills,
        up.motto,
        up.self_description,
        up.created_at,
        up.updated_at
    FROM public.user_profiles up
    ORDER BY RANDOM()
    LIMIT 100;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;