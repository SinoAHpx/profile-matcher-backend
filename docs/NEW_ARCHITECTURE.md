# 新数据库架构设计文档

## 概述

本文档描述了Profile Matcher后端的新模块化数据库架构设计。新架构将原有的单一schema重构为三个独立的schema，以提高模块化和可维护性。

## 架构设计原则

### 1. 模块化分离
- **Profile Schema**: 用户基本档案信息
- **Attributes Schema**: 用户属性/爱好管理
- **Ego Schema**: 人格特质/认知功能

### 2. 层级结构支持
- 支持无限层级的分类嵌套
- 灵活的属性组织方式
- 清晰的数据关系

### 3. 可扩展性
- 预定义字典表支持
- 用户自定义内容
- 多框架人格特质系统

## Schema详细设计

### Profile Schema - 用户画像总览

**核心表：**
- `profile.user_profiles` - 主用户档案表
- `profile.completion_status` - 档案完成度跟踪
- `profile.profile_versions` - 档案版本历史

**字典表：**
- `profile.regions` - 地区字典（支持层级：国家→省→市→区）
- `profile.occupations` - 职业字典
- `profile.occupation_categories` - 职业分类
- `profile.education_levels` - 教育程度
- `profile.relationship_statuses` - 关系状态
- `profile.genders` - 性别

**特点：**
- 包含预定义的用户基本信息列
- 每个预定义列都有对应的字典表
- 专注于用户的基本档案信息和静态属性

### Attributes Schema - 用户属性/爱好

**核心表：**
- `attributes.categories` - 属性分类表（支持无限层级嵌套）
- `attributes.attributes` - 具体属性表
- `attributes.user_attributes` - 用户属性关联表
- `attributes.attribute_relationships` - 属性关系表

**层级结构示例：**
```
运动 (一级分类)
├── 球类运动 (二级分类)
│   ├── 篮球 (三级分类)
│   │   ├── 打篮球 (具体属性)
│   │   ├── 看篮球比赛 (具体属性)
│   │   └── 篮球教练 (具体属性)
│   ├── 足球 (三级分类)
│   └── 网球 (三级分类)
├── 水上运动 (二级分类)
└── 户外运动 (二级分类)
```

**特点：**
- 将hobby概念重构为更通用的"属性"概念
- 支持多级分类的层级结构
- 预定义所有用户可选择的属性范围和分类层级
- 丰富的属性元数据（难度、时间投入、成本等）

### Ego Schema - 人格特质/认知功能

**认知功能表：**
- `ego.cognitive_functions` - 荣格8种认知功能主表
- `ego.user_cognitive_functions` - 用户认知功能评分
- `ego.cognitive_function_assessments` - 认知功能评估历史

**人格特质表：**
- `ego.trait_categories` - 特质分类（支持多种框架）
- `ego.trait_value_types` - 特质值类型定义
- `ego.personality_traits` - 人格特质主表
- `ego.user_personality_traits` - 用户人格特质值
- `ego.trait_assessments` - 特质评估历史

**特点：**
- 专注于用户的心理特质、人格类型、认知模式等内在属性
- 支持多种人格框架（大五人格、九型人格、DISC等）
- 可扩展的特质系统

## API接口设计

### Profile API (`/api/v1/profile/`)

**字典数据端点：**
- `GET /dictionaries/genders` - 获取性别字典
- `GET /dictionaries/regions` - 获取地区字典
- `GET /dictionaries/occupations` - 获取职业字典
- `GET /dictionaries/education-levels` - 获取教育程度字典
- `GET /dictionaries/relationship-statuses` - 获取关系状态字典

**档案管理端点：**
- `GET /{user_id}` - 获取用户档案
- `POST /{user_id}` - 创建用户档案
- `PUT /{user_id}` - 更新用户档案
- `DELETE /{user_id}` - 删除用户档案
- `GET /search` - 搜索用户档案

### Attributes API (`/api/v1/attributes/`)

