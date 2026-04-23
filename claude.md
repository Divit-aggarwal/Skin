# CLAUDE.md — SKIN App
# Behavioral guidelines + project context for Claude Code sessions.
# Update "Current Build Status" after every completed slice.

---

# PART 1: BEHAVIORAL GUIDELINES

Bias toward caution over speed. For trivial tasks, use judgment.

## 1. Think Before Coding

**Don't assume. Don't hide confusion. Surface tradeoffs.**

Before implementing:
- State your assumptions explicitly. If uncertain, ask.
- If multiple interpretations exist, present them — don't pick silently.
- If a simpler approach exists, say so. Push back when warranted.
- If something is unclear, stop. Name what's confusing. Ask.

## 2. Simplicity First

**Minimum code that solves the problem. Nothing speculative.**

- No features beyond what was asked.
- No abstractions for single-use code.
- No "flexibility" or "configurability" that wasn't requested.
- No error handling for impossible scenarios.
- If you write 200 lines and it could be 50, rewrite it.

Ask yourself: "Would a senior engineer say this is overcomplicated?" If yes, simplify.

## 3. Surgical Changes

**Touch only what you must. Clean up only your own mess.**

When editing existing code:
- Don't "improve" adjacent code, comments, or formatting.
- Don't refactor things that aren't broken.
- Match existing style, even if you'd do it differently.
- If you notice unrelated dead code, mention it — don't delete it.

When your changes create orphans:
- Remove imports/variables/functions that YOUR changes made unused.
- Don't remove pre-existing dead code unless asked.

Project-specific surgical rules:
- **Never modify completed migration files.** Only add new ones.
- **Never touch inference/ unless the session is explicitly about ML.**
- **Never implement Phase 2 or Phase 3 features during Phase 1 slices.**
- **Never merge inference service dependencies with the main API.**

The test: Every changed line should trace directly to the user's request.

## 4. Goal-Driven Execution

**Define success criteria. Loop until verified.**

Transform tasks into verifiable goals:
- "Add validation" → "Write tests for invalid inputs, then make them pass"
- "Fix the bug" → "Write a test that reproduces it, then make it pass"
- "Refactor X" → "Ensure tests pass before and after"

For multi-step tasks, state a brief plan:
```
1. [Step] → verify: [check]
2. [Step] → verify: [check]
3. [Step] → verify: [check]
```

Strong success criteria let you loop independently. Weak criteria ("make it work") require constant clarification.

---

# PART 2: PROJECT CONTEXT

## Project Overview

SKIN is a production-grade AI skincare analysis mobile app with a Digital Twin that builds a
persistent, evolving model of each user's skin over time. It uses real ML inference
(YOLOv11n for acne detection, U-Net for wrinkle segmentation) with a RAG-powered
conversational Twin in Phase 3.

**4 phases:**
- Phase 1 (Weeks 1–8): Full production shell. Real auth, real ML, real image upload. Twin tables scaffolded.
- Phase 2 (Weeks 9–14): Async pipeline. Celery/Redis, S3, pgvector embeddings, Twin memory ingestion.
- Phase 3 (Weeks 15–22): Twin intelligence. RAG, conversational chat, trend detection, recommendations.
- Phase 4 (Weeks 23+): Scale, environmental signals, population comparisons, data export.

---

## Complete Tech Stack

### Mobile (./mobile/)
- React Native + Expo (TypeScript)
- Expo Router (file-based navigation)
- TanStack Query (server state)
- Zustand (client state)
- React Hook Form + Zod (forms + validation)
- Axios (HTTP client with interceptor-based token refresh)
- expo-secure-store (token storage)
- expo-image-picker (camera/gallery)

### Backend API (./backend/)
- FastAPI (Python 3.12)
- SQLAlchemy async + asyncpg driver
- Alembic (migrations)
- pydantic-settings (config from env)
- passlib[bcrypt] 12 rounds (password hashing)
- python-jose[cryptography] (JWT)
- httpx (async HTTP client to inference service)
- slowapi (rate limiting)
- loguru (structured JSON logging)

