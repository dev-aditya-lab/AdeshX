# Graph Report - .  (2026-05-01)

## Corpus Check
- Corpus is ~10,222 words - fits in a single context window. You may not need a graph.

## Summary
- 198 nodes · 380 edges · 12 communities detected
- Extraction: 52% EXTRACTED · 48% INFERRED · 0% AMBIGUOUS · INFERRED: 182 edges (avg confidence: 0.56)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- [[_COMMUNITY_Frontend Pages & API|Frontend Pages & API]]
- [[_COMMUNITY_Backend Services (NLPLLM)|Backend Services (NLP/LLM)]]
- [[_COMMUNITY_Extraction API & Models|Extraction API & Models]]
- [[_COMMUNITY_Actions API & Models|Actions API & Models]]
- [[_COMMUNITY_Dashboard API & Schemas|Dashboard API & Schemas]]
- [[_COMMUNITY_Documents API & Models|Documents API & Models]]
- [[_COMMUNITY_Database & App Main|Database & App Main]]
- [[_COMMUNITY_Configuration|Configuration]]
- [[_COMMUNITY_OCR Service|OCR Service]]
- [[_COMMUNITY_Backend Schemas|Backend Schemas]]
- [[_COMMUNITY_Config Rationale|Config Rationale]]
- [[_COMMUNITY_Config Rationale|Config Rationale]]

## God Nodes (most connected - your core abstractions)
1. `Document` - 24 edges
2. `DocumentStatus` - 22 edges
3. `Base` - 20 edges
4. `ExtractedData` - 18 edges
5. `Verification` - 16 edges
6. `ActionPlan` - 15 edges
7. `VerificationStatus` - 12 edges
8. `Action plan & verification API endpoints.` - 11 edges
9. `Generate action plan for a document.` - 11 edges
10. `Get action plans for a document.` - 11 edges

## Surprising Connections (you probably didn't know these)
- `Generated action plan for government officials.` --uses--> `Base`  [INFERRED]
  backend\app\models\action_plan.py → backend\app\database.py
- `Represents an uploaded court judgment PDF.` --uses--> `Base`  [INFERRED]
  backend\app\models\document.py → backend\app\database.py
- `Human-in-the-loop verification record.` --uses--> `Base`  [INFERRED]
  backend\app\models\verification.py → backend\app\database.py
- `ActionPlan` --uses--> `Base`  [INFERRED]
  backend\app\models\action_plan.py → backend\app\database.py
- `Action plan database model.` --uses--> `Base`  [INFERRED]
  backend\app\models\action_plan.py → backend\app\database.py

## Communities

### Community 0 - "Frontend Pages & API"
Cohesion: 0.09
Nodes (21): loadAll(), loadCases(), handleDelete(), load(), handleExtract(), handleGeneratePlan(), handleVerify(), loadDocument() (+13 more)

### Community 1 - "Backend Services (NLP/LLM)"
Cohesion: 0.11
Nodes (24): _calculate_auto_deadlines(), generate_action_plan(), _generate_with_llm(), _get_demo_action_plan(), Action Engine — Generate action plans from extracted court judgment data., Generate an action plan based on extracted judgment data., Auto-calculate standard legal deadlines., call_llm() (+16 more)

### Community 2 - "Extraction API & Models"
Cohesion: 0.13
Nodes (21): get_extraction(), Extraction API endpoints — trigger and retrieve NLP extraction., Trigger text extraction and NLP analysis for a document., Get extracted data for a document., trigger_extraction(), Base, Base class for all database models., DeclarativeBase (+13 more)

### Community 3 - "Actions API & Models"
Cohesion: 0.18
Nodes (23): generate_actions(), get_actions(), get_verification(), Action plan & verification API endpoints., Get verification status for a document., Generate action plan for a document., Get action plans for a document., Submit human verification for a document's action plan. (+15 more)

