import openai
from openai import OpenAI
import time
import os
from typing import Dict, Any, Optional
from dotenv import load_dotenv
import logging
from sqlalchemy.orm import Session
from src.models.llm_requests import LLMRequest
import re

load_dotenv()

logger = logging.getLogger(__name__)

class LLMClient:
    """
    Client for making LLM API calls and handling responses
    """
    
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.model = os.getenv("LLM_MODEL", "gpt-3.5-turbo")
        self.max_tokens = int(os.getenv("MAX_TOKENS", "800")) 
        self.temperature = float(os.getenv("TEMPERATURE", "0.7"))
        self._client = None
    
    @property
    def client(self):
        """Lazy initialization of OpenAI client"""
        if self._client is None:
            if not self.api_key:
                raise ValueError("OPENAI_API_KEY environment variable is required")
            self._client = OpenAI(api_key=self.api_key)
        return self._client
    
    async def generate_resume_content(
        self, 
        profile_data: Dict[str, Any], 
        job_description: str,
        user_id: int,
        db: Session
    ) -> Dict[str, str]: # Return a dictionary of section contents
        """
        Generate tailored resume content as structured text using LLM
        """
        start_time = time.time()
        
        try:
            prompt = self._create_resume_prompt(profile_data, job_description)
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system", 
                        "content": "You are an expert resume writer. Your task is to generate concise, professional textual content for specific sections of a resume. This content will be programmatically inserted into a LaTeX resume template. Provide only the text for each requested section, clearly demarcated by the specified headers (PROFILE:, EDUCATION:, EXPERIENCE:, PROJECTS:, SKILLS:). Do not include any LaTeX commands or formatting. Focus on tailoring the content to the provided job description and candidate profile."
                    },
                    {"role": "user", "content": prompt}
                ],
                max_tokens=self.max_tokens,
                temperature=self.temperature
            )
            
            raw_content = response.choices[0].message.content.strip()
            parsed_content = self._parse_llm_output_to_dict(raw_content)
            
            response_time = int((time.time() - start_time) * 1000)
            self._log_request(
                user_id=user_id,
                response=response,
                response_time_ms=response_time,
                status="success",
                db=db
            )
            
            return parsed_content
            
        except Exception as e:
            logger.error(f"LLM API error for user {user_id}: {e}")
            response_time = int((time.time() - start_time) * 1000)
            self._log_request(
                user_id=user_id,
                response=None,
                response_time_ms=response_time,
                status="failed",
                db=db,
                error_message=str(e)
            )
            raise Exception(f"Failed to generate resume content: {str(e)}")

    def _parse_llm_output_to_dict(self, llm_output: str) -> Dict[str, str]:
        """
        Parses the LLM's structured string output into a dictionary.
        Expects sections like "PROFILE:\n...", "EDUCATION:\n...", etc.
        """
        sections_map = {
            "PROFILE": "",
            "EDUCATION": "",
            "EXPERIENCE": "",
            "PROJECTS": "",
            "SKILLS": ""
        }
        # Order matters for parsing: iterate through known section headers
        ordered_sections = ["PROFILE", "EDUCATION", "EXPERIENCE", "PROJECTS", "SKILLS"]
        
        current_section_key = None
        content_buffer = []

        for line in llm_output.splitlines():
            stripped_line = line.strip()
            matched_section = False
            for key in ordered_sections:
                if stripped_line.upper().startswith(key + ":"):
                    # If we were processing a section, save its content
                    if current_section_key and content_buffer:
                        sections_map[current_section_key] = "\n".join(content_buffer).strip()
                    
                    current_section_key = key
                    content_buffer = []
                    # Capture content on the same line as the header
                    header_content = stripped_line[len(key)+1:].strip()
                    if header_content:
                        content_buffer.append(header_content)
                    matched_section = True
                    break
            
            if not matched_section and current_section_key:
                # Only append non-empty lines to the current section's buffer
                if stripped_line:
                    content_buffer.append(stripped_line)

        # Save the last processed section
        if current_section_key and content_buffer:
            sections_map[current_section_key] = "\n".join(content_buffer).strip()

        # Log if any section is missing, but it's already initialized to ""
        for key in ordered_sections:
            if not sections_map[key]:
                logger.warning(f"Section '{key}' was not found or is empty in LLM output. LLM raw output snippet: {llm_output[:200]}...")

        if all(not content for content in sections_map.values()) and llm_output:
             logger.error(f"Could not parse LLM output into any known sections despite non-empty output. LLM output:\n{llm_output}")
             # Fallback: put all content under a generic key if no sections were parsed
             return {"GENERIC_CONTENT": llm_output}
        elif all(not content for content in sections_map.values()) and not llm_output:
            logger.error("LLM output was empty. Could not parse into sections.")
            # sections_map will already have empty strings for all keys

        return sections_map

    def _create_resume_prompt(self, profile_data: Dict[str, Any], job_description: str) -> str:
        """
        Create a structured prompt for resume generation. Requests plain text.
        """
        profile = profile_data.get("profile", {})
        education_list = profile_data.get("education", [])
        experience_list = profile_data.get("experience", [])
        project_list = profile_data.get("projects", [])
        skill_list = profile_data.get("skills", [])
        user_info = profile_data.get("user", {})
        
        user_name_parts = []
        if user_info.get('firstName'):
            user_name_parts.append(user_info.get('firstName'))
        if user_info.get('lastName'):
            user_name_parts.append(user_info.get('lastName'))
        
        user_name = " ".join(user_name_parts)
        if not user_name.strip():
            user_name = profile.get('name', 'The Candidate') # Fallback to profile name

        prompt = f"""
Generate tailored resume content for the following job description, based on the candidate's profile.
THE OUTPUT MUST BE PLAIN TEXT, structured with the exact section headers (PROFILE:, EDUCATION:, EXPERIENCE:, PROJECTS:, SKILLS:) each on a new line, followed immediately by the content for that section.

JOB DESCRIPTION:
{job_description}

CANDIDATE PROFILE FOR: {user_name}
(User's direct contact details like email, phone, LinkedIn will be populated into the final template from the database separately. Focus on the substance of their achievements and skills.)

EDUCATION:
{self._format_education_for_prompt(education_list)}

EXPERIENCE:
{self._format_experience_for_prompt(experience_list)}

PROJECTS:
{self._format_projects_for_prompt(project_list)}

SKILLS:
{self._format_skills_for_prompt(skill_list)}

INSTRUCTIONS:
1. Analyze the JOB DESCRIPTION and the CANDIDATE PROFILE provided above.
2. Generate compelling, concise, and professional PLAIN TEXT content for each of the following sections.
3. The content for each section should be suitable for direct insertion into a resume. Use bullet points (e.g., using '-' or '*') for lists within sections like experience and projects where appropriate.
4. **CRITICALLY IMPORTANT: Structure your entire output with these exact uppercase headers, each on a new line, followed by the content for that section. Example:**
   PROFILE:
   [Text for professional summary here...]

   EDUCATION:
   [Text for education section here...]

   EXPERIENCE:
   [Text for experience section here...]

   PROJECTS:
   [Text for projects section here...]

   SKILLS:
   [Text for skills section here...]

GUIDELINES FOR EACH SECTION'S TEXTUAL CONTENT:
   - PROFILE:
     Write a 2-4 sentence professional summary tailored to the job description, highlighting key skills and experiences from the candidate's profile.

   - EDUCATION:
     For each education entry, provide institution, degree, field of study (if any), graduation date (or expected). Optionally, include 1-2 bullet points per entry for key achievements, relevant coursework, or GPA if significant and high.
     Example format for one entry's text:
     Institution Name - Degree in Field of Study (Graduation: Month Year)
     - Relevant coursework: Course A, Course B
     - GPA: 3.X/4.0

   - EXPERIENCE:
     For each experience entry, provide company, position, and dates of employment. Follow with 2-4 bullet points detailing responsibilities and achievements. Quantify achievements where possible and tailor these points to the job description.
     Example format for one entry's text:
     Company Name - Position Title (Month Year - Month Year)
     - Achieved X by implementing Y, resulting in Z impact (e.g., 15% improvement in Q).
     - Led a team to develop a new feature, enhancing user engagement.

   - PROJECTS:
     For each project, provide the project title and optionally dates. Follow with 1-3 bullet points describing the project, technologies used, your role, and key outcomes or impact.
     Example format for one entry's text:
     Project Title (Optional: Month Year - Month Year)
     - Developed X using Y (e.g., Python, React) and Z (e.g., PostgreSQL).
     - Implemented feature A which resulted in B (e.g., reduced processing time by 10%).

   - SKILLS:
     Provide a categorized list of skills. Examples of categories: Programming Languages, Frameworks & Libraries, Databases, Tools, Cloud Platforms, Other Technical Skills, Soft Skills.
     Example format for the skills text:
     Programming Languages: Python, Java, JavaScript
     Frameworks & Libraries: React, Node.js, Spring Boot
     Databases: PostgreSQL, MongoDB
     Tools: Git, Docker, Kubernetes

5. **DO NOT** include any LaTeX commands (e.g., \\section, \\textbf, \\item).
6. **DO NOT** include any explanations, apologies, or conversational text outside of the requested section content. Output only the structured resume content starting with "PROFILE:".
7. Ensure each section header (PROFILE:, EDUCATION:, etc.) is ON ITS OWN LINE.
"""
        return prompt
    
    def _format_bullet_points(self, text: Optional[str], indent: str = "  ") -> str:
        if not text: return ""
        # Split by newline, filter empty, and prefix with '- '
        return "\n".join([f"{indent}- {line.strip()}" for line in text.splitlines() if line.strip()])

    def _format_education_for_prompt(self, education_list: list) -> str:
        if not education_list: return "No education data provided."
        formatted_entries = []
        for edu in education_list:
            entry_parts = []
            entry_parts.append(f"- Institution: {edu.get('institution', 'N/A')}")
            entry_parts.append(f"  Degree: {edu.get('degree', 'N/A')}")
            if edu.get('field_of_study'): entry_parts.append(f"  Field of Study: {edu.get('field_of_study')}")
            
            dates = []
            if edu.get('start_date'): dates.append(str(edu.get('start_date')))
            if edu.get('end_date'): dates.append(str(edu.get('end_date')))
            if dates: entry_parts.append(f"  Dates: {' - '.join(dates)}")

            if edu.get('description'):
                entry_parts.append(f"  Details (to be elaborated by LLM or used as bullet points):\n{self._format_bullet_points(edu.get('description'), indent='    ')}")
            formatted_entries.append("\n".join(entry_parts))
        return "\n\n".join(formatted_entries) # Separate entries by a blank line
    
    def _format_experience_for_prompt(self, experience_list: list) -> str:
        if not experience_list: return "No experience data provided."
        formatted_entries = []
        for exp in experience_list:
            entry_parts = []
            entry_parts.append(f"- Company: {exp.get('company', 'N/A')}")
            entry_parts.append(f"  Position: {exp.get('position', 'N/A')}")

            dates = []
            if exp.get('start_date'): dates.append(str(exp.get('start_date')))
            if exp.get('end_date'): dates.append(str(exp.get('end_date')))
            if dates: entry_parts.append(f"  Dates: {' - '.join(dates)}")
            
            if exp.get('description'):
                entry_parts.append(f"  Responsibilities/Achievements (to be elaborated by LLM as bullet points):\n{self._format_bullet_points(exp.get('description'), indent='    ')}")
            formatted_entries.append("\n".join(entry_parts))
        return "\n\n".join(formatted_entries)
    
    def _format_projects_for_prompt(self, project_list: list) -> str:
        if not project_list: return "No projects data provided."
        formatted_entries = []
        for proj in project_list:
            entry_parts = []
            entry_parts.append(f"- Title: {proj.get('title', 'N/A')}")

            dates = []
            if proj.get('start_date'): dates.append(str(proj.get('start_date')))
            if proj.get('end_date'): dates.append(str(proj.get('end_date')))
            if dates: entry_parts.append(f"  Dates: {' - '.join(dates)}")

            if proj.get('description'):
                entry_parts.append(f"  Description (to be elaborated by LLM as bullet points):\n{self._format_bullet_points(proj.get('description'), indent='    ')}")
            
            tech = proj.get('technologies')
            if tech:
                tech_str = ", ".join(tech) if isinstance(tech, list) else str(tech)
                entry_parts.append(f"  Technologies: {tech_str}")
            formatted_entries.append("\n".join(entry_parts))
        return "\n\n".join(formatted_entries)
    
    def _format_skills_for_prompt(self, skill_list: list) -> str:
        if not skill_list: return "No skills data provided."
        # For the prompt, provide a simple list. LLM will be asked to categorize.
        skill_details = []
        for skill in skill_list:
            name = skill.get('name', 'N/A')
            proficiency = skill.get('proficiency')
            detail = f"- {name}"
            if proficiency:
                detail += f" (Proficiency: {proficiency})"
            skill_details.append(detail)
        return "\n".join(skill_details) if skill_details else "No skills listed."

    def _log_request(
        self, 
        user_id: int, 
        response: Optional[Any], 
        response_time_ms: int, 
        status: str,
        db: Session,
        error_message: Optional[str] = None
    ):
        """Log the LLM request for monitoring and billing"""
        try:
            prompt_tokens, completion_tokens, total_tokens = None, None, None
            if response and hasattr(response, 'usage') and response.usage:
                prompt_tokens = response.usage.prompt_tokens
                completion_tokens = response.usage.completion_tokens
                total_tokens = response.usage.total_tokens
            
            log_entry = LLMRequest(
                user_id=user_id,
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
                total_tokens=total_tokens,
                model_used=self.model,
                response_time_ms=response_time_ms,
                status=status
            )
            db.add(log_entry)
            db.commit()
            token_info = total_tokens if total_tokens is not None else 'N/A'
            logger.info(f"LLM request logged for user {user_id}. Status: {status}. Tokens: {token_info}")
        except Exception as e:
            logger.error(f"Failed to log LLM request for user {user_id}: {e}")


