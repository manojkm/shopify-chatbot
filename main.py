import os
import gradio as gr
from groq import Groq
from litellm import completion
from dotenv import load_dotenv

load_dotenv()

GROQ_KEY = os.getenv("GROQ_API_KEY")
MODEL = "groq/llama-3.3-70b-versatile"

groq_client = Groq(api_key=GROQ_KEY)

DEFAULT_STORE_CONTEXT = """
Sunrise Skincare is an online store selling natural skincare products.

PRODUCTS:
- Hydrating Face Serum ($45): A lightweight serum with hyaluronic acid and vitamin C. Suitable for all skin types. Apply 2-3 drops every morning before moisturizer.
- Calming Night Cream ($55): Rich cream with aloe vera and chamomile. Best for dry or sensitive skin. Apply before bed.
- SPF 50 Sunscreen ($30): Lightweight, non-greasy daily sunscreen. Water resistant for 80 minutes. Reef-safe formula.
- Gentle Cleanser ($25): Sulfate-free face wash for all skin types. Use morning and night.

SHIPPING:
- Free standard shipping on all orders over $50.
- Standard shipping (5-7 business days): $5.99
- Express shipping (2-3 business days): $12.99
- We ship to the US, Canada, and the UK.

RETURNS & REFUNDS:
- 30-day return policy for unopened products.
- If you are not satisfied, contact us within 30 days for a full refund.
- Opened products are non-refundable unless damaged or defective.

INGREDIENTS & ALLERGENS:
- All products are vegan and cruelty-free.
- No parabens, sulfates, or artificial fragrances.
- The Night Cream contains shea butter — not suitable for nut allergies.

CONTACT:
- Email: support@sunriseskincare.com
- Hours: Monday to Friday, 9am - 5pm EST.
""".strip()


def transcribe_audio(audio_path: str) -> str:
    """Convert recorded audio to text using Groq Whisper."""
    if audio_path is None:
        return ""
    with open(audio_path, "rb") as f:
        result = groq_client.audio.transcriptions.create(
            file=f,
            model="whisper-large-v3-turbo",
            response_format="text",
        )
    return result


def answer_question(question: str, context: str, history: list) -> tuple:
    if not question.strip():
        return history, ""

    if not context.strip():
        history.append({"role": "user", "content": question})
        history.append({"role": "assistant", "content": "Please add your store information in the left panel first."})
        return history, ""

    messages = [
        {
            "role": "system",
            "content": (
                "You are a helpful customer support assistant for an online store. "
                "Answer questions ONLY based on the store information provided below. "
                "If the answer is not in the store info, say you don't have that information "
                "and suggest the customer contact support. Keep answers short and friendly.\n\n"
                f"STORE INFORMATION:\n{context}"
            ),
        }
    ]
    for msg in history:
        messages.append({"role": msg["role"], "content": msg["content"]})
    messages.append({"role": "user", "content": question})

    try:
        response = completion(model=MODEL, api_key=GROQ_KEY, messages=messages)
        reply = response.choices[0].message.content.strip()
    except Exception as e:
        reply = f"Sorry, something went wrong: {str(e)}"

    history.append({"role": "user", "content": question})
    history.append({"role": "assistant", "content": reply})
    return history, ""


def voice_to_answer(audio_path: str, context: str, history: list) -> tuple:
    """Transcribe voice then immediately send as a question."""
    question = transcribe_audio(audio_path)
    if not question:
        return history, "", None
    updated_history, _ = answer_question(question, context, history)
    return updated_history, question, None   # clear audio after use


with gr.Blocks(title="Shopify Store Chatbot") as app:
    gr.Markdown("# Shopify Store FAQ Chatbot")
    gr.Markdown("Built with **Gradio** (HuggingFace) + **Whisper + Llama 3.3** on Groq.")

    with gr.Row():
        with gr.Column(scale=1):
            gr.Markdown("### Store Info")
            gr.Markdown("Paste your products, prices, shipping policy, FAQs here.")
            store_context = gr.Textbox(
                value=DEFAULT_STORE_CONTEXT,
                label="Store context",
                lines=28,
                max_lines=40,
            )

        with gr.Column(scale=1):
            gr.Markdown("### Customer Chat")
            chatbot = gr.Chatbot(label="Chat", height=400)

            question_input = gr.Textbox(
                label="Type your question",
                placeholder="e.g. Do you offer free shipping?",
            )
            with gr.Row():
                send_btn = gr.Button("Send", variant="primary")
                clear_btn = gr.Button("Clear chat")

            gr.Markdown("#### Or ask by voice")
            audio_input = gr.Audio(
                sources=["microphone"],
                type="filepath",
                label="Record your question",
            )
            voice_btn = gr.Button("Transcribe & Send", variant="secondary")

            gr.Examples(
                label="Try these",
                examples=[
                    ["Do you offer free shipping?"],
                    ["What is your return policy?"],
                    ["Is the night cream safe for nut allergies?"],
                    ["How much does the face serum cost?"],
                    ["Do you ship to Canada?"],
                    ["What are your support hours?"],
                ],
                inputs=question_input,
            )

    send_btn.click(
        fn=answer_question,
        inputs=[question_input, store_context, chatbot],
        outputs=[chatbot, question_input],
    )
    question_input.submit(
        fn=answer_question,
        inputs=[question_input, store_context, chatbot],
        outputs=[chatbot, question_input],
    )
    voice_btn.click(
        fn=voice_to_answer,
        inputs=[audio_input, store_context, chatbot],
        outputs=[chatbot, question_input, audio_input],
    )
    clear_btn.click(fn=lambda: ([], ""), outputs=[chatbot, question_input])


if __name__ == "__main__":
    port = int(os.getenv("PORT", 7860))
    app.launch(server_name="0.0.0.0", server_port=port)

#greptile-test
#greptile-test2
#greptile-test3