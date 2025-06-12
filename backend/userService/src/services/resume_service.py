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
import subprocess # For PDF generation
import time # For unique filenames
import tempfile # For temporary LaTeX files

logger = logging.getLogger(__name__)

# Define the path to the template relative to this file's directory
TEMPLATE_DIR = os.path.dirname(__file__)
RESUME_TEMPLATE_PATH = os.path.join(TEMPLATE_DIR, "resume_template.tex")
# Define where PDFs will be stored INSIDE the container
PDF_OUTPUT_DIR_IN_CONTAINER = "/app/generated_pdfs"

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
        if text is None:
            return ""
        # Basic LaTeX escaping for special characters
        # This is not exhaustive but covers common cases.
        # A more robust solution might use a dedicated library if complex text is expected.
        char_map = {
            '&': r'\\&',
            '%': r'\\%',
            '$': r'\\$',
            '#': r'\\#',
            '_': r'\\_',
            '{': r'\\{',
            '}': r'\\}',
            '~': r'\\textasciitilde{}',
            '^': r'\\textasciicircum{}',
            '\\': r'\\textbackslash{}',
            '<': r'\\textless{}',
            '>': r'\\textgreater{}',
        }
        # Additionally, escape common problematic sequences if LLM outputs them despite instructions
        # For example, if LLM tries to make its own bullet points with LaTeX commands
        text = text.replace(r"\item", "-") # Replace LaTeX item with a simple dash for LLM content

        res = ""
        for char in text:
            res += char_map.get(char, char)
        return res

    def _compile_latex_to_pdf(self, latex_content: str, user_id: int, profile_id: int) -> Optional[str]:
        """
        Compiles LaTeX content to a PDF file.
        Returns the relative path to the PDF if successful, None otherwise.
        """
        timestamp = int(time.time())
        base_filename = f"resume_u{user_id}_p{profile_id}_{timestamp}"
        
        # Use a temporary directory for LaTeX compilation intermediate files
        with tempfile.TemporaryDirectory() as temp_dir:
            tex_file_path = os.path.join(temp_dir, f"{base_filename}.tex")
            pdf_filename = f"{base_filename}.pdf"
            # Final PDF path relative to the /app directory in the container
            final_pdf_relative_path = os.path.join(os.path.basename(PDF_OUTPUT_DIR_IN_CONTAINER), pdf_filename)
            # Absolute path for pdflatex output
            final_pdf_abs_path_in_container = os.path.join(PDF_OUTPUT_DIR_IN_CONTAINER, pdf_filename)


            with open(tex_file_path, "w", encoding="utf-8") as f:
                f.write(latex_content)

            try:
                # Run pdflatex twice to resolve cross-references (if any)
                for _ in range(2): 
                    process = subprocess.run(
                        [
                            "pdflatex",
                            "-interaction=nonstopmode",
                            "-output-directory", temp_dir, # Output .aux, .log, .pdf to temp_dir first
                            tex_file_path
                        ],
                        capture_output=True, text=True, check=False, timeout=30 # Added timeout
                    )
                    if process.returncode != 0:
                        logger.error(
                            f"pdflatex compilation failed (user {user_id}, profile {profile_id}). "
                            f"Return code: {process.returncode}\\n"
                            f"Stdout: {process.stdout}\\nStderr: {process.stderr}"
                        )
                        log_file_path = os.path.join(temp_dir, f"{base_filename}.log")
                        if os.path.exists(log_file_path):
                            with open(log_file_path, "r", encoding="utf-8") as log_f:
                                logger.error(f"pdflatex log:\\n{log_f.read()}")
                        return None
                
                # Move the generated PDF from temp_dir to the final PDF_OUTPUT_DIR_IN_CONTAINER
                temp_pdf_path = os.path.join(temp_dir, pdf_filename)
                if os.path.exists(temp_pdf_path):
                    os.makedirs(PDF_OUTPUT_DIR_IN_CONTAINER, exist_ok=True) # Ensure final dir exists
                    os.rename(temp_pdf_path, final_pdf_abs_path_in_container)
                    logger.info(f"PDF generated successfully: {final_pdf_relative_path}")
                    return final_pdf_relative_path
                else:
                    logger.error(f"PDF file not found at {temp_pdf_path} after pdflatex compilation.")
                    return None

            except subprocess.TimeoutExpired:
                logger.error(f"pdflatex compilation timed out for user {user_id}, profile {profile_id}.")
                return None
            except Exception as e:
                logger.error(f"Error during PDF compilation for user {user_id}, profile {profile_id}: {e}", exc_info=True)
                return None
        return None # Should not be reached if logic is correct

    async def generate_resume(
        self, 
        user_id: int, 
        profile_id: int, 
        job_description: str, 
        db: Session
    ) -> GeneratedResume:
        """
        Generate a tailored resume, compile to PDF, and save
        """
        try:
            if not self._latex_template or "template not found" in self._latex_template or "Error loading" in self._latex_template :
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
            
            populated_latex = populated_latex.replace("[User Name]", self._escape_latex(user_full_name) or "Your Name")
            populated_latex = populated_latex.replace("[User Email]", self._escape_latex(user_email))
            populated_latex = populated_latex.replace("[User LinkedIn URL]", "#")
            populated_latex = populated_latex.replace("[User LinkedIn Profile]", "Your LinkedIn Profile")
            populated_latex = populated_latex.replace("[User GitHub URL]", "#")
            populated_latex = populated_latex.replace("[User GitHub Profile]", "Your GitHub Profile")
            populated_latex = populated_latex.replace("[User City, State/Province, Country]", "Your City, State")
            populated_latex = populated_latex.replace("[User Phone Number]", "Your Phone Number")

            populated_latex = populated_latex.replace("[LLM_GENERATED_PROFILE_SUMMARY]", self._escape_latex(llm_generated_sections.get("PROFILE", "")))
            populated_latex = populated_latex.replace("[EDUCATION_SECTION_CONTENT]", self._escape_latex(llm_generated_sections.get("EDUCATION", "")))
            populated_latex = populated_latex.replace("[EXPERIENCE_SECTION_CONTENT]", self._escape_latex(llm_generated_sections.get("EXPERIENCE", "")))
            populated_latex = populated_latex.replace("[PROJECTS_SECTION_CONTENT]", self._escape_latex(llm_generated_sections.get("PROJECTS", "")))
            populated_latex = populated_latex.replace("[SKILLS_SECTION_CONTENT]", self._escape_latex(llm_generated_sections.get("SKILLS", "")))
            
            # Compile LaTeX to PDF
            pdf_path = None
            if populated_latex and "template not found" not in populated_latex and "Error loading" not in populated_latex:
                pdf_path = self._compile_latex_to_pdf(populated_latex, user_id, profile_id)
            else:
                logger.error(f"Skipping PDF compilation due to invalid LaTeX content for user {user_id}, profile {profile_id}.")


            generated_resume = GeneratedResume(
                user_id=user_id,
                profile_id=profile_id,
                job_description=job_description,
                latex_content=populated_latex,
                pdf_file_path=pdf_path # Store the relative path to the PDF
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