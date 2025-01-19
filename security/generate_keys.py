#!/usr/bin/env python3

import argparse
import sys
from pathlib import Path
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from datetime import datetime
import logging

def setup_logging():
    """Configure logging."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

def generate_key_pair(key_size: int = 2048) -> tuple:
    """Generate RSA key pair."""
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=key_size
    )
    public_key = private_key.public_key()
    return private_key, public_key

def save_private_key(private_key, path: Path, password: str = None):
    """Save private key with optional encryption."""
    encryption_algorithm = (
        serialization.BestAvailableEncryption(password.encode())
        if password
        else serialization.NoEncryption()
    )
    
    with open(path, 'wb') as f:
        f.write(private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=encryption_algorithm
        ))

def save_public_key(public_key, path: Path):
    """Save public key."""
    with open(path, 'wb') as f:
        f.write(public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        ))

def main():
    parser = argparse.ArgumentParser(description='Generate RSA key pair for ATF feed signing')
    parser.add_argument('--output-dir', type=str, default='security/keys',
                       help='Output directory for keys')
    parser.add_argument('--key-size', type=int, default=2048,
                       choices=[2048, 3072, 4096],
                       help='Key size in bits')
    parser.add_argument('--password', type=str,
                       help='Password for private key encryption')
    
    args = parser.parse_args()
    setup_logging()
    
    try:
        # Create output directory
        output_dir = Path(args.output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate timestamp for filenames
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Generate keys
        logging.info(f"Generating {args.key_size}-bit RSA key pair...")
        private_key, public_key = generate_key_pair(args.key_size)
        
        # Save private key
        private_key_path = output_dir / f"atf_private_{timestamp}.pem"
        save_private_key(private_key, private_key_path, args.password)
        logging.info(f"Private key saved to: {private_key_path}")
        
        # Save public key
        public_key_path = output_dir / f"atf_public_{timestamp}.pem"
        save_public_key(public_key, public_key_path)
        logging.info(f"Public key saved to: {public_key_path}")
        
        # Create symlinks to latest keys
        latest_private = output_dir / "atf_private_latest.pem"
        latest_public = output_dir / "atf_public_latest.pem"
        
        if latest_private.exists():
            latest_private.unlink()
        if latest_public.exists():
            latest_public.unlink()
            
        latest_private.symlink_to(private_key_path.name)
        latest_public.symlink_to(public_key_path.name)
        
        logging.info("Key generation completed successfully")
        
    except Exception as e:
        logging.error(f"Error generating keys: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()