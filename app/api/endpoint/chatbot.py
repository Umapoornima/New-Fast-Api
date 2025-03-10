import json
import os

import anthropic
from fastapi import APIRouter, Request, WebSocket
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from app.utils.hazmate_prompt import hazmate_prompt_string

# app = FastAPI()
router = APIRouter(prefix="/chatbot", )

# Set up Jinja2 templates to serve HTML files
templates = Jinja2Templates(directory="app/templates")

# In-memory storage for chat histories, indexed by user ID
chat_histories = {}

client = anthropic.Anthropic(api_key=os.environ['ANTHROPIC_API_KEY'])


@router.get("/", response_class=HTMLResponse)
async def get(request: Request):
    # Serve the chat HTML page when the root URL is accessed
    return templates.TemplateResponse("chat.html", {"request": request})


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    # Accept the WebSocket connection
    await websocket.accept()

    while True:
        # Wait for a message from the client
        data = await websocket.receive_text()
        print(f"Received data: {data}")  # Debug print for received data
        message_data = json.loads(data)  # Parse the incoming JSON data

        if message_data['type'] == 'message':
            # Handle incoming messages from the user
            user_message = message_data['content']
            print(f"User message received: {user_message}")

            try:
                response = client.messages.create(
                    model="claude-3-opus-20240229",
                    max_tokens=4096,
                    system=hazmate_prompt_string,
                    messages=[{
                        "role": "user",
                        "content": user_message
                    }],
                    stream=True,
                )

                # Iterate over the stream of events
                for event in response:
                    if event.type == "content_block_delta":  # Look for text delta events
                        await websocket.send_text(
                            json.dumps({
                                "type": "response",
                                "content": event.delta.text
                            }))  # Send to user
                        await websocket.receive_text()
                        print(event.delta.text, end="",
                              flush=True)  # Print to console
                        # Ensure the response is sent before continuing to the next iteration

            except Exception as e:
                print(f"Error during chat: {e}")
                await websocket.send_text(
                    json.dumps({
                        "type": "response",
                        "content": f"Error during chat: {e}"
                    })
                )  # Handle errors gracefully # Debug print for received user message


# async def websocket_endpoint(websocket: WebSocket):
#     # Accept the WebSocket connection
#     await websocket.accept()
#     user_id = None

#     while True:
#         # Wait for a message from the client
#         data = await websocket.receive_text()
#         print(f"Received data: {data}")  # Debug print for received data
#         message_data = json.loads(data)  # Parse the incoming JSON data

#         if message_data['type'] == 'set_userid':
#             # Set the user ID when the client connects
#             user_id = message_data['userId']
#             # Initialize chat history for the user if not already present
#             if user_id not in chat_histories:
#                 chat_histories[user_id] = []
#             # Send the existing chat history back to the user
#             history_message = json.dumps({
#                 "type": "history",
#                 "history": chat_histories[user_id]
#             })
#             print(f"Sending history: {history_message}"
#                   )  # Debug print for sent history
#             await websocket.send_text(history_message)

#         elif message_data['type'] == 'message' and user_id:
#             # Handle incoming messages from the user
#             user_message = message_data['content']
#             # Store the user message in chat history
#             chat_histories[user_id].append(user_message)
#             print(f"User message stored: {user_message}"
#                   )  # Debug print for stored user message

#             # Generate a random AI response
#             responses = [
#                 "That's interesting!", "Tell me more!", "I see!",
#                 "What do you think?", "That's a good question!"
#             ]
#             response = random.choice(responses)  # Select a random response

#             # Store the AI response in chat history
#             chat_histories[user_id].append(response)
#             print(f"Sending response: {response}"
#                   )  # Debug print for sent response

#             # await asyncio.sleep(30)
#             # Send the AI response back to the client as a JSON object
#             await websocket.send_text(
#                 json.dumps({
#                     "type": "response",
#                     "content": response
#                 }))
