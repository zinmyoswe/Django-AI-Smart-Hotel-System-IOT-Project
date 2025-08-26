import gradio as gr

def echo(msg, history):
    print("DEBUG: msg =", msg)
    history.append((msg, msg))
    return history, history

with gr.Blocks() as demo:
    chatbot = gr.Chatbot()
    txt = gr.Textbox(show_label=False, placeholder="Type your message...")
    txt.submit(echo, [txt, chatbot], [chatbot, chatbot])

# demo.launch(share=False, server_name="0.0.0.0", debug=True)
demo.launch(server_name="0.0.0.0", share=True, debug=True)
