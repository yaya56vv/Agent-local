# Multi-Agent Router Documentation

## Overview

The Multi-Agent Router is an intelligent routing system that manages automatic PRE/POST processing with a local agent and routes requests to specialized agents based on task requirements.

## Architecture

### Three-Stage Processing Pipeline

```
USER MESSAGE
     ↓
[1. PRE-PROCESS] ← Local Agent (Fast)
     ↓
[2. ROUTE] → Select Best Agent
     ↓
[3. EXECUTE] → Specialized Agent
     ↓
[4. POST-PROCESS] ← Local Agent (Fast)
     ↓
FINAL OUTPUT
```

## Components

### 1. AgentRegistry

Manages all available agents and their capabilities.

**Available Agents:**
- **local**: Fast local processing (summary, intention, clean, fast_analysis, postprocess, continuity, shorten, clarify)
- **orchestrator**: Main orchestration and general tasks
- **code**: Code-related tasks (code, bugfix, code_analysis, refactor, debug, optimize)
- **vision**: Visual analysis (image_analysis, screenshot, visual_inspection)
- **analyse**: Deep analysis and complex reasoning

**Key Methods:**
```python
# Get all agents
agents = AgentRegistry.get_agents()

# Find agent by capability
agent = AgentRegistry.get_agent_by_capability("code")
```

### 2. ModelRegistry

Manages model configurations for all agents.

**Available Models:**
- **reasoning**: General reasoning and planning
- **coding**: Code generation and analysis
- **vision**: Visual analysis
- **local**: Fast local processing (Ollama/LM Studio)

**Key Methods:**
```python
# Get all models
models = ModelRegistry.get_models()

# Get model for specific agent
model_config = ModelRegistry.get_model_for_agent("code")
```

### 3. MultiAgentRouter

Main router class that orchestrates the entire pipeline.

## Usage

### Basic Usage

```python
from backend.orchestrator.router import MultiAgentRouter

# Initialize router
router = MultiAgentRouter()

# Process a message through complete pipeline
result = await router.process_message("Fix this bug in my code")

# Access results
print(f"Agent used: {result['agent_used']}")
print(f"Model used: {result['model_used']}")
print(f"Final output: {result['final_output']}")
```

### Step-by-Step Usage

```python
# Step 1: PRE-PROCESS
pre_result = await router.pre_process(message)
# Returns: intention, cleaned_message, summary, tasks

# Step 2: ROUTE
routing = await router.route(message, pre_result)
# Returns: selected_agent, model_config, routing_reason, confidence

# Step 3: EXECUTE (handled by orchestrator)
# ... execution logic ...

# Step 4: POST-PROCESS
post_result = await router.post_process(execution_result, message)
# Returns: final_output, tasks applied
```

## PRE-Processing

The local agent performs fast initial processing:

### Tasks Performed:
- **intention**: Detect user intention (code/vision/analysis/general)
- **clean**: Clean and normalize the message
- **summary**: Create brief summary
- **fast_analysis**: Quick initial analysis

### Example:
```python
pre_result = await router.pre_process(
    "Can you help me fix this bug in my Python code?"
)

# Result:
{
    "status": "success",
    "original_message": "Can you help me fix this bug...",
    "processed_message": "Fix bug in Python code",
    "intention": "code",
    "tasks": ["intention", "clean"],
    "agent_used": "local",
    "model_used": "llama3.2"
}
```

## Routing Logic

The router selects the best agent based on:

1. **Pre-processed intention** (if available)
2. **Message content analysis**
3. **Keyword detection**
4. **Agent capabilities**

### Routing Rules:

| Condition | Selected Agent | Reason |
|-----------|---------------|---------|
| Image/screenshot keywords | vision | Visual analysis required |
| Code/bug/debug keywords | code | Code-related task |
| Complex analysis keywords | analyse | Deep reasoning needed |
| Default | orchestrator | General task handling |

### Example:
```python
routing = await router.route(
    message="Analyze this screenshot",
    pre_result={"intention": "vision"}
)

# Result:
{
    "status": "success",
    "selected_agent": "vision",
    "model_config": {
        "model": "google/gemini-2.0-flash-001",
        "provider": "openrouter"
    },
    "routing_reason": "Visual analysis required",
    "confidence": 0.9
}
```

## POST-Processing

The local agent refines and formats the final output:

### Tasks Performed:
- **postprocess**: Basic formatting and cleanup
- **shorten**: Reduce verbose output
- **clarify**: Improve clarity for errors/warnings
- **continuity**: Ensure response continuity

