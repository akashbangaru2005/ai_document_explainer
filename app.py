import streamlit as st
import os
from document_loader import load_document
from text_processor import clean_text, split_into_chunks
from ai_engine import summarize_doc, extract_key_points, answer_question, speak_telugu_voice, to_telugu


# Set page configuration
st.set_page_config(
    page_title="AI Document Explainer",
    layout="wide",
    page_icon="📄",
    initial_sidebar_state="expanded"
)

# ---------- SESSION STATE INITIALIZATION ----------
if "upload_history" not in st.session_state:
    st.session_state.upload_history = []

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "processed_chunks" not in st.session_state:
    st.session_state.processed_chunks = None

if "document_name" not in st.session_state:
    st.session_state.document_name = None

# ---------- SIDEBAR ----------
with st.sidebar:
    st.image("logo.png", width=200)  # Ensure logo.png exists in the project directory
    st.title("AI Document Explainer")
    st.markdown("""
### Features
- **Document Summary**: Generate concise summaries in English and Telugu with audio.
- **Key Point Extraction**: Extract and translate key points with voice output.
- **Question Answering**: Ask questions and get answers based on the document.
- **Multilingual Support**: Automatic Telugu translation and speech synthesis.
""")

    st.subheader("📂 Previously Uploaded Documents")
    if st.session_state.upload_history:
        for file in st.session_state.upload_history[-5:]:  # Show last 5 for brevity
            st.write(f"• {file}")
    else:
        st.write("No previous documents.")

    # Add a button to clear history
    if st.button("Clear Upload History"):
        st.session_state.upload_history = []
        st.success("Upload history cleared!")

    # Add a button to clear chat history
    if st.button("Clear Chat History"):
        st.session_state.chat_history = []
        st.success("Chat history cleared!")

# ---------- HEADER ----------
st.header("📄 AI Document Intelligence Dashboard")
st.markdown("Upload a document to analyze, summarize, extract key points, and ask questions with Telugu translation and voice output.")

# ---------- FILE UPLOADER ----------
uploaded_file = st.file_uploader(
    "Upload a Document (PDF or TXT)",
    type=["pdf", "txt"],
    help="Supported formats: PDF and TXT. Maximum file size: 10MB."
)

