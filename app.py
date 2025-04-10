import streamlit as st
import json
import os
from datetime import datetime
import time
import io

# Set page configuration
st.set_page_config(
    page_title="Franchise Proposal Evaluator",
    page_icon="📊",
    layout="wide"
)

# Function to read the default heuristics model
@st.cache_data
def load_default_heuristics():
    try:
        with open('spinelli_heuristics_model', 'r') as f:
            return f.read()
    except Exception as e:
        st.warning(f"Could not load default heuristics model: {str(e)}")
        # Return a simplified model as fallback
        return json.dumps({
            "name": "Spinelli Heuristics Model",
            "dimensions": [
                "Market Opportunity Assessment",
                "Value Creation & Brand Positioning",
                "Operational Excellence & Knowledge Transfer",
                "Financial Structure & Alignment",
                "Leadership & Support Systems",
                "Adaptability & Growth Potential"
            ]
        })

# Define the evaluation framework
evaluation_framework = {
    "dimensions": [
        {
            "name": "Market Opportunity Assessment",
            "criteria": [
                "Market Demand Extrapolation: Evaluating potential demand across geographic regions",
                "Untapped Market Opportunity Recognition: Identifying underserved market segments",
                "Scale Velocity Imperative: Assessing the need for rapid scaling in replicable business models"
            ]
        },
        {
            "name": "Value Creation & Brand Positioning",
            "criteria": [
                "Value Cluster Analysis: Understanding the 3D relationships with stakeholders",
                "Community Business Model: Evaluating relationship-building vs. transaction-focused approaches",
                "Brand Promise Execution Discipline: Assessing commitment to delivering core value proposition"
            ]
        },
        {
            "name": "Operational Excellence & Knowledge Transfer",
            "criteria": [
                "Systematic Knowledge Capture: Evaluating documentation of processes and operational insights",
                "Network Innovation Acceleration: Assessing franchisee collaboration potential for innovation",
                "Work Hard Testing Heuristic: Evaluating performance assessment and quality control systems"
            ]
        },
        {
            "name": "Financial Structure & Alignment",
            "criteria": [
                "Capital-Asset Alignment Principle: Matching funding sources with business needs",
                "Fixed Cost Coverage Pricing: Analyzing pricing strategy based on cost structure",
                "Break-Even Timeline Analysis: Evaluating time to profitability and sustainability",
                "Harvest Planning Heuristic: Assessing long-term exit strategy potential"
            ]
        },
        {
            "name": "Leadership & Support Systems",
            "criteria": [
                "Partner First Mentality: Evaluating the franchise relationship as a partnership",
                "Partnership vs. Employment Mindset: Assessing franchise owner treatment approach",
                "Service Leadership Model: Examining accountability and support from franchisor"
            ]
        },
        {
            "name": "Adaptability & Growth Potential",
            "criteria": [
                "Dealing with Ambiguity Skill: Assessing how the franchise model handles uncertainty",
                "Problem-Opportunity Conversion: Evaluating ability to turn challenges into business growth",
                "Entrepreneurial Agility Imperative: Examining flexibility for adaptation in changing markets"
            ]
        }
    ]
}

# Function to extract text from different file types
def extract_text_from_file(file):
    file_extension = file.name.split('.')[-1].lower()
    file_content = None
    
    if file_extension in ['txt', 'md']:
        # For text files, simply read the content
        file_content = file.read().decode('utf-8', errors='ignore')
    
    elif file_extension == 'pdf':
        try:
            import PyPDF2
            from io import BytesIO
            
            pdf_file = BytesIO(file.read())
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            
            text = []
            for page_num in range(len(pdf_reader.pages)):
                text.append(pdf_reader.pages[page_num].extract_text())
            
            file_content = "\n\n".join(text)
        except Exception as e:
            st.error(f"Error processing PDF file {file.name}: {str(e)}")
            file_content = f"[Error extracting text from PDF: {str(e)}]"
    
    elif file_extension in ['docx', 'doc']:
        try:
            import docx
            from io import BytesIO
            
            doc_file = BytesIO(file.read())
            doc = docx.Document(doc_file)
            
            text = []
            for para in doc.paragraphs:
                text.append(para.text)
            
            file_content = "\n".join(text)
        except Exception as e:
            st.error(f"Error processing Word file {file.name}: {str(e)}")
            file_content = f"[Error extracting text from DOCX: {str(e)}]"
    
    else:
        file_content = f"[Unsupported file type: {file_extension}]"
    
    return file_content

