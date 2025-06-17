import streamlit as st
import requests
import json
import time
from datetime import datetime
from openai import OpenAI
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from io import BytesIO
import os

# Configure Streamlit page
st.set_page_config(
    page_title="Question Paper Generator",
    page_icon="📝",
    layout="wide",
    initial_sidebar_state="expanded"
)



openai_api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=openai_api_key)

# API Endpoints
TEXTRACT_API_URL = os.getenv("TEXTRACT_API_URL")

def analyze_papers_with_syllabus(paper_texts, subject_name, syllabus, course_objectives):
    """Enhanced GPT analysis with syllabus and COs"""
    try:
        paper1_text = paper_texts[0]['extracted_text']
        paper2_text = paper_texts[1]['extracted_text']
        
        system_prompt = """You are an expert educational assessment analyst. Your task is to analyze question papers against a given syllabus and course objectives.

CRITICAL: Your job is to EXTRACT and ANALYZE the exact patterns from the sample papers, then use the FULL SYLLABUS scope for generation planning.

Analyze the papers for:
1. Structural compatibility and format consistency
2. EXACT question type distribution observed in papers (numerical vs theoretical vs mixed)
3. Internal choice patterns (1a/1b format recognition)
4. Bloom's taxonomy distribution (CRITICAL for engineering education)
5. Difficulty distribution as observed
6. Topic coverage analysis: Sample papers vs Complete syllabus
7. Generate detailed structure for FULL SYLLABUS coverage

Return analysis in this EXACT JSON format:

{
    "are_compatible": true/false,
    "compatibility_reason": "detailed explanation",
    "compatibility_score": 85,
    "subject_analysis": {
        "subject_name": "extracted subject name",
        "syllabus_coverage": {
            "total_topics_in_syllabus": 12,
            "topics_in_sample_papers": 6,
            "sample_coverage_percentage": 50,
            "uncovered_topics_in_samples": ["Topic A", "Topic B"],
            "topics_in_sample_papers": ["Topic C", "Topic D"],
            "full_syllabus_topics": ["All extracted topics from complete syllabus"]
        },
        "question_style_analysis": {
            "numerical_problems_percentage": 65,
            "theoretical_questions_percentage": 25,
            "mixed_questions_percentage": 10,
            "internal_choice_pattern": "1a/1b format in each section",
            "typical_question_formats": ["State and prove...", "Calculate the...", "Determine the..."]
        },
        "co_alignment": {
            "total_cos": 4,
            "cos_covered_in_samples": ["CO1", "CO2", "CO3"],
            "co_distribution_observed": {
                "CO1": 35,
                "CO2": 30,
                "CO3": 25,
                "CO4": 10
            },
            "co_alignment_score": 78
        }
    },
    "common_structure": {
        "exam_info": {
            "exam_type": "midterm_exam",
            "subject_name": "Engineering Mechanics",
            "total_marks": 40,
            "exam_duration_minutes": 120,
            "total_questions": 8,
            "instruction_text": "Answer any ONE question from each unit"
        },
        "sections": [
            {
                "section_id": "UNIT-I",
                "section_name": "Unit I Questions", 
                "section_instruction": "Answer any ONE question from this unit",
                "question_count": 2,
                "marks_per_question": 20,
                "total_section_marks": 20,
                "question_type": "long_answer",
                "is_compulsory": false,
                "has_internal_choice": true,
                "internal_choice_format": "1a/1b - student picks ONE complete question",
                "questions_to_answer": 1,
                "observed_topics": ["Statics", "Force Systems"],
                "question_style_distribution": {
                    "numerical_problems": 70,
                    "theoretical": 20,
                    "mixed": 10
                },
                "difficulty_distribution": {
                    "easy": 20,
                    "medium": 60,
                    "hard": 20
                },
                "bloom_distribution": {
                    "Remember": 10,
                    "Understand": 20,
                    "Apply": 50,
                    "Analyze": 20,
                    "Evaluate": 0,
                    "Create": 0
                },
                "co_distribution": {
                    "CO1": 70,
                    "CO2": 30
                }
            }
        ],
        "overall_distributions": {
            "difficulty_distribution": {
                "easy": 25,
                "medium": 55,
                "hard": 20
            },
            "bloom_distribution": {
                "Remember": 15,
                "Understand": 25,
                "Apply": 35,
                "Analyze": 25,
                "Evaluate": 0,
                "Create": 0
            },
            "co_distribution": {
                "CO1": 30,
                "CO2": 25,
                "CO3": 25,
                "CO4": 20
            },
            "question_type_distribution": {
                "numerical_problems": 65,
                "theoretical": 25,
                "mixed": 10
            }
        }
    },
    "generation_ready": {
        "can_generate": true,
        "generation_confidence": 85,
        "recommended_adjustments": ["Balance CO4 coverage", "Add more analytical questions"],
        "full_syllabus_utilization": "ready to use complete syllabus for topic diversity"
    }
}

Analysis Rules:
- Extract EXACT patterns from sample papers (don't impose artificial distributions)
- Use sample papers for FORMAT/STRUCTURE learning
- Identify complete syllabus scope for CONTENT generation
- Recognize internal choice patterns precisely
- Analyze actual question styles and formats used"""

        user_prompt = f"""Analyze these question papers against the subject syllabus and course objectives:

SUBJECT: {subject_name}

COMPLETE SYLLABUS (for full topic scope):
{syllabus}

COURSE OBJECTIVES:
{course_objectives}

PAPER 1 ({paper_texts[0]['filename']}) - {paper_texts[0]['text_length']} characters:
=== OCR EXTRACTED TEXT START ===
{paper1_text}
=== OCR EXTRACTED TEXT END ===

PAPER 2 ({paper_texts[1]['filename']}) - {paper_texts[1]['text_length']} characters:
=== OCR EXTRACTED TEXT START ===
{paper2_text}
=== OCR EXTRACTED TEXT END ===

CRITICAL ANALYSIS POINTS:
1. Extract EXACT question format patterns from sample papers
2. Identify actual question type distributions (numerical vs theoretical)
3. Recognize internal choice structures (1a/1b patterns)
4. Compare sample paper topics vs COMPLETE syllabus scope
5. Plan for using FULL SYLLABUS in generation (not just sample topics)
6. Maintain observed Bloom's taxonomy emphasis

Provide comprehensive analysis for generating papers that follow sample STRUCTURE but cover FULL SYLLABUS."""

        response = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.1,
            max_tokens=8000,
            response_format={"type": "json_object"}
        )
        
        analysis_text = response.choices[0].message.content
        structure_analysis = json.loads(analysis_text)
        
        return structure_analysis
        
    except Exception as e:
        st.error(f"Error in structure analysis: {str(e)}")
        return None

