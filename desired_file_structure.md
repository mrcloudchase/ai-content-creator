# Migration Plan: Feature-Based File Structure Reorganization

Based on my review of the current codebase and your desired file structure, here's a comprehensive plan to migrate the application into a feature-based structure.

## Current vs. Desired Structure Analysis

The current structure is organized by technical layer:
- Models, services, and routers are in separate directories
- Features are mixed across these technical layers

The desired structure is organized by feature:
- Primary feature groups: `input_processing` and `ai`
- Subfeatures with their own models, services, and routers

## Implementation Steps

1. Create the new directory structure according to the file tree below
2. Move and refactor core functionality into the appropriate feature directories
3. Update import statements to reflect the new file locations
4. Implement the test structure in parallel with the application code
5. Validate the workflow with integration tests before finalizing the migration

## Desired Functionality and Workflow

When a user request comes in, the application will follow this flow:

1. User uploads a file to `/api/v1/customer-intent` endpoint
2. `app/main.py` serves as the application entry point and routes the request 
3. Request is validated against schemas defined in `app/ai/customer_intent/models/ai_customer_intent_model.py`
4. Request is routed to `app/ai/customer_intent/routers/ai_customer_intent_router.py` which orchestrates the process
5. Router calls some routing logic in `app/input_processing/core/services/file_type_routing_logic_core_services.py`
6. `app/input_processing/core/services/file_type_routing_logic_core_services.py` determines the file type based on extension and which `app/input_processing/{markdown,docx}/services/` file to use for extracting text
7. Router calls the determined `app/input_processing/{markdown,docx}/services/` file to extract all text from uploaded file and passes that text back to the router
8. Router calls `app/input_processing/core/services/input_processing_core_service.py` to process the extracted text for escaping control and special characters
9. Router calls `app/ai/core/services/tokenizer_core_service.py` to count tokens and ensure we're under the configured token limit configured in `app/config/settings.py`
10. Router calls `app/ai/customer_intent/services/ai_customer_intent_service.py` to structure the prompt accordingly using the processed text
11. Router calls `app/ai/core/services/ai_core_service.py` which passes the structured prompt to the LLM
12. Response is structured according to the response model in `app/ai/customer_intent/models/ai_customer_intent_model.py`
13. Router returns a response with the processed text, token limit, token count, and remaining tokens

## File Execution Flow

```
User submits POST to `/api/v1/generate/customer/intent` endpoint 
    ↓
app/main.py (entry point) 
    ↓
app/ai/customer_intent/models/ai_customer_intent_model.py (validates request) 
    ↓
app/ai/customer_intent/routers/ai_customer_intent_router.py 
    ↓
app/input_processing/core/services/file_type_routing_logic_core_services.py 
    ↓
app/input_processing/{markdown,docx}/services/ 
    ↓
app/input_processing/core/services/input_processing_core_service.py 
    ↓
app/ai/core/services/tokenizer_core_service.py 
    ↓
app/ai/customer_intent/services/ai_customer_intent_service.py 
    ↓
app/ai/core/services/ai_core_service.py 
    ↓
app/ai/customer_intent/models/ai_customer_intent_model.py (structures response) 
    ↓
Returns response to user
```

## Complete Project Directory Structure