# Function to create a prompt for Claude
def create_prompt(franchise_files, heuristics_content=None):
    # Process franchise proposal documents
    document_content = ""
    for file_name, file_content in franchise_files.items():
        document_content += f"<document>\n<source>{file_name}</source>\n<document_content>{file_content}</document_content>\n</document>\n\n"
    
    # Process heuristics model if provided
    if heuristics_content:
        heuristics_model = heuristics_content
    else:
        # Use default heuristics model from file
        heuristics_model = load_default_heuristics()
    
    # Create the prompt for Claude
    prompt = f"""
<documents>
{document_content}
</documents>

Here is a heuristics model:
{heuristics_model}

I want you to create a comprehensive franchise proposal evaluation based on Dr. Spinelli's heuristics framework. Please analyze the provided franchise proposal documents using the heuristics model to evaluate the franchise opportunity.

Your evaluation should include:

1. An analysis of the franchise opportunity across these six dimensions:
   - Market Opportunity Assessment
   - Value Creation & Brand Positioning
   - Operational Excellence & Knowledge Transfer
   - Financial Structure & Alignment
   - Leadership & Support Systems
   - Adaptability & Growth Potential

2. For each dimension, provide:
   - A rating (STRONG, MODERATE, or WEAK)
   - Key strengths (2-3)
   - Key weaknesses (2-3)
   - Supporting quotes from both Dr. Spinelli's heuristics and the franchise documents
   - Specific recommendations (2-3)

3. An overall rating (RECOMMENDED, PROCEED WITH CAUTION, or NOT RECOMMENDED)
4. An executive summary (250-300 words)
5. 5 final recommendations for a potential franchisee

Please structure your response in the following format:

# Franchise Proposal Evaluation: [Name of Franchise]

## Executive Summary
[Your summary here]

## Overall Rating: [RATING]

## Detailed Analysis

### Market Opportunity Assessment
**Rating**: [STRONG/MODERATE/WEAK]

**Strengths**:
- [Strength 1]
- [Strength 2]
- [Strength 3]

**Weaknesses**:
- [Weakness 1]
- [Weakness 2]
- [Weakness 3]

**Supporting Quotes**:
- "[Quote from Spinelli heuristic]" — Dr. Spinelli
- "[Quote from franchise document]" — Franchise Document

**Recommendations**:
- [Recommendation 1]
- [Recommendation 2]
- [Recommendation 3]

[Repeat this structure for each dimension]

## Final Recommendations
1. [Recommendation 1]
2. [Recommendation 2]
3. [Recommendation 3]
4. [Recommendation 4]
5. [Recommendation 5]
"""
    
    return prompt

# Function to display evaluation results with formatting
def display_evaluation_results(response_text):
    st.markdown(response_text)

