# Teams API Documentation

## Overview

Teams API provides comprehensive functionality for managing events, teams, team members, posts, and recommendations within the profile matcher backend system.

**Base URL**: `/teams`

**Authentication**: All endpoints require Bearer token authentication.

## Authentication

Include the authorization header in all requests:
```
Authorization: Bearer <your_jwt_token>
```

## Events Management

### Get Events by Popularity
Get all active events sorted by participant count in descending order.

**Endpoint**: `GET /teams/events`

**Response**: `List[EventBase]`

```typescript
interface EventBase {
  id: string;
  name: string;
  description: string;
  participant_count: number;
  start_time: string;
  end_time: string;
  location: string;
}
```

**Example Response**:
```json
[
  {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "name": "AdventureX 2025",
    "description": "从今日起，我们将招募 800 名具有编程、设计、或其他能力的\"当代嬉皮士\"...",
    "participant_count": 150,
    "start_time": "2025-07-23T00:00:00+00:00",
    "end_time": "2025-07-26T23:59:59+00:00",
    "location": "浙江·杭州"
  }
]
```

### Join Event
Allow user to join a specific event.

**Endpoint**: `POST /teams/events/{event_id}/join`

**Path Parameters**:
- `event_id` (string): Event UUID

**Response**:
```json
{
  "message": "Successfully joined event"
}
```

**Error Responses**:
- `400`: Already joined this event
- `401`: Invalid token
- `404`: Event not found

## Team Management

### Create Team
Create a new team within an event.

**Endpoint**: `POST /teams/create`

**Request Body**: `TeamCreate`
```typescript
interface TeamCreate {
  event_id: string;
  name: string; // 1-100 characters
  say_something?: string;
}
```

**Response**: `Team`
```typescript
interface Team {
  id: string;
  event_id: string;
  name: string;
  say_something?: string;
  member_emails: string[];
  member_count: number;
  created_at: string;
}
```

**Example Request**:
```json
{
  "event_id": "550e8400-e29b-41d4-a716-446655440000",
  "name": "AI创新小队",
  "say_something": "我们专注于AI技术创新和实践"
}
```

**Error Responses**:
- `400`: Must join the event first / Already in a team

### Join Team
Join an existing team.

**Endpoint**: `POST /teams/join/{team_id}`

**Path Parameters**:
- `team_id` (string): Team UUID

**Response**:
```json
{
  "message": "Successfully joined team"
}
```

**Error Responses**:
- `400`: Must join the event first / Already in this team
- `404`: Team not found

### Leave Team
Leave current team.

**Endpoint**: `POST /teams/leave`

**Response**:
```json
{
  "message": "Successfully left team"
}
```

**Error Responses**:
- `400`: Not in any team

## Skills Management

### Set Team Member Skills
Set user's skills within their current team (maximum 2 skills).

**Endpoint**: `POST /teams/skills`

**Request Body**: `TeamMemberSkills`
```typescript
interface TeamMemberSkills {
  skill_ids: number[]; // Max 2 items, IDs between 1-36
}
```

**Example Request**:
```json
{
  "skill_ids": [1, 6] // Web前端开发, 算法/AI/机器学习
}
```

**Response**:
```json
{
  "message": "Skills updated successfully"
}
```

**Error Responses**:
- `400`: Not in any team / Invalid skill IDs / Max 2 skills allowed

### Get Team Members
Get information about current team members.

**Endpoint**: `GET /teams/members`

**Response**: `TeamMembers`
```typescript
interface TeamMembers {
  team_id: string;
  team_name: string;
  members: TeamMember[];
}

interface TeamMember {
  nickname: string;
  self_description?: string;
  skills: string[]; // Skill names
}
```

**Example Response**:
```json
{
  "team_id": "550e8400-e29b-41d4-a716-446655440000",
  "team_name": "AI创新小队",
  "members": [
    {
      "nickname": "张三",
      "self_description": "热爱AI技术的开发者",
      "skills": ["Web 前端开发", "算法 / AI / 机器学习"]
    },
    {
      "nickname": "李四",
      "self_description": "全栈工程师",
      "skills": ["服务器后端开发", "数据工程 / 大数据"]
    }
  ]
}
```