```
/
├── app/
│   ├── config/
│   │   └── settings.py                                  # Application configuration
│   ├── input_processing/
│   │   ├── core/
│   │   │   ├── models/
│   │   │   │   └── __init__.py
│   │   │   ├── routers/
│   │   │   │   └── __init__.py
│   │   │   ├── services/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── file_type_routing_logic_core_services.py  # File type detection based on extension
│   │   │   │   └── input_processing_core_service.py     # Core text processing functionality
│   │   │   └── __init__.py
│   │   ├── markdown/
│   │   │   ├── models/
│   │   │   │   └── __init__.py
│   │   │   ├── routers/
│   │   │   │   └── __init__.py
│   │   │   ├── services/
│   │   │   │   ├── __init__.py
│   │   │   │   └── markdown_service.py                  # Markdown input processing functionality
│   │   │   └── __init__.py
│   │   └── docx/
│   │       ├── models/
│   │       │   └── __init__.py
│   │       ├── routers/
│   │       │   └── __init__.py
│   │       ├── services/
│   │       │   ├── __init__.py
│   │       │   └── docx_service.py                      # DOCX input processing functionality
│   │       └── __init__.py
│   ├── ai/
│   │   ├── core/
│   │   │   ├── models/
│   │   │   │   └── __init__.py
│   │   │   ├── routers/
│   │   │   │   └── __init__.py
│   │   │   ├── services/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── ai_core_service.py                   # Core AI service for LLM interactions
│   │   │   │   └── tokenizer_core_service.py            # Token counting functionality
│   │   │   └── __init__.py
│   │   └── customer_intent/
│   │       ├── models/
│   │       │   ├── __init__.py
│   │       │   └── ai_customer_intent_model.py          # Request/response Pydantic models
│   │       ├── routers/
│   │       │   ├── __init__.py
│   │       │   └── ai_customer_intent_router.py         # Customer intent endpoint and orchestration
│   │       ├── services/
│   │       │   ├── __init__.py
│   │       │   └── ai_customer_intent_service.py        # Customer intent prompt structuring
│   │       └── __init__.py
│   ├── main.py                                          # Application entry point
│   └── __init__.py
├── tests/
│   ├── conftest.py                                      # Shared test fixtures and configuration
│   ├── __init__.py
│   ├── unit/                                            # Unit tests mirroring app structure
│   │   ├── __init__.py
│   │   ├── test_main.py                                 # Tests for main.py
│   │   ├── config/
│   │   │   ├── __init__.py
│   │   │   └── test_settings.py                         # Tests for configuration
│   │   ├── input_processing/
│   │   │   ├── __init__.py
│   │   │   ├── core/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── services/
│   │   │   │   │   ├── __init__.py
│   │   │   │   │   ├── test_file_type_routing_logic_core_services.py  # File type detection tests
│   │   │   │   │   └── test_input_processing_core_service.py  # Text processing tests
│   │   │   │   └── integration/
│   │   │   │       └── test_core_services_integration.py  # Core services integration tests
│   │   │   ├── markdown/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── services/
│   │   │   │   │   ├── __init__.py
│   │   │   │   │   └── test_markdown_service.py         # Markdown parsing tests
│   │   │   │   └── integration/
│   │   │   │       └── test_markdown_processing_flow.py  # Markdown flow tests
│   │   │   └── docx/
│   │   │       ├── __init__.py
│   │   │       ├── services/
│   │   │       │   ├── __init__.py
│   │   │       │   └── test_docx_service.py             # DOCX parsing tests
│   │   │       └── integration/
│   │   │           └── test_docx_processing_flow.py     # DOCX flow tests
│   │   └── ai/
│   │       ├── __init__.py
│   │       ├── core/
│   │       │   ├── __init__.py
│   │       │   ├── services/
│   │       │   │   ├── __init__.py
│   │       │   │   ├── test_ai_core_service.py          # AI service tests
│   │       │   │   └── test_tokenizer_core_service.py   # Token counting tests
│   │       │   └── integration/
│   │       │       └── test_ai_core_integration.py      # AI core integration tests
│   │       └── customer_intent/
│   │           ├── __init__.py
│   │           ├── models/
│   │           │   ├── __init__.py
│   │           │   └── test_ai_customer_intent_model.py  # Model validation tests
│   │           ├── services/
│   │           │   ├── __init__.py
│   │           │   └── test_ai_customer_intent_service.py  # Prompt structuring tests
│   │           ├── routers/
│   │           │   ├── __init__.py
│   │           │   └── test_ai_customer_intent_router.py  # Router functionality tests
│   │           └── integration/
│   │               └── test_customer_intent_flow.py     # Customer intent flow tests
│   ├── integration/                                     # Cross-feature integration tests
│   │   ├── __init__.py
│   │   ├── test_file_to_ai_flow.py                      # File processing to AI workflow tests
│   │   └── test_end_to_end_flow.py                      # End-to-end workflow tests
│   └── api/                                             # API endpoint tests
│       ├── __init__.py
│       └── v1/
│           ├── __init__.py
│           └── generate/
│               ├── __init__.py
│               └── test_customer_intent_api.py          # Customer intent API tests
├── server.py                                            # Server runner
├── pytest.ini                                           # Pytest configuration
├── requirements.txt                                     # Project dependencies
├── .env-example                                         # Example environment variables
├── .gitignore                                         # Ignores files from being added to repo
├── .env                                                 # Environment variables (not in repo)
├── product_spec.md                                      # Product specifications
└── README.md                                            # Project documentation
```

