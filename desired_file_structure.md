
# Migration Plan: Feature-Based File Structure Reorganization

Based on my review of the current codebase and your desired file structure, here's a comprehensive plan to migrate the application into a feature-based structure.

## Current vs. Desired Structure Analysis

The current structure is organized by technical layer:
- Models, services, and routers are in separate directories
- Features are mixed across these technical layers

The desired structure is organized by feature:
- Primary feature groups: `input_processing` and `ai`
- Subfeatures with their own models, services, and routers

## Migration Steps

### 1. Create New Directory Structure

```bash
mkdir -p app/input_processing/core/{models,routers,services}
mkdir -p app/input_processing/markdown/{models,routers,services}
mkdir -p app/input_processing/docx/{models,routers,services}
mkdir -p app/ai/core/{models,routers,services}
mkdir -p app/ai/customer_intent/{models,routers,services}
```

### 2. Move and Rename Input Processing Files

#### Document Parser
```bash
# Create core input processing service
touch app/input_processing/core/services/input_processing_core_service.py
# Extract core functionality from docx_parser.py to input_processing_core_service.py

# Move and rename docx files
cp app/models/document_models.py app/input_processing/docx/models/docx_model.py
cp app/routers/documents.py app/input_processing/docx/routers/docx_router.py
cp app/services/docx_parser.py app/input_processing/docx/services/docx_service.py
```

#### Markdown Processor
```bash
# Move and rename markdown files
cp app/models/markdown_models.py app/input_processing/markdown/models/markdown_model.py
cp app/routers/markdown.py app/input_processing/markdown/routers/markdown_router.py
cp app/services/markdown_service.py app/input_processing/markdown/services/markdown_service.py
```

### 3. Move and Rename AI Files

#### AI Core
```bash
# Move and rename AI files
cp app/models/ai_models.py app/ai/core/models/ai_core_model.py
cp app/routers/ai.py app/ai/core/routers/ai_core_router.py
cp app/services/openai_service.py app/ai/core/services/ai_core_service.py

# Move token service functionality to appropriate location
cp app/models/token_models.py app/ai/core/models/token_model.py
cp app/routers/tokens.py app/ai/core/routers/token_router.py  
cp app/services/token_service.py app/ai/core/services/token_service.py
```

#### Customer Intent
```bash
# Move and rename customer intent files
cp app/models/customer_intent_models.py app/ai/customer_intent/models/ai_customer_intent_model.py
cp app/routers/customer_intent.py app/ai/customer_intent/routers/ai_customer_intent_router.py
cp app/services/customer_intent_service.py app/ai/customer_intent/services/ai_customer_intent_service.py
```

### 4. Update Imports in All Files

```python
# For each file, update import paths to reflect new structure
# Example for app/ai/customer_intent/services/ai_customer_intent_service.py:
# Old: from app.services.openai_service import OpenAIService
# New: from app.ai.core.services.ai_core_service import OpenAIService
```

### 5. Update Main Application Entry Point

```python
# Update app/main.py to import from new locations and include new routers
# Example:
# Old: from app.routers import documents, ai, tokens, customer_intent, markdown
# New: 
# from app.input_processing.docx.routers import docx_router
# from app.input_processing.markdown.routers import markdown_router
# from app.ai.core.routers import ai_core_router, token_router
# from app.ai.customer_intent.routers import ai_customer_intent_router
```

### 6. Add Required `__init__.py` Files

```bash
# Create __init__.py files in all directories to ensure proper package imports
touch app/input_processing/__init__.py
touch app/input_processing/core/__init__.py
touch app/input_processing/markdown/__init__.py
touch app/input_processing/docx/__init__.py
touch app/ai/__init__.py
touch app/ai/core/__init__.py
touch app/ai/customer_intent/__init__.py
```

### 7. Refactor Core Functionality

1. Extract common input processing logic from `docx_parser.py` and `markdown_service.py` into `input_processing_core_service.py`
2. Modify `docx_service.py` and `markdown_service.py` to use the core service
3. Extract common AI functionality from `openai_service.py` into `ai_core_service.py`
4. Modify `ai_customer_intent_service.py` to use the core AI service

