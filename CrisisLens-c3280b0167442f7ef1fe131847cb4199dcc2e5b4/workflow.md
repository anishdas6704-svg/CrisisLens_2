You are an expert full-stack AI engineer and hackathon product developer.

Build a complete, functional, demo-ready software project named:

CRISISLENS

TAGLINE:
"When everything changes, know what changed."

DOMAIN:
AI & Open Innovation

TEAM:
INSEPTION

TEAM MEMBERS:
Utsab Pandey
Soumabha Ghosh
Anish Das

EVENT:
SAGE-A-THON 2026

==================================================
1. CORE PROBLEM
==================================================

CrisisLens solves ONE specific societal problem:

INFORMATION OVERLOAD DURING EMERGENCIES.

Problem Statement:

"During emergencies, people are overwhelmed by rapidly changing information from multiple sources such as government alerts, emergency agencies, news, and social media. Because updates arrive at different times and may conflict with each other, people struggle to identify what has changed, which update is current, and what information is relevant to their situation."

Do NOT turn this into a generic emergency-response application.

The project is specifically about:

RAPIDLY CHANGING + CONFLICTING EMERGENCY INFORMATION.

The primary question CrisisLens must answer is:

"WHAT CHANGED?"

==================================================
2. PRODUCT POSITIONING
==================================================

CrisisLens is NOT:

- A generic news aggregator
- A normal emergency alert application
- An emergency authority
- A disaster prediction system
- An AI system that gives emergency instructions

CrisisLens IS:

An AI-powered crisis information intelligence platform that organizes, compares, and explains rapidly changing emergency information.

IMPORTANT SAFETY/POSITIONING RULE:

Official authorities remain the source of truth.

CrisisLens must never invent emergency instructions or override official authorities.

The system should clearly show:

SOURCE
TIMESTAMP
CURRENT STATUS
PREVIOUS STATUS
CHANGE
CONFLICT

==================================================
3. PRIMARY MVP 
==================================================

For the hackathon, build ONE focused scenario:

WILDFIRE INFORMATION TRACKER

Do not initially support every disaster type.

The MVP should demonstrate:

1. Emergency update ingestion
2. AI information extraction
3. Entity matching
4. Old vs new comparison
5. Change detection
6. Conflict detection
7. Source and timestamp tracking
8. Location-based filtering
9. Priority ranking
10. Live crisis dashboard

==================================================
4. CORE USER FLOW
==================================================

The complete application flow should be:

Emergency Update
        ↓
Data Ingestion
        ↓
AI Information Extraction
        ↓
Entity Matching
        ↓
Find Previous State
        ↓
Compare OLD vs NEW
        ↓
Change Detection
        ↓
Conflict Detection
        ↓
Priority / Relevance Ranking
        ↓
CrisisLens Dashboard

==================================================
5. AI INFORMATION EXTRACTION
==================================================

Use an LLM API such as Gemini.

When an emergency update is received, extract structured information.

Example input:

"Highway 12 is now closed due to fire activity."

Convert it into:

{
  "location": "Highway 12",
  "event_type": "ROAD",
  "status": "CLOSED",
  "reason": "Fire activity",
  "affected_area": "Riverside County",
  "timestamp": "2026-09-05T10:30:00"
}

Extract:

- Location
- Event type
- Status
- Reason
- Affected area
- Timestamp
- Source

IMPORTANT:

The LLM should understand and structure the information.

The backend should perform deterministic comparison and state-change logic wherever possible.

Do NOT allow the LLM to invent missing information.

Return null/unknown when information is unavailable.

==================================================
6. ENTITY MATCHING
==================================================

The system must recognize different names referring to the same real-world entity.

Example:

"Highway 12"
"Hwy 12"
"HWY-12"

should be recognized as:

HIGHWAY 12

Similarly:

"Shelter B"
"Emergency Shelter B"

should be matched where appropriate.

Use normalization first.

Optionally use semantic similarity/LLM assistance for difficult cases.

==================================================
7. CHANGE DETECTION — CORE FEATURE
==================================================

THIS IS THE MOST IMPORTANT FEATURE OF THE PROJECT.

The system must maintain historical states.

Example:

Previous update:

Highway 12
Status: OPEN

New update:

Highway 12
Status: CLOSED

The system must automatically generate:

STATUS CHANGED

BEFORE:
OPEN

AFTER:
CLOSED

