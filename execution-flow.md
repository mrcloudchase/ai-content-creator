app/main.py # Entry point to application
app/ai/core/customer_intent/routers/ai_customer_intent_router.py # /api/v1/customer-intent
app/

# API -> File -> Code Execution flow

/
├── api/v1/customer-intent (API endpoint) - 0
│   ├── app/main.py (file) - 1
│   │   └── customer_intent_router (code) - 2
│   ├── app/ai/core/routers/ai_customer_intent_router.py (file) - 3
            └── router (code) - 4
                └── router.post (code) - 5
                    └── generate_customer_intent (code) - 6
                        └── extract_file_content (code) - 7
                            └── file_handler_routing_service.validate_file_type (code) - 8
                            └── router.post
                            └── router.post
│   ├── app/input_processing/core/services/file_handler_routing_logic_service.py (file)
            └── validate_file_type (code) - 9
                └── get_file_type (code) - 10
                    └── get_file_extension (code) - 11
                        └── extract_file_content (code) - 12
│   ├── app/ai/input_processing/{markdown,docx,txt}/services/{markdown,docx,txt}_service.py (file) - 13
            └── router (code) - 14
                └── router.post (code) - 15
                    └── generate_customer_intent (code) - 16
                        └── extract_file_content (code) - 17
                            └── file_handler_routing_service.validate_file_type (code) - 18
                            └── router.post
                            └── router.post

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