### 8. Test Migration

1. Implement the changes incrementally
2. Run tests after each major step
3. Validate API endpoints still work correctly
4. Check for any regressions in functionality

## Implementation Plan Sequence

1. Create the new directory structure
2. Add required `__init__.py` files
3. Create core service files with shared functionality
4. Copy and rename existing files to new locations
5. Update imports in all files
6. Update the main application file
7. Run tests to verify functionality
8. Remove old files after confirming everything works

This migration will result in a cleaner, feature-based architecture that improves maintainability and provides clearer boundaries between different parts of the application.



```
/
├──app/
│   ├──config/
│   │       └── settings.py                                 # Application configuration
│   ├──input_processing/
│   │   ├──core/
│   │   │   ├──models/
│   │   │   │   └──__init__.py
│   │   │   │
│   │   │   ├──routers/
│   │   │   │   └──__init__.py
│   │   │   │
│   │   │   ├──services/
│   │   │   │   ├──__init__.py
│   │   │   │   └──input_processing_core_service.py         # Provides core functionality for escaping special and control characters from inputs of any supported file type
│   │   │   └──__init__.py
│   │   ├──markdown/
│   │   │   ├──models/
│   │   │   │   ├──__init__.py
│   │   │   │   └──markdown_model.py                        # Provides the pydantic model for the markdown input functionality
│   │   │   ├──routers/
│   │   │   │   └──__init__.py
│   │   │   │
│   │   │   ├──services/
│   │   │   │   ├──__init__.py
│   │   │   │   └──markdown_service.py                      # Provides the markdown input functionality to prepare markdown inputs for processing by core processing functionality
│   │   │   └──__init__.py
│   │   └──docx/
│   │       ├──models/
│   │       │   ├──__init__.py
│   │       │   └──docx_model.py                            # Provides the pydantic model for the docx input functionality
│   │       ├──routers/
│   │       │   └──__init__.py
│   │       │
│   │       ├──services/
│   │       │   ├──__init__.py
│   │       │   └──docx_service.py                          # Provides the docx input functionality to prepare docx inputs for processing by core processing functionality
│   │       └──__init__.py
│   ├──ai/
│   │   ├──core/
│   │   │   ├──models/
│   │   │   │   ├──__init__.py
│   │   │   │   ├──ai_core_model.py                         # Provides the core pydantic model for querying the ai (LLM) operating behind the scenes
│   │   │   │   └──tokenizer_core_model.py 
│   │   │   ├──routers/
│   │   │   │   └───__init__.py
│   │   │   │
│   │   │   ├──services/
│   │   │   │   ├──__init__.py
│   │   │   │   ├──ai_core_service.py                       # Provides the core ai service for query the ai (LLM) operating behind the scenes
│   │   │   │   └──tokenizer_core_service.py 
│   │   │   └──__init__.py
│   │   └──customer_intent/
│   │       ├──models/
│   │       │   ├──__init__.py
│   │       │   └──ai_customer_intent_model.py              # Provides the pydantic model for the ai customer intent which will be generated by using the core ai service
│   │       ├──routers/
│   │       │   ├──__init__.py
│   │       │   └──ai_customer_intent_router.py             # Provides the /api/v1/create/customer/intent endpoint which will use the input processing functionality and then the ai core services functionality to create a customer intent from input
│   │       ├──services/
│   │       │   ├──__init__.py
│   │       │   └──ai_customer_intent_service.py            # Provides the customer intent service for the /api/v1/create/customer/intent endpoint
│   │       └──__init__.py
│   ├──main.py                                              # Entrypoint into application
│   └──__init__.py
├──tests/
│   ├──__init__.py
│   └──conftest.py
├──server.py                                                # Runs server for application
├──pytest.ini
├──requirements.txt
├──.env-example
├──.env
├──product_spec.md
└──README.md
```