## Test-Driven Development Plan

To ensure robust application functionality, we will implement a comprehensive testing strategy that mirrors our feature-based architecture. All tests will use pytest as the testing framework.

### Test Types and Approach

1. **Unit Tests**
   - Test individual functions and classes in isolation
   - Mock external dependencies and services
   - Focus on input/output validation and edge cases
   - Aim for high coverage of core business logic

2. **Integration Tests**
   - Feature-specific integration tests within each feature directory
   - Cross-feature integration tests in the root integration directory
   - Verify that data flows correctly between services
   - Test complete feature workflows
   - Use test fixtures to simulate realistic application state

3. **API Tests**
   - Test API endpoints with various request scenarios
   - Verify correct response structures and status codes
   - Test validation error handling
   - Test rate limiting and security features

### Testing Strategy

We will employ the following testing strategies:

1. **Test fixtures in conftest.py**
   - Sample files (markdown, docx) for testing file processing
   - Mock LLM responses for testing AI interactions
   - FastAPI TestClient for testing endpoints
   - Environment variable fixtures to control application configuration

2. **Mocking external dependencies**
   - Mock OpenAI API responses to test error handling
   - Create predictable test scenarios for token counting

3. **Parameterized tests**
   - Test multiple input scenarios efficiently
   - Cover edge cases systematically

4. **Test-driven development workflow**
   - Write tests before implementing features
   - Use failing tests to guide implementation
   - Refactor code once tests pass

5. **CI integration**
   - Run tests automatically on every commit
   - Maintain test coverage metrics
   - Block merges if tests fail

## Summary and Benefits

This feature-based restructuring provides several key benefits:

1. **Improved organization**: Code is organized by feature rather than technical layer, making it easier to understand the application structure
2. **Better maintainability**: Related code is located closer together, reducing the need to navigate between multiple directories
3. **Clearer dependencies**: Each feature has well-defined boundaries and dependencies
4. **Easier testing**: The test structure mirrors the application structure, making it clear which tests correspond to which features
5. **Scalability**: New features can be added as separate modules without disrupting existing code

The comprehensive test suite will ensure that the application functions correctly during and after the migration, while providing a foundation for future development using test-driven methodologies.

This test structure ensures that we maintain high-quality code, catch regressions early, and facilitate seamless feature development. The tests will serve as living documentation of expected behavior and provide confidence in the system's reliability.

## Implementation Plan & Timeline

The following is a practical week-by-week implementation plan to execute the file structure reorganization while maintaining functionality throughout the process:

### Phase 1: Preparation and Analysis (Week 1)

1. **Create a feature branch** for the reorganization work to isolate changes
   ```bash
   git checkout -b feature/restructure-codebase
   git push -u origin feature/restructure-codebase
   ```

2. **Map current files to their future locations**
   - Create a detailed mapping document showing where each existing file will move
   ```bash
   # Generate a list of current Python files
   find . -name "*.py" | sort > current_files.txt
   
   # Create mapping document (template)
   echo "Current Location,Future Location,Dependencies,Notes" > file_mapping.csv
   ```

