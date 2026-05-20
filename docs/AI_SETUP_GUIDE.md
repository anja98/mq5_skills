# 🤖 AI Platform Setup Guides

Detailed instructions for using this skill with different AI models.

---

## 🔷 Setup for Claude (Anthropic)

### Method 1: Via Claude.ai Skills (Recommended)
1. Log in to claude.ai
2. Go to Settings → Skills
3. Click "Add Skill"
4. Upload `SKILL.md` file
5. Name it: "MQL5 EA Expert"
6. Done! Claude will auto-use it when relevant

### Method 2: Via Conversation Context
1. Start new conversation
2. Upload `SKILL.md` file
3. Say: "Please use this skill to help me create MQL5 EAs"
4. Claude will reference it throughout the conversation

### Testing:
```
Ask: "Do you have the MQL5 EA Expert skill?"
Claude should confirm and list key features
```

---

## 🟢 Setup for ChatGPT (OpenAI)

### Method 1: Create Custom GPT (Best Experience)

**Step 1: Create GPT**
1. Go to ChatGPT → Explore GPTs
2. Click "Create a GPT"
3. Click "Create" tab

**Step 2: Configure**
```
Name: MQL5 EA Expert

Description: Expert MQL5 EA developer with survival-first approach. 
Creates professional Expert Advisors with advanced risk management, 
multi-timeframe analysis, and battle-tested strategies.

Instructions:
You are an expert MQL5 EA developer specializing in creating 
professional, production-ready Expert Advisors for MetaTrader 5. 

Your approach is survival-first: capital preservation is more 
important than maximum returns. Follow the comprehensive guidelines 
in your knowledge base (SKILL.md) for all EA development.

Key principles:
- Always prioritize risk management over profit maximization
- Include multiple safety layers (daily limits, drawdown protection)
- Use professional code structure with proper error handling
- Provide warnings for high-risk strategies
- Focus on creating EAs that can survive real market conditions

When creating an EA:
1. Read the relevant sections from SKILL.md
2. Follow the templates and best practices
3. Implement comprehensive risk management
4. Include proper documentation and comments
5. Warn about potential risks
```

**Step 3: Upload Knowledge**
1. Click "Knowledge" section
2. Upload `SKILL.md` file
3. Click "Save"

**Step 4: Configure Capabilities**
- ✅ Web Browsing (for research)
- ✅ Code Interpreter (for testing)
- ⬜ DALL-E (not needed)

**Step 5: Publish**
1. Click "Save" in top right
2. Choose "Only me" or "Anyone with link"
3. Done!

### Method 2: Custom Instructions (Quick Setup)

1. Settings → Personalization → Custom Instructions
2. In "How would you like ChatGPT to respond?", add:

```
When helping with MQL5 EA development:
- Follow survival-first philosophy (capital preservation > max profit)
- Always implement comprehensive risk management
- Include daily loss limits, drawdown protection, spread filters
- Use professional code structure with error handling
- Provide warnings for high-risk strategies (grid, martingale)
- Reference the MQL5 EA Expert skill guidelines
- Focus on creating robust, production-ready code

Key priorities:
1. Risk management over profit maximization
2. Robustness over complexity
3. Testing over deployment
4. Capital preservation over returns
```

3. When creating EA, start by saying:
   "I'm using the MQL5 EA Expert skill. Please follow its guidelines."

### Method 3: In-Chat Context

1. Start conversation with:
```
I have a comprehensive MQL5 EA development skill document. 
Please use it as your knowledge base for creating Expert Advisors.

[Upload SKILL.md file]

Follow the survival-first approach and professional practices 
outlined in this document.
```

---

## 🔴 Setup for Gemini (Google)

### Method 1: Upload to Conversation

1. Start new conversation in Gemini
2. Click the attachment icon (📎)
3. Upload `SKILL.md` file
4. Say:
```
I've uploaded a comprehensive MQL5 EA development skill document. 
Please use this as your knowledge base when helping me create 
Expert Advisors. Follow the survival-first approach and 
professional practices outlined in the document.
```

### Method 2: Google AI Studio

1. Go to ai.google.dev/aistudio
2. Create new prompt
3. In system instructions, add:

```
You are an expert MQL5 EA developer with a survival-first approach. 
You help users create professional Expert Advisors for MetaTrader 5 
that prioritize capital preservation over maximum returns.

Follow these principles:
- Risk management is paramount
- Multiple safety layers in every EA
- Professional code structure
- Comprehensive error handling
- Clear warnings for high-risk strategies

When creating EAs:
1. Follow the MQL5 EA Expert skill guidelines
2. Implement proper risk management
3. Use professional templates
4. Test thoroughly before deployment
5. Focus on survival over profit maximization
```

4. Upload `SKILL.md` to context
5. Save as custom model

### Method 3: Direct Context Injection

Each conversation, include this:
```
Context: I'm using the MQL5 EA Expert skill for EA development. 
Key principles: Survival-first, risk management focus, professional 
code structure, comprehensive testing.

[Paste relevant sections from SKILL.md when needed]
```

---

## 🟣 Setup for Microsoft Copilot

### In-Chat Setup:
1. Start conversation
2. Say:
```
I have a comprehensive MQL5 EA development framework. 
Please help me create Expert Advisors following these principles:

- Survival-first approach (capital preservation)
- Advanced risk management (Kelly Criterion, adaptive risk)
- Multi-timeframe analysis
- Professional code structure
- Comprehensive testing and validation

I'll provide specific guidelines from the framework as needed.
```

3. Reference sections from SKILL.md when needed

---

## 🟠 Setup for Open Source Models (LLaMA, Mistral, etc.)