### Inference Service (./inference/) — SEPARATE CONTAINER, NEVER MERGE WITH MAIN API
- FastAPI (Python 3.12)
- onnxruntime (ONNX model inference — CPU in Phase 1)
- opencv-python (image processing, oiliness heuristic)
- mediapipe (face detection for quality gate) — pin version explicitly
- YOLOv11n acne detection — exported to ONNX
- U-Net wrinkle segmentation — exported to ONNX

### Database
- PostgreSQL 16 with pgvector extension
- Docker image: pgvector/pgvector:pg16
- All PKs: UUID via gen_random_uuid()
- Soft deletes: deleted_at TIMESTAMPTZ NULL. All queries: WHERE deleted_at IS NULL

### Phase 2 (not yet — do not implement during Phase 1)
- Celery + Redis (async job queue)
- AWS S3 ap-south-1 (image storage)

### Phase 3 (not yet — do not implement during Phase 2 or earlier)
- OpenAI text-embedding-3-small → vector(1536)
- OpenAI gpt-4o-mini (Twin chat LLM)

---

## Monorepo Structure

```
skin/
├── backend/           ← FastAPI main API
├── inference/         ← FastAPI ML inference service (SEPARATE)
├── mobile/            ← React Native + Expo
├── docker-compose.yml
└── CLAUDE.md
```

---

## Backend Folder Structure (./backend/)

```
backend/
├── alembic/
│   ├── env.py                  ← async-configured
│   └── versions/               ← 001 through 008 migrations
├── app/
│   ├── main.py                 ← FastAPI factory, lifespan, routers, exception handlers
│   ├── config.py               ← pydantic-settings Settings class
│   ├── database.py             ← async engine, session factory, get_db dependency
│   ├── dependencies.py         ← get_current_user, get_db re-exports
│   ├── exceptions.py           ← custom exception hierarchy
│   ├── middleware.py           ← request logging, CORS, request_id UUID
│   ├── models/
│   │   ├── base.py             ← TimestampMixin, SoftDeleteMixin
│   │   ├── user.py
│   │   ├── profile.py
│   │   ├── refresh_token.py
│   │   ├── image.py
│   │   ├── analysis_session.py
│   │   ├── analysis_report.py
│   │   ├── recommendation.py
│   │   ├── twin_profile.py
│   │   ├── twin_memory_chunk.py
│   │   ├── product_interaction.py
│   │   └── twin_conversation.py
│   ├── api/v1/
│   │   ├── router.py
│   │   ├── auth/               ← router, service, repository, schemas
│   │   ├── users/              ← router, service, repository, schemas
│   │   ├── images/             ← router, service, repository, schemas
│   │   ├── analysis/
│   │   │   ├── router.py
│   │   │   ├── service.py      ← calls InferenceService, saves report
│   │   │   ├── repository.py
│   │   │   ├── schemas.py
│   │   │   └── inference_client.py  ← httpx client to inference service
│   │   └── twin/
│   │       ├── router.py
│   │       ├── service.py
│   │       ├── repository.py
│   │       └── schemas.py
│   └── utils/
│       ├── security.py         ← JWT encode/decode, bcrypt helpers
│       ├── pagination.py
│       └── validators.py
├── tests/
│   ├── conftest.py
│   ├── factories/
│   ├── unit/
│   └── integration/
├── .env.example
├── alembic.ini
├── pyproject.toml
└── Dockerfile
```

---

## Inference Service Folder Structure (./inference/)

```
inference/
├── main.py                     ← FastAPI app, POST /infer, POST /health
├── models/
│   ├── loader.py               ← load ONNX models on startup, cache as singletons
│   ├── acne.py                 ← YOLOv11n: preprocess → infer → parse detections
│   ├── wrinkle.py              ← U-Net: preprocess → infer → parse mask
│   └── oiliness.py             ← OpenCV HSV heuristic (T-zone saturation)
├── pipeline.py                 ← orchestrates all models → score aggregation
├── quality_gate.py             ← Laplacian blur check + MediaPipe face count
├── zone_mapper.py              ← maps bbox coordinates → face zone labels
├── schemas.py                  ← InferRequest / InferResponse Pydantic models
├── config.py                   ← model paths, thresholds from env
├── weights/                    ← ONNX model files (not in git)
│   ├── yolo11n_acne.onnx
│   └── unet_wrinkle.onnx
├── Dockerfile
└── requirements.txt            ← isolated deps, never shared with main API
```