def generate_question_bank(calibrated_structure, questions_per_section=25):
    """Generate comprehensive question bank organized section-wise"""
    try:
        system_prompt = """You are an expert question bank generator. Create a comprehensive pool of questions organized by sections.

Generate question banks that:
1. Cover COMPLETE SYLLABUS topics extensively
2. Provide variety in question formats and approaches
3. Include proper difficulty distribution per section
4. Maintain Bloom's taxonomy and CO coverage
5. Zero duplication within the question bank
6. Include proper numerical values and visual aids
7. Create questions suitable for mix-and-match paper assembly

VISUAL HANDLING (same as paper generation):
- ASCII diagrams for simple geometries
- Detailed descriptions for complex cases
- Complete numerical data with units
- Professional question formatting

Return response in this JSON format:

{
    "question_bank": {
        "UNIT-I": [
            {
                "question_id": "U1_Q001",
                "question_text": "A cantilever beam of length 4m carries a point load of 15kN at free end...",
                "visual_aid": {
                    "type": "ascii",
                    "content": "ASCII diagram here",
                    "visualization_guide": "Description for visualization"
                },
                "given_data": ["Length L = 4m", "Load P = 15kN", "E = 200 GPa"],
                "find": "Maximum deflection and slope",
                "marks": 10,
                "difficulty": "easy",
                "bloom_level": "Apply",
                "co": "CO1",
                "topic": "Deflection of Beams",
                "question_type": "numerical_problem",
                "solution_approach": "Use double integration method or standard formulas"
            }
        ]
    },
    "bank_summary": {
        "total_questions_generated": 50,
        "questions_per_section": {"UNIT-I": 25, "UNIT-II": 25},
        "difficulty_distribution": {"easy": 40, "medium": 40, "hard": 20},
        "bloom_distribution": {"Remember": 15, "Understand": 25, "Apply": 35, "Analyze": 25},
        "co_distribution": {"CO1": 25, "CO2": 25, "CO3": 25, "CO4": 25},
        "question_type_distribution": {"numerical": 60, "theoretical": 30, "mixed": 10},
        "topics_covered": ["Complete list of all topics covered"],
        "syllabus_utilization": "85% of complete syllabus covered"
    }
}"""

        user_prompt = f"""Generate a comprehensive question bank based on this calibrated structure:

CALIBRATED STRUCTURE:
{json.dumps(calibrated_structure, indent=2)}

QUESTION BANK REQUIREMENTS:
- Generate {questions_per_section} questions per section
- Cover MAXIMUM topics from complete syllabus
- Difficulty distribution per section: 40% Easy, 40% Medium, 20% Hard
- Follow calibrated Bloom's and CO distributions
- Include variety: numerical problems, theoretical questions, mixed types
- Ensure zero duplication across entire question bank
- Maintain professional engineering question format

QUALITY STANDARDS:
- Each question must be complete and solvable
- Include proper visual aids (ASCII/descriptions) where needed
- Provide realistic numerical values with units
- Cover diverse topics within each section
- Suitable for educators to pick and choose for paper assembly"""

        response = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.4,
            max_tokens=16000,
            response_format={"type": "json_object"}
        )
        
        question_bank_result = json.loads(response.choices[0].message.content)
        return question_bank_result
        
    except Exception as e:
        st.error(f"Error generating question bank: {str(e)}")
        return None

