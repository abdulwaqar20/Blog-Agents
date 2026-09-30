import os
from dotenv import load_dotenv
from pydantic import BaseModel
from langchain_groq import ChatGroq

load_dotenv()
llm = ChatGroq(model="openai/gpt-oss-20b", temperature=0.7)

class Review(BaseModel):
    approved: bool
    feedback: str

def planner(state):
    r = llm.invoke(f"Write a short outline (intro, 3 main points, conclusion) for a blog post on: {state['topic']}")
    return {"outline": r.content, "retries": 0, "approved": False, "feedback": ""}

def worker(state):
    prompt = f"Write a blog post following this outline:\n{state['outline']}"
    if state["feedback"]:
        prompt += f"\n\nPrevious draft:\n{state['draft']}\n\nFix these issues:\n{state['feedback']}"
    r = llm.invoke(prompt)
    return {"draft": r.content}

def reviewer(state):
    judge = llm.with_structured_output(Review, method="json_mode")
    r = judge.invoke(
        f"Outline:\n{state['outline']}\n\nDraft:\n{state['draft']}\n\n"
        "Does the draft follow the outline and read well? Approve only if it does; otherwise give specific feedback.\n"
        'Respond only with JSON: {"approved": true or false, "feedback": "string"}'
    )
    return {
        "approved": r.approved,
        "feedback": r.feedback,
        "retries": state["retries"] + (0 if r.approved else 1),
    }