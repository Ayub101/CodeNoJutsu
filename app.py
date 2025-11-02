# app.py
import streamlit as st
import io
import zipfile
import time
from datetime import datetime
import os
import shutil
import traceback

# Import run_agent from main.py (same folder)
from main import run_agent

st.set_page_config(page_title="CodeSmith AI — Generator UI", layout="wide")

PROJECT_FOLDER = "generated_project"

st.title("🛠️ CodeSmith AI")
st.caption("Enter a prompt and generate a multi-file project. Download the result as a ZIP.")

with st.form("prompt_form"):
    prompt = st.text_area("Describe the app you want (e.g. 'Create a calculator web app')", height=140)
    recursion_limit = st.number_input("Recursion limit (agent)", min_value=1, value=100, step=1)
    suggested_name = st.text_input("Zip filename (optional)", value="generated_project.zip")
    submit = st.form_submit_button("Generate")

# Ensure session state keys exist
if "generated_time" not in st.session_state:
    st.session_state.generated_time = None
if "last_result" not in st.session_state:
    st.session_state.last_result = None

if submit:
    if not prompt.strip():
        st.warning("Please enter a prompt first.")
    else:
        # Auto-delete old project folder (Option A)
        if os.path.exists(PROJECT_FOLDER):
            try:
                shutil.rmtree(PROJECT_FOLDER)
            except Exception as e:
                st.error(f"Failed to remove old project folder: {e}")
                st.stop()

        # Run agent (blocking call). Show spinner during generation.
        with st.spinner("Running agent and generating project... (this may take a while)"):
            try:
                result = run_agent(prompt, recursion_limit=recursion_limit)
                st.session_state.last_result = result
                st.session_state.generated_time = datetime.utcnow().isoformat() + "Z"
                # tiny pause for UX
                time.sleep(0.4)
                st.success("Generation complete ✅")
            except Exception as e:
                st.error("Agent failed — check logs.")
                tb = traceback.format_exc()
                # Log the traceback to console (server log)
                print(tb)
                st.stop()

# If project folder exists, show files and create ZIP for download
if os.path.exists(PROJECT_FOLDER):
    st.subheader("📂 Generated Project Ready")
    st.write(f"Generated at: {st.session_state.get('generated_time', 'Unknown')}")

    # File tree preview
    st.markdown("**Files (tree)**")
    for root, _, files in os.walk(PROJECT_FOLDER):
        for file in files:
            rel_path = os.path.relpath(os.path.join(root, file), PROJECT_FOLDER)
            st.write(f"- `{rel_path}`")

    st.markdown("---")
    st.markdown("**File contents (click to expand)**")
    # Allow quick preview of files
    for root, _, files in os.walk(PROJECT_FOLDER):
        for file in files:
            file_path = os.path.join(root, file)
            rel_path = os.path.relpath(file_path, PROJECT_FOLDER)
            try:
                with open(file_path, "rb") as f:
                    content_bytes = f.read()
                try:
                    text = content_bytes.decode("utf-8")
                except Exception:
                    text = "<binary content — preview not available>"

                with st.expander(rel_path, expanded=False):
                    if text != "<binary content — preview not available>":
                        # show as code block
                        st.code(text, language="auto")
                    else:
                        st.write(text)
            except Exception as e:
                st.write(f"- Could not read `{rel_path}`: {e}")

    st.markdown("---")

    # Create ZIP from folder
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as z:
        for root, _, files in os.walk(PROJECT_FOLDER):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, PROJECT_FOLDER)
                z.write(file_path, arcname=arcname)
    zip_buffer.seek(0)

    # Filename chosen by user
    filename = suggested_name.strip() or "generated_project.zip"
    if not filename.lower().endswith(".zip"):
        filename += ".zip"

    st.download_button(
        label="📦 Download ZIP",
        data=zip_buffer,
        file_name=filename,
        mime="application/zip",
    )
else:
    st.info("No project generated yet. Type a prompt above and click Generate.")

st.markdown("---")
st.markdown("### Integration / Notes")
st.markdown(
    """
- The agent should write files inside the `generated_project/` folder (use your write_file tool).
- Old `generated_project/` folder is deleted automatically before each run (Option A).
- The Streamlit UI zips whatever is present in `generated_project/` after the agent completes and provides it for download.
- If agent produces binary files (images), they will be included in the ZIP and binary previews will be omitted in the UI.
"""
)
