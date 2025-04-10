import streamlit as st
import json
import os
from datetime import datetime
import time

# Set page configuration
st.set_page_config(
    page_title="Franchise Proposal Evaluator",
    page_icon="📊",
    layout="wide"
)

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
        # Use a simplified default heuristics model
        heuristics_model = json.dumps(evaluation_framework)
    
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
        
        # Claude API Key input
        api_key = st.text_input("Claude API Key", type="password", help="Enter your Claude API key")
        
        # Model selection with default to recommended model
        model_options = ["claude-3-7-sonnet-20250219", "claude-3-5-sonnet-20240229", "claude-3-opus-20240229"]
        selected_model = st.selectbox("Claude Model", model_options, index=0, help="Select which Claude model to use")
        
        # Franchise document upload
        st.subheader("Franchise Proposal Documents")
        uploaded_files = st.file_uploader("Upload franchise proposal documents", 
                                          accept_multiple_files=True, 
                                          type=["txt", "md"])
        
        # Heuristics model upload (optional)
        st.subheader("Heuristics Model (Optional)")
        heuristics_file = st.file_uploader("Upload custom heuristics model", 
                                         type=["json", "txt"], 
                                         help="If not provided, we'll use our standard heuristics model")
        
        # Display uploaded files
        if uploaded_files:
            st.subheader("Uploaded Files")
            for file in uploaded_files:
                st.text(f"📄 {file.name}")
        
        # Analyze button
        if st.button("Analyze Franchise Proposal", disabled=not (api_key and uploaded_files)):
            if not api_key:
                st.warning("Please enter your Claude API key")
            elif not uploaded_files:
                st.warning("Please upload at least one franchise document")
            else:
                # Process files
                franchise_files = {}
                for file in uploaded_files:
                    # Read file content as text
                    file_content = file.read().decode("utf-8", errors="ignore")
                    franchise_files[file.name] = file_content
                
                # Read heuristics model if provided
                heuristics_content = None
                if heuristics_file:
                    heuristics_content = heuristics_file.read().decode("utf-8", errors="ignore")
                
                # Create progress bar
                progress_bar = st.progress(0)
                
                # Create placeholder for status
                status_placeholder = st.empty()
                status_placeholder.text("Preparing documents for analysis...")
                progress_bar.progress(10)
                
                # Generate prompt
                prompt = create_prompt(franchise_files, heuristics_content)
                progress_bar.progress(30)
                status_placeholder.text("Analyzing with Claude API...")
                
                # Call Claude API with selected model
                try:
                    # Import anthropic here directly
                    import anthropic
                    
                    client = anthropic.Anthropic(api_key=api_key)
                    
                    # Use the selected model
                    message = client.messages.create(
                        model=selected_model,  # Use selected model from dropdown
                        max_tokens=4000,
                        messages=[
                            {"role": "user", "content": prompt}
                        ]
                    )
                    response = message.content[0].text
                    
                    # Store raw response in session state
                    st.session_state.raw_response = response
                    
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
            st.markdown(st.session_state.raw_response)
            
            # Download options
            st.header("Download Results")
            
            if st.download_button(
                label="Download as Text",
                data=st.session_state.raw_response,
                file_name=f"franchise-evaluation-{datetime.now().strftime('%Y-%m-%d')}.txt",
                mime="text/plain"
            ):
                pass
        else:
            st.info("No analysis results yet. Please upload documents and run analysis in the 'Upload & Analyze' tab.")

if __name__ == "__main__":
    main()