---

## Mobile Folder Structure (./mobile/)

```
mobile/
├── app/
│   ├── _layout.tsx             ← Root: QueryClient, Zustand init, font loading
│   ├── index.tsx               ← Splash: auth check → redirect
│   ├── onboarding.tsx
│   ├── login.tsx
│   ├── register.tsx
│   ├── profile-setup.tsx
│   └── (app)/
│       ├── _layout.tsx         ← Auth guard + bottom tab navigator
│       ├── index.tsx           ← Home dashboard
│       ├── upload.tsx
│       ├── history.tsx
│       ├── twin.tsx
│       ├── settings.tsx
│       └── report/
│           └── [sessionId].tsx
├── components/
│   ├── ui/                     ← Button, Input, Card, ScoreRing, Badge, Avatar,
│   │                             ProgressBar, LoadingSpinner, ErrorBanner,
│   │                             EmptyState, BottomSheet, SafeAreaWrapper
│   └── features/
│       ├── onboarding/OnboardingStep.tsx
│       ├── dashboard/LatestReportCard.tsx
│       ├── report/ZoneBreakdownCard.tsx
│       ├── report/RecommendationItem.tsx
│       ├── history/SessionListItem.tsx
│       └── twin/TwinChatBubble.tsx
├── hooks/                      ← useAuth, useProfile, useAnalysis, useReport,
│                                 useHistory, useImagePicker, useTwin
├── store/                      ← authStore, userStore, sessionStore, twinStore
├── api/                        ← client.ts (axios + interceptors), auth, users,
│                                 images, analysis, twin, types
├── schemas/                    ← authSchemas, profileSchemas, analysisSchemas
├── constants/                  ← theme, queryKeys, config
├── utils/                      ← formatters, storage (SecureStore), imageUtils
└── types/                      ← domain, navigation
```

---

## Database Migration Sequence

| Migration | Tables |
|-----------|--------|
| 001 | users, refresh_tokens |
| 002 | profiles |
| 003 | images |
| 004 | analysis_sessions, analysis_reports |
| 005 | recommendations |
| 006 | skin_twin_profiles — scaffold in Phase 1, auto-created on register |
| 007 | twin_memory_chunks — embedding column NULL until Phase 2 |
| 008 | product_interactions, twin_conversations |
| P2-001 | HNSW index on twin_memory_chunks(embedding) — Phase 2 only |

### Key Schema Rules
- CASCADE DELETE wired to ALL twin tables — GDPR requirement
- skin_twin_profiles auto-created on register in same transaction as user + profile
- twin_memory_chunks.embedding is VECTOR(1536) — NULL in Phase 1, populated in Phase 2
- Composite index on analysis_sessions: (user_id, created_at DESC)
- recommendations stored as individual rows, NOT JSONB array

---

## API Contracts Summary

- Base URL: /api/v1/
- Auth header: Authorization: Bearer <access_token>
- Error envelope: { "error": { "code": "SNAKE_CASE", "message": "...", "detail": null } }

### Auth
- POST /auth/register → 201 { access_token, refresh_token, user }
- POST /auth/login → 200 { access_token, refresh_token, user }
- POST /auth/refresh → 200 { access_token, refresh_token } — rotates refresh token
- POST /auth/logout → 204

### Users & Profiles
- GET/PUT /users/me
- GET/PUT /users/me/profile
- DELETE /users/me — requires password confirmation, cascades all data

### Images
- POST /images/upload — base64, max 3MB, runs quality gate, returns image_id

### Analysis
- POST /analysis/sessions — { image_id } → full report (sync in Phase 1)
- GET /analysis/sessions/{id}
- GET /analysis/sessions/{id}/report
- GET /analysis/history — paginated, uses composite index

### Twin
- GET /twin/me — stub in Phase 1, real data from Phase 2
- POST /twin/chat — Phase 3 only