def generate_question_papers(calibrated_structure, num_papers=5):
    """Generate question papers based on calibrated structure"""
    try:
        system_prompt = """You are an expert question paper generator. Create unique, high-quality question papers based on the provided structure and specifications.

Generate question papers that:
1. Follow the EXACT structure and format patterns from sample papers
2. Have zero duplication across papers  
3. Use COMPLETE SYLLABUS scope for topic coverage (not just sample paper topics)
4. Maintain observed question style distributions (numerical vs theoretical)
5. Preserve internal choice format exactly (1a/1b where student picks ONE)
6. Follow specified difficulty progression across papers
7. Maintain proper Bloom's taxonomy and CO distributions
8. Create realistic questions matching the subject's typical formats
9. Include proper numerical values in numerical problems
10. Handle visual requirements intelligently

VISUAL HANDLING REQUIREMENTS:
- Generate ALL question types without limitation
- For questions needing visuals, choose appropriate method:

METHOD A - ASCII DIAGRAMS (for simple cases):
- Simple beams, basic trusses, elementary circuits, basic loading
- Use symbols: █ (fixed support), ▲ (pinned), ○ (roller), ↑↓←→ (forces), ──── (beams), ● (point loads), ████ (distributed loads)
- Keep clean and readable

METHOD B - DETAILED DESCRIPTIONS (for complex cases):
- Complex geometries, 3D structures, detailed mechanisms
- Provide comprehensive visualization guidance
- Include all dimensions, orientations, relationships

NUMERICAL PROBLEM REQUIREMENTS:
- Include specific numerical values with proper units
- Provide complete given data
- Use realistic engineering values
- Format as "Given: ..., Find: ..., Calculate: ..."

EXAMPLES:

ASCII SUITABLE:
"A simply supported beam carries loads as shown:
     15kN ↓    25kN ↓
A ────●────●──── B
█    2m   3m   █
|──────8m────────|
Given: E = 200 GPa, I = 150×10⁶ mm⁴
Find: (a) Reactions at supports (b) Maximum bending moment"

DESCRIPTION SUITABLE:
"A compound planetary gear system has: Sun gear (30 teeth) at center, three planet gears (20 teeth each) equally spaced around sun gear, ring gear (70 teeth) surrounding the system. Planet carrier rotates at 500 RPM clockwise. Sun gear is fixed. Calculate: (a) Speed of ring gear (b) Gear ratio of the system."

Return response in this JSON format:

{
    "generated_papers": [
        {
            "paper_id": "Paper_Set_1_Easy",
            "difficulty_level": "Easy",
            "total_marks": 40,
            "exam_duration": 120,
            "instructions": "Answer any ONE question from each unit",
            "sections": [
                {
                    "section_id": "UNIT-I",
                    "section_name": "Unit I Questions",
                    "questions": [
                        {
                            "question_group": "1",
                            "internal_choice": true,
                            "choice_instruction": "Answer any ONE question from this group",
                            "options": [
                                {
                                    "question_number": "1a",
                                    "question_text": "A steel cantilever beam AB of length 3m carries a uniformly distributed load of 20 kN/m over its entire span. Given: E = 200 GPa, I = 120×10⁶ mm⁴. Calculate: (a) Maximum deflection (b) Maximum slope",
                                    "visual_aid": {
                                        "type": "ascii",
                                        "content": "████████████ ← 20 kN/m UDL\nA ────────────── B\n█               (free end)\n|─────3m───────|\nFixed support",
                                        "visualization_guide": "Cantilever beam fixed at A, free at B, with uniform load across entire span"
                                    },
                                    "given_data": ["Length L = 3m", "UDL w = 20 kN/m", "E = 200 GPa", "I = 120×10⁶ mm⁴"],
                                    "find": "Maximum deflection and slope",
                                    "marks": 10,
                                    "co": "CO1",
                                    "bloom_level": "Apply",
                                    "difficulty": "easy",
                                    "topic": "Topic from full syllabus",
                                    "question_type": "numerical_problem"
                                },
                                {
                                    "question_number": "1b",
                                    "question_text": "A compound gear train system consists of: Input shaft with Gear A (25 teeth, 1200 RPM clockwise), meshing with Gear B (75 teeth) on intermediate shaft. Same intermediate shaft has Gear C (20 teeth) meshing with output Gear D (80 teeth). Calculate: (a) Speed of intermediate shaft (b) Final output speed and direction (c) Overall gear ratio",
                                    "visual_aid": {
                                        "type": "description",
                                        "content": "Visualize a compound gear train: Left side has input shaft (vertical) with small Gear A meshing with large Gear B on horizontal intermediate shaft. Right side of same intermediate shaft has small Gear C meshing with large output Gear D on vertical output shaft. Power flows: Input → A → B → Intermediate shaft → C → D → Output",
                                        "visualization_guide": "Draw three parallel shafts: input (left), intermediate (center horizontal), output (right). Show gear pairs A-B and C-D with size proportional to teeth count"
                                    },
                                    "given_data": ["Gear A: 25 teeth, 1200 RPM CW", "Gear B: 75 teeth", "Gear C: 20 teeth", "Gear D: 80 teeth"],
                                    "find": "Intermediate shaft speed, output speed and direction, overall gear ratio",
                                    "marks": 10,
                                    "co": "CO1", 
                                    "bloom_level": "Apply",
                                    "difficulty": "easy",
                                    "topic": "Different topic from full syllabus",
                                    "question_type": "numerical_problem"
                                }
                            ]
                        }
                    ]
                }
            ]
        }
    ],
    "generation_summary": {
        "total_papers_generated": 5,
        "unique_questions_created": 40,
        "topics_covered": ["Full list of topics used from complete syllabus"],
        "cos_covered": ["CO1", "CO2", "CO3"],
        "difficulty_progression": "Easy to Hard across papers",
        "syllabus_utilization": "Covered X% of complete syllabus across all papers"
    }
}"""

        user_prompt = f"""Generate {num_papers} unique question papers based on this calibrated structure:

CALIBRATED STRUCTURE:
{json.dumps(calibrated_structure, indent=2)}

GENERATION REQUIREMENTS:
- Paper 1: Easy level
- Paper 2: Easy-Medium level  
- Paper 3: Medium level
- Paper 4: Medium-Hard level
- Paper 5: Hard level
- ZERO question duplication across all papers
- Use COMPLETE SYLLABUS for topic diversity (not just sample paper topics)
- Maintain EXACT internal choice format from samples (1a/1b where applicable)
- Follow observed question style patterns (numerical vs theoretical ratios)
- Maintain proper section-wise distributions as calibrated
- Cover maximum possible topics from the full syllabus across all papers

CRITICAL VISUAL & NUMERICAL REQUIREMENTS:
- For NUMERICAL problems: Include specific values, units, realistic engineering data
- For questions needing visuals: Choose ASCII for simple geometries, detailed descriptions for complex cases
- ASCII examples: Simple beams, basic trusses, elementary loading diagrams
- Description examples: Complex 3D structures, multi-component systems, detailed mechanisms
- Every numerical question must have: Given data, Find statement, specific numerical values
- Ensure students can visualize and solve with provided information alone

QUALITY STANDARDS:
- Questions must be completely solvable with provided text/ASCII/descriptions
- No missing information or ambiguous setups
- Professional engineering question format
- Appropriate difficulty progression across papers"""

        response = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.3,
            max_tokens=16000,
            response_format={"type": "json_object"}
        )
        
        generation_result = json.loads(response.choices[0].message.content)
        return generation_result
        
    except Exception as e:
        st.error(f"Error generating papers: {str(e)}")
        return None

def upload_files_to_textract(file1, file2, csm_id="default_subject"):
    """Upload files to Textract API and get extracted text"""
    try:
        files = {
            'paper1': (file1.name, file1.getvalue(), 'application/pdf'),
            'paper2': (file2.name, file2.getvalue(), 'application/pdf')
        }
        data = {'csm_id': csm_id, 'mode':'1'}
        
        with st.spinner("🔍 Extracting text using Textract... This may take a few minutes."):
            response = requests.post(TEXTRACT_API_URL, files=files, data=data, timeout=500)
        
        if response.status_code == 200:
            response_data = response.json()
            if 'results' in response_data:
                return response_data
            elif 'body' in response_data:
                body_data = response_data['body']
                if isinstance(body_data, str):
                    body_data = json.loads(body_data)
                return body_data
            else:
                st.error("Unexpected response format from Textract API")
                return None
        else:
            st.error(f"Textract API error: {response.status_code} - {response.text}")
            return None
            
    except requests.exceptions.Timeout:
        st.error("⏰ Request timed out. Textract processing took too long.")
        return None
    except Exception as e:
        st.error(f"❌ Error uploading to Textract: {str(e)}")
        return None

