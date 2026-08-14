import os
import re
import google.generativeai as genai
import streamlit as st
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Page Config
st.set_page_config(
    page_title="AI Code Reviewer & Security Scanner", page_icon="🛡️", layout="wide"
)

st.title("🛡️ AI-Powered Code Reviewer & Security Scanner")
st.caption("Automated Python Security Auditing & GenAI Refactoring")

# Get API key automatically from .env
api_key = os.getenv("GEMINI_API_KEY")


# Security Scanner Function
def scan_security_issues(code):
    issues = []
    if re.search(r'(password|passwd|pwd)\s*=\s*["\'].+["\']', code, re.IGNORECASE):
        issues.append({
            "severity": "CRITICAL",
            "type": "Hardcoded Password",
            "msg": "Plain password detected! Use Environment Variables.",
        })
    if re.search(
        r'(api_key|secret|token)\s*=\s*["\'][A-Za-z0-9_\-]{16,}["\']',
        code,
        re.IGNORECASE,
    ):
        issues.append({
            "severity": "HIGH",
            "type": "Exposed API Key",
            "msg": "API Key detected! Security leak risk.",
        })
    if "eval(" in code:
        issues.append({
            "severity": "HIGH",
            "type": "Dangerous Function",
            "msg": "'eval()' creates code execution risks.",
        })
    return issues


# UI Layout
col1, col2 = st.columns(2)

with col1:
    st.subheader("📝 Input Python Code")
    default_code = (
        "def login():\n"
        '    password = "MySecretPassword123"\n'
        '    api_key = "AIzaSyD-1234567890abcdefghijklmnopqrst"\n'
        '    result = eval("2 + 2")\n'
        '    print("Logged in!")'
    )

    user_code = st.text_area("Paste code here:", value=default_code, height=300)
    scan_btn = st.button("🚀 Analyze & Scan Code", type="primary")

with col2:
    st.subheader("📊 Scan & Review Results")
    if scan_btn:
        # 1. Security Scan
        st.markdown("### 🔴 Security Vulnerabilities")
        issues = scan_security_issues(user_code)
        if not issues:
            st.success("✅ No obvious security issues found!")
        else:
            for issue in issues:
                st.error(
                    f"**[{issue['severity']}] {issue['type']}**: {issue['msg']}"
                )

        # 2. AI Review
        st.markdown("### 🤖 AI Optimization & Refactoring")
        if not api_key:
            st.error(
                "⚠️ API Key missing! Please check your .env file and ensure GEMINI_API_KEY is set."
            )
        else:
            with st.spinner("AI is analyzing your code..."):
                try:
                    genai.configure(api_key=api_key)

                    prompt = (
                        "You are an expert Python Developer. "
                        "Review and refactor the following Python code for performance, security, syntax, and best practices. "
                        "Provide clean refactored code:\n\n"
                        f"```python\n{user_code}\n```"
                    )

                    all_models = [
                        m.name
                        for m in genai.list_models()
                        if "generateContent" in m.supported_generation_methods
                    ]

                    valid_models = [
                        m for m in all_models if "2.5" not in m and "2.0" not in m
                    ]

                    if not valid_models:
                        target_model = (
                            all_models[0] if all_models else "models/gemini-1.5-flash"
                        )
                    else:
                        target_model = valid_models[0]

                    model = genai.GenerativeModel(target_model)
                    response = model.generate_content(prompt)

                    if response and response.text:
                        st.markdown(response.text)
                    else:
                        st.error("No response text returned.")

                except Exception as e:
                    st.error(f"Error Details: {str(e)}")