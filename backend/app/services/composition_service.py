import json
from typing import List, Dict, Any, Optional
from datetime import datetime
from openai import OpenAI
from ..core.config import settings
from ..utils.logger import setup_logger
from ..models.composition import (
    EmailComposeRequest, EmailComposeResponse, ProposalComposeRequest, 
    ProposalComposeResponse, CompositionHistory, CompositionListResponse,
    ToneType, EmailType, ProposalType
)

logger = setup_logger(__name__)

class CompositionService:
    def __init__(self):
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
        self.composition_history = {}  # In-memory storage for demo purposes
        
    async def compose_email(self, request: EmailComposeRequest) -> EmailComposeResponse:
        """
        Compose a professional email using OpenAI.
        
        Args:
            request: EmailComposeRequest with composition parameters
            
        Returns:
            EmailComposeResponse with generated email
        """
        try:
            logger.info(f"Composing {request.email_type.value} email for {request.recipient_name or request.recipient_email}")
            
            # Create email composition prompt
            prompt = self._create_email_prompt(request)
            
            # Get response from OpenAI
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=1000,
                temperature=0.7
            )
            
            email_body = response.choices[0].message.content
            
            # Generate alternative subjects
            alternative_subjects = await self._generate_alternative_subjects(request)
            
            # Generate suggestions for improvement
            suggestions = await self._generate_email_suggestions(email_body, request)
            
            # Create response
            response_obj = EmailComposeResponse(
                subject=request.subject,
                body=email_body,
                sender_name=request.sender_name,
                sender_email=request.sender_email,
                recipient_name=request.recipient_name,
                recipient_email=request.recipient_email,
                email_type=request.email_type,
                tone=request.tone,
                word_count=len(email_body.split()),
                alternative_subjects=alternative_subjects,
                suggestions=suggestions
            )
            
            # Store in history
            self._store_composition_history(response_obj, "email")
            
            logger.info(f"Email composed successfully with {response_obj.word_count} words")
            return response_obj
            
        except Exception as e:
            logger.error(f"Error composing email: {str(e)}")
            raise
    
    async def compose_proposal(self, request: ProposalComposeRequest) -> ProposalComposeResponse:
        """
        Compose a business proposal using OpenAI.
        
        Args:
            request: ProposalComposeRequest with composition parameters
            
        Returns:
            ProposalComposeResponse with generated proposal
        """
        try:
            logger.info(f"Composing {request.proposal_type.value} proposal for {request.client_name}")
            
            # Create proposal composition prompt
            prompt = self._create_proposal_prompt(request)
            
            # Get response from OpenAI
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=2000,
                temperature=0.6
            )
            
            proposal_content = response.choices[0].message.content
            
            # Parse proposal sections
            sections = self._parse_proposal_sections(proposal_content, request)
            
            # Generate suggestions
            suggestions = await self._generate_proposal_suggestions(sections, request)
            
            # Create response
            response_obj = ProposalComposeResponse(
                title=request.title,
                content=sections,
                proposal_type=request.proposal_type,
                client_name=request.client_name,
                company_name=request.company_name,
                tone=request.tone,
                word_count=len(proposal_content.split()),
                sections_included=list(sections.keys()),
                suggestions=suggestions
            )
            
            # Store in history
            self._store_composition_history(response_obj, "proposal")
            
            logger.info(f"Proposal composed successfully with {response_obj.word_count} words")
            return response_obj
            
        except Exception as e:
            logger.error(f"Error composing proposal: {str(e)}")
            raise
    
    def _create_email_prompt(self, request: EmailComposeRequest) -> str:
        """Create prompt for email composition."""
        tone_descriptions = {
            ToneType.FORMAL: "formal and professional",
            ToneType.PROFESSIONAL: "professional and business-like",
            ToneType.FRIENDLY: "friendly and approachable",
            ToneType.CASUAL: "casual and conversational",
            ToneType.PERSUASIVE: "persuasive and compelling",
            ToneType.INFORMATIVE: "informative and clear"
        }
        
        email_type_templates = {
            EmailType.FOLLOW_UP: "follow-up email",
            EmailType.INTRODUCTION: "introduction email",
            EmailType.MEETING_REQUEST: "meeting request email",
            EmailType.THANK_YOU: "thank you email",
            EmailType.ANNOUNCEMENT: "announcement email",
            EmailType.CUSTOM: "custom email"
        }
        
        prompt = f"""
        You are an expert business communication specialist. Compose a {email_type_templates[request.email_type]} with a {tone_descriptions[request.tone]} tone.
        
        Email Details:
        - Subject: {request.subject}
        - Sender: {request.sender_name} ({request.sender_email})
        - Recipient: {request.recipient_name or 'Recipient'} {f'({request.recipient_email})' if request.recipient_email else ''}
        - Context: {request.context}
        """
        
        if request.key_points:
            prompt += f"\nKey points to include:\n" + "\n".join([f"- {point}" for point in request.key_points])
        
        if request.call_to_action:
            prompt += f"\nCall to action: {request.call_to_action}"
        
        prompt += f"""
        
        Requirements:
        - Keep the email concise and focused
        - Use a {tone_descriptions[request.tone]} tone throughout
        - Make it professional and well-structured
        - Include a clear subject line
        - End with an appropriate closing
        """
        
        if request.include_signature:
            prompt += "\n- Include a professional email signature"
        
        if request.word_limit:
            prompt += f"\n- Target approximately {request.word_limit} words"
        
        prompt += "\n\nPlease compose the email body only (without the subject line):"
        
        return prompt
    
    def _create_proposal_prompt(self, request: ProposalComposeRequest) -> str:
        """Create prompt for proposal composition."""
        tone_descriptions = {
            ToneType.FORMAL: "formal and professional",
            ToneType.PROFESSIONAL: "professional and business-like",
            ToneType.FRIENDLY: "friendly and approachable",
            ToneType.CASUAL: "casual and conversational",
            ToneType.PERSUASIVE: "persuasive and compelling",
            ToneType.INFORMATIVE: "informative and clear"
        }
        
        proposal_type_templates = {
            ProposalType.BUSINESS_PROPOSAL: "business proposal",
            ProposalType.PROJECT_PROPOSAL: "project proposal",
            ProposalType.PARTNERSHIP_PROPOSAL: "partnership proposal",
            ProposalType.INVESTMENT_PROPOSAL: "investment proposal",
            ProposalType.CUSTOM: "custom proposal"
        }
        
        prompt = f"""
        You are an expert business proposal writer. Compose a {proposal_type_templates[request.proposal_type]} with a {tone_descriptions[request.tone]} tone.
        
        Proposal Details:
        - Title: {request.title}
        - Client: {request.client_name}
        - Company: {request.company_name}
        - Project Description: {request.project_description}
        - Objectives: {', '.join(request.objectives)}
        - Deliverables: {', '.join(request.deliverables)}
        """
        
        if request.timeline:
            prompt += f"\n- Timeline: {request.timeline}"
        
        if request.budget_range:
            prompt += f"\n- Budget Range: {request.budget_range}"
        
        prompt += f"""
        
        Required Sections:
        """
        
        if request.include_executive_summary:
            prompt += "- Executive Summary\n"
        
        if request.include_company_background:
            prompt += "- Company Background\n"
        
        prompt += "- Project Overview\n- Objectives and Deliverables\n- Methodology/Approach\n"
        
        if request.timeline:
            prompt += "- Timeline\n"
        
        if request.budget_range:
            prompt += "- Budget\n"
        
        prompt += "- Conclusion\n"
        
        if request.custom_sections:
            for section in request.custom_sections:
                prompt += f"- {section}\n"
        
        prompt += f"""
        
        Requirements:
        - Use a {tone_descriptions[request.tone]} tone throughout
        - Make it professional and well-structured
        - Include clear section headers
        - Be persuasive and compelling
        - Focus on value proposition for the client
        
        Please compose the proposal with clear section headers in the format:
        ## Section Name
        Content...
        """
        
        return prompt
    
    def _parse_proposal_sections(self, content: str, request: ProposalComposeRequest) -> Dict[str, str]:
        """Parse proposal content into sections."""
        sections = {}
        current_section = "main"
        current_content = []
        
        lines = content.split('\n')
        for line in lines:
            if line.strip().startswith('##'):
                # Save previous section
                if current_content:
                    sections[current_section] = '\n'.join(current_content).strip()
                
                # Start new section
                current_section = line.strip('#').strip().lower().replace(' ', '_')
                current_content = []
            else:
                current_content.append(line)
        
        # Save last section
        if current_content:
            sections[current_section] = '\n'.join(current_content).strip()
        
        return sections
    
    async def _generate_alternative_subjects(self, request: EmailComposeRequest) -> List[str]:
        """Generate alternative subject lines for the email."""
        try:
            prompt = f"""
            Generate 3 alternative subject lines for this email:
            
            Original subject: {request.subject}
            Email type: {request.email_type.value}
            Context: {request.context}
            Tone: {request.tone.value}
            
            Requirements:
            - Keep them concise (under 60 characters)
            - Make them compelling and professional
            - Avoid spam trigger words
            - Be specific and relevant
            
            Return only the subject lines, one per line:
            """
            
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=200,
                temperature=0.8
            )
            
            subjects = response.choices[0].message.content.strip().split('\n')
            return [s.strip() for s in subjects if s.strip()][:3]
            
        except Exception as e:
            logger.warning(f"Could not generate alternative subjects: {str(e)}")
            return []
    
    async def _generate_email_suggestions(self, email_body: str, request: EmailComposeRequest) -> List[str]:
        """Generate suggestions for improving the email."""
        try:
            prompt = f"""
            Review this email and provide 2-3 specific suggestions for improvement:
            
            Email Body:
            {email_body}
            
            Original Requirements:
            - Type: {request.email_type.value}
            - Tone: {request.tone.value}
            - Context: {request.context}
            
            Focus on:
            - Clarity and conciseness
            - Professional tone
            - Call to action effectiveness
            - Grammar and structure
            
            Provide specific, actionable suggestions:
            """
            
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=300,
                temperature=0.5
            )
            
            suggestions = response.choices[0].message.content.strip().split('\n')
            return [s.strip().lstrip('- ').lstrip('* ') for s in suggestions if s.strip()][:3]
            
        except Exception as e:
            logger.warning(f"Could not generate email suggestions: {str(e)}")
            return []
    
    async def _generate_proposal_suggestions(self, sections: Dict[str, str], request: ProposalComposeRequest) -> List[str]:
        """Generate suggestions for improving the proposal."""
        try:
            content_preview = "\n\n".join([f"{k}: {v[:200]}..." for k, v in sections.items()])
            
            prompt = f"""
            Review this proposal and provide 2-3 specific suggestions for improvement:
            
            Proposal Content Preview:
            {content_preview}
            
            Original Requirements:
            - Type: {request.proposal_type.value}
            - Tone: {request.tone.value}
            - Client: {request.client_name}
            
            Focus on:
            - Value proposition clarity
            - Professional presentation
            - Persuasiveness
            - Structure and flow
            
            Provide specific, actionable suggestions:
            """
            
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=300,
                temperature=0.5
            )
            
            suggestions = response.choices[0].message.content.strip().split('\n')
            return [s.strip().lstrip('- ').lstrip('* ') for s in suggestions if s.strip()][:3]
            
        except Exception as e:
            logger.warning(f"Could not generate proposal suggestions: {str(e)}")
            return []
    
    def _store_composition_history(self, composition, comp_type: str):
        """Store composition in history."""
        history_item = CompositionHistory(
            composition_type=comp_type,
            title=composition.subject if hasattr(composition, 'subject') else composition.title,
            content_preview=composition.body[:100] + "..." if hasattr(composition, 'body') else str(composition.content)[:100] + "..."
        )
        
        self.composition_history[history_item.id] = history_item
    
    async def get_composition_history(self, page: int = 1, per_page: int = 20) -> CompositionListResponse:
        """
        Get composition history with pagination.
        
        Args:
            page: Page number (1-based)
            per_page: Number of items per page
            
        Returns:
            CompositionListResponse with paginated history
        """
        try:
            all_compositions = list(self.composition_history.values())
            
            # Sort by creation date (newest first)
            all_compositions.sort(key=lambda x: x.created_at, reverse=True)
            
            # Apply pagination
            start_idx = (page - 1) * per_page
            end_idx = start_idx + per_page
            paginated_compositions = all_compositions[start_idx:end_idx]
            
            return CompositionListResponse(
                compositions=paginated_compositions,
                total_count=len(all_compositions),
                page=page,
                per_page=per_page
            )
            
        except Exception as e:
            logger.error(f"Error getting composition history: {str(e)}")
            raise 