**Error Responses**:
- `400`: Not in any team

## Posts Management

### Create Team Post
Create a new post for the team.

**Endpoint**: `POST /teams/posts`

**Request Body**: `TeamPost`
```typescript
interface TeamPost {
  title: string; // 1-200 characters
  content: string; // Min 1 character
}
```

**Response**: `TeamPostResponse`
```typescript
interface TeamPostResponse {
  post_id: string;
  author_email: string;
  title: string;
  content: string;
  created_at: string;
}
```

**Example Request**:
```json
{
  "title": "寻找UI设计师加入我们的团队",
  "content": "我们是一个专注于AI应用开发的团队，目前需要一名有经验的UI设计师来完善我们的产品界面。如果你对AI技术感兴趣，欢迎加入我们！"
}
```

**Error Responses**:
- `400`: Not in any team

### Get All Team Posts
Get all active team posts.

**Endpoint**: `GET /teams/posts`

**Response**: `List[TeamPostResponse]`

**Example Response**:
```json
[
  {
    "post_id": "550e8400-e29b-41d4-a716-446655440000",
    "author_email": "user@example.com",
    "title": "寻找UI设计师加入我们的团队",
    "content": "我们是一个专注于AI应用开发的团队...",
    "created_at": "2025-07-26T10:00:00+00:00"
  }
]
```

### Update Team Post
Update an existing post (author only).

**Endpoint**: `PATCH /teams/posts/{post_id}`

**Path Parameters**:
- `post_id` (string): Post UUID

**Request Body**: `TeamPost`

**Response**: `TeamPostResponse`

**Error Responses**:
- `404`: Post not found or not authorized

### Delete Team Post
Delete a post (author only). This performs a soft delete.

**Endpoint**: `DELETE /teams/posts/{post_id}`

**Path Parameters**:
- `post_id` (string): Post UUID

**Response**:
```json
{
  "message": "Post deleted successfully"
}
```

**Error Responses**:
- `404`: Post not found or not authorized

## Recommendations Management

### Get User Recommendations
Get active and non-expired team recommendations for the current user.

**Endpoint**: `GET /teams/recommendations`

**Response**: `List[UserRecommendation]`
```typescript
interface UserRecommendation {
  id: string;
  team_id: string;
  team_name: string;
  recommendation_reason?: string;
  algorithm_score?: number;
  expires_at: string;
  created_at: string;
}
```

**Example Response**:
```json
[
  {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "team_id": "660f9500-f39c-52e5-b827-557766551111",
    "team_name": "前端开发团队",
    "recommendation_reason": "基于您的前端技能匹配度",
    "algorithm_score": 85.5,
    "expires_at": "2025-07-30T00:00:00+00:00",
    "created_at": "2025-07-26T10:00:00+00:00"
  }
]
```

### Update Recommendation Status
Accept or reject a team recommendation.

**Endpoint**: `PATCH /teams/recommendations/{recommendation_id}`

**Path Parameters**:
- `recommendation_id` (string): Recommendation UUID

**Request Body**: `RecommendationUpdate`
```typescript
interface RecommendationUpdate {
  status: "accepted" | "rejected";
}
```

**Example Request**:
```json
{
  "status": "accepted"
}
```

**Response**:
```json
{
  "message": "Recommendation accepted"
}
```

**Note**: If status is "accepted", the user will automatically join the recommended team.

**Error Responses**:
- `404`: Recommendation not found

## User Management

### Get All Users
Get a random list of user profiles (up to 100 users).

**Endpoint**: `GET /teams/users`

**Response**: `List[UserProfile]`
```typescript
interface UserProfile {
  id: string;
  user_id: string;
  nickname: string;
  avatar_url?: string;
  mbti?: string;
  hobbies: number[];
  motto?: string;
  self_description?: string;
  created_at: string;
  updated_at: string;
}
```

