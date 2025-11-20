# Examples

Real-world examples and use cases for StreamShape.

## Table of Contents

1. [Content Generation](#content-generation)
2. [Data Extraction](#data-extraction)
3. [Code Generation](#code-generation)
4. [Customer Support](#customer-support)
5. [Data Analysis](#data-analysis)
6. [Integration Examples](#integration-examples)

## Content Generation

### Blog Post Generator

```python
from streamshape import OpenAI
from pydantic import BaseModel
from typing import List

class BlogPost(BaseModel):
    title: str
    introduction: str
    sections: List[str]
    conclusion: str
    tags: List[str]

client = OpenAI(api_key="...")

result = client.structured_output(
    model="gpt-4",
    system_prompt="You are a professional content writer.",
    user_prompt="Create 3 blog posts about sustainable living",
    output_schema=BlogPost,
    temperature=0.8
)

for post in result["data"]:
    print(f"\n# {post.title}\n")
    print(post.introduction)
    for i, section in enumerate(post.sections, 1):
        print(f"\n## Section {i}\n{section}")
    print(f"\n{post.conclusion}")
    print(f"\nTags: {', '.join(post.tags)}")
```

### Social Media Content

```python
from pydantic import BaseModel

class SocialPost(BaseModel):
    platform: str
    content: str
    hashtags: List[str]
    best_time_to_post: str

def generate_social_content(topic, num_posts=5):
    for post in client.structured_streaming_output(
        model="gpt-4",
        system_prompt="You are a social media manager.",
        user_prompt=f"Create {num_posts} social media posts about {topic}",
        output_schema=SocialPost
    ):
        print(f"\n📱 {post.platform}")
        print(f"   {post.content}")
        print(f"   {' '.join(post.hashtags)}")
        print(f"   ⏰ Best time: {post.best_time_to_post}")

generate_social_content("AI in healthcare")
```

## Data Extraction

### Resume Parser

```python
from pydantic import BaseModel
from typing import List, Optional

class Education(BaseModel):
    degree: str
    institution: str
    year: int

class Experience(BaseModel):
    title: str
    company: str
    duration: str
    responsibilities: List[str]

class Resume(BaseModel):
    name: str
    email: str
    phone: Optional[str]
    education: List[Education]
    experience: List[Experience]
    skills: List[str]

def parse_resume(resume_text):
    result = client.structured_output(
        model="gpt-4",
        system_prompt="Extract structured information from resumes.",
        user_prompt=f"Parse this resume:\n\n{resume_text}",
        output_schema=Resume
    )
    return result["data"][0]

resume_text = """
John Doe
john@email.com | (555) 123-4567

Education:
- BS Computer Science, MIT, 2020
- MS AI, Stanford, 2022

Experience:
Software Engineer at Google (2022-2024)
- Built ML pipelines
- Improved system performance by 40%

Skills: Python, TensorFlow, AWS, Docker
"""

resume = parse_resume(resume_text)
print(f"Name: {resume.name}")
print(f"Email: {resume.email}")
print(f"Skills: {', '.join(resume.skills)}")
```

### Invoice Extraction

```python
class LineItem(BaseModel):
    description: str
    quantity: int
    unit_price: float
    total: float

class Invoice(BaseModel):
    invoice_number: str
    date: str
    vendor: str
    items: List[LineItem]
    subtotal: float
    tax: float
    total: float

def extract_invoice_data(invoice_text):
    result = client.structured_output(
        model="gpt-4",
        system_prompt="Extract invoice data accurately.",
        user_prompt=f"Extract data from this invoice:\n\n{invoice_text}",
        output_schema=Invoice,
        temperature=0.1  # Low temperature for accuracy
    )
    return result["data"][0]
```

## Code Generation

### API Endpoint Generator

```python
class APIEndpoint(BaseModel):
    method: str
    path: str
    description: str
    parameters: List[str]
    response_schema: str
    example_code: str

def generate_api_endpoints(description):
    for endpoint in client.structured_streaming_output(
        model="gpt-4",
        system_prompt="You are an API designer. Generate RESTful endpoints.",
        user_prompt=f"Design API endpoints for: {description}",
        output_schema=APIEndpoint
    ):
        print(f"\n{endpoint.method} {endpoint.path}")
        print(f"Description: {endpoint.description}")
        print(f"Parameters: {', '.join(endpoint.parameters)}")
        print(f"\nExample:\n{endpoint.example_code}")

generate_api_endpoints("a task management system")
```

### SQL Query Generator

```python
def generate_sql_query(natural_language_query, schema_description):
    result = client.generate(
        model="gpt-4",
        system_prompt=f"""You are a SQL expert. Generate SQL queries.
        
Database schema:
{schema_description}

Return only the SQL query, no explanations.""",
        user_prompt=natural_language_query,
        temperature=0.1
    )
    return result["data"]

schema = """
Tables:
- users (id, name, email, created_at)
- orders (id, user_id, total, status, created_at)
- products (id, name, price, category)
"""

query = generate_sql_query(
    "Show me the top 10 customers by total order value",
    schema
)
print(query)
```

## Customer Support

### Ticket Classifier

```python
class SupportTicket(BaseModel):
    category: str  # technical, billing, general
    priority: str  # low, medium, high, urgent
    sentiment: str  # positive, neutral, negative
    suggested_response: str
    requires_human: bool

def classify_ticket(ticket_text):
    result = client.structured_output(
        model="gpt-4",
        system_prompt="You are a customer support AI. Classify and triage tickets.",
        user_prompt=f"Analyze this support ticket:\n\n{ticket_text}",
        output_schema=SupportTicket
    )
    return result["data"][0]

ticket = classify_ticket("""
I've been trying to log in for 2 hours and keep getting error 500.
This is urgent as I have a presentation in 30 minutes!
""")

print(f"Category: {ticket.category}")
print(f"Priority: {ticket.priority}")
print(f"Sentiment: {ticket.sentiment}")
print(f"Needs human: {ticket.requires_human}")
print(f"\nSuggested response:\n{ticket.suggested_response}")
```

### Chatbot with Context

```python
class ChatMessage:
    def __init__(self):
        self.history = []
    
    def send(self, user_message):
        # Build context
        context = "\n".join([
            f"User: {msg['user']}\nBot: {msg['bot']}"
            for msg in self.history[-5:]  # Last 5 messages
        ])
        
        full_prompt = f"{context}\nUser: {user_message}" if context else user_message
        
        response = ""
        print("Bot: ", end="", flush=True)
        
        for chunk in client.stream(
            model="gpt-4",
            system_prompt="You are a helpful customer support agent.",
            user_prompt=full_prompt,
            temperature=0.7
        ):
            response += chunk["data"]
            print(chunk["data"], end="", flush=True)
        
        print()
        
        self.history.append({"user": user_message, "bot": response})
        return response

# Usage
chat = ChatMessage()
chat.send("I need help with my order")
chat.send("Order number is #12345")
chat.send("When will it arrive?")
```

## Data Analysis

### Survey Analysis

```python
class SurveyInsight(BaseModel):
    theme: str
    sentiment: str
    frequency: str
    key_quotes: List[str]
    recommendation: str

def analyze_survey_responses(responses):
    result = client.structured_output(
        model="gpt-4",
        system_prompt="Analyze survey responses and extract insights.",
        user_prompt=f"Analyze these survey responses:\n\n{responses}",
        output_schema=SurveyInsight
    )
    
    for insight in result["data"]:
        print(f"\n📊 Theme: {insight.theme}")
        print(f"   Sentiment: {insight.sentiment}")
        print(f"   Frequency: {insight.frequency}")
        print(f"   Quotes: {', '.join(insight.key_quotes[:2])}")
        print(f"   💡 Recommendation: {insight.recommendation}")
```

### Report Generator

```python
def generate_report(data, report_type="summary"):
    print("Generating report...")
    
    report = ""
    for chunk in client.stream(
        model="gpt-4",
        system_prompt=f"You are a data analyst. Generate a {report_type} report.",
        user_prompt=f"Analyze this data and create a report:\n\n{data}",
        temperature=0.5
    ):
        report += chunk["data"]
        print(chunk["data"], end="", flush=True)
    
    return report

sales_data = """
Q1 2024 Sales:
- Product A: $150,000 (↑ 20%)
- Product B: $80,000 (↓ 5%)
- Product C: $120,000 (↑ 35%)
"""

report = generate_report(sales_data, "executive summary")
```

## Integration Examples

### Slack Bot

```python
from slack_sdk import WebClient
from slack_sdk.socket_mode import SocketModeClient

def handle_message(client_slack, event):
    user_message = event["text"]
    channel = event["channel"]
    
    # Generate response
    result = client.generate(
        model="gpt-4",
        system_prompt="You are a helpful Slack bot.",
        user_prompt=user_message
    )
    
    # Send to Slack
    client_slack.chat_postMessage(
        channel=channel,
        text=result["data"]
    )

# Initialize Slack client
slack_client = WebClient(token="xoxb-...")
socket_client = SocketModeClient(
    app_token="xapp-...",
    web_client=slack_client
)

# Register handler
socket_client.socket_mode_request_listeners.append(handle_message)
socket_client.connect()
```

### Discord Bot

```python
import discord

class LLMBot(discord.Client):
    async def on_message(self, message):
        if message.author == self.user:
            return
        
        if message.content.startswith('!ask'):
            question = message.content[5:]
            
            # Stream response
            response = ""
            async with message.channel.typing():
                for chunk in client.stream(
                    model="gpt-4",
                    system_prompt="You are a helpful Discord bot.",
                    user_prompt=question
                ):
                    response += chunk["data"]
            
            await message.channel.send(response)

bot = LLMBot()
bot.run("your-discord-token")
```

### FastAPI Integration

```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()

class Query(BaseModel):
    prompt: str
    temperature: float = 0.7

class Response(BaseModel):
    text: str

@app.post("/generate", response_model=Response)
async def generate_text(query: Query):
    try:
        response = client.generate(
            model="gpt-4",
            system_prompt="You are a helpful assistant.",
            user_prompt=query.prompt,
            temperature=query.temperature
        )
        return Response(text=response["data"])
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Run with: uvicorn main:app --reload
```

### Streamlit App

```python
import streamlit as st

st.title("AI Content Generator")

content_type = st.selectbox(
    "Content Type",
    ["Blog Post", "Email", "Social Media", "Code"]
)

prompt = st.text_area("Describe what you want to generate:")

if st.button("Generate"):
    with st.spinner("Generating..."):
        response = client.generate(
            model="gpt-4",
            system_prompt=f"You are a {content_type.lower()} writer.",
            user_prompt=prompt,
            temperature=0.8
        )
        st.write(response["data"])

# Run with: streamlit run app.py
```

## More Examples

See the `/examples` directory in the repository for more complete examples:

- E-commerce product description generator
- Legal document analyzer
- Medical report summarizer
- Code review assistant
- Language translation service
- Content moderation system