def display_and_edit_analysis(analysis_result):
    """Display analysis results with editable fields for calibration"""
    st.subheader("📊 Analysis Results & Calibration")
    
    if not analysis_result.get('are_compatible'):
        st.error("❌ Papers are NOT compatible")
        st.write(f"**Reason:** {analysis_result.get('compatibility_reason', 'Unknown')}")
        return None, False
    
    score = analysis_result.get('compatibility_score', 0)
    st.success(f"✅ Papers are compatible! Compatibility Score: {score}%")
    
    # Subject Analysis
    subject_analysis = analysis_result.get('subject_analysis', {})
    syllabus_coverage = subject_analysis.get('syllabus_coverage', {})
    co_alignment = subject_analysis.get('co_alignment', {})
    question_style = subject_analysis.get('question_style_analysis', {})
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.subheader("📚 Syllabus Analysis")
        sample_coverage = syllabus_coverage.get('sample_coverage_percentage', 0)
        st.metric("Sample Coverage", f"{sample_coverage}%")
        st.write(f"**Full Syllabus Topics:** {len(syllabus_coverage.get('full_syllabus_topics', []))}")
        st.write(f"**Sample Paper Topics:** {len(syllabus_coverage.get('topics_in_sample_papers', []))}")
    
    with col2:
        st.subheader("🎯 CO Alignment")
        co_score = co_alignment.get('co_alignment_score', 0)
        st.metric("CO Alignment", f"{co_score}%")
        
        co_dist = co_alignment.get('co_distribution_observed', {})
        if co_dist:
            st.write("**Observed CO Distribution:**")
            for co, pct in co_dist.items():
                st.write(f"• {co}: {pct}%")
    
    with col3:
        st.subheader("📝 Question Style Analysis")
        numerical_pct = question_style.get('numerical_problems_percentage', 0)
        theoretical_pct = question_style.get('theoretical_questions_percentage', 0)
        st.metric("Numerical Problems", f"{numerical_pct}%")
        st.metric("Theoretical Questions", f"{theoretical_pct}%")
        st.write(f"**Internal Choice:** {question_style.get('internal_choice_pattern', 'Not detected')}")
    
    # Editable Structure
    st.subheader("⚙️ Calibrate Generation Parameters")
    
    common_structure = analysis_result.get('common_structure', {})
    exam_info = common_structure.get('exam_info', {})
    
    with st.form("calibration_form"):
        st.write("### 📝 Exam Information")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            total_marks = st.number_input(
                "Total Marks", 
                min_value=20, 
                max_value=100, 
                value=exam_info.get('total_marks', 40),
                step=5
            )
        
        with col2:
            duration = st.number_input(
                "Duration (minutes)", 
                min_value=60, 
                max_value=300, 
                value=exam_info.get('exam_duration_minutes', 120),
                step=15
            )
        
        with col3:
            num_papers = st.number_input(
                "Papers to Generate", 
                min_value=1, 
                max_value=10, 
                value=5,
                step=1
            )
        
        instruction_text = st.text_area(
            "Instructions", 
            value=exam_info.get('instruction_text', 'Answer any ONE question from each unit'),
            height=68
        )
        
        st.write("### 📊 Section-wise Distribution Settings")
        
        sections = common_structure.get('sections', [])
        section_configs = []
        
        for i, section in enumerate(sections):
            st.write(f"#### {section.get('section_id', f'Section {i+1}')} Configuration")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                q_count = st.number_input(
                    f"Questions in {section.get('section_id', f'Section {i+1}')}",
                    min_value=1,
                    max_value=10,
                    value=section.get('question_count', 2),
                    key=f"q_count_{i}"
                )
            
            with col2:
                section_marks = st.number_input(
                    f"Section Marks",
                    min_value=5,
                    max_value=50,
                    value=section.get('total_section_marks', 20),
                    key=f"marks_{i}"
                )
            
            with col3:
                has_choice = st.checkbox(
                    "Internal Choice",
                    value=section.get('has_internal_choice', True),
                    key=f"choice_{i}"
                )
            
            # Section-wise distributions
            col1, col2 = st.columns(2)
            
            with col1:
                st.write(f"**{section.get('section_id', f'Section {i+1}')} - Difficulty Distribution (%)**")
                section_diff = section.get('difficulty_distribution', {})
                easy_pct = st.slider(f"Easy", 0, 100, section_diff.get('easy', 25), key=f"easy_{i}")
                medium_pct = st.slider(f"Medium", 0, 100, section_diff.get('medium', 55), key=f"medium_{i}")
                hard_pct = st.slider(f"Hard", 0, 100, section_diff.get('hard', 20), key=f"hard_{i}")
                
                if easy_pct + medium_pct + hard_pct != 100:
                    st.warning(f"⚠️ Section {section.get('section_id', f'{i+1}')} Total: {easy_pct + medium_pct + hard_pct}%")
            
            with col2:
                st.write(f"**{section.get('section_id', f'Section {i+1}')} - Bloom's Distribution (%)**")
                section_bloom = section.get('bloom_distribution', {})
                remember_pct = st.slider(f"Remember", 0, 100, section_bloom.get('Remember', 10), key=f"remember_{i}")
                understand_pct = st.slider(f"Understand", 0, 100, section_bloom.get('Understand', 20), key=f"understand_{i}")
                apply_pct = st.slider(f"Apply", 0, 100, section_bloom.get('Apply', 40), key=f"apply_{i}")
                analyze_pct = st.slider(f"Analyze", 0, 100, section_bloom.get('Analyze', 30), key=f"analyze_{i}")
                
                bloom_total = remember_pct + understand_pct + apply_pct + analyze_pct
                if bloom_total != 100:
                    st.warning(f"⚠️ Section {section.get('section_id', f'{i+1}')} Bloom's Total: {bloom_total}%")
            
            # Question style distribution
            st.write(f"**{section.get('section_id', f'Section {i+1}')} - Question Style Distribution (%)**")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                style_dist = section.get('question_style_distribution', {})
                numerical_pct = st.slider(f"Numerical Problems", 0, 100, style_dist.get('numerical_problems', 60), key=f"numerical_{i}")
            with col2:
                theoretical_pct = st.slider(f"Theoretical", 0, 100, style_dist.get('theoretical', 30), key=f"theoretical_{i}")
            with col3:
                mixed_pct = st.slider(f"Mixed Questions", 0, 100, style_dist.get('mixed', 10), key=f"mixed_{i}")
            
            style_total = numerical_pct + theoretical_pct + mixed_pct
            if style_total != 100:
                st.warning(f"⚠️ Section {section.get('section_id', f'{i+1}')} Style Total: {style_total}%")
            
            section_configs.append({
                'section_id': section.get('section_id', f'Section {i+1}'),
                'question_count': q_count,
                'total_section_marks': section_marks,
                'has_internal_choice': has_choice,
                'internal_choice_format': section.get('internal_choice_format', '1a/1b'),
                'topics_covered': section.get('observed_topics', []),
                'difficulty_distribution': {
                    'easy': easy_pct,
                    'medium': medium_pct,
                    'hard': hard_pct
                },
                'bloom_distribution': {
                    'Remember': remember_pct,
                    'Understand': understand_pct,
                    'Apply': apply_pct,
                    'Analyze': analyze_pct
                },
                'question_style_distribution': {
                    'numerical_problems': numerical_pct,
                    'theoretical': theoretical_pct,
                    'mixed': mixed_pct
                }
            })
            
            st.divider()
        
        # Overall CO Distribution
        st.write("### 🎯 Overall Course Objective Distribution")
        overall_dist = common_structure.get('overall_distributions', {})
        co_dist = overall_dist.get('co_distribution', {})
        
        co_values = {}
        total_co_pct = 0
        co_cols = st.columns(len(co_dist) if co_dist else 4)
        
        for idx, (co, default_pct) in enumerate(co_dist.items() if co_dist else [('CO1', 25), ('CO2', 25), ('CO3', 25), ('CO4', 25)]):
            with co_cols[idx % len(co_cols)]:
                co_values[co] = st.slider(co, 0, 100, default_pct, key=f"co_{co}")
                total_co_pct += co_values[co]
        
        if total_co_pct != 100:
            st.warning(f"⚠️ Total CO Distribution: {total_co_pct}% (should be 100%)")
        
        submitted = st.form_submit_button("✅ Confirm Calibration & Prepare Generation", type="primary")
        
        if submitted:
            # Build calibrated structure
            calibrated_structure = {
                "exam_info": {
                    "total_marks": total_marks,
                    "exam_duration_minutes": duration,
                    "instruction_text": instruction_text,
                    "subject_name": exam_info.get('subject_name', 'Unknown Subject')
                },
                "sections": section_configs,
                "overall_distributions": {
                    "co_distribution": co_values
                },
                "generation_params": {
                    "num_papers": num_papers,
                    "full_syllabus_topics": syllabus_coverage.get('full_syllabus_topics', []),
                    "sample_paper_topics": syllabus_coverage.get('topics_in_sample_papers', []),
                    "course_objectives": list(co_values.keys()),
                    "question_style_patterns": question_style.get('typical_question_formats', []),
                    "use_full_syllabus_scope": True
                }
            }
            
            return calibrated_structure, True
    
    return None, False

