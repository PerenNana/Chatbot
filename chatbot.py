from graph_builder import build_graph
from dotenv import load_dotenv 
from langgraph.prebuilt import ToolNode
from langgraph.graph import START, END
from langchain.chat_models import init_chat_model
from langgraph.checkpoint.memory import InMemorySaver
from graph_builder import State
from manage_conversation import load_conversation, save_conversation
from final_response import FinalResponse
import os
import tools

load_dotenv()


openai_api_key = os.getenv("OPENAI_API_KEY")
# Initialize the chat model
llm = init_chat_model("openai:gpt-4.1")

# Bind tools to the language model
llm_with_tools = llm.bind_tools(tools.tools)

# Create a chatbot node
def chatbot(state: State):
    message = llm_with_tools.invoke(state["messages"])
    return {"messages": [message]}

# Structured output node
def structured_output_node(state: State):
    message = llm_with_tools.with_structured_output(FinalResponse).invoke(state["messages"])
    # Transform message to dict if it's a Pydantic model
    if hasattr(message, "model_dump_json"):
        return {"messages": [{"role": "assistant", "content": message.model_dump_json()}]}
    elif hasattr(message, "dict"):
        import json
        return {"messages": [{"role": "assistant", "content": json.dumps(message.dict())}]}
    elif hasattr(message, "content"):
        return {"messages": [{"role": "assistant", "content": message.content}]}
    else:
        return {"messages": [{"role": "assistant", "content": str(message)}]}
    
# Custom condition function to route based on tool calls
def custom_condition(state):
    if isinstance(state, list):
        ai_message = state[-1]
    elif isinstance(state, dict):
        ai_message = state["messages"][-1]
    else:
        ai_message = getattr(state, "messages")[-1]
    
    if hasattr(ai_message, "tool_calls") and len(ai_message.tool_calls) > 0:
        return "tools"
    return "structured_output"

# add ToolNode
tool_node = ToolNode(tools=tools.tools)


# Initialize memory saver
memory_saver = InMemorySaver()

# Define nodes, edges, conditional edges, and entry point for the graph
tool_node = ToolNode(tools=tools.tools)
nodes = [
    ("chatbot", chatbot),
    ("tools", tool_node), 
    ("structured_output", structured_output_node)
]
edges = [
    (START, "chatbot"),
    ("structured_output", END),
    ("tools", "chatbot")
]
conditional_edges = [
    ("chatbot", custom_condition)
]
entry_point = "chatbot"

graph = build_graph(
    nodes=nodes,
    edges=edges,
    conditional_edges=conditional_edges,
    entry_point=entry_point,
    compile_kwargs={"checkpointer": memory_saver}
)

mermaid_source = graph.get_graph().draw_mermaid()
print(mermaid_source)

thread_id = input("Thread-ID: ")
messages = load_conversation(thread_id)

system_prompt = {
    "role": "system",
    "content": (
        "For a task, use the appropriate tool if available."
    )
}
if not messages or messages[0].get("role") != "system":
    messages.insert(0, system_prompt)

while True:
    try:
        user_input = input("User: ")
        if user_input.lower() in ["quit", "exit", "q"]:
            print("Goodbye!")
            break
        messages.append({"role": "user", "content": user_input})
        events = graph.stream({"messages": messages},
                  {"configurable": {"thread_id": thread_id}},
                  stream_mode="values",
                  )
        assistant_msg = None
        for event in events:
            assistant_msg = event["messages"][-1]
            assistant_msg.pretty_print()
        # Save only the last assistant message after the loop
        if assistant_msg:
            messages.append({"role": "assistant", "content": assistant_msg.content})
        save_conversation(thread_id, messages)
    except Exception as e:
        print("Assistant: Something went wrong!", e)
        break

