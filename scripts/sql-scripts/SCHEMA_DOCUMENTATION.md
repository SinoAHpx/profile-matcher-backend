# User Profile Database Schema Documentation

## Overview

This document describes the comprehensive database schema designed for the Profile Matcher backend, a social media MVP that helps users understand themselves through social interactions. The schema supports Jung's 8 cognitive functions personality typing, user interests and hobbies, and an extensible personality traits system.

## Design Principles

### 1. Dictionary/Lookup Tables + User Association Pattern
- **Lookup Tables**: Store master data once (cognitive functions, interests, hobbies, traits)
- **Association Tables**: Link users to lookup data with user-specific values (scores, preferences, levels)
- **Benefits**: Reduces data duplication, ensures consistency, enables easy updates to master data

### 2. Extensibility
- **JSONB Fields**: Flexible metadata storage for future requirements
- **Trait System**: Add new personality frameworks without schema changes
- **Custom Content**: Users can create custom interests and hobbies

### 3. Supabase Integration
- **Auth Integration**: All user tables reference `auth.users(id)`
- **Row Level Security**: Comprehensive RLS policies for data privacy
- **Real-time Ready**: Schema designed for Supabase real-time subscriptions

### 4. Performance Optimization
- **Strategic Indexing**: Indexes on frequently queried columns
- **Partial Indexes**: Optimized indexes for filtered queries
- **GIN Indexes**: Full-text search on array fields (tags)

## Core Schema Components

### 1. Core User Profile Tables

#### `user_profiles`
**Purpose**: Main user profile table extending Supabase auth.users
**Key Features**:
- Profile visibility controls (public, friends, private)
- Completion percentage tracking
- Flexible metadata storage (JSONB)
- Audit trail with timestamps

#### `profile_completion_status`
**Purpose**: Track completion of different profile sections
**Key Features**:
- Section-based completion tracking
- Percentage completion per section
- Automatic profile completion calculation

#### `user_profile_versions`
**Purpose**: Version history for profile changes
**Key Features**:
- Audit trail for profile modifications
- JSONB storage of profile snapshots
- Version numbering system

### 2. Cognitive Functions Schema

#### `cognitive_functions`
**Purpose**: Master table of Jung's 8 cognitive functions
**Functions Included**:
- **Ni** (Introverted Intuition) - Pattern recognition, future insights
- **Ne** (Extraverted Intuition) - Exploring possibilities, brainstorming
- **Si** (Introverted Sensing) - Past experiences, details, traditions
- **Se** (Extraverted Sensing) - Present moment awareness, action-oriented
- **Ti** (Introverted Thinking) - Internal logic, analysis, understanding
- **Te** (Extraverted Thinking) - External organization, efficiency, results
- **Fi** (Introverted Feeling) - Personal values, authenticity, harmony
- **Fe** (Extraverted Feeling) - Group harmony, others' emotions, social dynamics

#### `user_cognitive_functions`
**Purpose**: User-specific cognitive function scores and rankings
**Key Features**:
- Raw scores (0-100) and normalized scores
- Function rankings (1-8)
- Confidence levels for assessments
- Multiple assessment sources support

#### `cognitive_function_assessments`
**Purpose**: Track assessment history and sources
**Key Features**:
- Multiple assessment types (initial, periodic, AI analysis, peer feedback)
- Assessment method tracking
- Confidence scoring
- JSONB storage for assessment data

### 3. Interests and Hobbies Schema

#### Interest System
- **`interest_categories`**: Hierarchical categorization (Technology, Arts, Sports, etc.)
- **`interests`**: Specific interests within categories
- **`user_interests`**: User-interest associations with preference levels (1-10)

#### Hobby System
- **`hobby_categories`**: Hobby classification system
- **`hobbies`**: Specific hobbies with metadata (skill level, time commitment, cost)
- **`user_hobbies`**: User-hobby associations with engagement levels

**Key Features**:
- Hierarchical categorization for better organization
- Preference/engagement level scoring
- Support for custom user-defined content
- Experience and skill level tracking
- Time investment tracking

### 4. Extensible Personality Traits Schema

#### `trait_categories`
**Purpose**: Group traits by personality framework
**Supported Frameworks**:
- Big Five Personality Traits
- Enneagram Types
- DISC Assessment
- Custom frameworks