---

## Score Formula

- overall_score = acne×0.4 + wrinkle×0.3 + oiliness×0.3
- All scores: 0.0–100.0, clipped
- severity_level: overall < 33 → mild, 33–66 → moderate, > 66 → severe
- model_version format: "yolo11n-acne-v0.1_unet-wrinkle-v0.1_oiliness-heuristic-v1"

---

## Design System Tokens

### Colors
| Token | Value |
|-------|-------|
| Primary background | #F5EFE6 (warm beige) |
| Accent / primary | #6B8F71 (sage green) |
| Surface | #FFFFFF / #FAFAFA |
| Danger / severe | #E05C5C |
| Warning / moderate | #D4A017 |
| Success / mild | #4CAF7D |
| Text primary | #1A1A1A |
| Text secondary | #6B6B6B |

### Typography
| Style | Spec |
|-------|------|
| H1 | 28px / semibold — screen titles |
| H2 | 22px / semibold — section headers |
| Body | 16px / regular |
| Caption | 13px / regular — labels, metadata |
| Score display | 36px / bold |

### Spacing Scale
Base unit 4px. Valid values: 4, 8, 12, 16, 20, 24, 32, 48, 64. Never use values outside this scale.

### Score Color Logic
- score < 33 → #4CAF7D (mild/green)
- score 33–66 → #D4A017 (moderate/amber)
- score > 66 → #E05C5C (severe/red)

---

## Key Environment Variables

```
DATABASE_URL=postgresql+asyncpg://user:password@postgres:5432/skin_db
SECRET_KEY=<min 32 chars — openssl rand -hex 32>
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=30
ENVIRONMENT=development
INFERENCE_SERVICE_URL=http://inference:8001
INFERENCE_TIMEOUT_SECONDS=30
MAX_IMAGE_SIZE_MB=3
BLUR_SCORE_THRESHOLD=100.0    ← tune from calibration sprint
YOLO_CONF_THRESHOLD=0.4       ← tune from calibration sprint
```

---

## Critical Non-Negotiable Rules

1. **Quality gate before ML** — Slice 4 must be complete and tested before Slice 5 starts.
2. **Separate containers** — inference/ and backend/ are never merged. Separate Dockerfiles, separate requirements.txt.
3. **Twin tables in Phase 1** — migrations 006–008 exist from day one. They start empty. Never retrofit.
4. **CASCADE DELETE is a GDPR requirement** — DELETE /users/me must cascade to ALL tables including Twin. Test explicitly.
5. **JWT single-flight refresh lock** — implement in api/client.ts during Slice 2. Never remove or simplify.
6. **One slice at a time** — complete backend + tests fully before building the frontend screen for that slice.
7. **Hard phase gates** — no Phase 2 features until Phase 1 is tested. No Phase 3 until Phase 2 is stable.
8. **Calibration sprint is mandatory** — do not show ML scores to any user before running 50+ real selfie tests.
9. **Pin mediapipe version** — breaking API changes between versions. Pin explicitly in inference/requirements.txt.

---

## Current Build Status

> Update this section at the end of every Claude Code session.

### ✅ Completed
- Slice 1: Scaffolding + CI (Days 1–3) — monorepo, FastAPI shell, async SQLAlchemy, docker-compose, alembic async env
- Slice 2: Auth (Days 4–8) — migration 001, security utils, AuthRepository/Service, /auth/register|login|refresh|logout, get_current_user dep, 12/12 tests passing

### 🔄 In Progress
- Slice 3: Profile CRUD — Days 9–11

### ⏳ Remaining
- Slice 3: Profile CRUD — Days 9–11
- Slice 4: Image Upload + Quality Gate — Days 12–15
- Slice 5: ML Inference Integration — Days 16–22 (includes calibration sprint)
- Slice 6: Report Detail UI — Days 23–26
- Slice 7: History Screen — Days 27–30
- Slice 8: Onboarding + Settings — Days 31–36
- Slice 9: Digital Twin Scaffold — Days 37–39
- Slice 10: Integration Pass + Production Foundations — Days 40–44