def display_generated_papers(generation_result):
    """Display generated question papers with download options"""
    st.subheader("📄 Generated Question Papers")
    
    if not generation_result:
        st.error("❌ No papers were generated")
        return
    
    generated_papers = generation_result.get('generated_papers', [])
    generation_summary = generation_result.get('generation_summary', {})
    
    # Summary metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Papers Generated", generation_summary.get('total_papers_generated', 0))
    with col2:
        st.metric("Unique Questions", generation_summary.get('unique_questions_created', 0))
    with col3:
        st.metric("Topics Covered", len(generation_summary.get('topics_covered', [])))
    with col4:
        st.metric("COs Covered", len(generation_summary.get('cos_covered', [])))
    
    if 'syllabus_utilization' in generation_summary:
        st.info(f"📚 **Syllabus Utilization:** {generation_summary['syllabus_utilization']}")
    
    st.success("✅ All papers generated successfully!")
    
    # Display each paper
    for i, paper in enumerate(generated_papers):
        with st.expander(f"📋 {paper.get('paper_id', f'Paper {i+1}')} - {paper.get('difficulty_level', 'Unknown')} Level"):
            
            # Paper header info
            col1, col2, col3 = st.columns(3)
            with col1:
                st.write(f"**Total Marks:** {paper.get('total_marks', 0)}")
            with col2:
                st.write(f"**Duration:** {paper.get('exam_duration', 0)} minutes")
            with col3:
                st.write(f"**Difficulty:** {paper.get('difficulty_level', 'Unknown')}")
            
            st.write(f"**Instructions:** {paper.get('instructions', '')}")
            
            # Display questions by section
            sections = paper.get('sections', [])
            for section in sections:
                st.write(f"### {section.get('section_id', 'Section')}: {section.get('section_name', '')}")
                
                questions = section.get('questions', [])
                for q_group in questions:
                    if q_group.get('internal_choice', False):
                        st.write(f"**{q_group.get('choice_instruction', 'Choose one option')}**")
                        
                        for option in q_group.get('options', []):
                            col1, col2, col3, col4, col5 = st.columns([3, 1, 1, 1, 1])
                            
                            with col1:
                                st.write(f"**{option.get('question_number', '')}** {option.get('question_text', '')}")
                                
                                # Display visual aid if present
                                visual_aid = option.get('visual_aid', {})
                                if visual_aid and visual_aid.get('content'):
                                    if visual_aid.get('type') == 'ascii':
                                        st.code(visual_aid['content'], language=None)
                                    else:
                                        st.info(f"📝 **Visualization Guide:** {visual_aid['content']}")
                                
                                # Display given data if present
                                given_data = option.get('given_data', [])
                                if given_data:
                                    st.write("**Given:**")
                                    for item in given_data:
                                        st.write(f"• {item}")
                                
                                # Display what to find
                                find_text = option.get('find', '')
                                if find_text:
                                    st.write(f"**Find:** {find_text}")
                                    
                            with col2:
                                st.write(f"**{option.get('marks', 0)} marks**")
                            with col3:
                                st.write(f"{option.get('co', '')}")
                            with col4:
                                st.write(f"{option.get('bloom_level', '')}")
                            with col5:
                                st.write(f"{option.get('question_type', '')}")
                                
                            st.divider()
                    else:
                        # Direct questions without internal choice
                        col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
                        
                        with col1:
                            st.write(f"**{q_group.get('question_number', '')}** {q_group.get('question_text', '')}")
                            
                            # Display visual aid if present
                            visual_aid = q_group.get('visual_aid', {})
                            if visual_aid and visual_aid.get('content'):
                                if visual_aid.get('type') == 'ascii':
                                    st.code(visual_aid['content'], language=None)
                                else:
                                    st.info(f"📝 **Visualization Guide:** {visual_aid['content']}")
                            
                            # Display given data if present
                            given_data = q_group.get('given_data', [])
                            if given_data:
                                st.write("**Given:**")
                                for item in given_data:
                                    st.write(f"• {item}")
                            
                            # Display what to find
                            find_text = q_group.get('find', '')
                            if find_text:
                                st.write(f"**Find:** {find_text}")
                                
                        with col2:
                            st.write(f"**{q_group.get('marks', 0)} marks**")
                        with col3:
                            st.write(f"{q_group.get('co', '')}")
                        with col4:
                            st.write(f"{q_group.get('bloom_level', '')}")
                            
                        st.divider()
    
    # Download options
    st.subheader("💾 Download Options")
    
    col1, col2 = st.columns(2)
    
    with col1:
        json_data = json.dumps(generation_result, indent=2)
        st.download_button(
            label="📥 Download All Papers (JSON)",
            data=json_data,
            file_name=f"generated_papers_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json",
            type="secondary",
            use_container_width=True
        )
    
    with col2:
        st.button("📄 Generate PDF Downloads", type="secondary", use_container_width=True, 
                 help="PDF generation feature - coming soon!")

