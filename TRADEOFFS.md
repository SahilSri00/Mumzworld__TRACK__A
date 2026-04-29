# Tradeoffs

## Problem Selection

### Why "Mom's Message → Structured Shopping List"

This problem was chosen because it sits at the intersection of **real business value** and **rich AI engineering**:

1. **High leverage for Mumzworld**: Busy moms are the core customer. They think in natural language ("need diapers for Layla, size 3"), not in search queries. Bridging that gap directly increases conversion.
2. **Non-trivial AI**: Requires entity extraction, classification, structured output generation, multilingual support, calendar reasoning, and uncertainty handling — not just a single prompt wrapper.
3. **Measurable**: Structured output means clear eval criteria — did it extract the right items, categories, and dates?
4. **Bilingual by nature**: Mumzworld's customers switch between English and Arabic (and mix them). This is where AI adds value that a simple form cannot.

### What I Rejected

| Option | Why Not |
|--------|---------|
| Product image → PDP content | Requires real product images; quality evaluation is subjective; harder to build a rigorous eval suite in 5 hours |
| Gift finder chatbot | Too close to a thin wrapper around an LLM; less structured output rigor |
| Duplicate product detection | Needs real catalog data and embedding infrastructure; hard to mock convincingly |
| Pediatric symptom triage | Medical domain liability; evaluating medical advice accuracy is beyond scope |
| Return reason classifier | Strong option, but felt more like a standard NLP classification task — less creative |

## Architecture Choices

### Why FastAPI + Vanilla Frontend (not Next.js, Streamlit, etc.)

- **FastAPI**: Async Python, built-in OpenAPI docs, native Pydantic integration for schema validation. The API can be tested independently via curl or Swagger.
- **Vanilla HTML/CSS/JS**: Zero build step. Clone → open browser. No npm, no webpack, no framework lock-in. The brief says "sets up and runs in under 5 minutes" — this guarantees it.
- **No Streamlit**: While faster to prototype, Streamlit hides the API layer and makes evaluation harder. A proper API + frontend separation shows engineering maturity.

### Why Groq API + Llama 3.3 70B

- **Blazing fast**: Groq's LPU hardware generates tokens at ~800 tok/s — the fastest inference available. Responses feel instant.
- **Free tier**: Generous free tier with 100K tokens/day — no credit card required.
- **OpenAI-compatible**: Uses the standard OpenAI SDK, so the system is portable. We can swap to OpenAI, Anthropic, or local vLLM without changing the parser.
- **JSON mode**: Native `response_format: json_object` support ensures the model always returns valid JSON.
- **Fallback**: If the 70B model is rate-limited, we fall back to `llama-3.1-8b-instant` (also free, also fast).

### Why Pydantic for Validation (not just JSON.parse)

LLMs are unreliable JSON generators. Pydantic v2 gives us:
- Type checking (is `confidence` actually a float between 0 and 1?)
- Enum validation (is `category` one of our defined categories?)
- Required field enforcement (no silent empty strings)
- Clear error messages when validation fails

When the LLM produces malformed output, the user gets an explicit error — not silently wrong data.

## Uncertainty Handling

This was designed as a first-class feature, not an afterthought:

1. **Confidence scores**: Every extracted item and event gets a 0.0–1.0 confidence score from the LLM.
2. **Threshold at 0.6**: Items below this get an `uncertainty_reason` explaining what's unclear.
3. **Out-of-scope detection**: Non-shopping messages (recipes, politics, gibberish) are caught and politely refused — the system returns empty lists with an explanation.
4. **Grounding rule**: The system prompt explicitly forbids inventing products, brands, or prices not mentioned in the input.
5. **Visual indicators**: The UI shows confidence badges (green/yellow/red) and uncertainty warnings so the mom knows which items to double-check.

## What I Cut

- **Voice-to-text via Whisper API**: Used browser's Web Speech API instead (free, no API key, works client-side). Trade-off: Chrome/Edge only for voice.
- **Product search integration**: Would have linked items directly to Mumzworld search results, but scraping is forbidden by the brief.
- **User accounts / history**: A real product would save past lists. Cut for scope.
- **Fine-tuning**: Would improve Arabic quality and category accuracy. Requires more data and time than available.

## What I Would Build Next

1. **Mumzworld catalog RAG**: Embed the product catalog and match extracted items to real products with prices and availability.
2. **Conversation memory**: Remember past purchases ("you bought size 3 last month — has Layla grown?").
3. **WhatsApp integration**: Most GCC moms use WhatsApp. A bot that reads voice notes and returns a shopping cart link would be the real product.
4. **A/B evaluation**: Compare Gemma 3 vs. Claude vs. GPT-4o on Arabic output quality with native speaker ratings.
5. **Fine-tuning on real data**: Train on actual customer messages (with PII removed) to improve extraction accuracy.
