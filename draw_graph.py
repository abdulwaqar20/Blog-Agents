from src.graph import app

png = app.get_graph().draw_mermaid_png()
with open("docs/graph.png", "wb") as f:
    f.write(png)
print("Saved docs/graph.png")