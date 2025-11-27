from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from src.models.users import User
from src.models.profiles import Profile
from src.models.education import Education
from src.models.experience import Experience
from src.models.projects import Project
from src.models.skills import Skill
from src.models.generated_resumes import GeneratedResume
from src.services.llm_client import LLMClient
import logging
import os
import re

logger = logging.getLogger(__name__)


TEMPLATE_DIR = os.path.dirname(__file__)
RESUME_TEMPLATE_PATH = os.path.join(TEMPLATE_DIR, "resume_template.tex")

class ResumeService:
    """
    Service for handling resume generation and management
    """
    
    def __init__(self):
        self.llm_client = LLMClient()
        self._latex_template = self._load_latex_template()

    def _load_latex_template(self) -> str:
        try:
            with open(RESUME_TEMPLATE_PATH, "r", encoding="utf-8") as f:
                return f.read()
        except FileNotFoundError:
            logger.error(f"FATAL: LaTeX resume template not found at {RESUME_TEMPLATE_PATH}")
            # In a real scenario, this might raise an error that stops the service
            # or uses a hardcoded fallback template.
            return "LaTeX template not found. Please configure."
        except Exception as e:
            logger.error(f"FATAL: Error loading LaTeX resume template: {e}")
            return f"Error loading LaTeX template: {e}"

    def _escape_latex(self, text: Optional[str]) -> str:
        """Escape special characters for LaTeX. Must be called on ALL user/LLM content."""
        if text is None:
            return ""
        
        # Convert to string if needed
        text = str(text).strip()
        if not text:
            return ""
        
        # Order matters: backslash must be escaped first
        # Use order: \ -> & -> % -> $ -> # -> _ -> { } -> ~ -> ^ -> < >
        char_map = {
            '\\': r'\textbackslash{}',
            '&': r'\&',
            '%': r'\%',
            '$': r'\$',
            '#': r'\#',
            '_': r'\_',
            '{': r'\{',
            '}': r'\}',
            '~': r'\textasciitilde{}',
            '^': r'\textasciicircum{}',
            '<': r'\textless{}',
            '>': r'\textgreater{}',
        }
        
        # Replace LaTeX commands from LLM with plain text equivalents
        text = text.replace(r'\item', '-')
        text = text.replace(r'\textbf', '')
        text = text.replace(r'\textit', '')
        text = text.replace(r'\emph', '')
        text = text.replace(r'\texttt', '')
        
        # Escape character by character to ensure proper handling
        result = ""
        for char in text:
            result += char_map.get(char, char)
        
        return result

    def _format_education_section(self, education_content: str, profile_data: Dict[str, Any]) -> str:
        """Format education content into proper LaTeX resume commands"""
        if not education_content.strip():
            # Fallback to database education if LLM content is empty
            education_list = profile_data.get("education", [])
            if not education_list:
                return ""
            
            latex_education = ""
            for edu in education_list:
                institution = self._escape_latex(edu.get('institution', ''))
                degree = self._escape_latex(edu.get('degree', ''))
                field = self._escape_latex(edu.get('field_of_study', ''))
                start_date = edu.get('start_date', '')
                end_date = edu.get('end_date', '') or 'Present'
                gpa = edu.get('gpa')
                description = self._escape_latex(edu.get('description', ''))
                
                degree_text = f"{degree}"
                if field:
                    degree_text += f" in {field}"
                if gpa:
                    degree_text += f", GPA: {gpa}"
                
                latex_education += f"""    \\resumeSubheading
      {{{institution}}}{{}}
      {{{degree_text}}}{{{start_date} -- {end_date}}}"""
                
                if description:
                    latex_education += f"""
      \\resumeItemListStart
          \\resumeItem{{{description}}}
      \\resumeItemListEnd"""
                
                latex_education += "\n"
            
            return latex_education.strip()
        
        # Parse LLM-generated education content
        lines = [line.strip() for line in education_content.split('\n') if line.strip()]
        latex_education = ""
        
        current_entry = {}
        for line in lines:
            # Look for institution and degree patterns
            if ' - ' in line and ('University' in line or 'College' in line or 'Institute' in line):
                if current_entry:
                    # Process previous entry
                    latex_education += self._format_single_education_entry(current_entry)
                    current_entry = {}
                
                # Parse institution and degree
                parts = line.split(' - ', 1)
                current_entry['institution'] = parts[0].strip()
                if len(parts) > 1:
                    degree_part = parts[1].strip()
                    # Extract graduation date if present
                    date_match = re.search(r'\(.*?(\d{4}).*?\)', degree_part)
                    if date_match:
                        current_entry['end_date'] = date_match.group(1)
                        current_entry['degree'] = degree_part.replace(date_match.group(0), '').strip()
                    else:
                        current_entry['degree'] = degree_part
                current_entry['items'] = []
            elif line.startswith('-') or line.startswith('*'):
                # This is a bullet point for the current education entry
                if current_entry:
                    item_text = line[1:].strip()
                    current_entry['items'].append(item_text)
        
        # Process the last entry
        if current_entry:
            latex_education += self._format_single_education_entry(current_entry)
        
        return latex_education.strip()

    def _format_single_education_entry(self, entry: Dict[str, Any]) -> str:
        """Format a single education entry into LaTeX"""
        institution = self._escape_latex(entry.get('institution', ''))
        degree = self._escape_latex(entry.get('degree', ''))
        start_date = entry.get('start_date', '')
        end_date = entry.get('end_date', 'Present')
        items = entry.get('items', [])
        
        latex_entry = f"""    \\resumeSubheading
      {{{institution}}}{{}}
      {{{degree}}}{{{start_date} -- {end_date}}}"""
        
        if items:
            latex_entry += "\n      \\resumeItemListStart"
            for item in items:
                latex_entry += f"\n          \\resumeItem{{{self._escape_latex(item)}}}"
            latex_entry += "\n      \\resumeItemListEnd"
        
        latex_entry += "\n"
        return latex_entry

    def _format_experience_section(self, experience_content: str, profile_data: Dict[str, Any]) -> str:
        """Format experience content into proper LaTeX resume commands"""
        if not experience_content.strip():
            # Fallback to database experience if LLM content is empty
            experience_list = profile_data.get("experience", [])
            if not experience_list:
                return ""
            
            latex_experience = ""
            for exp in experience_list:
                company = self._escape_latex(exp.get('company', ''))
                position = self._escape_latex(exp.get('position', ''))
                start_date = exp.get('start_date', '')
                end_date = exp.get('end_date', '') or 'Present'
                description = self._escape_latex(exp.get('description', ''))
                
                latex_experience += f"""    \\resumeSubheading
      {{{company}}}{{}}
      {{{position}}}{{{start_date} -- {end_date}}}"""
                
                if description:
                    latex_experience += f"""
      \\resumeItemListStart
          \\resumeItem{{{description}}}
      \\resumeItemListEnd"""
                
                latex_experience += "\n"
            
            return latex_experience.strip()
        
        # Parse LLM-generated experience content
        lines = [line.strip() for line in experience_content.split('\n') if line.strip()]
        latex_experience = ""
        
        current_entry = {}
        for line in lines:
            # Look for company - position pattern
            if ' - ' in line and not line.startswith('-') and not line.startswith('*'):
                if current_entry:
                    # Process previous entry
                    latex_experience += self._format_single_experience_entry(current_entry)
                    current_entry = {}
                
                # Parse company and position
                parts = line.split(' - ', 1)
                current_entry['company'] = parts[0].strip()
                if len(parts) > 1:
                    position_and_date = parts[1].strip()
                    # Extract dates if present
                    date_match = re.search(r'\(([^)]+)\)', position_and_date)
                    if date_match:
                        date_range = date_match.group(1)
                        current_entry['date_range'] = date_range
                        current_entry['position'] = position_and_date.replace(date_match.group(0), '').strip().rstrip(',').strip()
                    else:
                        current_entry['position'] = position_and_date
                current_entry['items'] = []
            elif line.startswith('-') or line.startswith('*'):
                # This is a bullet point for the current experience entry
                if current_entry:
                    item_text = line[1:].strip()
                    current_entry['items'].append(item_text)
        
        # Process the last entry
        if current_entry:
            latex_experience += self._format_single_experience_entry(current_entry)
        
        return latex_experience.strip()

    def _format_single_experience_entry(self, entry: Dict[str, Any]) -> str:
        """Format a single experience entry into LaTeX"""
        company = self._escape_latex(entry.get('company', ''))
        position = self._escape_latex(entry.get('position', ''))
        date_range = entry.get('date_range', '')
        items = entry.get('items', [])
        
        latex_entry = f"""    \\resumeSubheading
      {{{company}}}{{}}
      {{{position}}}{{{date_range}}}"""
        
        if items:
            latex_entry += "\n      \\resumeItemListStart"
            for item in items:
                latex_entry += f"\n          \\resumeItem{{{self._escape_latex(item)}}}"
            latex_entry += "\n      \\resumeItemListEnd"
        
        latex_entry += "\n"
        return latex_entry

    def _format_projects_section(self, projects_content: str, profile_data: Dict[str, Any]) -> str:
        """Format projects content into proper LaTeX resume commands"""
        if not projects_content.strip():
            # Fallback to database projects if LLM content is empty
            project_list = profile_data.get("projects", [])
            if not project_list:
                return ""
            
            latex_projects = ""
            for proj in project_list:
                title = self._escape_latex(proj.get('title', ''))
                description = self._escape_latex(proj.get('description', ''))
                technologies = self._escape_latex(proj.get('technologies', ''))
                
                latex_projects += f"""    \\resumeProjectHeading
      {{\\textbf{{{title}}}}}"""
                
                project_items = []
                if description:
                    project_items.append(description)
                if technologies:
                    project_items.append(f"Technologies: {technologies}")
                
                if project_items:
                    latex_projects += "\n      \\resumeItemListStartNoSpace"
                    for item in project_items:
                        latex_projects += f"\n          \\resumeItemNoSpace{{{item}}}"
                    latex_projects += "\n      \\resumeItemListEndNoSpace"
                
                latex_projects += "\n"
            
            return latex_projects.strip()
        
        # Parse LLM-generated projects content
        lines = [line.strip() for line in projects_content.split('\n') if line.strip()]
        latex_projects = ""
        
        current_project = {}
        for line in lines:
            # Look for project titles (lines that don't start with - or *)
            if not line.startswith('-') and not line.startswith('*'):
                if current_project:
                    # Process previous project
                    latex_projects += self._format_single_project_entry(current_project)
                    current_project = {}
                
                current_project['title'] = line.strip()
                current_project['items'] = []
            elif line.startswith('-') or line.startswith('*'):
                # This is a bullet point for the current project
                if current_project:
                    item_text = line[1:].strip()
                    current_project['items'].append(item_text)
        
        # Process the last project
        if current_project:
            latex_projects += self._format_single_project_entry(current_project)
        
        return latex_projects.strip()

    def _format_single_project_entry(self, entry: Dict[str, Any]) -> str:
        """Format a single project entry into LaTeX"""
        title = self._escape_latex(entry.get('title', ''))
        items = entry.get('items', [])
        
        latex_entry = f"""    \\resumeProjectHeading
      {{\\textbf{{{title}}}}}"""
        
        if items:
            latex_entry += "\n      \\resumeItemListStartNoSpace"
            for item in items:
                latex_entry += f"\n          \\resumeItemNoSpace{{{self._escape_latex(item)}}}"
            latex_entry += "\n      \\resumeItemListEndNoSpace"
        
        latex_entry += "\n"
        return latex_entry

    def _validate_latex_content(self, latex_content: str) -> List[str]:
        """Validate LaTeX content and return list of potential issues"""
        issues = []
        
        # Check for unescaped special characters that could cause compilation issues
        # These patterns look for special chars NOT preceded by a backslash
        problematic_patterns = [
            (r'(?<!\\)&(?![&\s])', "Unescaped & character found"),
            (r'(?<!\\)%(?![%\s])', "Unescaped % character found"),
            (r'(?<!\\)\$(?![\$\s])', "Unescaped $ character found"),
            (r'(?<!\\)#(?![#\s])', "Unescaped # character found"),
        ]
        
        for pattern, message in problematic_patterns:
            matches = re.findall(pattern, latex_content)
            # Only report if we have actual issues (allowing some false positives in comments)
            if len(matches) > 2:  # Allow up to 2 matches which might be false positives
                issues.append(message)
        
        # Check for proper list structure
        if '\\resumeSubheading' in latex_content:
            start_lists = latex_content.count('\\resumeSubHeadingListStart')
            end_lists = latex_content.count('\\resumeSubHeadingListEnd')
            if start_lists != end_lists:
                issues.append(f"Mismatched list environments: {start_lists} starts vs {end_lists} ends")
        
        # Only report if we found actual critical issues
        return issues

    async def generate_resume(
        self, 
        user_id: int, 
        profile_id: int, 
        job_description: str, 
        db: Session
    ) -> GeneratedResume:
        """
        Generate a tailored resume in LaTeX format.
        Users can copy the LaTeX and use with Overleaf or local LaTeX editor.
        """
        try:
            if not self._latex_template or "template not found" in self._latex_template or "Error loading" in self._latex_template:
                raise ValueError(f"LaTeX template is not loaded properly: {self._latex_template}")

            profile_data_dict = self._get_profile_data(user_id, profile_id, db)
            
            if not profile_data_dict.get("profile") or not profile_data_dict.get("user"):
                raise ValueError("Core profile or user data is missing.")

            llm_generated_sections = await self.llm_client.generate_resume_content(
                profile_data=profile_data_dict,
                job_description=job_description,
                user_id=user_id,
                db=db
            )

            populated_latex = self._latex_template
            user_obj = profile_data_dict["user"]
            
            user_full_name = f"{user_obj.get('firstName', '')} {user_obj.get('lastName', '')}".strip()
            user_email = user_obj.get('email', '[Your Email]')
            user_linkedin = profile_data_dict.get("profile", {}).get("linkedin_url", "").strip()
            user_github = profile_data_dict.get("profile", {}).get("github_url", "").strip()
            user_phone = profile_data_dict.get("profile", {}).get("phone_number", "").strip()
            user_location = profile_data_dict.get("profile", {}).get("location", "").strip()
            
            # Populate user info
            populated_latex = populated_latex.replace("[User Name]", self._escape_latex(user_full_name) or "Your Name")
            populated_latex = populated_latex.replace("[User Email]", self._escape_latex(user_email))
            
            # Build contact info based on what user provided
            contact_info = ""
            if user_linkedin:
                contact_info += f" $|$ \\faLinkedinSquare \\hspace{{.5pt}} \\href{{{self._escape_latex(user_linkedin)}}}{{LinkedIn}}"
            if user_github:
                contact_info += f" $|$ \\faGithub \\hspace{{.5pt}} \\href{{{self._escape_latex(user_github)}}}{{GitHub}}"
            if user_location:
                contact_info += f" $|$ \\faMapMarker \\hspace{{.5pt}} {{{self._escape_latex(user_location)}}}"
            if user_phone:
                contact_info += f" $|$ \\faPhone \\hspace{{.5pt}} {{{self._escape_latex(user_phone)}}}"
            
            populated_latex = populated_latex.replace("[LINKEDIN_CONTACT]", "")
            populated_latex = populated_latex.replace("[GITHUB_CONTACT]", "")
            populated_latex = populated_latex.replace("[LOCATION_CONTACT]", "")
            populated_latex = populated_latex.replace("[PHONE_CONTACT]", "")
            
            # Replace with actual contact info if provided
            if contact_info:
                populated_latex = populated_latex.replace("[LINKEDIN_CONTACT][GITHUB_CONTACT][LOCATION_CONTACT][PHONE_CONTACT]", contact_info)

            populated_latex = populated_latex.replace("[LLM_GENERATED_PROFILE_SUMMARY]", self._escape_latex(llm_generated_sections.get("PROFILE", "")))
            populated_latex = populated_latex.replace("[EDUCATION_SECTION_CONTENT]", self._format_education_section(llm_generated_sections.get("EDUCATION", ""), profile_data_dict))
            populated_latex = populated_latex.replace("[EXPERIENCE_SECTION_CONTENT]", self._format_experience_section(llm_generated_sections.get("EXPERIENCE", ""), profile_data_dict))
            populated_latex = populated_latex.replace("[PROJECTS_SECTION_CONTENT]", self._format_projects_section(llm_generated_sections.get("PROJECTS", ""), profile_data_dict))
            populated_latex = populated_latex.replace("[SKILLS_SECTION_CONTENT]", self._escape_latex(llm_generated_sections.get("SKILLS", "")))
            
            validation_issues = self._validate_latex_content(populated_latex)
            if validation_issues:
                logger.warning(f"LaTeX validation issues for user {user_id}, profile {profile_id}: {validation_issues}")

            generated_resume = GeneratedResume(
                user_id=user_id,
                profile_id=profile_id,
                job_description=job_description,
                latex_content=populated_latex
            )
            
            db.add(generated_resume)
            db.commit()
            db.refresh(generated_resume)
            
            return generated_resume
            
        except ValueError as ve:
            logger.warning(f"Resume generation ValueError for user {user_id}, profile {profile_id}: {ve}")
            raise
        except Exception as e:
            logger.error(f"Resume generation failed for user {user_id}, profile {profile_id}: {e}", exc_info=True)
            raise
    
    def _get_profile_data(self, user_id: int, profile_id: int, db: Session) -> Dict[str, Any]:
        """
        Retrieve complete profile data including user, profile, and related items.
        Keys in returned dictionaries are snake_case.
        """
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise ValueError(f"User {user_id} not found")

        profile = db.query(Profile).filter(Profile.id == profile_id, Profile.user_id == user_id).first()
        if not profile:
            raise ValueError(f"Profile {profile_id} not found for user {user_id}")
        
        education_list = db.query(Education).filter(Education.profile_id == profile_id).all()
        experience_list = db.query(Experience).filter(Experience.profile_id == profile_id).all()
        project_list = db.query(Project).filter(Project.profile_id == profile_id).all()
        skill_list = db.query(Skill).filter(Skill.profile_id == profile_id).all()
        
        # Return data with snake_case keys matching model attributes
        return {
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "firstName": user.firstName, # Note: User model uses camelCase from existing schema
                "lastName": user.lastName,   # This should be ideally snake_case in model too
            },
            "profile": {
                "id": profile.id,
                "name": profile.name, # This is the profile's custom name, not the user's name
                "user_id": profile.user_id
            },
            "education": [
                {
                    "institution": edu.institution,
                    "degree": edu.degree,
                    "field_of_study": edu.field_of_study, # snake_case
                    "start_date": str(edu.start_date) if edu.start_date else None, # snake_case
                    "end_date": str(edu.end_date) if edu.end_date else None, # snake_case
                    "description": edu.description
                }
                for edu in education_list
            ],
            "experience": [
                {
                    "company": exp.company,
                    "position": exp.position,
                    "start_date": str(exp.start_date) if exp.start_date else None, # snake_case
                    "end_date": str(exp.end_date) if exp.end_date else None, # snake_case
                    "description": exp.description
                }
                for exp in experience_list
            ],
            "projects": [
                {
                    "title": proj.title,
                    "start_date": str(proj.start_date) if proj.start_date else None, # snake_case
                    "end_date": str(proj.end_date) if proj.end_date else None, # snake_case
                    "description": proj.description,
                    "technologies": proj.technologies # This is likely a list or string
                }
                for proj in project_list
            ],
            "skills": [
                {
                    "name": skill.name,
                    "proficiency": skill.proficiency # snake_case
                }
                for skill in skill_list
            ]
        }
    
    def get_user_resumes(self, user_id: int, db: Session) -> List[GeneratedResume]:
        """
        Get all generated resumes for a user
        """
        return db.query(GeneratedResume).filter(
            GeneratedResume.user_id == user_id
        ).order_by(GeneratedResume.created_at.desc()).all()
    
    def get_resume_by_id(self, resume_id: int, user_id: int, db: Session) -> GeneratedResume:
        """
        Get a specific resume by ID (ensuring user ownership)
        """
        resume = db.query(GeneratedResume).filter(
            GeneratedResume.id == resume_id,
            GeneratedResume.user_id == user_id
        ).first()
        
        if not resume:
            # Consider raising a more specific exception or allowing route to handle 404
            raise ValueError(f"Resume {resume_id} not found for user {user_id}")
        
        return resume
    
    def delete_resume(self, resume_id: int, user_id: int, db: Session) -> bool:
        """
        Delete a generated resume (ensuring user ownership)
        """
        resume = self.get_resume_by_id(resume_id, user_id, db) # This already raises if not found
        db.delete(resume)
        db.commit()
        return True 