**Example Response**:
```json
[
  {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "user_id": "660f9500-f39c-52e5-b827-557766551111",
    "nickname": "技术达人",
    "avatar_url": "https://example.com/avatar.jpg",
    "mbti": "INTJ",
    "hobbies": [1, 3, 19],
    "motto": "代码改变世界",
    "self_description": "热爱技术的全栈开发者",
    "created_at": "2025-07-26T10:00:00+00:00",
    "updated_at": "2025-07-26T10:00:00+00:00"
  }
]
```

## Error Handling

All endpoints may return the following common error responses:

### 401 Unauthorized
```json
{
  "detail": "Missing authorization header"
}
```

### 500 Internal Server Error
```json
{
  "detail": "Internal server error message"
}
```

## Skills Reference

Skills are referenced by ID (1-36):

### 软件类 (1-9)
- 1: Web 前端开发
- 2: 服务器后端开发
- 3: iOS 原生开发
- 4: Android 原生开发
- 5: 跨端 / 小程序开发
- 6: 算法 / AI / 机器学习
- 7: 数据工程 / 大数据
- 8: DevOps / 云原生
- 9: 自动化测试 / QA

### 硬件类 (10-18)
- 10: 嵌入式固件 (C/C++)
- 11: 物联网 (IoT) 设备开发
- 12: 单片机 / MCU 开发
- 13: FPGA / CPLD 设计
- 14: 机器人控制
- 15: 传感器集成与调试
- 16: PCB 设计与打样
- 17: 硬件驱动开发
- 18: 硬件测试与可靠性

### 设计类 (19-27)
- 19: UX 研究 / 用户访谈
- 20: UI 视觉设计
- 21: 交互设计 (IxD)
- 22: 平面 / 海报设计
- 23: 动效 / 微交互
- 24: 品牌 VI / Logo
- 25: 原型制作 (Figma/Sketch)
- 26: 3D 建模 / 渲染
- 27: 游戏美术 / 像素风

### 产品类 (28-36)
- 28: 产品经理 / PRD 编写
- 29: 需求分析 / 优先级划分
- 30: 市场 & 竞品调研
- 31: 增长黑客 / 运营
- 32: 数据分析 / 指标体系
- 33: 商业策划 / 商业模型
- 34: 用户体验 (UX) 评审
- 35: 文案 / Storytelling
- 36: 项目管理 / Scrum

## TypeScript Client Example