3. **Identify and document dependencies** between components to understand impact
   ```bash
   # Example command to analyze imports in Python files
   for file in $(find . -name "*.py"); do
     echo "Analyzing $file"
     grep -E "^import|^from" $file
   done > import_analysis.txt
   ```

4. **Set up baseline tests** to verify functionality before and after changes
   ```bash
   # Run existing tests and save results
   pytest --verbose > baseline_test_results.txt
   
   # Generate coverage report
   pytest --cov=app --cov-report=xml:baseline_coverage.xml
   ```

#### Verification Steps for Phase 1
- [ ] Feature branch created and accessible by the team
- [ ] File mapping document is complete and reviewed by at least two team members
- [ ] All import statements and dependencies are documented
- [ ] Baseline test suite runs successfully with >90% pass rate
- [ ] Current code coverage metrics are captured and documented
- [ ] Critical API endpoints are identified and documented for priority testing

### Phase 2: Scaffold Creation (Week 1)

1. **Create the new directory structure** while keeping the old structure intact
   ```bash
   # Create main feature directories
   mkdir -p app/input_processing/core/{models,routers,services}
   mkdir -p app/input_processing/markdown/{models,routers,services}
   mkdir -p app/input_processing/docx/{models,routers,services}
   mkdir -p app/ai/core/{models,routers,services}
   mkdir -p app/ai/customer_intent/{models,routers,services}
   
   # Create __init__.py files
   find app -type d -exec touch {}/__init__.py \;
   ```

2. **Implement a basic version of app/main.py** with routing patterns that will support both old and new structures during transition
   ```python
   # app/main.py modification to support both structures
   from fastapi import FastAPI, Request
   
   app = FastAPI()
   
   # Import both old and new routers
   try:
       # Try new structure first
       from app.ai.customer_intent.routers.ai_customer_intent_router import router as customer_intent_router
   except ImportError:
       # Fall back to old structure
       from old_location.customer_intent_router import router as customer_intent_router
   
   # Include router with prefix
   app.include_router(customer_intent_router, prefix="/api/v1/generate")
   
   # Health check endpoint
   @app.get("/health")
   def health_check():
       return {"status": "ok"}
   ```

#### Verification Steps for Phase 2
- [ ] Directory structure validation script confirms all required directories exist
   ```bash
   # Check for all required directories
   for dir in app/input_processing/core/{models,routers,services} \
              app/input_processing/markdown/{models,routers,services} \
              app/input_processing/docx/{models,routers,services} \
              app/ai/core/{models,routers,services} \
              app/ai/customer_intent/{models,routers,services}; do
       if [ ! -d "$dir" ]; then echo "Missing: $dir"; fi
   done
   ```
- [ ] All `__init__.py` files are present and properly configured for imports
- [ ] Modified app/main.py successfully routes requests to both old and new file locations
- [ ] Test endpoints with curl/Postman to confirm basic functionality remains intact
   ```bash
   # Test health endpoint
   curl -v http://localhost:8000/health
   
   # Test customer intent endpoint
   curl -v -X POST -H "Content-Type: multipart/form-data" \
        -F "file=@sample.md" \
        http://localhost:8000/api/v1/generate/customer/intent
   ```
- [ ] Run linting tools to verify Python package structure is valid
   ```bash
   flake8 app/
   pylint app/
   ```
- [ ] Verify imports work from the new structure locations using simple test scripts
   ```python
   # test_imports.py
   try:
       import app.input_processing.core.services.file_type_routing_logic_core_services
       print("✅ Core services imports work")
   except ImportError as e:
       print(f"❌ Core services import failed: {e}")
   ```

### Phase 3: Feature-by-Feature Migration (Weeks 2-3)