REASON:
Fire activity

Dashboard representation:

🔴 HIGHWAY 12

OPEN → CLOSED

STATUS CHANGED

Do not simply display the newest update.

Always compare the newest state against historical information.

==================================================
8. CONFLICT DETECTION
==================================================

Detect contradictory information between sources.

Example:

OFFICIAL EMERGENCY AGENCY:
Shelter A → OPEN
10:42 AM

NEWS:
Shelter A → FULL
10:15 AM

SOCIAL MEDIA:
Shelter A → CLOSED
Unknown timestamp

Display:

⚠️ INFORMATION CONFLICT

Shelter A

Official:
OPEN — 10:42 AM

News:
FULL — 10:15 AM

Social:
CLOSED — Unknown

The system should NOT blindly declare which statement is true.

Instead:

- Display all relevant sources
- Display timestamps
- Identify source type
- Highlight the latest official/verified source
- Link/show the original source where available

Display:

"Official authorities remain the source of truth."

==================================================
9. SOURCE RELIABILITY
==================================================

Implement source classification.

Suggested categories:

OFFICIAL GOVERNMENT
VERIFIED EMERGENCY ORGANIZATION
ESTABLISHED NEWS
UNVERIFIED SOCIAL SOURCE

For the MVP, use a simple source reliability/context indicator.

Example:

Official Government
██████████

Emergency Organization
█████████

Established News
████████

Unknown Social Source
██

IMPORTANT:

Do NOT represent this as an absolute "truth score."

Call it:

SOURCE RELIABILITY / SOURCE CONTEXT

The goal is to help users understand where information came from.

==================================================
10. LOCATION FEATURE
==================================================

Add:

"WHAT CHANGED NEAR ME?"

Allow the user to select a location.

Example:

📍 Riverside County

Then show only relevant updates.

Example:

YOUR AREA

🔴 HIGHWAY 12
OPEN → CLOSED

🟠 EVACUATION ZONE
ZONE 3 → ZONE 4

🔴 SHELTER B
AVAILABLE → FULL

Filter information using:

- Location
- Affected area
- Recency
- Priority

==================================================
11. WILDFIRE DEMO SCENARIO
==================================================

Create built-in demo data so the application can be demonstrated even without live external APIs.

Use this exact scenario:

UPDATE 1 — 8:00 AM

Source:
Official Emergency Agency

Information:

"Highway 12 is open.
Shelter B is available.
Evacuation Zone 3 remains unchanged."

Expected result:

🟢 No major changes

--------------------------------------------------

UPDATE 2 — 10:30 AM

Source:
Official Emergency Agency

Information:

"Highway 12 is now closed due to fire activity."

Expected result:

🔴 CHANGE DETECTED

HIGHWAY 12

OPEN → CLOSED

Reason:
Fire activity

--------------------------------------------------

UPDATE 3 — 11:15 AM

Source:
Official Emergency Agency

Information:

"Shelter B is now full and is no longer accepting new arrivals."

Expected result:

🔴 CHANGE DETECTED

SHELTER B

AVAILABLE → FULL

--------------------------------------------------

UPDATE 4 — 12:00 PM

Source:
Official Emergency Agency

Information:

"Evacuation Zone has expanded from Zone 3 to Zone 4."

Expected result:

🟠 CHANGE DETECTED

EVACUATION ZONE

ZONE 3 → ZONE 4

--------------------------------------------------

CONFLICT DEMO:

News Source:
"Shelter B is full."

Official Source:
"Shelter B remains available."

Expected:

⚠️ INFORMATION CONFLICT

Show both sources and timestamps.

==================================================
12. LIVE DEMO MODE
==================================================

Create a DEMO MODE in the dashboard.

Allow the user/judge to press:

"PROCESS NEXT UPDATE"

Each click should introduce the next wildfire update.

Timeline:

8:00 AM
↓
10:30 AM
↓
11:15 AM
↓
12:00 PM

The dashboard should visibly change after each update.

This is critical for the hackathon presentation.

The judges should be able to SEE:

OLD STATE
↓
NEW STATE
↓
AI/ENGINE DETECTS CHANGE
↓
DASHBOARD UPDATES

==================================================
13. DASHBOARD DESIGN
==================================================

Build a professional hackathon-quality dashboard.

Do NOT make it look like a basic student CRUD application.

Main layout:

