#!/usr/bin/env python3

import sys
import argparse
from pathlib import Path
from typing import Union, List
from lxml import etree
from datetime import datetime

class ATFValidator:
    """Validator for Algorithmic Transparency Feed (ATF) files."""
    
    def __init__(self, schema_path: Union[str, Path]):
        """Initialize validator with schema path."""
        self.schema_path = Path(schema_path)
        self._load_schema()
    
    def _load_schema(self):
        """Load and parse the XSD schema."""
        try:
            with open(self.schema_path) as schema_file:
                schema_doc = etree.parse(schema_file)
                self.schema = etree.XMLSchema(schema_doc)
        except Exception as e:
            raise ValueError(f"Failed to load schema: {e}")
    
    def validate_file(self, xml_path: Union[str, Path]) -> List[str]:
        """Validate an ATF XML file against the schema."""
        errors = []
        try:
            xml_path = Path(xml_path)
            with open(xml_path) as xml_file:
                doc = etree.parse(xml_file)
                
                # Validate against schema
                try:
                    self.schema.assertValid(doc)
                except etree.DocumentInvalid as e:
                    errors.extend(str(error) for error in e.error_log)
                
                # Additional semantic validations
                errors.extend(self._validate_dates(doc))
                errors.extend(self._validate_uris(doc))
                
        except Exception as e:
            errors.append(f"Failed to parse XML file: {e}")
        
        return errors
    
    def _validate_dates(self, doc: etree._ElementTree) -> List[str]:
        """Validate date formats and logical consistency."""
        errors = []
        try:
            # Check lastBuildDate
            last_build = doc.find(".//{*}lastBuildDate")
            if last_build is not None:
                try:
                    datetime.strptime(last_build.text, "%Y-%m-%dT%H:%M:%SZ")
                except ValueError:
                    errors.append(f"Invalid lastBuildDate format: {last_build.text}")
            
            # Check pubDates
            for pub_date in doc.findall(".//{*}pubDate"):
                try:
                    datetime.strptime(pub_date.text, "%Y-%m-%dT%H:%M:%SZ")
                except ValueError:
                    errors.append(f"Invalid pubDate format: {pub_date.text}")
        
        except Exception as e:
            errors.append(f"Date validation error: {e}")
        
        return errors
    
    def _validate_uris(self, doc: etree._ElementTree) -> List[str]:
        """Validate URI formats."""
        errors = []
        for link in doc.findall(".//{*}link"):
            if not link.text.startswith(('http://', 'https://')):
                errors.append(f"Invalid URI format: {link.text}")
        return errors

def main():
    parser = argparse.ArgumentParser(description='Validate ATF XML files')
    parser.add_argument('xml_file', help='Path to the ATF XML file to validate')
    parser.add_argument('--schema', default='schema/atf-1.0.xsd',
                      help='Path to the ATF schema file (default: schema/atf-1.0.xsd)')
    args = parser.parse_args()
    
    try:
        validator = ATFValidator(args.schema)
        errors = validator.validate_file(args.xml_file)
        
        if errors:
            print("Validation errors found:")
            for error in errors:
                print(f"  - {error}")
            sys.exit(1)
        else:
            print("Validation successful!")
            sys.exit(0)
    
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(2)

if __name__ == '__main__':
    main()