1. **Input Processing Core Migration**
   - Move core file type detection functionality first
   ```bash
   # Copy the file type detection logic to new location
   cp <old_file_path> app/input_processing/core/services/file_type_routing_logic_core_services.py
   
   # Create input processing core service
   cp <old_service_path> app/input_processing/core/services/input_processing_core_service.py
   ```
   
   - Update imports and adjust any interface changes
   ```python
   # Original import
   from old.path import file_type_detection
   
   # New import
   from app.input_processing.core.services.file_type_routing_logic_core_services import detect_file_type
   ```
   
   - Run tests to verify functionality
   ```bash
   # Run tests for the specific component
   pytest tests/unit/input_processing/core/services/
   ```

#### Verification Steps for Input Processing Core
- [ ] All core input processing files are moved to their new locations
- [ ] Unit tests for file type detection pass
- [ ] Manual testing with sample files confirms proper file type detection
   ```bash
   # Create a test script
   python -c "from app.input_processing.core.services.file_type_routing_logic_core_services import detect_file_type; print(detect_file_type('test.md'))"
   ```
- [ ] Import statements updated across codebase referencing these modules
- [ ] No regressions in API response when uploading different file types

2. **File Format Handlers Migration**
   - Migrate markdown and docx handlers one at a time
   ```bash
   # Markdown handler migration
   cp <old_markdown_handler> app/input_processing/markdown/services/markdown_service.py
   
   # Update imports in markdown service
   sed -i 's/from old.path.core import/from app.input_processing.core.services import/g' app/input_processing/markdown/services/markdown_service.py
   
   # DOCX handler migration (similar)
   cp <old_docx_handler> app/input_processing/docx/services/docx_service.py
   ```
   
   - Update imports and references
   ```python
   # Old import
   from markdown_processor import process_markdown
   
   # New import
   from app.input_processing.markdown.services.markdown_service import process_markdown
   ```
   
   - Test each handler after migration
   ```bash
   pytest tests/unit/input_processing/markdown/services/
   pytest tests/unit/input_processing/docx/services/
   ```

#### Verification Steps for File Format Handlers
- [ ] Markdown handler correctly processes sample markdown files
   ```bash
   # Create a test file
   echo "# Test Markdown" > test.md
   
   # Test markdown processing
   python -c "from app.input_processing.markdown.services.markdown_service import process_markdown; print(process_markdown('test.md'))"
   ```
- [ ] DOCX handler correctly processes sample DOCX files
- [ ] Unit tests for both handlers pass in the new location
- [ ] Integration tests with the core input processing pass
- [ ] API endpoints correctly process files of each type
- [ ] No functionality loss compared to pre-migration handlers

3. **AI Core Services Migration**
   - Move tokenizer and core AI service to their new locations
   ```bash
   # Move tokenizer service
   cp <old_tokenizer_path> app/ai/core/services/tokenizer_core_service.py
   
   # Move AI core service
   cp <old_ai_service> app/ai/core/services/ai_core_service.py
   ```
   
   - Update imports and references
   ```python
   # Update tokenizer imports
   from app.ai.core.services.tokenizer_core_service import count_tokens
   
   # Update AI service imports
   from app.ai.core.services.ai_core_service import query_llm
   ```
   
   - Test AI services functionality
   ```bash
   pytest tests/unit/ai/core/services/
   ```

#### Verification Steps for AI Core Services
- [ ] Tokenizer service correctly counts tokens in sample texts
   ```bash
   # Test tokenizer
   python -c "from app.ai.core.services.tokenizer_core_service import count_tokens; print(count_tokens('This is a test'))"
   ```
- [ ] AI core service successfully communicates with LLM
   ```bash
   # Test with environment variables for credentials
   export OPENAI_API_KEY=test_key
   python -c "from app.ai.core.services.ai_core_service import query_llm; print(query_llm('Hello world', max_tokens=10))"
   ```