--------------------------------------------------
CRISISLENS                         🟢 LIVE
Riverside County
--------------------------------------------------

🔥 WILDFIRE

3 MAJOR CHANGES

--------------------------------------------------

🔴 HIGHWAY 12

OPEN → CLOSED

Status Changed

Fire activity

Official Emergency Agency
10:30 AM

--------------------------------------------------

🔴 SHELTER B

AVAILABLE → FULL

Status Changed

Official Emergency Agency
11:15 AM

--------------------------------------------------

🟠 EVACUATION ZONE

ZONE 3 → ZONE 4

Area Expanded

Official Emergency Agency
12:00 PM

--------------------------------------------------

⚠️ INFORMATION CONFLICT

Shelter B

Official → AVAILABLE
News → FULL

--------------------------------------------------

LAST VERIFIED UPDATE:
12:00 PM

--------------------------------------------------

FROM INFORMATION OVERLOAD
        ↓
TO INFORMATION CLARITY

==================================================
14. UI COMPONENTS
==================================================

Create reusable components:

- Header
- Crisis status banner
- Location selector
- Update timeline
- Change card
- Conflict card
- Source badge
- Timestamp badge
- Before/After comparison
- Priority indicator
- Demo controls
- Update ingestion panel
- Dashboard statistics
- Source history modal

Each change card should clearly show:

ENTITY
BEFORE
AFTER
TIME
SOURCE
REASON
STATUS

==================================================
15. UPDATE INGESTION PANEL
==================================================

Create a panel where a user can manually enter an emergency update.

Example:

SOURCE:
County Emergency Agency

SOURCE TYPE:
Official

TIMESTAMP:
10:30 AM

UPDATE:

"Highway 12 is now closed due to fire activity."

Button:

PROCESS UPDATE

When clicked:

1. Send text to backend
2. AI extracts structured information
3. Match entity
4. Retrieve previous state
5. Compare
6. Detect change/conflict
7. Store update
8. Update dashboard

==================================================
16. TECHNICAL ARCHITECTURE
==================================================

Use:

FRONTEND:
Next.js
React
Tailwind CSS

BACKEND:
Python
FastAPI

AI:
Gemini API

DATABASE:
Supabase / PostgreSQL

DATA:
Official emergency feeds
RSS
Structured demo data

Architecture:

OFFICIAL APIs / RSS / DEMO DATA
            ↓
      DATA INGESTION
            ↓
       FASTAPI BACKEND
            ↓
       AI PROCESSING
            ↓
 ┌──────────┼──────────┐
 ↓          ↓          ↓
Extraction Entity     Change
           Matching   Detection
              ↓
       Conflict Detection
              ↓
       Priority Ranking
              ↓
          SUPABASE
              ↓
       NEXT.JS DASHBOARD

==================================================
17. DATABASE DESIGN
==================================================

Create at least these tables.

TABLE:
crisis_updates

Fields:

id
source_name
source_type
published_at
location
event_type
status
reason
affected_area
raw_text
reliability_context
created_at

TABLE:
detected_changes

Fields:

id
update_id
entity
previous_status
new_status
change_type
reason
detected_at

TABLE:
conflicts

Fields:

id
entity
source_a
status_a
source_b
status_b
detected_at
resolution_context

Do not overcomplicate the database.

==================================================
18. API ENDPOINTS
==================================================

Create clean backend APIs.

GET /

GET /health

POST /updates

POST /updates/process

GET /updates

GET /changes

GET /conflicts

GET /timeline

GET /location/{location}

GET /demo/next

GET /dashboard

Use proper validation and error handling.

==================================================
19. AI ENDPOINT
==================================================

Create a dedicated AI service.

Example:

POST /updates/process

Input:

{
  "text": "Highway 12 is now closed due to fire activity.",
  "source": "County Emergency Agency",
  "source_type": "OFFICIAL",
  "timestamp": "2026-09-05T10:30:00"
}

Return structured information:

{
  "location": "Highway 12",
  "event_type": "ROAD",
  "status": "CLOSED",
  "reason": "Fire activity",
  "affected_area": null,
  "timestamp": "2026-09-05T10:30:00"
}

Then the backend performs comparison.

==================================================
20. ERROR HANDLING
==================================================

Handle:

- Invalid AI response
- Missing fields
- Missing timestamp
- Duplicate updates
- API failure
- Database failure
- Empty input
- Unknown location
- Conflicting information
- No previous state

