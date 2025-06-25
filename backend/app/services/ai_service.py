"""
AI service for intelligent contract analysis and suggestions
"""
import asyncio
from typing import List, Dict, Any, Optional
import json
import re
from datetime import datetime

# Import AI libraries
try:
    import openai
    from openai import AsyncOpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

try:
    import anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False

from app.core.config import settings
from app.schemas.ai_suggestion import AISuggestionCreate
from app.schemas.contract import ContractAnalytics

class AIService:
    def __init__(self):
        self.openai_client = None
        self.anthropic_client = None
        
        if OPENAI_AVAILABLE and settings.OPENAI_API_KEY:
            self.openai_client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        
        if ANTHROPIC_AVAILABLE and settings.ANTHROPIC_API_KEY:
            self.anthropic_client = anthropic.AsyncAnthropic(api_key=settings.ANTHROPIC_API_KEY)

    async def analyze_contract(self, contract_content: str, contract_type: Optional[str] = None) -> ContractAnalytics:
        """Perform comprehensive contract analysis"""
        if not self.openai_client and not self.anthropic_client:
            return self._basic_analysis(contract_content)
        
        try:
            # Use AI for analysis
            analysis_prompt = self._build_analysis_prompt(contract_content, contract_type)
            
            if self.openai_client:
                result = await self._analyze_with_openai(analysis_prompt)
            elif self.anthropic_client:
                result = await self._analyze_with_anthropic(analysis_prompt)
            else:
                return self._basic_analysis(contract_content)
            
            return self._parse_analysis_result(result, contract_content)
            
        except Exception as e:
            print(f"AI analysis failed: {e}")
            return self._basic_analysis(contract_content)

    async def generate_suggestions(self, contract_content: str, contract_id: int, suggestion_types: List[str] = None) -> List[AISuggestionCreate]:
        """Generate AI-powered suggestions for contract improvement"""
        if not self.openai_client and not self.anthropic_client:
            return self._generate_basic_suggestions(contract_content, contract_id)
        
        try:
            suggestions_prompt = self._build_suggestions_prompt(contract_content, suggestion_types)
            
            if self.openai_client:
                result = await self._generate_with_openai(suggestions_prompt)
            elif self.anthropic_client:
                result = await self._generate_with_anthropic(suggestions_prompt)
            else:
                return self._generate_basic_suggestions(contract_content, contract_id)
            
            return self._parse_suggestions_result(result, contract_id)
            
        except Exception as e:
            print(f"AI suggestion generation failed: {e}")
            return self._generate_basic_suggestions(contract_content, contract_id)

    async def _analyze_with_openai(self, prompt: str) -> str:
        """Analyze contract using OpenAI"""
        response = await self.openai_client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a legal contract analysis expert. Provide detailed, structured analysis."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.1,
            max_tokens=2000
        )
        return response.choices[0].message.content

    async def _analyze_with_anthropic(self, prompt: str) -> str:
        """Analyze contract using Anthropic Claude"""
        response = await self.anthropic_client.messages.create(
            model="claude-3-sonnet-20240229",
            max_tokens=2000,
            temperature=0.1,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        return response.content[0].text

    async def _generate_with_openai(self, prompt: str) -> str:
        """Generate suggestions using OpenAI"""
        response = await self.openai_client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a legal contract expert. Generate practical, actionable suggestions for contract improvement. Return suggestions in JSON format."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=1500
        )
        return response.choices[0].message.content

    async def _generate_with_anthropic(self, prompt: str) -> str:
        """Generate suggestions using Anthropic Claude"""
        response = await self.anthropic_client.messages.create(
            model="claude-3-sonnet-20240229",
            max_tokens=1500,
            temperature=0.3,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        return response.content[0].text

    def _build_analysis_prompt(self, content: str, contract_type: Optional[str] = None) -> str:
        """Build prompt for contract analysis"""
        type_context = f" This is a {contract_type} contract." if contract_type else ""
        
        return f"""
        Analyze the following legal contract and provide a comprehensive assessment.{type_context}
        
        Contract Content:
        {content[:4000]}  # Limit content length
        
        Please provide analysis in the following JSON format:
        {{
            "risk_score": 0.0-1.0,
            "completeness_score": 0.0-1.0,
            "reading_level": "Grade 8-12 or Professional",
            "identified_risks": [
                {{"type": "error|warning|info", "message": "description", "section": "clause location"}}
            ],
            "missing_clauses": [
                {{"clause_type": "type", "description": "what's missing", "importance": "high|medium|low"}}
            ],
            "compliance_issues": [
                {{"issue": "description", "severity": "critical|high|medium|low", "recommendation": "how to fix"}}
            ]
        }}
        """

    def _build_suggestions_prompt(self, content: str, suggestion_types: List[str] = None) -> str:
        """Build prompt for suggestions generation"""
        types_context = ""
        if suggestion_types:
            types_context = f" Focus on: {', '.join(suggestion_types)}."
        
        return f"""
        Analyze this legal contract and generate specific improvement suggestions.{types_context}
        
        Contract Content:
        {content[:4000]}
        
        Generate suggestions in JSON format:
        {{
            "suggestions": [
                {{
                    "title": "Brief title",
                    "description": "Detailed explanation",
                    "suggestion_type": "clause_addition|text_improvement|risk_mitigation|compliance_check",
                    "category": "payment_terms|liability|termination|etc",
                    "severity": "low|medium|high|critical",
                    "confidence_score": 0.0-1.0,
                    "suggested_text": "replacement text if applicable",
                    "position": {{"start": 0, "end": 100, "line": 5}},
                    "legal_basis": "legal reasoning",
                    "jurisdiction_specific": true/false
                }}
            ]
        }}
        """

    def _basic_analysis(self, content: str) -> ContractAnalytics:
        """Provide basic analysis without AI"""
        word_count = len(content.split())
        
        # Simple risk assessment based on keywords
        risk_keywords = ["shall", "must", "penalty", "terminate", "breach", "default"]
        risk_score = min(len([w for w in content.lower().split() if w in risk_keywords]) / 100, 1.0)
        
        # Basic completeness check
        required_sections = ["payment", "term", "scope", "liability"]
        completeness = len([s for s in required_sections if s in content.lower()]) / len(required_sections)
        
        return ContractAnalytics(
            word_count=word_count,
            reading_level="Grade 10-12",
            risk_score=risk_score,
            completeness_score=completeness,
            identified_risks=[
                {"type": "info", "message": "Basic analysis - AI services not available"}
            ],
            missing_clauses=[],
            compliance_issues=[]
        )

    def _generate_basic_suggestions(self, content: str, contract_id: int) -> List[AISuggestionCreate]:
        """Generate basic suggestions without AI"""
        suggestions = []
        
        # Check for common missing elements
        if "termination" not in content.lower():
            suggestions.append(AISuggestionCreate(
                contract_id=contract_id,
                title="Add Termination Clause",
                description="Consider adding a clear termination clause to define how the contract can be ended.",
                suggestion_type="clause_addition",
                category="termination",
                severity="medium",
                confidence_score=0.8,
                legal_basis="Standard contract practice"
            ))
        
        if "liability" not in content.lower():
            suggestions.append(AISuggestionCreate(
                contract_id=contract_id,
                title="Add Liability Limitations",
                description="Consider adding liability limitation clauses to protect both parties.",
                suggestion_type="risk_mitigation",
                category="liability",
                severity="high",
                confidence_score=0.9,
                legal_basis="Risk management best practice"
            ))
        
        return suggestions

    def _parse_analysis_result(self, result: str, content: str) -> ContractAnalytics:
        """Parse AI analysis result into ContractAnalytics"""
        try:
            # Try to extract JSON from the result
            json_match = re.search(r'\{.*\}', result, re.DOTALL)
            if json_match:
                data = json.loads(json_match.group())
                return ContractAnalytics(
                    word_count=len(content.split()),
                    reading_level=data.get("reading_level", "Grade 10-12"),
                    risk_score=data.get("risk_score", 0.5),
                    completeness_score=data.get("completeness_score", 0.7),
                    identified_risks=data.get("identified_risks", []),
                    missing_clauses=data.get("missing_clauses", []),
                    compliance_issues=data.get("compliance_issues", [])
                )
        except Exception as e:
            print(f"Failed to parse analysis result: {e}")
        
        return self._basic_analysis(content)

    def _parse_suggestions_result(self, result: str, contract_id: int) -> List[AISuggestionCreate]:
        """Parse AI suggestions result into AISuggestionCreate objects"""
        try:
            # Try to extract JSON from the result
            json_match = re.search(r'\{.*\}', result, re.DOTALL)
            if json_match:
                data = json.loads(json_match.group())
                suggestions = []
                
                for suggestion_data in data.get("suggestions", []):
                    suggestion = AISuggestionCreate(
                        contract_id=contract_id,
                        title=suggestion_data.get("title", "AI Suggestion"),
                        description=suggestion_data.get("description", ""),
                        suggestion_type=suggestion_data.get("suggestion_type", "text_improvement"),
                        category=suggestion_data.get("category"),
                        severity=suggestion_data.get("severity", "medium"),
                        confidence_score=suggestion_data.get("confidence_score"),
                        suggested_text=suggestion_data.get("suggested_text"),
                        position=suggestion_data.get("position"),
                        legal_basis=suggestion_data.get("legal_basis"),
                        jurisdiction_specific=suggestion_data.get("jurisdiction_specific", False),
                        ai_model="gpt-4" if self.openai_client else "claude-3-sonnet"
                    )
                    suggestions.append(suggestion)
                
                return suggestions
        except Exception as e:
            print(f"Failed to parse suggestions result: {e}")
        
        return self._generate_basic_suggestions("", contract_id)