#### `trait_value_types`
**Purpose**: Define data types for trait measurements
**Supported Types**:
- Integer (scores, rankings)
- Decimal (precise measurements)
- Boolean (yes/no traits)
- Text (descriptions)
- Enum (predefined choices)

#### `personality_traits`
**Purpose**: Master list of all personality traits
**Key Features**:
- Framework categorization
- Flexible value type assignment
- Reverse scoring support
- Tag-based organization

#### `user_personality_traits`
**Purpose**: User-specific trait values
**Key Features**:
- Multiple value type storage (numeric, text, boolean)
- Confidence level tracking
- Assessment source attribution
- Privacy controls

## Relationships and Constraints

### Primary Relationships
```
auth.users (Supabase)
    ↓ (1:1)
user_profiles
    ↓ (1:many)
├── user_cognitive_functions → cognitive_functions
├── user_interests → interests → interest_categories
├── user_hobbies → hobbies → hobby_categories
├── user_personality_traits → personality_traits → trait_categories
└── profile_completion_status
```

### Key Constraints
- **Score Ranges**: Check constraints ensure valid score ranges (0-100, 1-10, etc.)
- **Unique Constraints**: Prevent duplicate user-trait associations
- **Foreign Key Cascades**: Proper cleanup when users are deleted
- **Enum Constraints**: Validate categorical values

## Security Model (Row Level Security)

### Public Access
- Dictionary tables (cognitive functions, interests, hobbies, traits) are publicly readable
- User profile summaries are visible based on privacy settings

### User Access
- Users can only modify their own data
- Users can view public profiles and their own private data
- Assessment data is private to the user and assessor

### Privacy Controls
- Profile visibility settings (public, friends, private)
- Individual trait/interest privacy controls
- Assessment confidentiality

## Performance Considerations

### Indexing Strategy
- **User-centric indexes**: Fast user data retrieval
- **Score-based indexes**: Efficient ranking and matching queries
- **Category indexes**: Quick filtering by categories
- **Partial indexes**: Optimized for active/public records only

### Query Optimization
- **Materialized views**: Pre-computed user summaries
- **JSONB indexes**: Efficient metadata queries
- **Array indexes**: Fast tag-based searches

## Usage Patterns

### Common Queries
1. **User Profile Summary**: Complete profile with top cognitive functions
2. **Personality Matching**: Find users with similar cognitive function patterns
3. **Interest-based Matching**: Find users with shared interests/hobbies
4. **Assessment Progress**: Track completion of personality assessments

### API Integration
- RESTful endpoints for CRUD operations
- Real-time subscriptions for profile updates
- Batch operations for assessment results
- Search and filtering capabilities

## Extension Points

### Adding New Personality Frameworks
1. Insert new category in `trait_categories`
2. Define traits in `personality_traits`
3. No schema changes required

### Custom User Content
- Users can create custom interests and hobbies
- Custom traits can be added through the extensible system
- Metadata fields support arbitrary additional data

### Assessment Integration
- New assessment types can be added without schema changes
- Assessment data stored in flexible JSONB format
- Multiple assessment sources supported

## Migration and Deployment

### Initial Setup
1. Run the schema creation script
2. Seed data is automatically inserted
3. RLS policies are automatically applied

### Future Migrations
- Use Supabase migration system
- Backward-compatible changes preferred
- Version tracking in `user_profile_versions`

## Monitoring and Maintenance

### Key Metrics
- Profile completion rates
- Assessment participation
- Interest/hobby popularity
- System performance metrics

### Data Quality
- Constraint violations monitoring
- Orphaned record detection
- Assessment confidence tracking
- User engagement metrics

## Quick Reference for Developers

### Essential Tables for Common Operations

#### User Profile Creation
```sql
-- 1. Create user profile (after Supabase auth)
INSERT INTO user_profiles (id, display_name, bio)
VALUES (auth.uid(), 'John Doe', 'Software developer interested in psychology');

-- 2. Initialize profile completion tracking
INSERT INTO profile_completion_status (user_id, section_name, completion_percentage)
VALUES
  (auth.uid(), 'basic_info', 100),
  (auth.uid(), 'cognitive_functions', 0),
  (auth.uid(), 'interests', 0),
  (auth.uid(), 'hobbies', 0);
```

