from src.graph import app

topic = input("Blog topic: ")
result = app.invoke({
    "topic": topic,
    "outline": "",
    "draft": "",
    "feedback": "",
    "retries": 0,
    "approved": False,
})

print("\nOUTLINE:\n", result["outline"])
print("\nFINAL DRAFT:\n", result["draft"])
print("\nApproved:", result["approved"], "| Retries:", result["retries"])
print("Last feedback:", result["feedback"])