from typing import Dict, List, Optional
import jwt
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from dataclasses import dataclass
import time
import yaml
from pathlib import Path
import logging
from datetime import datetime, timedelta

@dataclass
class SecurityConfig:
    """Security configuration container."""
    rate_limits: Dict
    access_control: Dict
    content_security: Dict
    feed_auth: Dict
    encryption: Dict
    audit: Dict

class SecurityManager:
    """Manages security features for the ATF service."""
    
    def __init__(self, config_path: Path):
        """Initialize security manager with configuration."""
        self.config = self._load_config(config_path)
        self.logger = logging.getLogger(__name__)
        self._init_keys()
    
    def _load_config(self, config_path: Path) -> SecurityConfig:
        """Load security configuration from YAML file."""
        with open(config_path) as f:
            config = yaml.safe_load(f)['security']
        return SecurityConfig(
            rate_limits=config['rate_limiting'],
            access_control=config['access_control'],
            content_security=config['content_security'],
            feed_auth=config['feed_auth'],
            encryption=config['encryption'],
            audit=config['audit']
        )
    
    def _init_keys(self):
        """Initialize cryptographic keys."""
        self.signing_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=self.config.feed_auth['signatures']['key_size']
        )
        self.public_key = self.signing_key.public_key()
    
    def sign_feed(self, feed_content: str) -> str:
        """Sign feed content with RSA key."""
        signature = self.signing_key.sign(
            feed_content.encode(),
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )
        return signature.hex()
    
    def verify_feed(self, feed_content: str, signature: str) -> bool:
        """Verify feed signature."""
        try:
            self.public_key.verify(
                bytes.fromhex(signature),
                feed_content.encode(),
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )
            return True
        except Exception as e:
            self.logger.warning(f"Signature verification failed: {e}")
            return False
    
    def check_rate_limit(self, endpoint: str, client_id: str) -> bool:
        """Check if request is within rate limits."""
        limits = self.config.rate_limits['endpoints'].get(
            endpoint,
            self.config.rate_limits['default']
        )
        
        # Implementation would use Redis or similar for rate tracking
        # This is a placeholder
        return True
    
    def validate_jwt(self, token: str) -> Optional[Dict]:
        """Validate JWT token."""
        try:
            payload = jwt.decode(
                token,
                self.public_key,
                algorithms=self.config.access_control['jwt']['algorithms'],
                audience=self.config.access_control['jwt']['audience']
            )
            return payload
        except jwt.InvalidTokenError as e:
            self.logger.warning(f"JWT validation failed: {e}")
            return None
    
    def generate_jwt(self, claims: Dict) -> str:
        """Generate new JWT token."""
        claims.update({
            'iss': self.config.access_control['jwt']['issuer'],
            'aud': self.config.access_control['jwt']['audience'],
            'iat': int(time.time()),
            'exp': int(time.time() + 3600)  # 1 hour expiry
        })
        return jwt.encode(claims, self.signing_key, algorithm='RS256')
    
    def get_security_headers(self) -> Dict[str, str]:
        """Get security headers for HTTP responses."""
        headers = {}
        
        # Add CSP headers
        csp_parts = []
        for directive, sources in self.config.content_security['policies'].items():
            csp_parts.append(f"{directive} {' '.join(sources)}")
        headers['Content-Security-Policy'] = "; ".join(csp_parts)
        
        # Add other security headers
        headers.update(self.config.content_security['headers'])
        
        return headers
    
    def check_ip_whitelist(self, ip_address: str) -> bool:
        """Check if IP is in whitelist."""
        if not self.config.access_control['ip_whitelist']['enabled']:
            return True
            
        # Implementation would use IP address range checking
        # This is a placeholder
        return True
    
    def audit_log(self, event_type: str, details: Dict):
        """Log audit event."""
        if not self.config.audit['enabled']:
            return
            
        event = {
            'timestamp': datetime.utcnow().isoformat(),
            'event_type': event_type,
            'details': details
        }
        
        # Implementation would use secure audit logging
        # This is a placeholder
        self.logger.info(f"Audit event: {event}")
    
    def rotate_keys(self):
        """Rotate cryptographic keys."""
        old_key = self.signing_key
        self._init_keys()
        
        # Implementation would handle key transition period
        # This is a placeholder
        self.audit_log('key_rotation', {
            'old_key_id': id(old_key),
            'new_key_id': id(self.signing_key)
        })
    
    def validate_cors(self, origin: str, method: str, headers: List[str]) -> bool:
        """Validate CORS request."""
        cors_config = self.config.access_control['cors']
        
        # Check origin
        if origin not in cors_config['allowed_origins']:
            return False
            
        # Check method
        if method not in cors_config['allowed_methods']:
            return False
            
        # Check headers
        if not all(h in cors_config['allowed_headers'] for h in headers):
            return False
            
        return True