Never crash the dashboard.

Show clear user-friendly errors.

==================================================
21. SECURITY
==================================================

Never hardcode API keys.

Use:

.env

Variables:

GEMINI_API_KEY=
SUPABASE_URL=
SUPABASE_KEY=

Add .env to .gitignore.

Never expose secret keys to the frontend.

==================================================
22. DEMO-FIRST DEVELOPMENT
==================================================

Prioritize a working demo over unnecessary features.

The minimum successful flow must be:

ENTER UPDATE
↓
AI EXTRACTS DATA
↓
SYSTEM FINDS PREVIOUS STATE
↓
SYSTEM COMPARES
↓
CHANGE DETECTED
↓
DASHBOARD DISPLAYS:

OPEN → CLOSED

Do this before implementing advanced features.

==================================================
23. OPTIONAL FEATURES — ONLY AFTER MVP
==================================================

If the core MVP is completely stable, optionally add:

- Map visualization
- Multiple disaster categories
- More data sources
- Multilingual summaries
- Advanced source history
- Personalized location
- Mobile responsive improvements

Do NOT sacrifice the core change-detection system for these features.

==================================================
24. FUTURE ROADMAP
==================================================

The production vision can eventually expand to:

→ Multiple disaster types
→ More official data sources
→ Mobile application
→ Multilingual support
→ Advanced map visualization
→ Personalized alerts

But these are NOT required for the first MVP.

==================================================
25. PROJECT PHILOSOPHY
==================================================

The central product philosophy is:

"People don't need more emergency information.
They need to understand what changed."

The core transformation is:

INFORMATION OVERLOAD
        ↓
AI ORGANIZATION
        ↓
CHANGE DETECTION
        ↓
CONFLICT DETECTION
        ↓
INFORMATION CLARITY

==================================================
26. IMPORTANT PRODUCT RULES
==================================================

Always:

✓ Show source
✓ Show timestamp
✓ Show previous state
✓ Show current state
✓ Highlight changes
✓ Highlight conflicts
✓ Preserve official source authority
✓ Avoid hallucinating information
✓ Keep the interface simple

Never:

✗ Invent emergency instructions
✗ Pretend to be an emergency authority
✗ Hide source information
✗ Claim an uncertain report is definitely true
✗ Replace official emergency systems
✗ Generate fake emergency alerts

==================================================
27. HACKATHON SUCCESS CRITERIA
==================================================

The final application should allow a judge to understand the concept within 30 seconds.

They should immediately see:

PROBLEM:
Too much rapidly changing information.

SOLUTION:
CrisisLens.

AI:
Extract → Match → Compare → Detect.

RESULT:

"What Changed?"

==================================================
28. DEVELOPMENT PRIORITY
==================================================

Implement in this exact order:

PHASE 1
Project setup

PHASE 2
Supabase database

PHASE 3
FastAPI backend

PHASE 4
Gemini extraction

PHASE 5
Entity matching

PHASE 6
CHANGE DETECTION

PHASE 7
CONFLICT DETECTION

PHASE 8
Next.js dashboard

PHASE 9
Frontend-backend integration

PHASE 10
Wildfire demo mode

PHASE 11
Testing

PHASE 12
UI polish

PHASE 13
Deployment

==================================================
29. FINAL DELIVERABLE
==================================================

Generate a complete working repository containing:

/frontend
/backend
/data
README.md
.env.example
.gitignore

The README must contain:

- Project overview
- Problem statement
- Solution
- Features
- Architecture
- Technology stack
- Setup instructions
- Environment variables
- Database setup
- AI setup
- How to run frontend
- How to run backend
- Demo instructions
- Example wildfire scenario
- Future roadmap

==================================================
30. FINAL QUALITY REQUIREMENT
==================================================

This is a competitive hackathon project.

Do not generate a superficial prototype with static screens only.

The core pipeline must actually work:

TEXT INPUT
→ AI EXTRACTION
→ ENTITY MATCHING
→ DATABASE LOOKUP
→ OLD/NEW COMPARISON
→ CHANGE DETECTION
→ CONFLICT DETECTION
→ DASHBOARD

The application must be functional, visually polished, responsive, and easy to demonstrate.

Prioritize reliability and the core "WHAT CHANGED?" experience over unnecessary complexity.

FINAL PRODUCT:

CRISISLENS

"When everything changes, know what changed."