```typescript
class TeamsAPIClient {
  private baseURL: string;
  private token: string;

  constructor(baseURL: string, token: string) {
    this.baseURL = baseURL;
    this.token = token;
  }

  private get headers() {
    return {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${this.token}`,
    };
  }

  // Get all events
  async getEvents(): Promise<EventBase[]> {
    const response = await fetch(`${this.baseURL}/teams/events`, {
      method: 'GET',
      headers: this.headers,
    });
    
    if (!response.ok) {
      throw new Error(`Failed to get events: ${response.status}`);
    }
    
    return response.json();
  }

  // Join an event
  async joinEvent(eventId: string): Promise<void> {
    const response = await fetch(`${this.baseURL}/teams/events/${eventId}/join`, {
      method: 'POST',
      headers: this.headers,
    });
    
    if (!response.ok) {
      throw new Error(`Failed to join event: ${response.status}`);
    }
  }

  // Create a team
  async createTeam(teamData: TeamCreate): Promise<Team> {
    const response = await fetch(`${this.baseURL}/teams/create`, {
      method: 'POST',
      headers: this.headers,
      body: JSON.stringify(teamData),
    });
    
    if (!response.ok) {
      throw new Error(`Failed to create team: ${response.status}`);
    }
    
    return response.json();
  }

  // Join a team
  async joinTeam(teamId: string): Promise<void> {
    const response = await fetch(`${this.baseURL}/teams/join/${teamId}`, {
      method: 'POST',
      headers: this.headers,
    });
    
    if (!response.ok) {
      throw new Error(`Failed to join team: ${response.status}`);
    }
  }

  // Set skills for current team
  async setTeamSkills(skills: TeamMemberSkills): Promise<void> {
    const response = await fetch(`${this.baseURL}/teams/skills`, {
      method: 'POST',
      headers: this.headers,
      body: JSON.stringify(skills),
    });
    
    if (!response.ok) {
      throw new Error(`Failed to set skills: ${response.status}`);
    }
  }

  // Get team members
  async getTeamMembers(): Promise<TeamMembers> {
    const response = await fetch(`${this.baseURL}/teams/members`, {
      method: 'GET',
      headers: this.headers,
    });
    
    if (!response.ok) {
      throw new Error(`Failed to get team members: ${response.status}`);
    }
    
    return response.json();
  }

  // Create a team post
  async createPost(postData: TeamPost): Promise<TeamPostResponse> {
    const response = await fetch(`${this.baseURL}/teams/posts`, {
      method: 'POST',
      headers: this.headers,
      body: JSON.stringify(postData),
    });
    
    if (!response.ok) {
      throw new Error(`Failed to create post: ${response.status}`);
    }
    
    return response.json();
  }

  // Get all posts
  async getPosts(): Promise<TeamPostResponse[]> {
    const response = await fetch(`${this.baseURL}/teams/posts`, {
      method: 'GET',
      headers: this.headers,
    });
    
    if (!response.ok) {
      throw new Error(`Failed to get posts: ${response.status}`);
    }
    
    return response.json();
  }

  // Get user recommendations
  async getRecommendations(): Promise<UserRecommendation[]> {
    const response = await fetch(`${this.baseURL}/teams/recommendations`, {
      method: 'GET',
      headers: this.headers,
    });
    
    if (!response.ok) {
      throw new Error(`Failed to get recommendations: ${response.status}`);
    }
    
    return response.json();
  }

  // Accept or reject recommendation
  async updateRecommendationStatus(
    recommendationId: string, 
    status: 'accepted' | 'rejected'
  ): Promise<void> {
    const response = await fetch(`${this.baseURL}/teams/recommendations/${recommendationId}`, {
      method: 'PATCH',
      headers: this.headers,
      body: JSON.stringify({ status }),
    });
    
    if (!response.ok) {
      throw new Error(`Failed to update recommendation: ${response.status}`);
    }
  }
}

// Usage example
const client = new TeamsAPIClient('http://localhost:8000', 'your_jwt_token_here');

// Complete workflow example
async function completeTeamWorkflow() {
  try {
    // 1. Get available events
    const events = await client.getEvents();
    console.log('Available events:', events);
    
    if (events.length > 0) {
      const eventId = events[0].id;
      
      // 2. Join an event
      await client.joinEvent(eventId);
      console.log('Joined event successfully');
      
      // 3. Create a team
      const team = await client.createTeam({
        event_id: eventId,
        name: '我的创新团队',
        say_something: '欢迎有想法的小伙伴加入我们！'
      });
      console.log('Team created:', team);
      
      // 4. Set skills
      await client.setTeamSkills({
        skill_ids: [1, 6] // Web frontend & AI/ML
      });
      console.log('Skills set successfully');
      
      // 5. Get team members
      const members = await client.getTeamMembers();
      console.log('Team members:', members);
      
      // 6. Create a post
      const post = await client.createPost({
        title: '寻找UI设计师',
        content: '我们需要一名有经验的UI设计师来完善产品界面设计'
      });
      console.log('Post created:', post);
    }
  } catch (error) {
    console.error('Workflow failed:', error);
  }
}
```

## Database Migrations

Required database migrations are located in:
- `scripts/migration/cicd/002_create_events_and_teams.sql`
- `scripts/migration/cicd/003_add_team_features.sql`
- `scripts/migration/cicd/004_add_random_users_function.sql`

Execute these migrations in order to set up the required database schema.