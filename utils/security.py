"""
Security guards to prevent misuse of the application
"""
import re
from typing import Dict, List, Tuple, Optional
from datetime import datetime, timedelta
from collections import defaultdict


class SecurityGuard:
    """Security guard for input validation and abuse prevention"""
    
    def __init__(self):
        self.rate_limit_store: Dict[str, List[datetime]] = defaultdict(list)
        self.blocked_patterns = [
            r"ignore\s+(previous|all)\s+(instructions|prompts)",
            r"you\s+are\s+now\s+(jailbroken|hacked)",
            r"system\s*:\s*you\s+are",
            r"forget\s+everything",
            r"repeat\s+the\s+following",
            r"\\[SYSTEM\\]",
            r"<\|system\|>",
        ]
    
    def validate_input_length(self, text: str, max_length: int = 10000) -> Tuple[bool, Optional[str]]:
        """Validate input length"""
        if len(text) > max_length:
            return False, f"Input exceeds maximum length of {max_length} characters"
        return True, None
    
    def detect_prompt_injection(self, text: str) -> Tuple[bool, Optional[str]]:
        """Detect potential prompt injection attacks"""
        text_lower = text.lower()
        
        for pattern in self.blocked_patterns:
            if re.search(pattern, text_lower, re.IGNORECASE):
                return False, "Potential prompt injection detected. Please rephrase your input."
        
        # Check for suspicious patterns
        suspicious_patterns = [
            (r"execute|run|system\(|eval\(", "Potential code execution attempt"),
            (r"(http|https|ftp)://", "External links not allowed in input"),
            (r"<script|javascript:|onerror=|onload=", "Potential XSS attempt"),
        ]
        
        for pattern, message in suspicious_patterns:
            if re.search(pattern, text_lower):
                return False, message
        
        return True, None
    
    def sanitize_input(self, text: str) -> str:
        """Sanitize user input"""
        # Remove null bytes
        text = text.replace('\x00', '')
        
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Truncate if too long
        if len(text) > 10000:
            text = text[:10000]
        
        return text.strip()
    
    def validate_job_description(self, job_desc: str, max_length: int = 50000) -> Tuple[bool, Optional[str]]:
        """Validate job description input"""
        # Check length
        if len(job_desc) > max_length:
            return False, f"Job description exceeds maximum length of {max_length} characters"
        
        # Check for prompt injection
        is_safe, error = self.detect_prompt_injection(job_desc)
        if not is_safe:
            return False, error
        
        return True, None
    
    def rate_limit_check(self, user_id: str, max_requests: int = 50, window_hours: int = 1) -> Tuple[bool, Optional[str]]:
        """Check if user has exceeded rate limit"""
        now = datetime.now()
        window_start = now - timedelta(hours=window_hours)
        
        # Clean old entries
        self.rate_limit_store[user_id] = [
            req_time for req_time in self.rate_limit_store[user_id]
            if req_time > window_start
        ]
        
        # Check limit
        if len(self.rate_limit_store[user_id]) >= max_requests:
            return False, f"Rate limit exceeded. Maximum {max_requests} requests per {window_hours} hour(s)."
        
        # Record this request
        self.rate_limit_store[user_id].append(now)
        return True, None
    
    def validate_system_prompt(self, system_prompt: str) -> Tuple[bool, Optional[str]]:
        """Validate system prompt for security"""
        # Check for dangerous instructions
        dangerous_patterns = [
            r"ignore\s+security",
            r"bypass\s+validation",
            r"reveal\s+api\s+key",
            r"delete\s+all",
        ]
        
        for pattern in dangerous_patterns:
            if re.search(pattern, system_prompt.lower()):
                return False, "System prompt contains potentially dangerous instructions"
        
        return True, None
    
    def content_filter(self, content: str) -> Tuple[bool, Optional[str]]:
        """Filter inappropriate content"""
        inappropriate_keywords = [
            "hate speech", "discrimination",  # Add more as needed
        ]
        
        content_lower = content.lower()
        for keyword in inappropriate_keywords:
            if keyword in content_lower:
                return False, "Content contains inappropriate language"
        
        return True, None
    
    def comprehensive_check(
        self,
        user_input: str,
        system_prompt: Optional[str] = None,
        job_description: Optional[str] = None,
        user_id: str = "default"
    ) -> Tuple[bool, Optional[str]]:
        """Perform comprehensive security check"""
        # Validate input length
        is_valid, error = self.validate_input_length(user_input)
        if not is_valid:
            return False, error
        
        # Check for prompt injection
        is_safe, error = self.detect_prompt_injection(user_input)
        if not is_safe:
            return False, error
        
        # Validate system prompt if provided
        if system_prompt:
            is_valid, error = self.validate_system_prompt(system_prompt)
            if not is_valid:
                return False, error
        
        # Validate job description if provided
        if job_description:
            is_valid, error = self.validate_job_description(job_description)
            if not is_valid:
                return False, error
        
        # Rate limiting
        is_allowed, error = self.rate_limit_check(user_id)
        if not is_allowed:
            return False, error
        
        # Content filter
        is_appropriate, error = self.content_filter(user_input)
        if not is_appropriate:
            return False, error
        
        return True, None
    
    def get_security_report(self) -> Dict[str, any]:
        """Get security statistics"""
        total_requests = sum(len(requests) for requests in self.rate_limit_store.values())
        unique_users = len(self.rate_limit_store)
        
        return {
            "total_requests": total_requests,
            "unique_users": unique_users,
            "blocked_patterns_count": len(self.blocked_patterns),
            "active_rate_limits": dict(self.rate_limit_store)
        }