### For Local Models:

**Method 1: System Prompt**
```python
system_prompt = """
You are an expert MQL5 EA developer specializing in creating 
professional Expert Advisors with a survival-first approach.

Follow these principles from the MQL5 EA Expert skill:
- Capital preservation over maximum profit
- Comprehensive risk management (daily limits, drawdown protection)
- Multi-timeframe analysis for confirmation
- Professional code structure with error handling
- Multiple safety layers
- Extensive testing before deployment

When creating EAs:
1. Implement proper risk management
2. Use professional templates
3. Include safety protections
4. Provide warnings for high-risk strategies
5. Focus on robustness over complexity

[Append relevant sections from SKILL.md]
"""
```

**Method 2: RAG (Retrieval Augmented Generation)**
1. Index `SKILL.md` in your vector database
2. Retrieve relevant sections based on query
3. Inject into context window
4. Query LLM with retrieved context

**Example with LangChain:**
```python
from langchain.document_loaders import TextLoader
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import FAISS
from langchain.chains import RetrievalQA

# Load skill document
loader = TextLoader("SKILL.md")
documents = loader.load()

# Create vector store
embeddings = HuggingFaceEmbeddings()
vectorstore = FAISS.from_documents(documents, embeddings)

# Create QA chain
qa_chain = RetrievalQA.from_chain_type(
    llm=your_llm,
    chain_type="stuff",
    retriever=vectorstore.as_retriever()
)

# Query
result = qa_chain("Create an EA with RSI strategy")
```

---

## ⚪ Setup for Any Other AI

### Universal Approach:

1. **Understand the AI's Context Method**
   - File upload?
   - System prompt?
   - Custom instructions?
   - In-chat context?

2. **Prepare the Content**
   - Full SKILL.md for comprehensive context
   - Or extract relevant sections for focused tasks

3. **Setup Instructions Template**
```
You are an expert MQL5 EA developer. Use the provided skill 
document to create professional Expert Advisors.

Key principles:
- Survival-first approach
- Comprehensive risk management
- Professional code structure
- Multiple safety protections
- Focus on capital preservation

[Upload or paste SKILL.md content]
```

4. **Test the Setup**
```
Test prompt: "Create a simple MA crossover EA with proper risk management"
Expected: EA with risk management, daily limits, error handling, etc.
```

---

## 📊 Comparison Table

| AI Platform | Best Method | Ease of Use | Persistence | Notes |
|-------------|-------------|-------------|-------------|-------|
| **Claude** | Skills Upload | ⭐⭐⭐⭐⭐ | Permanent | Auto-applies when relevant |
| **ChatGPT** | Custom GPT | ⭐⭐⭐⭐⭐ | Permanent | Can share with others |
| **Gemini** | File Upload | ⭐⭐⭐⭐ | Per-session | Re-upload each session |
| **Copilot** | In-Chat | ⭐⭐⭐ | Per-session | Manual context injection |
| **Open Source** | RAG/System Prompt | ⭐⭐⭐ | Custom | Requires technical setup |

---

## 🎯 Verification Checklist

After setup on any platform, verify with these tests:

### Test 1: Basic EA Creation
```
Prompt: "Create a simple MA crossover EA"
Expected: Should include risk management, error handling, safety checks
```

### Test 2: Advanced Features
```
Prompt: "Create an EA with multi-timeframe analysis"
Expected: Should implement MTF class from skill
```

### Test 3: Risk Management
```
Prompt: "Add money management to this EA"
Expected: Should implement CMoneyManagement class with proper features
```

### Test 4: Warning System
```
Prompt: "Create a martingale EA"
Expected: Should provide extensive warnings and safety limitations
```

### Test 5: Code Quality
```
Prompt: "Create any EA"
Expected: Professional structure, comments, error handling, organized inputs
```

---

## 💡 Pro Tips

### For Best Results:

1. **Be Specific**
   ```
   Bad:  "Make an EA"
   Good: "Create an RSI EA with multi-timeframe confirmation and Kelly Criterion money management"
   ```

2. **Reference Skill Sections**
   ```
   "Use the safe grid system from the skill documentation"
   "Follow the money management class template"
   ```

3. **Request Explanations**
   ```
   "Explain why you chose this risk management approach"
   "What safety features are included and why?"
   ```

4. **Iterate and Improve**
   ```
   "Add trailing stop following the skill guidelines"
   "Improve the risk management based on best practices"
   ```

---

## 🚀 Quick Start Commands

Copy-paste these to start:

### Claude:
```
Create a professional EA following the MQL5 EA Expert skill guidelines.
[Describe your strategy]
```

### ChatGPT:
```
Using the MQL5 EA Expert knowledge base, create a professional EA with:
[Describe your strategy]
Ensure comprehensive risk management and safety features.
```

### Gemini:
```
Based on the uploaded MQL5 EA Expert skill document, create a professional EA:
[Describe your strategy]
Follow survival-first principles and include all safety features.
```

---

## 📞 Support

**Issues with Setup?**
- Check if file uploaded correctly
- Verify file uploaded correctly (SKILL.md)
- Ensure AI can access uploaded content
- Try alternative setup method for your platform

**Not Getting Expected Output?**
- Explicitly mention the skill in your prompt
- Reference specific sections you want followed
- Ask AI to confirm it's using the skill guidelines
- Check if context window is sufficient

**For Platform-Specific Help:**
- Claude: Check claude.ai documentation
- ChatGPT: Check help.openai.com
- Gemini: Check ai.google.dev
- Others: Consult platform documentation

---

**Happy EA Development with Your Favorite AI! 🚀**
