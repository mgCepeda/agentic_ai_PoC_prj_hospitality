# 📋 TODO - Agentic AI Hospitality PoC

> Last updated: 2025-12-16

---

## 🔥 In Progress (Current)

| Task | Priority | Started | Notes |
|------|----------|---------|-------|
| _No tasks in progress_ | - | - | - |

---

## 📌 Pending (Backlog)

### High Priority
| # | Task | Created | Context |
|---|------|--------|---------|
| 1 | Re-test simple agent with generated data | 2025-12-16 | Validate responses reflect generated hotels |
| 2 | Add switch to select dataset source via config/env | 2025-12-16 | Toggle between sample and generated datasets |


### Medium Priority
| # | Task | Created | Context |
|---|------|--------|---------|
| - | _No tasks_ | - | - |

### Low Priority
| # | Task | Created | Context |
|---|------|--------|---------|
| - | _No tasks_ | - | - |

---

## ✅ Completed (Done)

| Task | Completed | Commit | Notes |
|------|-----------|--------|-------|
| Create and activate virtual environment | 2025-12-16 | - | `.venv` configured |
| Configure `AI_AGENTIC_API_KEY` in `~/.bashrc` | 2025-12-16 | - | Key exported and persisted |
| Generate synthetic hotel data | 2025-12-16 | - | Files in `bookings-db/output_files/hotels/` |
| Fix agent data source path to use generated hotels | 2025-12-16 | - | Prioritize `bookings-db/output_files/hotels/` over local sample |

---

## 🐛 Technical Debt

| Description | Impact | Detected | Status |
|-------------|--------|----------|--------|
| Agent defaulted to local sample data path | Medium | 2025-12-16 | Addressed by path update; consider config-driven source. Rationale: during testing, the agent loaded the local sample dataset instead of the freshly generated synthetic data. We now prioritize `bookings-db/output_files/hotels/` if `hotels.json` exists and keep a fallback to the local set for compatibility. |

---

## ⚠️ Problems Encountered

### Working under WSL `/mnt` paths
- Observation: We started the workshop on WSL-mounted Windows paths (e.g., `/mnt/c/...`). On these paths, creating virtual environments (`.venv`) and installing dependencies is significantly slower and more error-prone.
- Impact: Much longer install times, potential timeouts, and permission/path anomalies caused by NTFS semantics and Windows–Linux interoperability overhead.
- Recommendation (professional): Work under native Linux filesystem paths, e.g., `/home/marina/...`, where IO is faster and POSIX semantics are consistent. This provides:
	- Faster and more reliable environment creation (`python -m venv .venv`) and package installation.
	- Fewer permission/path issues during build and runtime.
	- A more stable development experience for Python tooling inside WSL.

Recommended working path for this project: `/home/marina/workshop/agentic_ai_PoC_prj_hospitality`

---

## 📝 Usage Notes

### How to manage this file

1. **New task** → Add to **Backlog** with date and priority
2. **Start task** → Move to **In Progress** with start date
3. **Complete task** → Move to **Completed** with date and commit hash
4. **Technical debt** → Register in specific section to not forget it

### Commit format
When you complete a task, reference the commit like this:
- Short hash: `abc1234`
- With link (if using GitHub): `[abc1234](url-to-commit)`

### Priorities
- 🔴 **High**: Blocks other tasks or is critical
- 🟡 **Medium**: Important but not urgent
- 🟢 **Low**: Nice-to-have, minor improvements

---

## 🎓 Workshop Exercise Plans

### Exercise 0: Simple Agentic Assistant with File Context

#### Phase 1: Setup & Data Preparation
- [x] Install LangChain dependencies (`langchain`, `langchain-google-genai`)
- [x] Configure Google Gemini API key as environment variable (`AI_AGENTIC_API_KEY`)
- [x] Generate synthetic hotel data (3 hotels) using `gen_synthetic_hotels.py`
- [x] Verify hotel files are created in `bookings-db/output_files/hotels/`
- [x] Completed on 2025-12-16

#### Phase 2: Core Implementation
- [x] Create function to load hotel JSON file (`hotels.json`)
- [x] Create function to load hotel details markdown (`hotel_details.md`)
- [x] Implement `answer_hotel_question()` function with file context
- [x] Create ChatPromptTemplate with system prompt for hotel assistant
- [x] Build LangChain chain (prompt template + LLM)

#### Phase 3: Integration & Testing
- [x] Create `handle_hotel_query_simple()` async function for WebSocket API
- [x] Test with basic queries (hotel names, addresses, locations)
- [x] Test with meal plan queries
- [ ] Test with room information queries
- [ ] Verify error handling works correctly
- [ ] Initial agent test executed on 2025-12-16; found path issue

#### Phase 4: Documentation & Cleanup
- [ ] Add code comments and docstrings
- [ ] Test integration with WebSocket API endpoint
- [ ] Verify responses are properly formatted

---

