# Working with Prompt Templates for Chat Model Invocations

## Overview

This guide provides comprehensive information on working with prompt templates to provide background information to chat model invocations using LangChain. Prompt templates are essential for creating structured, reusable prompts that can be dynamically populated with context and variables.

## Table of Contents

1. [Introduction to Prompt Templates](#introduction-to-prompt-templates)
2. [Basic Prompt Template Usage](#basic-prompt-template-usage)
3. [Chat Prompt Templates](#chat-prompt-templates)
4. [System Messages and Background Information](#system-messages-and-background-information)
5. [Variable Substitution](#variable-substitution)
6. [Advanced Template Features](#advanced-template-features)
7. [Best Practices](#best-practices)
8. [Examples](#examples)

## Introduction to Prompt Templates

Prompt templates are structured formats for creating prompts that can be dynamically populated with variables. They provide a way to:
- Maintain consistent prompt structure
- Reuse prompts across different contexts
- Dynamically inject background information
- Create more maintainable and testable code

## Basic Prompt Template Usage

### Creating a Simple Prompt Template

```python
from langchain.prompts import PromptTemplate

# Basic prompt template
template = "You are a helpful assistant. Answer the following question: {question}"
prompt = PromptTemplate.from_template(template)

# Using the template
formatted_prompt = prompt.format(question="What is the capital of France?")
```

### Template with Multiple Variables

```python
template = """
You are an expert in {domain}.
Context: {context}
Question: {question}

Please provide a detailed answer based on the context provided.
"""

prompt = PromptTemplate(
    input_variables=["domain", "context", "question"],
    template=template
)
```

## Chat Prompt Templates

For chat models, you'll typically use `ChatPromptTemplate` which allows you to structure prompts with different message types (system, human, assistant).

### Basic Chat Prompt Template

```python
from langchain.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate

# Create message templates
system_template = "You are a helpful assistant with expertise in {domain}."
system_message_prompt = SystemMessagePromptTemplate.from_template(system_template)

human_template = "{question}"
human_message_prompt = HumanMessagePromptTemplate.from_template(human_template)

# Combine into chat prompt template
chat_prompt = ChatPromptTemplate.from_messages([
    system_message_prompt,
    human_message_prompt
])
```

## System Messages and Background Information

System messages are crucial for providing background information and context to chat models. They set the tone, expertise level, and constraints for the conversation.

### Providing Background Information

```python
system_template = """
You are an expert {role} with the following background:
- {background_info}
- {expertise_areas}
- {constraints}

Your task is to {task_description}.
"""

system_message_prompt = SystemMessagePromptTemplate.from_template(system_template)
```

### Dynamic Background Information

```python
# Template with dynamic background
system_template = """
You are a {role} with expertise in {domain}.

Background Information:
{background_info}

Current Context:
{current_context}

Constraints:
{constraints}

Please respond according to your role and expertise.
"""
```

## Variable Substitution

### Basic Variable Substitution

```python
# Variables are enclosed in curly braces
template = "Hello {name}, how can I help you with {topic}?"
prompt = PromptTemplate.from_template(template)

# Format with variables
formatted = prompt.format(name="Alice", topic="Python programming")
```

### Using Default Values

```python
from langchain.prompts import PromptTemplate

template = "You are a {role} assistant. {custom_instruction}"
prompt = PromptTemplate.from_template(template)

# With default values
formatted = prompt.format(
    role="helpful",
    custom_instruction="Please be concise in your responses."
)
```

## Advanced Template Features

### Partial Templates

```python
from langchain.prompts import PromptTemplate

# Create a base template
base_template = "You are a {role} assistant. {instruction}"
base_prompt = PromptTemplate.from_template(base_template)

# Create a partial template with some variables pre-filled
partial_prompt = base_prompt.partial(role="technical")
```

### Template with Functions

```python
from langchain.prompts import PromptTemplate
from datetime import datetime

def get_current_time():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

template = """
Current time: {current_time}
User question: {question}

Please provide an answer considering the current context.
"""

prompt = PromptTemplate.from_template(template)
formatted = prompt.format(
    current_time=get_current_time(),
    question="What's the weather like?"
)
```

### Few-Shot Templates

```python
from langchain.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate

system_template = "You are a helpful assistant that provides accurate information."

few_shot_template = """
Question: {question}
Answer: {answer}

Question: {question2}
Answer: {answer2}

Question: {user_question}
Answer:"""

chat_prompt = ChatPromptTemplate.from_messages([
    SystemMessagePromptTemplate.from_template(system_template),
    HumanMessagePromptTemplate.from_template(few_shot_template)
])
```

## Best Practices

### 1. Structure Your Prompts Clearly

```python
# Good structure
template = """
Role: {role}
Background: {background}
Task: {task}
Constraints: {constraints}

Question: {question}
"""

# Avoid overly complex, nested templates
```

### 2. Use Descriptive Variable Names

```python
# Good
template = "You are a {expert_role} with {years_experience} years of experience."

# Avoid
template = "You are a {r} with {y} years of experience."
```

### 3. Provide Clear Instructions

```python
template = """
You are a {role} assistant.

Your responsibilities:
- {responsibility_1}
- {responsibility_2}
- {responsibility_3}

Please respond in a {tone} manner and keep responses under {max_length} words.
"""
```

### 4. Include Error Handling

```python
def safe_format(template, **kwargs):
    try:
        return template.format(**kwargs)
    except KeyError as e:
        missing_var = str(e).strip("'")
        raise ValueError(f"Missing required variable: {missing_var}")
```

### 5. Validate Template Variables

```python
def validate_template_variables(template, provided_vars):
    import re
    required_vars = set(re.findall(r'\{(\w+)\}', template))
    provided_vars = set(provided_vars.keys())
    
    missing = required_vars - provided_vars
    if missing:
        raise ValueError(f"Missing variables: {missing}")
    
    extra = provided_vars - required_vars
    if extra:
        print(f"Warning: Extra variables provided: {extra}")
```

## Examples

### Example 1: Research Assistant

```python
from langchain.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate

# Research assistant template
system_template = """
You are a research assistant with expertise in {research_domain}.

Your capabilities:
- Analyze complex topics
- Provide evidence-based answers
- Cite relevant sources
- Maintain academic tone

Current research context: {research_context}
"""

human_template = """
Research question: {question}

Please provide a comprehensive analysis with supporting evidence.
"""

chat_prompt = ChatPromptTemplate.from_messages([
    SystemMessagePromptTemplate.from_template(system_template),
    HumanMessagePromptTemplate.from_template(human_template)
])

# Usage
messages = chat_prompt.format_messages(
    research_domain="artificial intelligence",
    research_context="Focus on recent developments in 2024",
    question="What are the latest advances in transformer architectures?"
)
```

### Example 2: Customer Service Agent

```python
system_template = """
You are a customer service representative for {company_name}.

Company Information:
- Industry: {industry}
- Products: {products}
- Policies: {policies}

Your role:
- Provide helpful, accurate information
- Follow company policies
- Maintain professional tone
- Escalate complex issues when necessary

Current customer: {customer_type}
"""

human_template = """
Customer inquiry: {inquiry}

Please respond professionally and helpfully.
"""

chat_prompt = ChatPromptTemplate.from_messages([
    SystemMessagePromptTemplate.from_template(system_template),
    HumanMessagePromptTemplate.from_template(human_template)
])
```

### Example 3: Code Review Assistant

```python
system_template = """
You are a senior software engineer conducting code reviews.

Your expertise:
- {programming_languages}
- {frameworks}
- {best_practices}

Review focus areas:
- Code quality and readability
- Security considerations
- Performance optimization
- Maintainability
- Testing coverage

Current project: {project_context}
"""

human_template = """
Code to review:
```{language}
{code}
```

Please provide a thorough code review with specific recommendations.
"""

chat_prompt = ChatPromptTemplate.from_messages([
    SystemMessagePromptTemplate.from_template(system_template),
    HumanMessagePromptTemplate.from_template(human_template)
])
```

## Integration with LangChain

### Using with LLM Chains

```python
from langchain.chains import LLMChain
from langchain.llms import OpenAI

# Create prompt template
template = "You are a {role}. Answer this question: {question}"
prompt = PromptTemplate.from_template(template)

# Create chain
llm = OpenAI()
chain = LLMChain(llm=llm, prompt=prompt)

# Run chain
response = chain.run(role="expert programmer", question="How do I implement a binary search?")
```

### Using with Chat Models

```python
from langchain.chat_models import ChatOpenAI
from langchain.chains import LLMChain

# Create chat prompt template
chat_prompt = ChatPromptTemplate.from_messages([
    SystemMessagePromptTemplate.from_template("You are a {role}."),
    HumanMessagePromptTemplate.from_template("{question}")
])

# Create chain with chat model
chat_model = ChatOpenAI()
chain = LLMChain(llm=chat_model, prompt=chat_prompt)

# Run chain
response = chain.run(role="helpful assistant", question="What is machine learning?")
```

## Troubleshooting

### Common Issues

1. **Missing Variables**
   ```python
   # Error: KeyError: 'missing_variable'
   # Solution: Ensure all variables in template are provided
   ```

2. **Template Syntax Errors**
   ```python
   # Error: Invalid template syntax
   # Solution: Check for unmatched braces or invalid syntax
   ```

3. **Variable Type Issues**
   ```python
   # Error: TypeError when formatting
   # Solution: Ensure variables are strings or convert appropriately
   ```

### Debugging Tips

```python
# Print template variables
print(prompt.input_variables)

# Validate template before use
def validate_template(template, variables):
    try:
        template.format(**variables)
        return True
    except KeyError as e:
        print(f"Missing variable: {e}")
        return False
    except Exception as e:
        print(f"Template error: {e}")
        return False
```

## Conclusion

Prompt templates are powerful tools for creating structured, reusable prompts that can be dynamically populated with background information and context. By following the patterns and best practices outlined in this guide, you can create effective prompts that provide rich context to chat model invocations.

Remember to:
- Structure your prompts clearly
- Use descriptive variable names
- Provide comprehensive background information
- Validate your templates before use
- Follow best practices for maintainability

For more advanced features and detailed documentation, refer to the official LangChain documentation. 