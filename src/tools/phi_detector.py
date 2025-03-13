from typing import Dict, List, Any, Tuple, Set
import re
from datetime import datetime
import json

class PHIDetector:
    """Advanced PHI detection and redaction system."""
    
    def __init__(self):
        # Common medical terms that might be part of PHI
        self.medical_terms = {
            'dr', 'doctor', 'nurse', 'patient', 'hospital', 'clinic', 'medical center',
            'healthcare', 'pharmacy', 'lab', 'laboratory', 'center', 'dept', 'department',
            'ward', 'room', 'unit', 'wing'
        }
        
        # Initialize pattern dictionaries
        self.initialize_patterns()
    
    def initialize_patterns(self):
        """Initialize comprehensive pattern matching for PHI detection."""
        self.patterns = {
            # Personal Identifiers
            "name": [
                # Full names with titles
                r'\b(?:Dr|Mr|Mrs|Ms|Miss|Prof)\.?\s+[A-Z][a-zA-Z\'-]+(?:\s+[A-Z][a-zA-Z\'-]+)+\b',
                # Full names without titles
                r'\b[A-Z][a-zA-Z\'-]+(?:\s+[A-Z][a-zA-Z\'-]+){1,3}\b',
                # Last name, First name format
                r'\b[A-Z][a-zA-Z\'-]+,\s+[A-Z][a-zA-Z\'-]+(?:\s+[A-Z][a-zA-Z\'-]+)?\b'
            ],
            
            # Contact Information
            "phone": [
                # Standard US phone formats
                r'\b(?:\+?1[-.]?)?\s*\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b',
                # Extension formats
                r'\b(?:ext|x|extension)\.?\s*\d{2,5}\b',
                # International format
                r'\b\+\d{1,3}[-.\s]?\d{1,3}[-.\s]?\d{3,4}[-.\s]?\d{4}\b'
            ],
            
            "email": [
                r'\b[\w\.-]+@[\w\.-]+\.\w+\b',
                # Common health organization domains
                r'\b[\w\.-]+@(?:health|medical|hospital|clinic|healthcare)\.\w+\b'
            ],
            
            # Geographic Identifiers
            "address": [
                # Street address
                r'\b\d{1,5}\s+[A-Z][a-zA-Z\s]+(?:Street|St|Avenue|Ave|Road|Rd|Boulevard|Blvd|Lane|Ln|Drive|Dr|Way|Court|Ct|Circle|Cir|Trail|Trl|Highway|Hwy|Suite|Ste|Unit|#)\b',
                # PO Box
                r'\bP\.?O\.?\s*Box\s+\d+\b',
                # ZIP codes
                r'\b\d{5}(?:-\d{4})?\b'
            ],
            
            # Identification Numbers
            "ssn": [
                # Standard SSN format
                r'\b\d{3}-\d{2}-\d{4}\b',
                # SSN without dashes
                r'\b\d{9}\b(?=.*?(?:ssn|social|security))',
                # Partial SSN
                r'\bxxx-xx-\d{4}\b'
            ],
            
            "medical_record": [
                # Common MRN formats
                r'\b(?:MRN|Medical Record Number|Patient ID)[:# ][\w\-]{4,}\b',
                r'\b(?:MR|#)\d{5,8}\b',
                # Health plan beneficiary numbers
                r'\b[A-Z]\d{8}\b'
            ],
            
            # Dates
            "dates": [
                # Various date formats
                r'\b(?:\d{1,2}[-/]\d{1,2}[-/]\d{2,4})',
                r'\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s+\d{1,2},?\s+\d{4}\b',
                # Age over 89
                r'\b(?:age|aged)\s+(?:9\d|1\d{2})\b',
                r'\b(?:9\d|1\d{2})\s+(?:years?\s+old|yo|y\.o\.)\b'
            ],
            
            # Device Identifiers
            "device_id": [
                r'\b(?:Serial|Device|Model)[\s#:][A-Z0-9\-]{4,}\b',
                r'\b(?:UDI|DI|PI):[\w\-]{4,}\b'
            ],
            
            # Biometric Identifiers
            "biometric": [
                r'\b(?:Biometric|Fingerprint|Retinal|DNA)\s+ID[\s#:][A-Z0-9\-]{4,}\b',
                r'\b(?:Sample|Specimen)\s+ID[\s#:][A-Z0-9\-]{4,}\b'
            ],
            
            # Vehicle Identifiers
            "vehicle": [
                r'\b[A-Z0-9]{17}\b(?=.*?(?:VIN|Vehicle))',
                r'\b[A-Z]{1,3}[-\s]?\d{1,4}[-\s]?[A-Z]{1,2}\b(?=.*?(?:License|Plate))'
            ],
            
            # Web URLs and IP Addresses
            "web_identifiers": [
                r'\b(?:https?://|www\.)[^\s<>"]+\b',
                r'\b(?:\d{1,3}\.){3}\d{1,3}\b'
            ],
            
            # Account Numbers
            "account": [
                r'\b(?:Account|Acct)[\s#:][A-Z0-9\-]{4,}\b',
                r'\b(?:Credit|Debit|Card)[\s#:][A-Z0-9\-]{4,}\b'
            ]
        }
        
        # Compile all patterns for efficiency
        self.compiled_patterns = {
            category: [re.compile(pattern, re.IGNORECASE) for pattern in patterns]
            for category, patterns in self.patterns.items()
        }
    
    def detect_phi(self, text: str) -> List[Dict[str, Any]]:
        """
        Detect potential PHI in text with context.
        Returns a list of detected PHI instances with category and confidence.
        """
        phi_instances = []
        
        # Check each category
        for category, patterns in self.compiled_patterns.items():
            for pattern in patterns:
                matches = pattern.finditer(text)
                for match in matches:
                    # Calculate confidence based on context and pattern strength
                    confidence = self._calculate_confidence(
                        match.group(),
                        category,
                        text[max(0, match.start()-50):match.end()+50]  # Get context
                    )
                    
                    if confidence > 0.5:  # Only include likely PHI
                        phi_instances.append({
                            "category": category,
                            "value": match.group(),
                            "confidence": confidence,
                            "position": (match.start(), match.end()),
                            "context": text[max(0, match.start()-20):match.end()+20]
                        })
        
        return phi_instances
    
    def redact_phi(self, text: str, threshold: float = 0.7) -> Tuple[str, List[Dict[str, Any]]]:
        """
        Redact detected PHI from text and return both redacted text and PHI instances.
        Uses confidence threshold to determine what to redact.
        """
        phi_instances = self.detect_phi(text)
        redacted_text = text
        
        # Sort instances by position in reverse order to maintain string indices
        phi_instances.sort(key=lambda x: x["position"][0], reverse=True)
        
        # Redact instances that meet threshold
        for phi in phi_instances:
            if phi["confidence"] >= threshold:
                start, end = phi["position"]
                redacted_text = (
                    redacted_text[:start] +
                    f"[REDACTED {phi['category']}]" +
                    redacted_text[end:]
                )
        
        return redacted_text, phi_instances
    
    def _calculate_confidence(self, value: str, category: str, context: str) -> float:
        """
        Calculate confidence score for a potential PHI instance.
        Uses multiple factors including pattern strength, context, and known medical terms.
        """
        confidence = 0.0
        context = context.lower()
        
        # Base confidence from pattern match
        confidence += 0.5
        
        # Context-based confidence boosting
        if any(term in context for term in self.medical_terms):
            confidence += 0.2
        
        # Category-specific confidence adjustments
        if category == "name":
            # Check for medical titles
            if re.search(r'\b(?:Dr|Doctor|Nurse|Provider)\b', context, re.IGNORECASE):
                confidence += 0.2
        elif category == "dates":
            # Check for medical date context
            if re.search(r'\b(?:appointment|admission|discharge|visit)\b', context, re.IGNORECASE):
                confidence += 0.2
        elif category == "medical_record":
            # Strong confidence for well-formatted MRNs
            if re.match(r'^(?:MRN|#)\d{6,}$', value, re.IGNORECASE):
                confidence += 0.3
        
        # Penalize very short or common values
        if len(value) < 3:
            confidence -= 0.2
        
        # Cap confidence at 1.0
        return min(1.0, max(0.0, confidence))
    
    def analyze_document(self, text: str) -> Dict[str, Any]:
        """
        Perform comprehensive PHI analysis on a document.
        Returns detailed analysis including statistics and recommendations.
        """
        redacted_text, phi_instances = self.redact_phi(text)
        
        # Analyze PHI distribution
        phi_stats = {}
        for phi in phi_instances:
            category = phi["category"]
            if category not in phi_stats:
                phi_stats[category] = {
                    "count": 0,
                    "avg_confidence": 0.0,
                    "examples": []
                }
            
            phi_stats[category]["count"] += 1
            phi_stats[category]["avg_confidence"] += phi["confidence"]
            if len(phi_stats[category]["examples"]) < 3:  # Keep up to 3 examples
                phi_stats[category]["examples"].append(phi["value"])
        
        # Calculate averages
        for category in phi_stats:
            if phi_stats[category]["count"] > 0:
                phi_stats[category]["avg_confidence"] /= phi_stats[category]["count"]
        
        return {
            "redacted_text": redacted_text,
            "phi_count": len(phi_instances),
            "phi_categories": list(phi_stats.keys()),
            "phi_statistics": phi_stats,
            "timestamp": datetime.utcnow().isoformat(),
            "recommendations": self._generate_recommendations(phi_stats)
        }
    
    def _generate_recommendations(self, phi_stats: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on PHI analysis."""
        recommendations = []
        
        # Check for high-risk categories
        high_risk_categories = {"ssn", "medical_record", "biometric"}
        for category in high_risk_categories:
            if category in phi_stats and phi_stats[category]["count"] > 0:
                recommendations.append(
                    f"High-risk PHI detected: {category}. Consider additional encryption."
                )
        
        # Check for volume-based risks
        total_phi = sum(stats["count"] for stats in phi_stats.values())
        if total_phi > 10:
            recommendations.append(
                f"Large amount of PHI detected ({total_phi} instances). "
                "Consider implementing batch encryption."
            )
        
        # Check for confidence-based risks
        low_confidence_categories = [
            category for category, stats in phi_stats.items()
            if stats["avg_confidence"] < 0.7
        ]
        if low_confidence_categories:
            recommendations.append(
                f"Low confidence detection in categories: {', '.join(low_confidence_categories)}. "
                "Consider manual review."
            )
        
        return recommendations 