#### Cognitive Function Assessment
```sql
-- Record cognitive function scores
INSERT INTO user_cognitive_functions (user_id, cognitive_function_id, raw_score, function_rank)
SELECT
  auth.uid(),
  cf.id,
  CASE cf.code
    WHEN 'Ni' THEN 85
    WHEN 'Te' THEN 78
    -- ... other scores
  END,
  ROW_NUMBER() OVER (ORDER BY score DESC)
FROM cognitive_functions cf;
```

#### Interest/Hobby Management
```sql
-- Add user interests with preference levels
INSERT INTO user_interests (user_id, interest_id, preference_level, experience_level)
SELECT auth.uid(), i.id, 8, 'intermediate'
FROM interests i
WHERE i.name IN ('Programming', 'Psychology', 'Music');

-- Add user hobbies with engagement data
INSERT INTO user_hobbies (user_id, hobby_id, engagement_level, frequency, time_spent_weekly)
SELECT auth.uid(), h.id, 9, 'daily', 20
FROM hobbies h
WHERE h.name = 'Coding';
```

### Common Query Patterns

#### Find Similar Users by Cognitive Functions
```sql
SELECT
  up.display_name,
  similarity_score
FROM user_profiles up
JOIN (
  SELECT
    ucf2.user_id,
    1.0 - (SUM(ABS(ucf1.normalized_score - ucf2.normalized_score)) / 800.0) as similarity_score
  FROM user_cognitive_functions ucf1
  JOIN user_cognitive_functions ucf2 ON ucf1.cognitive_function_id = ucf2.cognitive_function_id
  WHERE ucf1.user_id = auth.uid() AND ucf2.user_id != auth.uid()
  GROUP BY ucf2.user_id
  HAVING COUNT(*) = 8  -- All 8 functions
) similarities ON up.id = similarities.user_id
ORDER BY similarity_score DESC
LIMIT 10;
```

#### Get User's Top Interests by Category
```sql
SELECT
  ic.name as category,
  i.name as interest,
  ui.preference_level,
  ui.experience_level
FROM user_interests ui
JOIN interests i ON ui.interest_id = i.id
JOIN interest_categories ic ON i.category_id = ic.id
WHERE ui.user_id = auth.uid()
ORDER BY ic.name, ui.preference_level DESC;
```

### API Integration Examples

#### Profile Summary Endpoint
```sql
-- Use the provided view for efficient profile summaries
SELECT * FROM user_profile_summary
WHERE id = $1;
```

#### Personality Matching Algorithm
```sql
-- Comprehensive personality similarity calculation
WITH cognitive_similarity AS (
  -- Calculate cognitive function similarity
  SELECT user_id, AVG(similarity) as cog_similarity
  FROM user_cognitive_function_similarities
  WHERE target_user_id = $1
  GROUP BY user_id
),
interest_similarity AS (
  -- Calculate shared interests
  SELECT user_id, COUNT(*) / 10.0 as int_similarity
  FROM shared_user_interests
  WHERE target_user_id = $1
  GROUP BY user_id
)
SELECT
  up.id,
  up.display_name,
  (COALESCE(cs.cog_similarity, 0) * 0.6 +
   COALESCE(is.int_similarity, 0) * 0.4) as overall_similarity
FROM user_profiles up
LEFT JOIN cognitive_similarity cs ON up.id = cs.user_id
LEFT JOIN interest_similarity is ON up.id = is.user_id
WHERE up.id != $1
ORDER BY overall_similarity DESC;
```

### Testing and Validation

#### Data Integrity Checks
```sql
-- Verify cognitive function completeness
SELECT user_id, COUNT(*) as function_count
FROM user_cognitive_functions
GROUP BY user_id
HAVING COUNT(*) != 8;

-- Check for invalid scores
SELECT * FROM user_cognitive_functions
WHERE raw_score NOT BETWEEN 0 AND 100
   OR normalized_score NOT BETWEEN 0 AND 100
   OR function_rank NOT BETWEEN 1 AND 8;
```

#### Performance Monitoring
```sql
-- Monitor profile completion rates
SELECT
  section_name,
  AVG(completion_percentage) as avg_completion,
  COUNT(*) as total_users
FROM profile_completion_status
GROUP BY section_name;

-- Track assessment participation
SELECT
  assessment_type,
  COUNT(*) as total_assessments,
  AVG(confidence_score) as avg_confidence
FROM cognitive_function_assessments
WHERE completed_at >= NOW() - INTERVAL '30 days'
GROUP BY assessment_type;
```