### Exercise 1: Hotel Details with RAG

#### Phase 1: Setup & Data Preparation
- [ ] Install RAG dependencies (`langchain-community`, `chromadb`)
- [ ] Generate full hotel dataset (50 hotels) using `gen_synthetic_hotels.py`
- [ ] Verify all hotel files are created (JSON, markdown files)

#### Phase 2: Vector Store Creation
- [ ] Implement document loader for `hotels.json` (JSONLoader)
- [ ] Implement document loader for `hotel_details.md` (TextLoader)
- [ ] Implement document loader for `hotel_rooms.md` (TextLoader)
- [ ] Configure RecursiveCharacterTextSplitter (chunk_size=1000, overlap=200)
- [ ] Create GoogleGenerativeAIEmbeddings instance
- [ ] Build ChromaDB vector store from all documents
- [ ] Persist vector store to disk for reuse

#### Phase 3: RAG Chain Implementation
- [ ] Create ChatGoogleGenerativeAI LLM instance (gemini-2.5-flash-lite, temperature=0)
- [ ] Implement RetrievalQA chain with vector store
- [ ] Design system prompt for hotel assistant context
- [ ] Configure retrieval parameters (k=5 documents)
- [ ] Test retrieval quality with sample queries

#### Phase 4: Agent Implementation
- [ ] Create hotel details agent function
- [ ] Implement query preprocessing (normalization, validation)
- [ ] Add response formatting (markdown structure)
- [ ] Handle edge cases (no results, ambiguous queries)

#### Phase 5: Integration & Testing
- [ ] Integrate RAG agent with WebSocket API
- [ ] Test with hotel location queries
- [ ] Test with meal plan and pricing queries
- [ ] Test with room comparison queries
- [ ] Verify performance (response time < 10s)
- [ ] Compare results with Exercise 0 (should be more accurate)

#### Phase 6: Optimization
- [ ] Tune chunk size and overlap if needed
- [ ] Optimize retrieval k parameter
- [ ] Add caching for frequent queries (optional)
- [ ] Document vector store persistence strategy

---

### Exercise 2: Booking Analytics with SQL Agent

#### Phase 1: Setup & Database Connection
- [ ] Start PostgreSQL database using `./start-app.sh --no_ai_agent`
- [ ] Install SQL dependencies (`langchain-community`, `psycopg2-binary`)
- [ ] Verify database connection (test connection string)
- [ ] Inspect database schema and understand table structure
- [ ] Load sample booking data to test queries

#### Phase 2: SQL Database Integration
- [ ] Create SQLDatabase instance from connection URI
- [ ] Test basic SQL queries manually (SELECT, COUNT, SUM)
- [ ] Verify database schema introspection works
- [ ] Test date filtering and aggregation queries

#### Phase 3: SQL Agent Implementation
- [ ] Create SQLDatabaseToolkit with database and LLM
- [ ] Implement create_sql_agent with proper system prompt
- [ ] Configure agent for hospitality context (hotel names, dates, metrics)
- [ ] Add custom system prompt explaining booking schema
- [ ] Test agent with simple queries (booking counts)

#### Phase 4: Analytics Calculations
- [ ] Implement bookings count query logic
- [ ] Implement occupancy rate calculation (two-step: query + formula)
- [ ] Implement total revenue aggregation
- [ ] Implement RevPAR calculation (revenue / available room-nights)
- [ ] Handle edge cases (no bookings, division by zero)

#### Phase 5: Two-Step Query Process
- [ ] Implement Step 1: Generate SQL from natural language
- [ ] Implement Step 2: Execute query and format results
- [ ] Add query validation before execution
- [ ] Implement result formatting (tables, markdown)
- [ ] Add error handling for SQL syntax errors

#### Phase 6: Advanced Queries & Testing
- [ ] Test with date range queries (months, quarters, years)
- [ ] Test with hotel-specific filters
- [ ] Test with guest country/city filters
- [ ] Test with meal plan comparisons
- [ ] Verify occupancy and RevPAR calculations are accurate
- [ ] Test with edge cases (empty results, invalid dates)

#### Phase 7: Integration & Error Handling
- [ ] Integrate SQL agent with WebSocket API
- [ ] Add comprehensive error handling (connection errors, query errors)
- [ ] Implement query timeout protection
- [ ] Add logging for debugging SQL generation
- [ ] Test end-to-end with WebSocket interface

#### Phase 8: Optimization & Documentation
- [ ] Optimize system prompt for better SQL generation
- [ ] Add query result caching for common queries (optional)
- [ ] Document SQL agent limitations and best practices
- [ ] Add code comments and docstrings

---

## 📊 Quick Summary

```
📌 Pending:  2
🔥 In progress: 0
✅ Completed: 4
🐛 Technical debt: 1
🎓 Workshop Exercises: 3 (Exercise 0, 1, 2)
```

> ⚠️ **Remember**: Update this file after each work session
