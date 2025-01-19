#!/usr/bin/env python3

import argparse
import sys
from pathlib import Path
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding
import logging
import json
from datetime import datetime
import base64

def setup_logging():
    """Configure logging."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

def load_private_key(key_path: Path, password: str = None) -> serialization.PrivateKeyTypes:
    """Load private key from file."""
    with open(key_path, 'rb') as f:
        private_key = serialization.load_pem_private_key(
            f.read(),
            password=password.encode() if password else None
        )
    return private_key

def sign_feed(feed_content: str, private_key: serialization.PrivateKeyTypes) -> str:
    """Sign feed content with private key."""
    signature = private_key.sign(
        feed_content.encode(),
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.MAX_LENGTH
        ),
        hashes.SHA256()
    )
    return base64.b64encode(signature).decode()

def save_signature(feed_path: Path, signature: str):
    """Save signature alongside feed file."""
    signature_path = feed_path.with_suffix('.sig')
    metadata = {
        "signature": signature,
        "timestamp": datetime.utcnow().isoformat(),
        "feed_file": feed_path.name
    }
    
    with open(signature_path, 'w') as f:
        json.dump(metadata, f, indent=2)
    return signature_path

def main():
    parser = argparse.ArgumentParser(description='Sign ATF feed file')
    parser.add_argument('feed_file', type=str,
                       help='Path to the feed XML file')
    parser.add_argument('--key', type=str,
                       default='security/keys/atf_private_latest.pem',
                       help='Path to private key file')
    parser.add_argument('--password', type=str,
                       help='Password for encrypted private key')
    parser.add_argument('--verify', action='store_true',
                       help='Verify signature after signing')
    
    args = parser.parse_args()
    setup_logging()
    
    try:
        # Load feed content
        feed_path = Path(args.feed_file)
        if not feed_path.exists():
            raise FileNotFoundError(f"Feed file not found: {feed_path}")
        
        with open(feed_path) as f:
            feed_content = f.read()
        
        # Load private key
        logging.info("Loading private key...")
        key_path = Path(args.key)
        private_key = load_private_key(key_path, args.password)
        
        # Sign feed
        logging.info("Signing feed...")
        signature = sign_feed(feed_content, private_key)
        
        # Save signature
        signature_path = save_signature(feed_path, signature)
        logging.info(f"Signature saved to: {signature_path}")
        
        # Verify signature if requested
        if args.verify:
            logging.info("Verifying signature...")
            public_key = private_key.public_key()
            try:
                signature_bytes = base64.b64decode(signature)
                public_key.verify(
                    signature_bytes,
                    feed_content.encode(),
                    padding.PSS(
                        mgf=padding.MGF1(hashes.SHA256()),
                        salt_length=padding.PSS.MAX_LENGTH
                    ),
                    hashes.SHA256()
                )
                logging.info("Signature verified successfully")
            except Exception as e:
                logging.error(f"Signature verification failed: {e}")
                sys.exit(1)
        
    except Exception as e:
        logging.error(f"Error signing feed: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()