def display_question_bank(question_bank_result):
    """Display generated question bank with filtering and download options"""
    st.subheader("📊 Generated Question Bank")
    
    if not question_bank_result:
        st.error("❌ No question bank was generated")
        return
    
    question_bank = question_bank_result.get('question_bank', {})
    bank_summary = question_bank_result.get('bank_summary', {})
    
    # Summary metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Questions", bank_summary.get('total_questions_generated', 0))
    with col2:
        st.metric("Sections", len(question_bank))
    with col3:
        st.metric("Topics Covered", len(bank_summary.get('topics_covered', [])))
    with col4:
        st.metric("Syllabus Utilization", bank_summary.get('syllabus_utilization', 'Unknown'))
    
    # Distribution info
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Difficulty Distribution:**")
        diff_dist = bank_summary.get('difficulty_distribution', {})
        for level, pct in diff_dist.items():
            st.write(f"• {level.title()}: {pct}%")
    
    with col2:
        st.write("**Question Type Distribution:**")
        type_dist = bank_summary.get('question_type_distribution', {})
        for qtype, pct in type_dist.items():
            st.write(f"• {qtype.title()}: {pct}%")
    
    st.success("✅ Question bank generated successfully!")
    
    # Filtering options
    st.subheader("🔍 Filter Questions")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        selected_section = st.selectbox(
            "Filter by Section",
            ["All Sections"] + list(question_bank.keys())
        )
    
    with col2:
        selected_difficulty = st.selectbox(
            "Filter by Difficulty", 
            ["All Difficulties", "easy", "medium", "hard"]
        )
    
    with col3:
        selected_bloom = st.selectbox(
            "Filter by Bloom Level",
            ["All Bloom Levels", "Remember", "Understand", "Apply", "Analyze", "Evaluate", "Create"]
        )
    
    with col4:
        selected_type = st.selectbox(
            "Filter by Question Type",
            ["All Types", "numerical_problem", "theoretical", "mixed"]
        )
    
    # Display filtered questions
    st.subheader("📋 Question Bank Details")
    
    for section_id, questions in question_bank.items():
        if selected_section != "All Sections" and section_id != selected_section:
            continue
            
        # Filter questions based on selections
        filtered_questions = []
        for q in questions:
            if (selected_difficulty == "All Difficulties" or q.get('difficulty') == selected_difficulty) and \
               (selected_bloom == "All Bloom Levels" or q.get('bloom_level') == selected_bloom) and \
               (selected_type == "All Types" or q.get('question_type') == selected_type):
                filtered_questions.append(q)
        
        if not filtered_questions:
            continue
            
        with st.expander(f"📖 {section_id} - {len(filtered_questions)} questions (filtered)"):
            
            for i, question in enumerate(filtered_questions):
                st.write(f"**Question {question.get('question_id', f'{section_id}_Q{i+1:03d}')}**")
                
                col1, col2, col3, col4, col5 = st.columns([3, 1, 1, 1, 1])
                
                with col1:
                    st.write(question.get('question_text', ''))
                    
                    # Display visual aid if present
                    visual_aid = question.get('visual_aid', {})
                    if visual_aid and visual_aid.get('content'):
                        if visual_aid.get('type') == 'ascii':
                            st.code(visual_aid['content'], language=None)
                        else:
                            st.info(f"📝 **Visualization:** {visual_aid['content']}")
                    
                    # Display given data if present
                    given_data = question.get('given_data', [])
                    if given_data:
                        st.write("**Given:**")
                        for item in given_data:
                            st.write(f"• {item}")
                    
                    # Display what to find
                    find_text = question.get('find', '')
                    if find_text:
                        st.write(f"**Find:** {find_text}")
                        
                    # Solution approach if provided
                    solution_approach = question.get('solution_approach', '')
                    if solution_approach:
                        st.write(f"**Approach:** {solution_approach}")
                
                with col2:
                    st.write(f"**{question.get('marks', 0)} marks**")
                    st.write(f"**{question.get('difficulty', 'Unknown').title()}**")
                
                with col3:
                    st.write(f"**{question.get('co', '')}**")
                
                with col4:
                    st.write(f"**{question.get('bloom_level', '')}**")
                
                with col5:
                    st.write(f"**{question.get('question_type', '').replace('_', ' ').title()}**")
                    st.write(f"*{question.get('topic', '')}*")
                
                st.divider()
    
    # Download options
    st.subheader("💾 Download Question Bank")
    
    col1, col2 = st.columns(2)
    
    with col1:
        json_data = json.dumps(question_bank_result, indent=2)
        st.download_button(
            label="📥 Download Complete Question Bank (JSON)",
            data=json_data,
            file_name=f"question_bank_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json",
            type="secondary",
            use_container_width=True
        )
    
    with col2:
        st.button("📄 Export to Excel/PDF", type="secondary", use_container_width=True,
                 help="Export functionality - coming soon!")