# Example usage (for testing purposes, not part of the class)
if __name__ == '__main__':
    # This part would require a mock DB session and profile data for actual testing.
    # For now, let's test the parsing logic.
    test_client = LLMClient()
    
    sample_llm_output_ideal = """
PROFILE:
This is the profile summary.
It spans multiple lines.

EDUCATION:
University of Hard Knocks - PhD in Street Smarts (Jan 2010 - Dec 2014)
- Learned a lot.
- Survived.

Another University - BS in Computer Science (Aug 2005 - May 2009)
- Relevant coursework: Algorithms, Data Structures.
- GPA: 3.8/4.0

EXPERIENCE:
Big Corp - Senior Developer (Jun 2015 - Present)
- Did amazing things with code.
- Led a team of 5.

PROJECTS:
Cool Project (Jan 2023 - Mar 2023)
- Built a thing using Python and Flask.
- It was very cool.

SKILLS:
Programming Languages: Python, JavaScript
Frameworks: Flask, React
Databases: PostgreSQL
"""

    # Test with mixed case headers and slightly off formatting
    sample_llm_output_mixed_case = """
profile:
This is the profile summary.
education:
University of Hard Knocks - PhD (2010-2014)
experience:
Big Corp - Dev (2015-Present)
- Did things.
projects:
Cool Project
- Built with Python.
skills:
Languages: Python
"""

    sample_llm_output_condensed = (
        "PROFILE:This is a profile summary.\n"
        "EDUCATION:University of Life - Degree in Living (2000-2024)\n"
        "EXPERIENCE:Job Co - Worker (2010-2020) - Did stuff.\n"
        "PROJECTS:My Project - Made a thing.\n"
        "SKILLS:Skill1, Skill2"
    )
    
    sample_llm_output_no_profile_section = """
EDUCATION:
University of Hard Knocks - PhD in Street Smarts (Jan 2010 - Dec 2014)
- Learned a lot.
- Survived.
EXPERIENCE:
Big Corp - Senior Developer (Jun 2015 - Present)
- Did amazing things with code.
SKILLS:
Programming Languages: Python, JavaScript
"""

    sample_llm_output_empty = ""
    sample_llm_only_profile = "PROFILE:\nThis is only a profile."


    def run_parser_test(name, output_str):
        print(f"\n--- Testing: {name} ---")
        parsed_data = test_client._parse_llm_output_to_dict(output_str)
        for section, content in parsed_data.items():
            print(f"SECTION: {section}\nCONTENT:\n'{content}'\n----")

    run_parser_test("Ideal Output", sample_llm_output_ideal)
    run_parser_test("Mixed Case Headers", sample_llm_output_mixed_case)
    run_parser_test("Condensed Output", sample_llm_output_condensed)
    run_parser_test("No PROFILE Section", sample_llm_output_no_profile_section)
    run_parser_test("Empty Output", sample_llm_output_empty)
    run_parser_test("Only PROFILE Section", sample_llm_only_profile)
        
    # Example of creating a prompt (would need mock data for full test)
    mock_profile_data_for_prompt = {
        "profile": {"name": "Jane Doe"},
        "user": {"firstName": "Jane", "lastName": "Doe"},
        "education": [
            {"institution": "Mock Uni", "degree": "BS CS", "field_of_study": "Comp Sci", 
             "start_date": "2010-08", "end_date": "2014-05", "description": "Top student.\nRelevant coursework: AI, ML."}
        ],
        "experience": [
            {"company": "Mock Co", "position": "Software Developer", 
             "start_date": "2015-06", "end_date": "2020-12", "description": "- Developed new features for X.\n- Optimized Y by Z%."}
        ],
        "projects": [
            {"title": "Mock Project Alpha", "description": "A cool project using Python.", "technologies": ["Python", "Flask"]}
        ],
        "skills": [
            {"name": "Python", "proficiency": "Expert"}, 
            {"name": "SQL"}
        ]
    }
    mock_job_desc_for_prompt = "Seeking an experienced Python developer with knowledge of web frameworks and databases."
    
    # print("\n--- Testing Prompt Generation ---")
    # generated_prompt = test_client._create_resume_prompt(mock_profile_data_for_prompt, mock_job_desc_for_prompt)
    # print(generated_prompt) 