- [ ] Error handling scenarios work as expected
- [ ] Latency and performance metrics remain consistent
- [ ] Unit and integration tests pass for both services
- [ ] API endpoints using these services return expected responses

4. **Customer Intent Feature Migration**
   - Move models, router, and service to their new locations
   ```bash
   # Move customer intent model
   cp <old_model_path> app/ai/customer_intent/models/ai_customer_intent_model.py
   
   # Move router
   cp <old_router_path> app/ai/customer_intent/routers/ai_customer_intent_router.py
   
   # Move service
   cp <old_service_path> app/ai/customer_intent/services/ai_customer_intent_service.py
   ```
   
   - Update imports and fix any issues
   ```python
   # Update imports in router
   from app.input_processing.core.services.file_type_routing_logic_core_services import detect_file_type
   from app.ai.core.services.tokenizer_core_service import count_tokens
   from app.ai.core.services.ai_core_service import query_llm
   from app.ai.customer_intent.models.ai_customer_intent_model import CustomerIntentRequest, CustomerIntentResponse
   from app.ai.customer_intent.services.ai_customer_intent_service import structure_prompt
   ```
   
   - Test the complete customer intent feature
   ```bash
   pytest tests/unit/ai/customer_intent/
   pytest tests/integration/test_file_to_ai_flow.py
   ```

#### Verification Steps for Customer Intent Feature
- [ ] Model validation works for all request scenarios
   ```bash
   # Test model validation
   python -c "from app.ai.customer_intent.models.ai_customer_intent_model import CustomerIntentRequest; request = CustomerIntentRequest(file_content='test'); print(request)"
   ```
- [ ] Router correctly orchestrates the entire process flow
- [ ] Service properly structures prompts for the LLM
- [ ] End-to-end API tests pass for the customer intent endpoint
   ```bash
   # Test endpoint with curl
   curl -v -X POST -H "Content-Type: multipart/form-data" \
        -F "file=@sample.md" \
        http://localhost:8000/api/v1/generate/customer/intent
   ```
- [ ] Error scenarios are handled properly and return appropriate responses
- [ ] Response structures match pre-migration expectations
- [ ] Performance metrics remain within acceptable thresholds

### Phase 4: Test Structure Implementation (Week 3)

1. **Create the unit test directory structure** mirroring the application structure
   ```bash
   # Create test directories
   mkdir -p tests/unit/config
   mkdir -p tests/unit/input_processing/core/services
   mkdir -p tests/unit/input_processing/markdown/services
   mkdir -p tests/unit/input_processing/docx/services
   mkdir -p tests/unit/ai/core/services
   mkdir -p tests/unit/ai/customer_intent/{models,services,routers}/
   mkdir -p tests/integration
   mkdir -p tests/api/v1/generate
   
   # Create __init__.py files
   find tests -type d -exec touch {}/__init__.py \;
   ```

2. **Migrate existing tests** to the new structure
   ```bash
   # Example of moving a test file
   cp <old_test_path> tests/unit/input_processing/core/services/test_file_type_routing_logic_core_services.py
   
   # Update imports in test files
   sed -i 's/from old.path import/from app.input_processing.core.services import/g' tests/unit/input_processing/core/services/test_file_type_routing_logic_core_services.py
   ```

3. **Implement missing tests** based on the test-driven development plan
   ```python
   # Example of a new test
   # tests/unit/ai/core/services/test_tokenizer_core_service.py
   
   import pytest
   from app.ai.core.services.tokenizer_core_service import count_tokens
   
   def test_count_tokens_empty_string():
       assert count_tokens("") == 0
       
   def test_count_tokens_simple_text():
       assert count_tokens("Hello world") > 0
       
   def test_count_tokens_long_text():
       long_text = "This is a longer text " * 100
       assert count_tokens(long_text) > 100
   ```