### Community 4 - "Dashboard API & Schemas"
Cohesion: 0.18
Nodes (22): get_cases(), get_deadlines(), get_summary(), Dashboard API endpoints — stats, verified cases, deadlines., Get upcoming deadlines sorted by urgency., Get dashboard summary statistics., Get verified cases with optional filters., BaseModel (+14 more)

### Community 5 - "Documents API & Models"
Cohesion: 0.19
Nodes (19): delete_document(), get_document(), list_documents(), Document API endpoints — upload, list, get, serve PDF., Upload a PDF document., List all uploaded documents., Get a single document by ID., Serve the PDF file for viewing. (+11 more)

### Community 6 - "Database & App Main"
Cohesion: 0.15
Nodes (10): get_db(), init_db(), SQLAlchemy database setup for SQLite., Dependency to get database session., Create all database tables., on_startup(), AdeshX — FastAPI Application Entry Point., Initialize database on startup. (+2 more)

### Community 7 - "Configuration"
Cohesion: 0.25
Nodes (5): Config, Application configuration using Pydantic Settings., Application settings loaded from environment variables., Settings, BaseSettings

### Community 8 - "OCR Service"
Cohesion: 0.32
Nodes (7): _clean_text(), extract_text_from_pdf(), _ocr_page(), OCR Service — PDF text extraction using PyMuPDF and Tesseract., OCR a single PDF page using Tesseract., Clean extracted text — remove noise, fix spacing., Extract text from a PDF file.      Strategy:     1. Try PyMuPDF for digital text

### Community 9 - "Backend Schemas"
Cohesion: 1.0
Nodes (1): Pydantic schemas package.

### Community 12 - "Config Rationale"
Cohesion: 1.0
Nodes (1): Get absolute upload directory path.

### Community 13 - "Config Rationale"
Cohesion: 1.0
Nodes (1): Check if AI services are available.

## Knowledge Gaps
- **41 isolated node(s):** `Config`, `Application configuration using Pydantic Settings.`, `Application settings loaded from environment variables.`, `Get absolute upload directory path.`, `Check if AI services are available.` (+36 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **Thin community `Backend Schemas`** (2 nodes): `__init__.py`, `Pydantic schemas package.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Config Rationale`** (1 nodes): `Get absolute upload directory path.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Config Rationale`** (1 nodes): `Check if AI services are available.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Base` connect `Extraction API & Models` to `Actions API & Models`, `Dashboard API & Schemas`, `Documents API & Models`, `Database & App Main`?**
  _High betweenness centrality (0.140) - this node is a cross-community bridge._
- **Why does `trigger_extraction()` connect `Extraction API & Models` to `OCR Service`, `Backend Services (NLP/LLM)`?**
  _High betweenness centrality (0.120) - this node is a cross-community bridge._
- **Why does `ExtractedData` connect `Extraction API & Models` to `Actions API & Models`, `Dashboard API & Schemas`?**
  _High betweenness centrality (0.095) - this node is a cross-community bridge._
- **Are the 21 inferred relationships involving `Document` (e.g. with `Action plan & verification API endpoints.` and `Generate action plan for a document.`) actually correct?**
  _`Document` has 21 INFERRED edges - model-reasoned connections that need verification._
- **Are the 19 inferred relationships involving `DocumentStatus` (e.g. with `Action plan & verification API endpoints.` and `Generate action plan for a document.`) actually correct?**
  _`DocumentStatus` has 19 INFERRED edges - model-reasoned connections that need verification._
- **Are the 17 inferred relationships involving `Base` (e.g. with `ActionType` and `Priority`) actually correct?**
  _`Base` has 17 INFERRED edges - model-reasoned connections that need verification._
- **Are the 15 inferred relationships involving `ExtractedData` (e.g. with `Action plan & verification API endpoints.` and `Generate action plan for a document.`) actually correct?**
  _`ExtractedData` has 15 INFERRED edges - model-reasoned connections that need verification._