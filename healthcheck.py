#!/usr/bin/env python3
import http.client
import sys
import os

def check_health():
    """Check if the ATF service is healthy."""
    try:
        conn = http.client.HTTPConnection("localhost:8000")
        conn.request("GET", "/health")
        response = conn.getresponse()
        
        if response.status == 200:
            data = response.read()
            if b'"status":"healthy"' in data:
                return True
            
        return False
    except Exception:
        return False
    finally:
        conn.close()

if __name__ == "__main__":
    if check_health():
        sys.exit(0)
    sys.exit(1)