4. **Create integration tests** for cross-feature workflows
   ```python
   # Example integration test
   # tests/integration/test_file_to_ai_flow.py
   
   import pytest
   from app.input_processing.markdown.services.markdown_service import process_markdown
   from app.input_processing.core.services.input_processing_core_service import sanitize_text
   from app.ai.core.services.tokenizer_core_service import count_tokens
   
   def test_markdown_to_tokens_flow():
       # Given a markdown file
       with open("test.md", "w") as f:
           f.write("# Test heading\n\nTest paragraph")
       
       # When processing through the pipeline
       raw_text = process_markdown("test.md")
       processed_text = sanitize_text(raw_text)
       token_count = count_tokens(processed_text)
       
       # Then the token count should be positive
       assert token_count > 0
       
       # And the processed text should contain the original content
       assert "Test heading" in processed_text
       assert "Test paragraph" in processed_text
   ```

5. **Implement API tests** for the customer intent endpoint
   ```python
   # Example API test
   # tests/api/v1/generate/test_customer_intent_api.py
   
   from fastapi.testclient import TestClient
   import pytest
   from app.main import app
   
   client = TestClient(app)
   
   def test_customer_intent_endpoint():
       # Given a markdown file
       with open("test.md", "w") as f:
           f.write("# Test document\n\nThis is a test.")
       
       # When calling the endpoint
       with open("test.md", "rb") as f:
           response = client.post(
               "/api/v1/generate/customer/intent",
               files={"file": ("test.md", f, "text/markdown")}
           )
       
       # Then the response should be successful
       assert response.status_code == 200
       
       # And contain the expected fields
       data = response.json()
       assert "processed_text" in data
       assert "token_count" in data
       assert "token_limit" in data
       assert "tokens_remaining" in data
   ```

#### Verification Steps for Phase 4
- [ ] Test directory structure mirrors application structure
- [ ] All existing tests have been migrated and pass
   ```bash
   pytest tests/unit/
   ```
- [ ] Test coverage metrics match or exceed pre-migration coverage
   ```bash
   pytest --cov=app --cov-report=xml:post_migration_coverage.xml
   
   # Compare coverage
   diff-cover baseline_coverage.xml post_migration_coverage.xml
   ```
- [ ] New integration tests verify cross-feature workflows
   ```bash
   pytest tests/integration/
   ```
- [ ] API tests confirm endpoint functionality
   ```bash
   pytest tests/api/
   ```
- [ ] CI pipeline successfully runs all tests
- [ ] Test reports are generated and reviewed
- [ ] Edge cases and error scenarios have dedicated tests

### Phase 5: Validation and Cleanup (Week 4)

1. **Run the complete test suite** to validate functionality
   ```bash
   pytest
   ```

2. **Perform end-to-end testing** with real API requests
   ```bash
   # Start the server
   python server.py &
   
   # Test with real files
   curl -v -X POST -H "Content-Type: multipart/form-data" \
        -F "file=@real_document.md" \
        http://localhost:8000/api/v1/generate/customer/intent
   ```

3. **Remove deprecated code paths** that were kept for backward compatibility
   ```bash
   # Update main.py to remove old imports
   sed -i '/# Fall back to old structure/d' app/main.py
   sed -i '/from old_location/d' app/main.py
   
   # Remove old files after confirming they're no longer needed
   git rm <old_file_paths>
   ```

4. **Update documentation** to reflect the new structure
   ```bash
   # Update README.md
   sed -i 's/old\/file\/structure/app\/input_processing\/core\/services/g' README.md
   
   # Update API documentation
   openapi-generator generate -i http://localhost:8000/openapi.json -g markdown -o api_docs/
   ```