### Example:
```python
post_result = await router.post_process(
    result={"status": "success", "output": "Code fixed..."},
    original_message="Fix my code"
)

# Result:
{
    "status": "success",
    "original_output": {...},
    "final_output": "Your code has been fixed successfully...",
    "tasks": ["postprocess", "clarify"],
    "agent_used": "local",
    "model_used": "llama3.2"
}
```

## Configuration

All configuration comes from `backend/config/settings.py`:

```python
# Agent Models
ORCHESTRATOR_MODEL = "openrouter/google/gemini-2.0-flash-001"
CODE_AGENT_MODEL = "openrouter/google/gemini-2.0-flash-001"
VISION_AGENT_MODEL = "openrouter/google/gemini-2.0-flash-001"
LOCAL_AGENT_MODEL = "ollama/llama3.2"
ANALYSE_AGENT_MODEL = None  # Falls back to ORCHESTRATOR_MODEL

# Local LLM
LOCAL_LLM_BASE_URL = "http://127.0.0.1:11434"
LOCAL_LLM_MODEL = "llama3.2"
LOCAL_LLM_PROVIDER = "ollama"  # or "lm_studio"
```

## Integration with Orchestrator

The router can be integrated into the orchestrator:

```python
from backend.orchestrator.orchestrator import Orchestrator
from backend.orchestrator.router import MultiAgentRouter

class Orchestrator:
    def __init__(self):
        # ... existing init ...
        self.router = MultiAgentRouter(orchestrator=self)
    
    async def run(self, prompt: str, **kwargs):
        # Use router for intelligent routing
        routing_result = await self.router.process_message(prompt)
        
        # Execute based on routing decision
        agent = routing_result['agent_used']
        # ... execute with selected agent ...
```

## Error Handling

The router includes comprehensive error handling:

```python
# PRE-processing error
{
    "status": "error",
    "error": "Connection timeout",
    "original_message": "...",
    "processed_message": "..."  # Falls back to original
}

# Routing error (fallback to orchestrator)
{
    "status": "fallback",
    "selected_agent": "orchestrator",
    "routing_reason": "Error in routing: ...",
    "confidence": 0.5
}

# POST-processing error
{
    "status": "error",
    "error": "...",
    "final_output": {...}  # Returns original result
}
```

## Testing

Run the comprehensive test suite:

```bash
python test_router.py
```

Tests include:
1. Agent Registry functionality
2. Model Registry functionality
3. PRE-processing
4. Routing logic
5. POST-processing
6. Complete pipeline

## Performance Considerations

### Local Agent Benefits:
- **Fast**: Local LLM for quick pre/post processing
- **Efficient**: Reduces load on expensive cloud models
- **Privacy**: Sensitive pre-processing stays local

### Optimization Tips:
1. Use local agent for all pre/post tasks
2. Cache routing decisions for similar messages
3. Batch process multiple messages when possible
4. Monitor agent performance and adjust routing rules

## Future Enhancements

1. **Dynamic Agent Registration**: Allow runtime agent addition
2. **Learning Routing**: ML-based routing decisions
3. **Parallel Processing**: Execute multiple agents simultaneously
4. **Agent Chaining**: Complex multi-agent workflows
5. **Performance Metrics**: Track agent performance and costs

## Troubleshooting

### Common Issues:

**Issue**: Local agent not responding
- **Solution**: Check LOCAL_LLM_BASE_URL and ensure Ollama/LM Studio is running

**Issue**: Wrong agent selected
- **Solution**: Review routing rules and adjust keyword detection

**Issue**: POST-processing too slow
- **Solution**: Reduce max_tokens or disable unnecessary post-tasks

## API Reference

### MultiAgentRouter

#### `__init__(orchestrator=None)`
Initialize the router with optional orchestrator instance.

#### `async pre_process(message: str, context: Optional[Dict] = None) -> Dict`
Perform PRE-processing on user message.

#### `async route(message: str, pre_result: Optional[Dict] = None) -> Dict`
Route message to appropriate agent.

#### `async post_process(result: Dict, original_message: str) -> Dict`
Perform POST-processing on agent result.

#### `async process_message(message: str, context: Optional[Dict] = None) -> Dict`
Complete pipeline: PRE -> ROUTE -> EXECUTE -> POST.

### AgentRegistry

#### `static get_agents() -> Dict[str, Dict]`
Get all available agents and their configurations.

#### `static get_agent_by_capability(capability: str) -> Optional[str]`
Find best agent for a given capability.

### ModelRegistry

#### `static get_models() -> Dict[str, Dict]`
Get all available models and their configurations.

#### `static get_model_for_agent(agent_name: str) -> Optional[Dict]`
Get model configuration for specific agent.

## License

Part of the Agent Local project.