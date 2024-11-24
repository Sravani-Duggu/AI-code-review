import streamlit as st
import google.generativeai as genai
import re
from typing import Dict, Tuple
from PIL import Image

# Set your Gemini API key directly
GEMINI_API_KEY = "AIzaSyBiOppVl-ptCaEg2zvCqRLmfvm1EZDBZws"  # Replace with your API key


class CodeReviewer:
    def __init__(self):
        """Initialize the CodeReviewer with Gemini AI."""
        genai.configure(api_key=GEMINI_API_KEY)
        self.model = genai.GenerativeModel('gemini-pro')

    def review_code(self, code: str) -> Tuple[Dict, str]:
        """
        Review the provided code using Gemini AI.
        Returns a tuple of (issues_dict, fixed_code).
        """
        try:
            prompt = f"""
            Please review the following Python code and provide:
            1. A list of potential bugs and issues
            2. Code quality improvements
            3. A corrected version of the code

            Here's the code to review:
            ```python
            {code}
            ```

            Please format your response exactly as shown below:
            ISSUES:
            - [issue description]

            IMPROVEMENTS:
            - [improvement suggestion]

            FIXED_CODE:
            ```python
            [corrected code]
            ```

            Please ensure to maintain this exact format in your response.
            """

            response = self.model.generate_content(prompt)
            response_text = response.text

            # Initialize dictionary to store issues
            issues = {'bugs': [], 'improvements': []}

            # Extract issues
            issues_match = re.findall(r'ISSUES:\n(.*?)(?=IMPROVEMENTS:|FIXED_CODE:|$)', response_text, re.DOTALL)
            if issues_match:
                issues['bugs'] = [bug.strip() for bug in issues_match[0].split('\n') if bug.strip()]

            # Extract improvements
            improvements_match = re.findall(r'IMPROVEMENTS:\n(.*?)(?=FIXED_CODE:|$)', response_text, re.DOTALL)
            if improvements_match:
                issues['improvements'] = [imp.strip() for imp in improvements_match[0].split('\n') if imp.strip()]

            # Extract fixed code
            fixed_code_match = re.findall(r'```python\n(.*?)```', response_text, re.DOTALL)
            fixed_code = fixed_code_match[-1].strip() if fixed_code_match else ""

            return issues, fixed_code

        except Exception as e:
            st.error(f"Error during code review: {str(e)}")
            return {"bugs": [], "improvements": []}, ""


def main():
    st.set_page_config(
        page_title="CodeRefine: AI-Powered Python Code Review & Enhancement",
        page_icon="💡",
        layout="wide"
    )

    # Set a custom background color and elegant font styles
    st.markdown("""
        <style>
            body {
                background-color: #f9f9f9;
                font-family: 'Georgia', serif;
            }
            .title {
                font-size: 40px;
                color: #2c3e50;
                font-weight: bold;
                text-align: center;
                margin-bottom: 15px;
                font-family: 'Georgia', serif;
            }
            .subtitle {
                font-size: 22px;
                color: #7f8c8d;
                text-align: center;
                margin-bottom: 40px;
                font-family: 'Georgia', serif;
            }
            .sidebar-title {
                font-size: 20px;
                font-weight: bold;
                color: #34495e;
            }
            .code-area {
                border: 2px solid #e5e5e5;
                padding: 15px;
                border-radius: 8px;
                background-color: #ffffff;
            }
            .code-header {
                font-size: 24px;
                font-weight: bold;
                color: #34495e;
                margin-top: 30px;
            }
            .code-text {
                font-size: 16px;
                color: #5f6368;
            }
            .button {
                background-color: #2980b9;
                color: white;
                font-size: 18px;
                font-weight: bold;
                padding: 10px 20px;
                border-radius: 6px;
                border: none;
            }
            .button:hover {
                background-color: #1f6fa1;
            }
            .section-header {
                font-size: 26px;
                font-weight: bold;
                color: #1abc9c;
                text-align: center;
                margin-top: 40px;
                margin-bottom: 20px;
            }
            .section-header-bug {
                font-size: 26px;
                font-weight: bold;
                color: #e74c3c;
                text-align: center;
                margin-top: 40px;
                margin-bottom: 20px;
            }
            .section-header-improvement {
                font-size: 26px;
                font-weight: bold;
                color: #27ae60;
                text-align: center;
                margin-top: 40px;
                margin-bottom: 20px;
            }
            .section-header-fixed {
                font-size: 26px;
                font-weight: bold;
                color: #f39c12;
                text-align: center;
                margin-top: 40px;
                margin-bottom: 20px;
            }
            .section-content {
                font-size: 16px;
                color: #5f6368;
                line-height: 1.5;
                text-align: left;
            }
        </style>
    """, unsafe_allow_html=True)

    # Title and description
    st.markdown("<div class='title'>💡 CodeRefine AI</div>", unsafe_allow_html=True)
    st.markdown(
        "<div class='subtitle'>Unlock Perfection in Your Python Code with Smart Reviews, Bug Fixes, and Performance Boosts!!</div>",
        unsafe_allow_html=True)

    # Sidebar for user input
    st.sidebar.title("📋 Code Submission Panel")
    user_code = st.sidebar.text_area(
        "📝 Paste Your Python Code Below",
        height=300,
        placeholder="# Paste your Python code here..."
    )

    if st.sidebar.button("🔍 Analyze Code", key="analyze_button", use_container_width=True):
        if not user_code.strip():
            st.sidebar.warning("⚠️ Please enter some code to review.")
        else:
            with st.spinner("Analyzing your code..."):
                reviewer = CodeReviewer()
                issues, fixed_code = reviewer.review_code(user_code)

                st.session_state.issues = issues
                st.session_state.fixed_code = fixed_code

    # Main area for results
    st.header("🔍 AI-Powered Review Results")
    if 'issues' in st.session_state and st.session_state.issues:
        st.markdown("<div class='section-header-bug'>🐞 Identified Issues</div>", unsafe_allow_html=True)
        for bug in st.session_state.issues['bugs']:
            st.markdown(f"<div class='section-content'>- {bug.strip('- ')}</div>", unsafe_allow_html=True)

        st.markdown("<div class='section-header-improvement'>✨ Suggested Improvements</div>", unsafe_allow_html=True)
        for improvement in st.session_state.issues['improvements']:
            st.markdown(f"<div class='section-content'>- {improvement.strip('- ')}</div>", unsafe_allow_html=True)

        st.markdown("<div class='section-header-fixed'>✅ Fixed Code</div>", unsafe_allow_html=True)
        if 'fixed_code' in st.session_state:
            st.markdown(f"<div class='code-header'>Fixed Code:</div>", unsafe_allow_html=True)
            st.code(st.session_state.fixed_code, language="python")
    else:
        st.info("Submit your code in the sidebar to get started.")


def initialize_session_state():
    """Initialize session state variables."""
    if 'issues' not in st.session_state:
        st.session_state.issues = {'bugs': [], 'improvements': []}
    if 'fixed_code' not in st.session_state:
        st.session_state.fixed_code = ""


if __name__ == "__main__":
    initialize_session_state()
    main()