**分类和属性端点：**
- `GET /categories/tree` - 获取完整的属性分类树结构
- `GET /categories/{category_id}/attributes` - 获取指定分类下的所有属性
- `GET /categories/{category_id}/subcategories` - 获取指定分类的直接子分类
- `GET /search` - 搜索属性
- `GET /popular` - 获取热门属性列表

**用户属性管理端点：**
- `GET /user/{user_id}` - 获取用户的属性列表
- `POST /user/{user_id}` - 为用户添加新的属性关联
- `PUT /user/{user_id}/{attribute_id}` - 更新用户的属性关联信息
- `DELETE /user/{user_id}/{attribute_id}` - 删除用户的属性关联

### Ego API (`/api/v1/ego/`)

**认知功能端点：**
- `GET /cognitive-functions` - 获取所有认知功能
- `GET /cognitive-functions/{user_id}` - 获取用户的认知功能评分
- `POST /cognitive-functions/{user_id}` - 为用户创建认知功能评分
- `PUT /cognitive-functions/{user_id}/{function_id}` - 更新用户的认知功能评分
- `DELETE /cognitive-functions/{user_id}/{function_id}` - 删除用户的认知功能评分
- `GET /cognitive-functions/{user_id}/distribution` - 获取用户的认知功能分布

**人格特质端点：**
- `GET /trait-categories` - 获取特质分类
- `GET /trait-value-types` - 获取特质值类型
- `GET /personality-traits` - 获取人格特质
- `GET /personality-traits/{user_id}` - 获取用户的人格特质

## 数据库初始化

### 1. 执行SQL脚本
```bash
# 按顺序执行以下脚本
scripts/sql-scripts/01_profile_schema.sql
scripts/sql-scripts/02_attributes_schema.sql
scripts/sql-scripts/03_ego_schema.sql
```

### 2. 使用初始化脚本
```bash
python scripts/init_database.py
```

### 3. 环境变量配置
创建 `.env` 文件：
```env
DB_HOST=localhost
DB_PORT=5432
DB_NAME=profile_matcher
DB_USER=postgres
DB_PASSWORD=your_password
```

## 种子数据

### Profile Schema
- 性别：男性、女性、非二元性别、不愿透露
- 教育程度：小学到博士的完整层级
- 关系状态：单身、恋爱中、已婚等
- 地区：中国主要城市（可扩展）

### Attributes Schema
- 一级分类：运动、艺术、音乐、阅读、科技、烹饪、旅行、游戏、手工、社交
- 二级分类：如运动下的球类运动、水上运动、户外运动、健身
- 三级分类：如球类运动下的篮球、足球、网球、羽毛球
- 具体属性：如篮球下的打篮球、看篮球比赛、篮球教练

### Ego Schema
- 荣格8种认知功能：Ni, Ne, Si, Se, Ti, Te, Fi, Fe
- 特质分类：大五人格、九型人格、DISC、自定义
- 特质值类型：百分比、李克特量表、布尔值、文本

## 优势

### 1. 模块化设计
- 清晰的职责分离
- 独立的数据管理
- 便于维护和扩展

### 2. 灵活的层级结构
- 支持无限层级嵌套
- 动态路径生成
- 便于分类管理

### 3. 丰富的元数据
- 属性的详细描述
- 多维度的分类标准
- 支持个性化推荐

### 4. 可扩展性
- 用户自定义内容
- 多框架支持
- 灵活的数据结构

### 5. 性能优化
- 合理的索引策略
- 视图简化查询
- 触发器自动维护

## 使用示例

### 获取属性分类树
```http
GET /api/v1/attributes/categories/tree
```

### 搜索篮球相关属性
```http
GET /api/v1/attributes/search?q=篮球
```

### 获取用户的认知功能分布
```http
GET /api/v1/ego/cognitive-functions/{user_id}/distribution
```

### 为用户添加新属性
```http
POST /api/v1/attributes/user/{user_id}
{
  "attribute_id": "uuid",
  "interest_level": 8,
  "skill_level": "intermediate",
  "experience_years": 3
}
```

这个新架构提供了更好的模块化、可维护性和扩展性，同时保持了数据的完整性和性能。