5. **Create a migration guide** for developers
   ```markdown
   # Migration Guide
   
   ## File Structure Changes
   
   The codebase has been restructured from a technical layer-based organization to a feature-based organization.
   
   ### Old Structure:
   ```
   /models
   /services
   /routers
   ```
   
   ### New Structure:
   ```
   /app
     /input_processing
       /core
       /markdown
       /docx
     /ai
       /core
       /customer_intent
   ```
   
   ## Import Changes
   
   You'll need to update your imports to reflect the new structure:
   
   ### Old imports:
   ```python
   from models.customer_intent import CustomerIntent
   from services.file_processor import process_file
   ```
   
   ### New imports:
   ```python
   from app.ai.customer_intent.models.ai_customer_intent_model import CustomerIntent
   from app.input_processing.core.services.input_processing_core_service import process_file
   ```
   ```

#### Verification Steps for Phase 5
- [ ] Complete test suite passes with >95% success rate
- [ ] End-to-end tests with real-world examples are successful
- [ ] No references to deprecated code paths remain
   ```bash
   # Check for old imports
   grep -r "from old_location" app/
   ```
- [ ] Code linting shows no unused imports or dead code
   ```bash
   flake8 app/
   pylint app/
   ```
- [ ] Documentation accurately reflects the new structure
- [ ] API documentation is updated with current endpoints
- [ ] Migration guide is reviewed by team members
- [ ] Sample code snippets in documentation work with new structure

### Phase 6: Final Review and Merge (Week 4)

1. **Conduct a code review** of all changes
   ```bash
   # Create pull request
   gh pr create --title "Restructure codebase to feature-based organization" --body "This PR reorganizes the codebase from a technical layer-based structure to a feature-based structure."
   ```

2. **Check test coverage** to ensure adequate testing
   ```bash
   pytest --cov=app --cov-report term-missing
   ```

3. **Perform a final validation** of the application
   ```bash
   # Run full test suite
   pytest
   
   # Start server and make test request
   python server.py &
   
   curl -v -X POST -H "Content-Type: multipart/form-data" \
        -F "file=@validation_doc.md" \
        http://localhost:8000/api/v1/generate/customer/intent
   ```

4. **Merge the feature branch** into the main branch
   ```bash
   git checkout main
   git merge feature/restructure-codebase
   git push origin main
   ```

5. **Deploy and monitor** the application in production
   ```bash
   # Deploy (specific to your deployment process)
   ./deploy.sh
   
   # Monitor logs
   tail -f /var/log/app/application.log
   ```

#### Verification Steps for Phase 6
- [ ] Code review completed with all feedback addressed
- [ ] Test coverage meets target metrics (e.g., >90% for core functionality)
- [ ] Final validation passes all test cases
- [ ] Feature branch successfully merges into main branch
- [ ] Deployment to staging environment is successful
   ```bash
   # Test staging environment
   curl -v -X POST -H "Content-Type: multipart/form-data" \
        -F "file=@test.md" \
        https://staging.example.com/api/v1/generate/customer/intent
   ```
- [ ] Smoke tests pass in staging environment
- [ ] Production deployment is successful
- [ ] Monitoring shows no unexpected errors or performance issues
   ```bash
   # Check error rates
   grep ERROR /var/log/app/application.log | wc -l
   ```
- [ ] Key performance indicators remain within expected ranges

### Post-Implementation Verification

Two weeks after the migration is complete, conduct a final verification:

- [ ] No regression bugs related to the restructuring have been reported
   ```bash
   # Check issue tracker for regressions
   gh issue list --label regression
   ```
- [ ] Developer feedback on new structure is positive
- [ ] Documentation remains accurate and helpful
- [ ] Development velocity metrics show maintenance is more efficient
- [ ] New features are being developed according to the feature-based structure

### Success Criteria

The reorganization will be considered successful when:

1. All functionality works exactly as before
2. All tests pass with the new structure
3. The codebase follows the feature-based organization outlined in the plan
4. Documentation accurately reflects the new structure
5. Developers can easily understand and navigate the codebase

This phased approach minimizes risk by making incremental changes, testing at each step, and maintaining backward compatibility throughout the process. The feature-by-feature migration ensures that we can quickly identify and fix any issues that arise during the reorganization.