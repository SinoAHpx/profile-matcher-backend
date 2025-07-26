# Profile Matcher API Documentation

## 用户注册
**POST** `/register`

注册新用户账户。

**Request Body:**
```json
{
  "username": "string",
  "email": "string", 
  "password": "string"
}
```

**Response:**
```json
{
  "user_id": "string",
  "username": "string",
  "email": "string"
}
```

**TypeScript Example:**
```typescript
interface RegisterRequest {
  username: string;
  email: string;
  password: string;
}

interface RegisterResponse {
  user_id: string;
  username: string;
  email: string;
}

const register = async (data: RegisterRequest): Promise<RegisterResponse> => {
  const response = await fetch('/register', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data)
  });
  return response.json();
};
```

## 获取MBTI类型
**GET** `/users/{user_id}/mbti`

获取用户的MBTI性格类型。

**Response:**
```json
{
  "mbti_type": "string"
}
```

**TypeScript Example:**
```typescript
interface MBTIResponse {
  mbti_type: string;
}

const getMBTI = async (userId: string): Promise<MBTIResponse> => {
  const response = await fetch(`/users/${userId}/mbti`);
  return response.json();
};
```

## 更新MBTI类型
**PUT** `/users/{user_id}/mbti`

更新用户的MBTI性格类型。

**Request Body:**
```json
{
  "mbti_type": "string"
}
```

**Response:**
```json
{
  "mbti_type": "string"
}
```

**TypeScript Example:**
```typescript
interface UpdateMBTIRequest {
  mbti_type: string;
}

interface UpdateMBTIResponse {
  mbti_type: string;
}

const updateMBTI = async (userId: string, data: UpdateMBTIRequest): Promise<UpdateMBTIResponse> => {
  const response = await fetch(`/users/${userId}/mbti`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data)
  });
  return response.json();
};
```

## 获取所有兴趣爱好
**GET** `/interests`

获取系统中所有可选的兴趣爱好列表。

**Response:**
```json
{
  "interests": [
    {
      "id": "string",
      "name": "string"
    }
  ]
}
```

**TypeScript Example:**
```typescript
interface Interest {
  id: string;
  name: string;
}

interface InterestsResponse {
  interests: Interest[];
}

const getAllInterests = async (): Promise<InterestsResponse> => {
  const response = await fetch('/interests');
  return response.json();
};
```

## 更新用户兴趣爱好
**PUT** `/users/{user_id}/interests`

更新用户的兴趣爱好列表。

**Request Body:**
```json
{
  "interest_ids": ["string"]
}
```

**Response:**
```json
{
  "interest_ids": ["string"]
}
```

**TypeScript Example:**
```typescript
interface UpdateInterestsRequest {
  interest_ids: string[];
}

interface UpdateInterestsResponse {
  interest_ids: string[];
}

const updateInterests = async (userId: string, data: UpdateInterestsRequest): Promise<UpdateInterestsResponse> => {
  const response = await fetch(`/users/${userId}/interests`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data)
  });
  return response.json();
};
```

## 更新一句话介绍
**PUT** `/users/{user_id}/tagline`

更新用户的一句话介绍。

**Request Body:**
```json
{
  "tagline": "string"
}
```

**Response:**
```json
{
  "tagline": "string"
}
```

**TypeScript Example:**
```typescript
interface UpdateTaglineRequest {
  tagline: string;
}

interface UpdateTaglineResponse {
  tagline: string;
}

const updateTagline = async (userId: string, data: UpdateTaglineRequest): Promise<UpdateTaglineResponse> => {
  const response = await fetch(`/users/${userId}/tagline`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data)
  });
  return response.json();
};
```

## 更新自我介绍
**PUT** `/users/{user_id}/description`

更新用户的详细自我介绍。

**Request Body:**
```json
{
  "description": "string"
}
```

**Response:**
```json
{
  "description": "string"
}
```

**TypeScript Example:**
```typescript
interface UpdateDescriptionRequest {
  description: string;
}

interface UpdateDescriptionResponse {
  description: string;
}

const updateDescription = async (userId: string, data: UpdateDescriptionRequest): Promise<UpdateDescriptionResponse> => {
  const response = await fetch(`/users/${userId}/description`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data)
  });
  return response.json();
};
```

## 上传用户头像
**POST** `/auth/upload-avatar`

通过邮箱指定用户并上传头像图片。

**Request:**
- Content-Type: `multipart/form-data`
- Form Data:
  - `email`: 用户邮箱地址
  - `avatar`: 图片文件 (支持 JPEG, PNG, GIF, WebP)

**Response:**
```json
{
  "message": "Avatar uploaded successfully",
  "email": "user@example.com",
  "user_id": "uuid",
  "avatar_url": "https://your-storage-url/bucket/avatars/user_id/unique_filename.jpg"
}
```

**TypeScript Example:**
```typescript
interface AvatarUploadResponse {
  message: string;
  email: string;
  user_id: string;
  avatar_url: string;
}

const uploadAvatar = async (file: File, email: string): Promise<AvatarUploadResponse> => {
  const formData = new FormData();
  formData.append('email', email);
  formData.append('avatar', file);

  const response = await fetch('/auth/upload-avatar', {
    method: 'POST',
    body: formData
  });
  return response.json();
};
```

## 根据邮箱获取用户ID
**GET** `/auth/user-id/{email}`

根据用户邮箱地址获取对应的用户ID。

**Response:**
```json
{
  "email": "user@example.com",
  "user_id": "uuid"
}
```

**TypeScript Example:**
```typescript
interface UserIdResponse {
  email: string;
  user_id: string;
}

const getUserIdByEmail = async (email: string): Promise<UserIdResponse> => {
  const response = await fetch(`/auth/user-id/${encodeURIComponent(email)}`);
  return response.json();
};
```

## 根据邮箱获取用户头像
**GET** `/auth/avatar/{email}`

根据用户邮箱地址获取对应的头像链接。

**Response:**
```json
{
  "email": "user@example.com", 
  "user_id": "uuid",
  "avatar_url": "https://your-storage-url/bucket/avatars/user_id/avatar.jpg"
}
```

**TypeScript Example:**
```typescript
interface UserAvatarResponse {
  email: string;
  user_id: string;
  avatar_url: string | null;
}

const getUserAvatarByEmail = async (email: string): Promise<UserAvatarResponse> => {
  const response = await fetch(`/auth/avatar/${encodeURIComponent(email)}`);
  return response.json();
};
```