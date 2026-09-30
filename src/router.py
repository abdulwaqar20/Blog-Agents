MAX_RETRIES = 2

def route(state):
    if state["approved"] or state["retries"] >= MAX_RETRIES:
        return "end"
    return "retry"