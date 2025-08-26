# chat_interface.py
import os
import logging
from dotenv import load_dotenv
import gradio as gr
from llm_service import decide_action
from functions.sensors_api import get_hotels, get_floors, get_rooms, get_iaq_data, get_presence_data
from functions.energy_api import get_energy_summary

# Load env
load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))

# Logging
logging.basicConfig(level=logging.DEBUG, format="%(asctime)s [%(levelname)s] %(message)s")

# ----------------------
# Handle user message
# ----------------------
def handle_user_message(message, chat_history):
    logging.debug(f"msg = {message}")
    try:
        result = decide_action(message)
        action = result.get("action")
        params = result.get("parameters", {})
        logging.debug(f"LLM decided: action={action}, parameters={params}")

        # Call appropriate function
        if action == "get_hotels":
            data = get_hotels()
        elif action == "get_floors":
            hotel_id = params.get("hotel_id")
            data = get_floors(hotel_id) if hotel_id else {"error": "hotel_id missing"}
        elif action == "get_rooms":
            floor_id = params.get("floor_id")
            data = get_rooms(floor_id) if floor_id else {"error": "floor_id missing"}
        elif action == "get_iaq_data":
            room_id = params.get("room_id")
            data = get_iaq_data(room_id) if room_id else {"error": "room_id missing"}
        elif action == "get_presence_data":
            room_id = params.get("room_id")
            data = get_presence_data(room_id) if room_id else {"error": "room_id missing"}
        elif action == "get_energy_summary":
            hotel_id = params.get("hotel_id")
            subsystem = params.get("subsystem")
            start_time = params.get("start_time")
            end_time = params.get("end_time")
            resolution = params.get("resolution", "1hour")
            if hotel_id:
                data = get_energy_summary(hotel_id, subsystem, start_time, end_time, resolution)
            else:
                data = {"error": "hotel_id missing"}
        else:
            data = {"error": f"Unknown action: {action}"}

        bot_content = str(data)

    except Exception as e:
        logging.exception("Error in handle_user_message")
        bot_content = f"Error: {str(e)}"

    # Append messages in correct Gradio format
    # Each message is a dict with role and content
    chat_history.append({"role": "user", "content": message})
    chat_history.append({"role": "assistant", "content": bot_content})

    return chat_history

# ----------------------
# Gradio UI
# ----------------------
with gr.Blocks() as demo:
    chatbot = gr.Chatbot(label="Smart Hotel LLM Chatbot", type="messages")
    with gr.Row():
        msg = gr.Textbox(label="Enter your message", placeholder="Type here...")
        submit_btn = gr.Button("Send")

    # Connect Enter and Button
    msg.submit(handle_user_message, inputs=[msg, chatbot], outputs=[chatbot])
    submit_btn.click(handle_user_message, inputs=[msg, chatbot], outputs=[chatbot])

# Launch
if __name__ == "__main__":
    # demo.launch(server_name="0.0.0.0", server_port=7860, debug=True)
    demo.launch(server_name="0.0.0.0", share=True, debug=True)