def main():
    """Main Streamlit application"""
    
    st.title("📝 Intelligent Question Paper Generator")
    st.markdown("Generate unique question paper sets based on syllabus, course objectives, and sample papers")
    
    with st.sidebar:
        st.header("📋 Workflow")
        st.write("1. Enter subject details")
        st.write("2. Upload sample papers")
        st.write("3. Extract & analyze")
        st.write("4. Calibrate parameters")
        st.write("5. Choose generation type")
        st.write("6. Generate content")
        
        st.header("⚙️ Settings")
        show_debug = st.checkbox("Show debug info", False)
    
    # Initialize session state
    for key in ['textract_output', 'structure_analysis', 'calibrated_structure', 'generated_papers', 'question_bank', 'generation_type']:
        if key not in st.session_state:
            st.session_state[key] = None
    
    # Replace the "Step 1: Subject Information" section in your main() function:

    # Step 1: Subject Information
    st.header("📚 Step 1: Subject Information")
    
    # Default prefilled content
    DEFAULT_SUBJECT_NAME = "Data Structures"
    
    DEFAULT_SYLLABUS = """UNIT – I (Text book 1, Chapter 1, 2 & 13)
    Algorithms: Preliminaries of algorithm, Algorithm analysis and complexity. Recursion: Definition, Design Methodology and Implementation of recursive algorithms, types of recursion, recursive algorithms for factorial function, GCD computation, Fibonacci sequence, Towers of Hanoi, Searching Techniques: Linear Search, Binary Search.
    
    UNIT – II (Text book 1, Chapter 12)
    Sorting Techniques: Basic concepts, Insertion Sort, Selection Sort, Bubble Sort, Quick Sort, Merge Sort and Counting Sort. Hashing: Hash table representations, Collision resolution: separate chaining, open addressing, linear probing, quadratic probing, Double hashing, Rehashing.
    
    UNIT – III (Text book 1, Chapter 3 & 4)
    Stacks: Basic Stack Operations, Representation of a Stack using Arrays, Stack Applications: Reversing a list, Infix to postfix Transformation, Evaluating Postfix Expression. Queues: Basic Queues Operations, Implementation of Queue Operations using arrays, Application of Queues: Round Robin Algorithm, Circular Queues.
    
    UNIT – IV (Text book 1, Chapter 5)
    Linked Lists: Introduction, single linked list, representation of a linked list in memory, Operations on a single linked list, merging two single linked lists into one list, reversing a single linked list, advantages and disadvantages of single linked list, Circular linked list, Double linked list.
    
    UNIT –V (Text book 1, Chapter 6, 7 & 11)
    Trees: Basic tree concepts, Binary Tree: Properties, Representation of Binary Trees – Array Representation and Linked Representation, Binary Tree Traversals (recursive), Creation of binary tree from in-order and pre/post-order traversals, Binary Search Tree Operations and Implementation. Graphs: Definition, Properties, Representation of Un-Weighted Graphs, Weighted Graphs, Graph Search Methods: BFS, DFS, and Implementation."""
    
    DEFAULT_COURSE_OBJECTIVES = """CO1: Interpret the performance of linear and binary searching algorithms based on recursive functions, time and space complexities. (BL-2)
    
    CO2: Implement sorting, hashing and collision resolution techniques. (BL-2)
    
    CO3: Develop linear data structures for stacks, queues using arrays. (BL-3)
    
    CO4: Develop singly, doubly & circular linked list data structures. (BL-3)
    
    CO5: Illustrate binary tree and binary search trees and Understand graph types, representations and graph traversal algorithms. (BL-3)"""
    
    DEFAULT_SUBJECT_CODE = "CSE201"
    
    col1, col2 = st.columns(2)
    
    with col1:
        subject_name = st.text_input(
            "Subject Name",
            value=DEFAULT_SUBJECT_NAME,  # Prefilled value
            placeholder="e.g., Engineering Mechanics",
            help="Enter the complete subject name"
        )
        
        syllabus = st.text_area(
            "Complete Syllabus",
            value=DEFAULT_SYLLABUS,  # Prefilled value
            height=400,  # Increased height to accommodate the content
            placeholder="Enter the complete syllabus with all topics, units, and sub-topics...",
            help="Paste the complete syllabus including all units and topics - this will be used for generating questions across ALL topics"
        )
    
    with col2:
        course_objectives = st.text_area(
            "Course Objectives (COs)",
            value=DEFAULT_COURSE_OBJECTIVES,  # Prefilled value
            height=300,  # Increased height to accommodate the content
            placeholder="Enter all course objectives...",
            help="List all course objectives that should be covered"
        )
        
        csm_id = st.text_input(
            "Subject Code",
            value=DEFAULT_SUBJECT_CODE,  # Prefilled value
            placeholder="e.g., ME101",
            help="Enter the subject code for reference"
        )
        
        # Add a clear button for convenience
        if st.button("🗑️ Clear All Fields", type="secondary", use_container_width=True):
            # Clear session state to force empty fields
            for key in ['subject_name', 'syllabus', 'course_objectives', 'csm_id']:
                if key in st.session_state:
                    del st.session_state[key]
            st.rerun()
        
        # Add an info box about the prefilled content
        st.info("💡 **Demo Content Loaded!** The fields above are pre-filled with Data Structures content for easy testing. You can modify or replace with your own content.")
    
    # Optional: Add a toggle to show/hide the prefilled content
    with st.expander("📝 About the Prefilled Content"):
        st.write("**Subject:** Data Structures")
        st.write("**Units:** 5 comprehensive units covering algorithms, sorting, data structures, and graphs")
        st.write("**Course Outcomes:** 5 COs aligned with Bloom's taxonomy levels")
        st.write("**Purpose:** This content is prefilled to demonstrate the app's capabilities. Feel free to replace with your own syllabus and course objectives.")
    
    # Step 2: Upload Papers
    if subject_name and syllabus and course_objectives:
        st.header("📤 Step 2: Upload Sample Question Papers")
        st.info("💡 **Note:** Sample papers are used to learn the FORMAT and STRUCTURE. The complete syllabus above will be used for topic coverage in generated papers.")
        
        col1, col2 = st.columns(2)
        
        with col1:
            uploaded_file1 = st.file_uploader(
                "Upload First Sample Paper",
                type=['pdf'],
                key="file1",
                help="Upload the first PDF question paper"
            )
        
        with col2:
            uploaded_file2 = st.file_uploader(
                "Upload Second Sample Paper",
                type=['pdf'],
                key="file2",
                help="Upload the second PDF question paper"
            )
        
        # Step 3: Extract Text
        if uploaded_file1 and uploaded_file2:
            st.header("🔍 Step 3: Extract Text from Papers")
            
            if st.button("🚀 Extract Text with Textract", type="primary", use_container_width=True):
                textract_output = upload_files_to_textract(uploaded_file1, uploaded_file2, csm_id or "default")
                
                if textract_output:
                    st.session_state.textract_output = textract_output
                    st.success("✅ Text extraction completed!")
                    
                    results = textract_output.get('results', [])
                    if len(results) == 2:
                        col1, col2 = st.columns(2)
                        for i, result in enumerate(results):
                            with col1 if i == 0 else col2:
                                # Use 'file_name' instead of 'pdf_file'
                                st.write(f"**📄 {result.get('file_name', 'Unknown File')}**")
                                # Use 'final_status' if available, otherwise 'status'
                                status = result.get('final_status', result.get('status', 'Unknown'))
                                st.write(f"✅ Status: {status}")
                                st.write(f"📊 Characters: {result.get('text_length', 0)}")
                                
                                # Show any errors if present
                                if 'error' in result:
                                    st.error(f"❌ Error: {result['error']}")
                    else:
                        st.warning(f"Expected 2 results, got {len(results)}")
                        # Display whatever results we have
                        for i, result in enumerate(results):
                            st.write(f"**File {i+1}:** {result.get('file_name', 'Unknown')}")
                            st.write(f"**Status:** {result.get('final_status', result.get('status', 'Unknown'))}")
                            if 'error' in result:
                                st.error(f"Error: {result['error']}")
    
    # Step 4: Analyze Structure
    if st.session_state.textract_output:
        st.header("🧠 Step 4: Analyze Structure with Full Syllabus Context")
        
        if st.button("🔬 Analyze Papers with Complete Syllabus", type="primary", use_container_width=True):
            textract_results = st.session_state.textract_output.get('results', [])
            
            if len(textract_results) >= 2:
                # Take only the first 2 results if more than 2
                paper_texts = [
                    {
                        'filename': result.get('file_name', f'Paper_{i+1}'),  # Use 'file_name' instead of 'pdf_file'
                        'extracted_text': result.get('extracted_text', ''),
                        'text_length': result.get('text_length', 0)
                    }
                    for i, result in enumerate(textract_results[:2])  # Only take first 2
                ]
                
                # Only proceed if we have valid extracted text
                valid_papers = [p for p in paper_texts if p['extracted_text'] and len(p['extracted_text'].strip()) > 0]
                
                if len(valid_papers) >= 2:
                    with st.spinner("🤖 Analyzing papers for structure patterns and syllabus mapping..."):
                        structure_analysis = analyze_papers_with_syllabus(
                            valid_papers[:2], subject_name, syllabus, course_objectives  # Use only first 2 valid papers
                        )
                    
                    if structure_analysis:
                        st.session_state.structure_analysis = structure_analysis
                        st.success("✅ Structure analysis completed!")
                else:
                    st.error("❌ Need at least 2 papers with valid extracted text to proceed with analysis")
                    st.write("**Available papers:**")
                    for i, paper in enumerate(paper_texts):
                        st.write(f"• {paper['filename']}: {paper['text_length']} characters")
            else:
                st.error(f"❌ Need at least 2 extracted papers, got {len(textract_results)}")
    
    # Step 5: Calibrate Parameters
    if st.session_state.structure_analysis:
        calibrated_structure, ready_to_generate = display_and_edit_analysis(st.session_state.structure_analysis)
        
        if ready_to_generate and calibrated_structure:
            st.session_state.calibrated_structure = calibrated_structure
            st.success("🎯 Parameters calibrated! Ready to generate papers covering the full syllabus.")
    
    # Step 6: Choose Generation Type
    if st.session_state.calibrated_structure:
        st.header("🎯 Step 5: Choose Generation Type")
        
        if not st.session_state.generation_type:
            st.info("Choose your preferred generation approach based on your needs:")
            
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("📊 Generate Question Bank", type="primary", use_container_width=True):
                    st.session_state.generation_type = "question_bank"
                    st.rerun()
                
                st.write("**Question Bank Features:**")
                st.write("• Comprehensive question pool")
                st.write("• Section-wise organization")
                st.write("• Multiple difficulties per section")
                st.write("• Perfect for mix-and-match")
                st.write("• Complete syllabus coverage")
                st.write("• Flexible question selection")
            
            with col2:
                if st.button("📄 Generate Complete Paper Sets", type="primary", use_container_width=True):
                    st.session_state.generation_type = "paper_sets"
                    st.rerun()
                
                st.write("**Paper Sets Features:**")
                st.write("• Ready-to-use exam papers")
                st.write("• Balanced distributions")
                st.write("• Progressive difficulty levels")
                st.write("• Zero duplication across papers")
                st.write("• Structured exam format")
                st.write("• Immediate deployment ready")
        
        # Generate Question Bank
        elif st.session_state.generation_type == "question_bank":
            st.subheader("📊 Question Bank Generation")
            
            col1, col2 = st.columns(2)
            with col1:
                questions_per_section = st.number_input(
                    "Questions per Section", 
                    min_value=10, 
                    max_value=50, 
                    value=25,
                    step=5,
                    help="Number of questions to generate for each section"
                )
            with col2:
                if st.button("🔄 Change Generation Type", type="secondary"):
                    st.session_state.generation_type = None
                    st.rerun()
            
            total_questions = questions_per_section * len(st.session_state.calibrated_structure.get('sections', []))
            st.info(f"Will generate approximately {total_questions} questions total across all sections")
            
            if st.button("🚀 Generate Question Bank", type="primary", use_container_width=True):
                with st.spinner(f"🎯 Generating comprehensive question bank with {questions_per_section} questions per section... This may take a few minutes."):
                    question_bank = generate_question_bank(st.session_state.calibrated_structure, questions_per_section)
                
                if question_bank:
                    st.session_state.question_bank = question_bank
                    st.balloons()
                    st.success(f"🎉 Successfully generated question bank with {total_questions}+ questions!")
        
        # Generate Paper Sets
        elif st.session_state.generation_type == "paper_sets":
            st.subheader("📄 Question Paper Sets Generation")
            
            col1, col2 = st.columns(2)
            with col1:
                num_papers = st.number_input(
                    "Number of Papers", 
                    min_value=1, 
                    max_value=10, 
                    value=5,
                    step=1,
                    help="Number of complete paper sets to generate"
                )
            with col2:
                if st.button("🔄 Change Generation Type", type="secondary"):
                    st.session_state.generation_type = None
                    st.rerun()
            
            st.info(f"Will generate {num_papers} complete question papers with progressive difficulty (Easy → Hard)")
            
            if st.button("🚀 Generate Question Paper Sets", type="primary", use_container_width=True):
                with st.spinner(f"🎯 Generating {num_papers} unique question papers from complete syllabus... This may take a few minutes."):
                    generated_papers = generate_question_papers(st.session_state.calibrated_structure, num_papers)
                
                if generated_papers:
                    st.session_state.generated_papers = generated_papers
                    st.balloons()
                    st.success(f"🎉 Successfully generated {num_papers} unique question papers!")
    
    # Display Generated Content
    if st.session_state.generated_papers:
        display_generated_papers(st.session_state.generated_papers)
    
    if st.session_state.question_bank:
        display_question_bank(st.session_state.question_bank)
    
    # Debug Information
    if show_debug:
        st.header("🔧 Debug Information")
        
        debug_items = [
            ("Textract Output", st.session_state.textract_output),
            ("Structure Analysis", st.session_state.structure_analysis),
            ("Calibrated Structure", st.session_state.calibrated_structure),
            ("Generated Papers", st.session_state.generated_papers),
            ("Question Bank", st.session_state.question_bank)
        ]
        
        for title, data in debug_items:
            if data:
                with st.expander(title):
                    st.json(data)

if __name__ == "__main__":
    main()