# Main Streamlit UI
def main():
    st.title("Franchise Proposal Evaluator")
    st.subheader("Upload your franchise documents for a comprehensive analysis based on Dr. Spinelli's heuristics framework")
    
    # Create tabs
    tab1, tab2, tab3 = st.tabs(["Evaluation Framework", "Upload & Analyze", "Results"])
    
    # Tab 1: Evaluation Framework
    with tab1:
        st.header("Dr. Spinelli's Franchise Evaluation Framework")
        
        for i, dimension in enumerate(evaluation_framework["dimensions"]):
            with st.expander(f"{dimension['name']}", expanded=False):
                for criterion in dimension["criteria"]:
                    st.markdown(f"- {criterion}")
    
    # Tab 2: Upload & Analyze
    with tab2:
        st.header("Upload Documents")
        
        # Check for Claude API key in secrets
        if 'api_keys' in st.secrets and 'claude' in st.secrets.api_keys:
            api_key = st.secrets.api_keys.claude
            st.success("✅ Claude API key loaded from secrets")
        else:
            # If we can't find the key in secrets, show a more helpful message
            st.error("Claude API key not found in secrets. Please contact the administrator.")
            # Set a dummy key that won't work, just to avoid errors
            api_key = "not_found"
        
        # Model selection with default to recommended model
        model_options = ["claude-3-7-sonnet-20250219", "claude-3-5-sonnet-20240229", "claude-3-opus-20240229"]
        selected_model = st.selectbox("Claude Model", model_options, index=0, help="Select which Claude model to use")
        
        # Franchise document upload
        st.subheader("Franchise Proposal Documents")
        uploaded_files = st.file_uploader("Upload franchise proposal documents", 
                                          accept_multiple_files=True, 
                                          type=["txt", "md", "pdf", "docx", "doc"])
        
        # Display uploaded files
        if uploaded_files:
            st.subheader("Uploaded Files")
            files_container = st.container()
            with files_container:
                for file in uploaded_files:
                    st.text(f"📄 {file.name}")
        
        # Analyze button - disable if no API key or no files
        button_disabled = not uploaded_files or api_key == "not_found"
        
        if st.button("Analyze Franchise Proposal", disabled=button_disabled):
            if api_key == "not_found":
                st.error("API key not found. Please contact the administrator.")
            elif not uploaded_files:
                st.warning("Please upload at least one franchise document")
            else:
                # Process files
                franchise_files = {}
                
                # Create progress bar for file processing
                file_progress = st.progress(0)
                file_status = st.empty()
                
                # Process each file
                for i, file in enumerate(uploaded_files):
                    file_status.text(f"Processing file {i+1} of {len(uploaded_files)}: {file.name}")
                    
                    # Extract text from file
                    file_content = extract_text_from_file(file)
                    
                    # Add to files dictionary
                    franchise_files[file.name] = file_content
                    
                    # Update progress
                    file_progress.progress((i+1) / len(uploaded_files))
                
                file_status.text("All files processed successfully")
                
                # Create progress bar for analysis
                progress_bar = st.progress(0)
                
                # Create placeholder for status
                status_placeholder = st.empty()
                status_placeholder.text("Preparing documents for analysis...")
                progress_bar.progress(10)
                
                # Load default heuristics model
                heuristics_content = load_default_heuristics()
                
                # Generate prompt
                prompt = create_prompt(franchise_files, heuristics_content)
                progress_bar.progress(30)
                status_placeholder.text("Analyzing with Claude API...")
                
                # Call Claude API with selected model
                try:
                    # Import anthropic here directly
                    import anthropic
                    
                    # Try the older Client approach first (pre-1.0)
                    try:
                        # Check if the older Client class exists
                        if hasattr(anthropic, 'Client'):
                            client = anthropic.Client(api_key=api_key)
                            
                            # Use the selected model with older API format
                            constants_exist = hasattr(anthropic, 'HUMAN_PROMPT') and hasattr(anthropic, 'AI_PROMPT')
                            if constants_exist:
                                response = client.completion(
                                    prompt=f"{anthropic.HUMAN_PROMPT} {prompt} {anthropic.AI_PROMPT}",
                                    model=selected_model,
                                    max_tokens_to_sample=4000,
                                )
                                message_content = response['completion']
                            else:
                                st.error("Anthropic library version mismatch. Missing constants.")
                                raise Exception("Anthropic library version mismatch")
                        else:
                            raise AttributeError("Client class not found, trying newer API")
                    except (AttributeError, TypeError):
                        # For newer versions (1.0+)
                        client = anthropic.Anthropic(api_key=api_key)
                        
                        # Use the selected model
                        message = client.messages.create(
                            model=selected_model,
                            max_tokens=4000,
                            messages=[
                                {"role": "user", "content": prompt}
                            ]
                        )
                        message_content = message.content[0].text
                    # Store raw response in session state
                    st.session_state.raw_response = message_content
                    
                    # Update progress and status
                    progress_bar.progress(100)
                    status_placeholder.text("Analysis complete!")
                    
                    # Automatically switch to results tab
                    st.info("Analysis complete! Click on the 'Results' tab to view the evaluation.")
                    
                except Exception as e:
                    st.error(f"Error calling Claude API: {str(e)}")
                    progress_bar.progress(100)
    
    # Tab 3: Results
    with tab3:
        if 'raw_response' in st.session_state and st.session_state.raw_response:
            # Display formatted evaluation results
            display_evaluation_results(st.session_state.raw_response)
            
            # Download options
            st.header("Download Results")
            
            # Offer multiple download formats
            col1, col2 = st.columns(2)
            
            with col1:
                if st.download_button(
                    label="Download as Text",
                    data=st.session_state.raw_response,
                    file_name=f"franchise-evaluation-{datetime.now().strftime('%Y-%m-%d')}.txt",
                    mime="text/plain"
                ):
                    pass
            
            with col2:
                # Create a markdown version with better formatting
                if st.download_button(
                    label="Download as Markdown",
                    data=st.session_state.raw_response,
                    file_name=f"franchise-evaluation-{datetime.now().strftime('%Y-%m-%d')}.md",
                    mime="text/markdown"
                ):
                    pass
        else:
            st.info("No analysis results yet. Please upload documents and run analysis in the 'Upload & Analyze' tab.")

if __name__ == "__main__":
    main()
