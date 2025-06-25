"""
Document analysis service for contract processing
"""
import re
import json
from typing import Dict, Any, List, Optional
from datetime import datetime

class DocumentAnalyzer:
    """Service for analyzing contract documents and extracting insights"""
    
    def __init__(self):
        # Legal terms that indicate risk
        self.risk_indicators = [
            "penalty", "liquidated damages", "breach", "default", "termination for cause",
            "indemnification", "liability", "force majeure", "confidentiality breach",
            "non-compete", "non-disclosure violation", "intellectual property infringement"
        ]
        
        # Essential contract clauses
        self.essential_clauses = [
            "payment terms", "scope of work", "deliverables", "timeline",
            "termination", "liability", "confidentiality", "intellectual property",
            "dispute resolution", "governing law", "force majeure"
        ]
        
        # Compliance keywords by jurisdiction
        self.compliance_keywords = {
            "gdpr": ["personal data", "data processing", "data subject rights", "privacy"],
            "ccpa": ["consumer rights", "personal information", "opt-out"],
            "sox": ["financial reporting", "internal controls", "audit"],
            "hipaa": ["protected health information", "phi", "medical records"]
        }

    def analyze_document_structure(self, content: str) -> Dict[str, Any]:
        """Analyze the structure and organization of a contract"""
        lines = content.split('\n')
        
        # Count sections and subsections
        section_pattern = r'^(\d+\.|\([a-z]\)|\([0-9]+\)|[A-Z]+\.)'
        sections = [line for line in lines if re.match(section_pattern, line.strip())]
        
        # Find headings (lines in ALL CAPS or with specific formatting)
        heading_pattern = r'^[A-Z\s\d\.\-]+$'
        headings = [line.strip() for line in lines if re.match(heading_pattern, line.strip()) and len(line.strip()) > 5]
        
        # Calculate readability metrics
        word_count = len(content.split())
        sentence_count = len(re.findall(r'[.!?]+', content))
        avg_sentence_length = word_count / sentence_count if sentence_count > 0 else 0
        
        # Estimate reading level (simplified Flesch-Kincaid)
        reading_level = self._calculate_reading_level(content)
        
        return {
            "structure": {
                "total_lines": len(lines),
                "sections": len(sections),
                "headings": len(headings),
                "section_list": sections[:10]  # First 10 sections
            },
            "readability": {
                "word_count": word_count,
                "sentence_count": sentence_count,
                "avg_sentence_length": round(avg_sentence_length, 2),
                "reading_level": reading_level
            }
        }

    def identify_contract_type(self, content: str) -> str:
        """Identify the type of contract based on content analysis"""
        content_lower = content.lower()
        
        type_indicators = {
            "service_agreement": ["services", "performance", "deliverables", "scope of work"],
            "employment": ["employee", "employment", "salary", "benefits", "termination"],
            "nda": ["confidentiality", "non-disclosure", "proprietary information", "trade secrets"],
            "license": ["license", "intellectual property", "software", "usage rights"],
            "lease": ["lease", "rent", "premises", "landlord", "tenant"],
            "purchase": ["purchase", "sale", "goods", "delivery", "payment terms"],
            "partnership": ["partnership", "joint venture", "profit sharing", "management"],
            "consulting": ["consultant", "advisory", "professional services", "expertise"]
        }
        
        max_score = 0
        identified_type = "general"
        
        for contract_type, keywords in type_indicators.items():
            score = sum(1 for keyword in keywords if keyword in content_lower)
            if score > max_score:
                max_score = score
                identified_type = contract_type
        
        return identified_type

    def extract_key_terms(self, content: str) -> Dict[str, Any]:
        """Extract key terms and dates from the contract"""
        # Extract dates
        date_pattern = r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b|\b(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},?\s+\d{4}\b'
        dates = re.findall(date_pattern, content, re.IGNORECASE)
        
        # Extract monetary amounts
        money_pattern = r'\$[\d,]+(?:\.\d{2})?'
        amounts = re.findall(money_pattern, content)
        
        # Extract email addresses
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = re.findall(email_pattern, content)
        
        # Extract phone numbers
        phone_pattern = r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b'
        phones = re.findall(phone_pattern, content)
        
        # Extract percentages
        percentage_pattern = r'\b\d+(?:\.\d+)?%\b'
        percentages = re.findall(percentage_pattern, content)
        
        return {
            "dates": dates[:10],  # Limit to first 10
            "monetary_amounts": amounts[:10],
            "email_addresses": emails,
            "phone_numbers": phones,
            "percentages": percentages
        }

    def assess_completeness(self, content: str, contract_type: str = "general") -> Dict[str, Any]:
        """Assess how complete the contract is based on essential clauses"""
        content_lower = content.lower()
        
        # Get relevant essential clauses for contract type
        relevant_clauses = self._get_relevant_clauses(contract_type)
        
        found_clauses = []
        missing_clauses = []
        
        for clause in relevant_clauses:
            # Check if clause or related terms are present
            clause_found = False
            for term in clause["keywords"]:
                if term in content_lower:
                    clause_found = True
                    break
            
            if clause_found:
                found_clauses.append(clause["name"])
            else:
                missing_clauses.append({
                    "clause_type": clause["name"],
                    "description": clause["description"],
                    "importance": clause["importance"]
                })
        
        completeness_score = len(found_clauses) / len(relevant_clauses) if relevant_clauses else 1.0
        
        return {
            "completeness_score": round(completeness_score, 2),
            "found_clauses": found_clauses,
            "missing_clauses": missing_clauses,
            "total_expected": len(relevant_clauses)
        }

    def identify_risks(self, content: str) -> List[Dict[str, Any]]:
        """Identify potential risks in the contract"""
        content_lower = content.lower()
        identified_risks = []
        
        # Check for risk indicators
        for indicator in self.risk_indicators:
            if indicator in content_lower:
                # Find context around the risk indicator
                pattern = rf'.{{0,100}}{re.escape(indicator)}.{{0,100}}'
                matches = re.findall(pattern, content_lower, re.IGNORECASE)
                
                for match in matches[:3]:  # Limit to 3 matches per indicator
                    identified_risks.append({
                        "type": "warning",
                        "message": f"Risk indicator found: {indicator}",
                        "context": match.strip(),
                        "severity": self._assess_risk_severity(indicator)
                    })
        
        # Check for imbalanced terms
        imbalanced_terms = self._check_imbalanced_terms(content_lower)
        identified_risks.extend(imbalanced_terms)
        
        # Check for vague language
        vague_language = self._check_vague_language(content_lower)
        identified_risks.extend(vague_language)
        
        return identified_risks[:20]  # Limit to 20 risks

    def check_compliance(self, content: str, jurisdiction: str = "general") -> List[Dict[str, Any]]:
        """Check for compliance issues based on jurisdiction"""
        content_lower = content.lower()
        compliance_issues = []
        
        # Check for GDPR compliance if EU jurisdiction
        if jurisdiction.lower() in ["eu", "europe", "gdpr"]:
            gdpr_issues = self._check_gdpr_compliance(content_lower)
            compliance_issues.extend(gdpr_issues)
        
        # Check for general compliance issues
        general_issues = self._check_general_compliance(content_lower)
        compliance_issues.extend(general_issues)
        
        return compliance_issues

    def _calculate_reading_level(self, content: str) -> str:
        """Calculate reading level using simplified metrics"""
        words = content.split()
        sentences = re.split(r'[.!?]+', content)
        
        if not words or not sentences:
            return "Unable to determine"
        
        avg_sentence_length = len(words) / len(sentences)
        
        # Simplified reading level calculation
        if avg_sentence_length < 15:
            return "Grade 8-10"
        elif avg_sentence_length < 20:
            return "Grade 10-12"
        elif avg_sentence_length < 25:
            return "College level"
        else:
            return "Professional/Legal"

    def _get_relevant_clauses(self, contract_type: str) -> List[Dict[str, Any]]:
        """Get relevant clauses based on contract type"""
        base_clauses = [
            {
                "name": "parties",
                "keywords": ["party", "parties", "between"],
                "description": "Identification of contracting parties",
                "importance": "high"
            },
            {
                "name": "consideration",
                "keywords": ["payment", "consideration", "fee", "compensation"],
                "description": "Payment terms and consideration",
                "importance": "high"
            },
            {
                "name": "term",
                "keywords": ["term", "duration", "effective date", "expiration"],
                "description": "Contract duration and effective period",
                "importance": "high"
            },
            {
                "name": "termination",
                "keywords": ["termination", "terminate", "end", "cancel"],
                "description": "Contract termination conditions",
                "importance": "medium"
            }
        ]
        
        # Add type-specific clauses
        if contract_type == "service_agreement":
            base_clauses.extend([
                {
                    "name": "scope_of_work",
                    "keywords": ["scope", "services", "deliverables", "work"],
                    "description": "Detailed scope of services",
                    "importance": "high"
                },
                {
                    "name": "performance_standards",
                    "keywords": ["performance", "standards", "quality", "metrics"],
                    "description": "Performance standards and metrics",
                    "importance": "medium"
                }
            ])
        elif contract_type == "employment":
            base_clauses.extend([
                {
                    "name": "job_duties",
                    "keywords": ["duties", "responsibilities", "role", "position"],
                    "description": "Job duties and responsibilities",
                    "importance": "high"
                },
                {
                    "name": "benefits",
                    "keywords": ["benefits", "insurance", "vacation", "sick leave"],
                    "description": "Employee benefits and compensation",
                    "importance": "medium"
                }
            ])
        
        return base_clauses

    def _assess_risk_severity(self, indicator: str) -> str:
        """Assess the severity of a risk indicator"""
        high_risk = ["penalty", "liquidated damages", "indemnification", "breach"]
        medium_risk = ["termination", "liability", "confidentiality"]
        
        if indicator in high_risk:
            return "high"
        elif indicator in medium_risk:
            return "medium"
        else:
            return "low"

    def _check_imbalanced_terms(self, content: str) -> List[Dict[str, Any]]:
        """Check for imbalanced or unfair terms"""
        risks = []
        
        # Check for one-sided termination clauses
        if "either party may terminate" not in content and "party may terminate" in content:
            risks.append({
                "type": "warning",
                "message": "Potentially one-sided termination clause",
                "context": "Termination rights may be imbalanced",
                "severity": "medium"
            })
        
        # Check for unlimited liability
        if "unlimited liability" in content or "no limit" in content:
            risks.append({
                "type": "error",
                "message": "Unlimited liability clause detected",
                "context": "Consider liability limitations",
                "severity": "high"
            })
        
        return risks

    def _check_vague_language(self, content: str) -> List[Dict[str, Any]]:
        """Check for vague or ambiguous language"""
        risks = []
        vague_terms = ["reasonable", "best efforts", "as soon as possible", "in a timely manner"]
        
        for term in vague_terms:
            if term in content:
                risks.append({
                    "type": "info",
                    "message": f"Vague term detected: '{term}'",
                    "context": "Consider more specific language",
                    "severity": "low"
                })
        
        return risks

    def _check_gdpr_compliance(self, content: str) -> List[Dict[str, Any]]:
        """Check for GDPR compliance issues"""
        issues = []
        
        if "personal data" in content and "data protection" not in content:
            issues.append({
                "issue": "GDPR compliance concern",
                "severity": "high",
                "recommendation": "Include data protection clauses for GDPR compliance"
            })
        
        return issues

    def _check_general_compliance(self, content: str) -> List[Dict[str, Any]]:
        """Check for general compliance issues"""
        issues = []
        
        # Check for governing law clause
        if "governing law" not in content and "governed by" not in content:
            issues.append({
                "issue": "Missing governing law clause",
                "severity": "medium",
                "recommendation": "Specify which jurisdiction's laws govern the contract"
            })
        
        # Check for dispute resolution
        if "dispute" not in content and "arbitration" not in content:
            issues.append({
                "issue": "No dispute resolution mechanism",
                "severity": "medium",
                "recommendation": "Include dispute resolution procedures"
            })
        
        return issues