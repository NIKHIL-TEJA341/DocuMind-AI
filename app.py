import streamlit as st
import time
import utils
import agent

# Page Configuration
st.set_page_config(
    page_title="DocuMind AI",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for specific overrides (buttons, layout tweaks)
st.markdown("""
    <style>
    .stButton>button {
        width: 100%;
        font-weight: 600;
        border-radius: 6px;
    }
    .main-title {
        text-align: center;
        font-weight: 700;
        font-size: 3rem;
        margin-bottom: 0;
    }
    .sub-title {
        text-align: center;
        color: #94a3b8;
        font-size: 1.1rem;
        margin-bottom: 2rem;
    }
    .badge {
        display: inline-block;
        background-color: rgba(0, 232, 93, 0.1);
        color: #00E85D;
        padding: 0.3rem 0.8rem;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 600;
        border: 1px solid rgba(0, 232, 93, 0.2);
        margin: 0 auto 1rem auto;
    }
    .center-div {
        display: flex;
        justify-content: center;
    }
    </style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# Initialize Session State
# ---------------------------------------------------------
if 'view' not in st.session_state:
    st.session_state.view = "Dashboard"

if 'is_analyzing' not in st.session_state:
    st.session_state.is_analyzing = False

if 'analysis_complete' not in st.session_state:
    st.session_state.analysis_complete = False

if 'extraction_source' not in st.session_state:
    st.session_state.extraction_source = None

if 'doc_content' not in st.session_state:
    st.session_state.doc_content = ""

if 'code_stats' not in st.session_state:
    st.session_state.code_stats = {"files": 0, "size": "0 KB"}

# ---------------------------------------------------------
# Sidebar
# ---------------------------------------------------------
with st.sidebar:
    st.title("📂 DocuMind AI")
    st.caption("v1.0.4-stable")
    st.divider()
    
    # API key is managed securely in the backend
    st.divider()
    
    views = ["Dashboard", "Analysis Logs", "Documentation"]
    current_index = views.index(st.session_state.view)
    
    view_selection = st.radio(
        "Navigation",
        views,
        index=current_index
    )
    
    # If user clicks a different radio button, update session state and rerun
    if view_selection != st.session_state.view:
        st.session_state.view = view_selection
        st.rerun()
    
    st.divider()
    st.caption("powered by")
    st.markdown("**Groq | Agno AI | JetBrains**")


# ---------------------------------------------------------
# Main Content Area
# ---------------------------------------------------------

if st.session_state.view == "Dashboard":
    
    # Hero Section
    st.markdown('<div class="center-div"><span class="badge">⚡ Powered by Agno + Groq</span></div>', unsafe_allow_html=True)
    st.markdown('<h1 class="main-title">Turn Code into Clarity. <span style="color: #00E85D;">Instantly.</span></h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-title">The AI-powered documentation engine for modern development teams.<br>Connect your repo and let DocuMind synthesize high-fidelity technical guides in seconds.</p>', unsafe_allow_html=True)
    
    st.write("---")
    
    # Input Area
    col1, col2 = st.columns([3, 1])
    with col1:
        repo_url = st.text_input("🔗 GitHub Repository URL", placeholder="https://github.com/user/repo", label_visibility="collapsed")
    with col2:
        if st.button("🪄 Scan Repository", type="primary"):
            if not repo_url:
                st.error("Please enter a valid GitHub URL.")
            else:
                st.session_state.extraction_source = ('github', repo_url)
                st.session_state.view = "Analysis Logs"
                st.session_state.is_analyzing = True
                st.rerun()

    st.write("")
    
    # Upload Cards
    col3, col4 = st.columns(2)
    with col3:
        st.markdown("### 📄 Upload Files")
        st.caption("Select source files (.py, .js, .java, etc.)")
        uploaded_files = st.file_uploader("Upload files", accept_multiple_files=True, label_visibility="collapsed")
        if st.button("Scan Uploaded Files"):
            if not uploaded_files:
                st.error("Please upload at least one file.")
            else:
                st.session_state.extraction_source = ('files', uploaded_files)
                st.session_state.view = "Analysis Logs"
                st.session_state.is_analyzing = True
                st.rerun()
                
    with col4:
        st.markdown("### 🗂️ Upload Project ZIP")
        st.caption("Bulk process entire archives")
        uploaded_zip = st.file_uploader("Upload zip", type=['zip'], label_visibility="collapsed")
        if st.button("Scan ZIP Archive"):
            if not uploaded_zip:
                st.error("Please upload a ZIP file.")
            else:
                st.session_state.extraction_source = ('zip', uploaded_zip)
                st.session_state.view = "Analysis Logs"
                st.session_state.is_analyzing = True
                st.rerun()


elif st.session_state.view == "Analysis Logs":
    st.header("Terminal - Analysis Log")
    
    # Layout for analysis view
    left_col, right_col = st.columns([2, 1])
    
    with left_col:
        st.info("🟢 AI Engine Online - Ready to analyze.")
        
        # Terminal mock container
        terminal_container = st.empty()
        
        if st.session_state.is_analyzing:
            with st.spinner("Executing analysis pipeline..."):
                source_type, source_data = st.session_state.extraction_source
                code_dict = {}
                
                terminal_container.code("[INFO] Initializing extraction protocols...", language="bash")
                time.sleep(1) # Small delay for UI effect
                
                if source_type == 'github':
                    terminal_container.code(f"[INFO] Cloning repository: {source_data}\n[INFO] This may take a few moments...", language="bash")
                    code_dict = utils.extract_from_github(source_data)
                elif source_type == 'files':
                    terminal_container.code("[INFO] Processing directly uploaded files...", language="bash")
                    code_dict = utils.extract_from_files(source_data)
                elif source_type == 'zip':
                    terminal_container.code("[INFO] Extracting uploaded ZIP archive...", language="bash")
                    code_dict = utils.extract_from_zip(source_data)
                
                if 'error.txt' in code_dict:
                    terminal_container.code(f"[ERROR] Extraction failed:\n{code_dict['error.txt']}", language="bash")
                    st.error("Extraction failed. Check the logs.")
                    st.session_state.is_analyzing = False
                else:
                    file_count = len(code_dict)
                    total_size = sum(len(content) for content in code_dict.values())
                    st.session_state.code_stats = {
                        "files": file_count,
                        "size": f"{total_size / 1024:.1f} KB"
                    }
                    
                    terminal_container.code(f"[INFO] Extraction complete. Found {file_count} valid files.\n[AI] Initializing Agno Agent with Groq (llama-3.3-70b)...\n[AI] Synthesizing documentation...", language="bash")
                    
                    # Generate documentation
                    doc_result = agent.generate_documentation(code_dict)
                    
                    terminal_container.code("[SUCCESS] Documentation generated successfully.", language="bash")
                    
                    st.session_state.doc_content = doc_result
                    st.session_state.is_analyzing = False
                    st.session_state.analysis_complete = True
                    
                    st.success("Analysis complete! Switch to the Documentation tab or click the button on the right.")
        else:
            if st.session_state.analysis_complete:
                terminal_container.code("Analysis complete. Ready for export.", language="bash")
            else:
                terminal_container.code("Waiting for input...\nReturn to Dashboard to scan a repository.", language="bash")

    with right_col:
        st.markdown("### Quick Insights")
        st.write(f"**Total Valid Files:** {st.session_state.code_stats.get('files', 0)}")
        st.write(f"**Codebase Size:** {st.session_state.code_stats.get('size', '0 KB')}")
        st.divider()
        
        if st.session_state.analysis_complete:
            if st.button("📄 View Documentation", type="primary"):
                st.session_state.view = "Documentation"
                st.rerun()
        else:
            st.info("Analysis metrics will appear here once scanning is complete.")


elif st.session_state.view == "Documentation":
    st.header("Result Workspace")
    
    if not st.session_state.analysis_complete:
        st.warning("No documentation has been generated yet. Please run an analysis from the Dashboard.")
        if st.button("Go to Dashboard"):
            st.session_state.view = "Dashboard"
            st.rerun()
    else:
        left_panel, main_doc, right_panel = st.columns([1, 3, 1])
        
        with left_panel:
            st.markdown("### Files")
            st.markdown("""
            - 📄 **README.md** (Active Output)
            """)
            
        with main_doc:
            st.markdown("### PREVIEW | README.md")
            st.info("✨ AI Generation Complete")
            
            # Display actual Markdown output
            st.markdown(st.session_state.doc_content)

        with right_panel:
            st.markdown("### Export Assets")
            st.download_button(
                label="⬇️ Download .md",
                data=st.session_state.doc_content,
                file_name="README.md",
                mime="text/markdown",
                use_container_width=True
            )
            st.download_button(
                label="⬇️ Download .txt",
                data=st.session_state.doc_content,
                file_name="README.txt",
                mime="text/plain",
                use_container_width=True
            )
            st.button("📋 Copy to Clipboard", use_container_width=True) # Note: Clipboard button might not work inherently in standard Streamlit without custom components, kept for UI mock
            
            st.divider()
            
            if st.button("New Analysis"):
                st.session_state.view = "Dashboard"
                st.session_state.analysis_complete = False
                st.session_state.doc_content = ""
                st.rerun()
