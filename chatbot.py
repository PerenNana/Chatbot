from graph_builder import build_graph
from dotenv import load_dotenv 
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.graph import START, END
from langchain.chat_models import init_chat_model
from langgraph.checkpoint.memory import InMemorySaver
from graph_builder import State
from manage_conversation import load_conversation, save_conversation
from final_response import FinalResponse
import os
import tools

load_dotenv()


openai_api_key = os.getenv("...")
# Initialize the chat model
llm = init_chat_model("openai:gpt-4.1")

# Bind tools to the language model
llm_with_tools = llm.bind_tools(tools.tools)

# Bind schema to the language model
llm_with_tools_structured_output = llm_with_tools.with_structured_output(FinalResponse)

# Create a chatbot node
def chatbot(state: State):
    message = llm_with_tools_structured_output.invoke(state["messages"])
    return {"messages": [{"role": "assistant", "content": str(message)}]}

# add ToolNode
tool_node = ToolNode(tools=tools.tools)


# Initialize memory saver
memory_saver = InMemorySaver()

# Define nodes, edges, conditional edges, and entry point for the graph
tool_node = ToolNode(tools=tools.tools)
nodes = [
    ("chatbot", chatbot),
    ("tools", tool_node)
]
edges = [
    (START, "chatbot"),
    ("chatbot", END),
    ("tools", "chatbot")
]
conditional_edges = [
    ("chatbot", tools_condition)
]
entry_point = "chatbot"

graph = build_graph(
    nodes=nodes,
    edges=edges,
    conditional_edges=conditional_edges,
    entry_point=entry_point,
    compile_kwargs={"checkpointer": memory_saver}
)

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