if uploaded_file is not None:
    # Check if the file is already processed
    if st.session_state.document_name != uploaded_file.name:
        st.session_state.document_name = uploaded_file.name
        if uploaded_file.name not in st.session_state.upload_history:
            st.session_state.upload_history.append(uploaded_file.name)

        # Save the uploaded file temporarily
        file_path = os.path.join(os.getcwd(), uploaded_file.name)
        try:
            with open(file_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
        except Exception as e:
            st.error(f"Error saving file: {e}")
            st.stop()

        # -------- PROGRESS BAR --------
        progress = st.progress(0)
        status = st.empty()

        try:
            status.text("Reading document...")
            progress.progress(20)
            raw_text = load_document(file_path)

            status.text("Cleaning text...")
            progress.progress(50)
            clean = clean_text(raw_text)

            status.text("Splitting into chunks...")
            progress.progress(80)
            chunks = split_into_chunks(clean)

            st.session_state.processed_chunks = chunks

            progress.progress(100)
            status.text("Document ready!")
            st.success("Document processed successfully!")

        except Exception as e:
            st.error(f"Error processing document: {e}")
            st.stop()
        finally:
            # Clean up the temporary file
            if os.path.exists(file_path):
                os.remove(file_path)

    # -------- LAYOUT COLUMNS --------
    col1, col2 = st.columns([2, 1])

    with col1:
        st.subheader("📄 Document Content Preview")
        if st.session_state.processed_chunks:
            # Show a preview of the first chunk or a summary
            preview = " ".join(st.session_state.processed_chunks[0].split()[:100]) + "..." if st.session_state.processed_chunks else "No content."
            st.write(preview)
            with st.expander("View Full Document"):
                st.write(" ".join(st.session_state.processed_chunks))
        else:
            st.write("No document processed yet.")

    with col2:
        st.subheader("📊 Document Statistics")
        if st.session_state.processed_chunks:
            num_chunks = len(st.session_state.processed_chunks)
            total_words = sum(len(chunk.split()) for chunk in st.session_state.processed_chunks)
            st.write(f"**Number of Chunks:** {num_chunks}")
            st.write(f"**Total Words:** {total_words}")
        else:
            st.write("No statistics available.")

    st.divider()

    # ---------- SUMMARY SECTION ----------
    st.subheader("📌 Document Summary")
    if st.button("Generate Summary", key="summary_btn"):
        if st.session_state.processed_chunks:
            with st.spinner("Analyzing document and generating summary..."):
                try:
                    summary, telugu_summary, audio = summarize_doc(st.session_state.processed_chunks)

                    col1, col2 = st.columns(2)
                    with col1:
                        st.markdown("**English Summary**")
                        st.write(summary)

                    with col2:
                        st.markdown("**Telugu Summary**")
                        st.write(telugu_summary)
                        if audio:
                            st.audio(audio)
                            # Add download button for audio
                            with open(audio, "rb") as f:
                                st.download_button(
                                    label="Download Telugu Audio",
                                    data=f,
                                    file_name="telugu_summary.mp3",
                                    mime="audio/mpeg"
                                )
                except Exception as e:
                    st.error(f"Error generating summary: {e}")
        else:
            st.warning("Please upload and process a document first.")

    # ---------- KEY POINTS SECTION ----------
    st.subheader("📝 Key Points Extraction")
    if st.button("Extract Key Points", key="keypoints_btn"):
        if st.session_state.processed_chunks:
            with st.spinner("Extracting key points..."):
                try:
                    points, telugu_points, audio = extract_key_points(st.session_state.processed_chunks)

                    col1, col2 = st.columns(2)
                    with col1:
                        st.markdown("**Key Points (English)**")
                        st.write(points)

                    with col2:
                        st.markdown("**Key Points (Telugu)**")
                        st.write(telugu_points)
                        if audio:
                            st.audio(audio)
                            # Add download button for audio
                            with open(audio, "rb") as f:
                                st.download_button(
                                    label="Download Telugu Audio",
                                    data=f,
                                    file_name="telugu_keypoints.mp3",
                                    mime="audio/mpeg"
                                )
                except Exception as e:
                    st.error(f"Error extracting key points: {e}")
        else:
            st.warning("Please upload and process a document first.")

    st.divider()

    # ---------- CHAT SECTION ----------
    st.subheader("💬 Question Answering")
    st.markdown("Ask questions about the document. The AI will search for relevant information.")

    question = st.text_input("Type your question here:", key="question_input")

    if st.button("Ask", key="ask_btn") and question:
        if st.session_state.processed_chunks:
            with st.spinner("Searching the document and generating answer..."):
                try:
                    answer = answer_question(question, st.session_state.processed_chunks)
                    st.session_state.chat_history.append(("You", question))
                    st.session_state.chat_history.append(("AI", answer))
                except Exception as e:
                    st.error(f"Error answering question: {e}")
        else:
            st.warning("Please upload and process a document first.")

    # Display chat history
    if st.session_state.chat_history:
        st.markdown("### Chat History")
        for sender, msg in st.session_state.chat_history:
            if sender == "You":
                st.markdown(f"**🧑 You:** {msg}")
            else:
                st.markdown(f"**🤖 AI:** {msg}")
    else:
        st.info("No questions asked yet. Start a conversation!")


else:
    st.info("👆 Upload a document to get started. Supported formats: PDF and TXT.")

# ---------- FOOTER ----------
st.markdown("---")
st.markdown(
    """
    <div style="text-align: center; color: gray;">
        Powered by Streamlit | AI Document Explainer v2.0
    </div>
    """,
    unsafe_allow_html=True
)