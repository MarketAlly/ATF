#!/usr/bin/env python3

import sys
import re
import argparse
from pathlib import Path
from typing import Union, List, Dict, Set
from lxml import etree
from datetime import datetime
import urllib.parse

class ValidationError(Exception):
    """Custom exception for validation errors."""
    pass

class ATFValidator:
    """Enhanced validator for Algorithmic Transparency Feed (ATF) files."""
    
    # Constants for validation
    MAX_FEED_SIZE = 10 * 1024 * 1024  # 10MB
    MIN_RETENTION_DAYS = 365  # 1 year
    ALLOWED_LANGUAGES = {'en-us', 'en-gb', 'es', 'fr', 'de', 'zh'}  # Example set
    STANDARD_CATEGORIES = {
        'Ranking Algorithm',
        'Content Moderation',
        'Recommendation System',
        'User Classification',
        'Privacy Enhancement',
        'Bias Mitigation',
        'Machine Learning',
        'Data Processing',
        'Security',
        'Performance'
    }
    
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
        """Validate an ATF XML file with enhanced checks."""
        errors = []
        try:
            xml_path = Path(xml_path)
            
            # Check file size
            if xml_path.stat().st_size > self.MAX_FEED_SIZE:
                errors.append(f"Feed file exceeds maximum size of {self.MAX_FEED_SIZE/1024/1024}MB")
                return errors
            
            with open(xml_path) as xml_file:
                doc = etree.parse(xml_file)
                
                # Basic schema validation
                try:
                    self.schema.assertValid(doc)
                except etree.DocumentInvalid as e:
                    errors.extend(str(error) for error in e.error_log)
                
                # Enhanced validations
                errors.extend(self._validate_dates(doc))
                errors.extend(self._validate_uris(doc))
                errors.extend(self._validate_percentages(doc))
                errors.extend(self._validate_metrics(doc))
                errors.extend(self._validate_categories(doc))
                errors.extend(self._validate_language(doc))
                errors.extend(self._validate_retention(doc))
                
        except Exception as e:
            errors.append(f"Failed to parse XML file: {e}")
        
        return errors

    def _validate_percentages(self, doc: etree._ElementTree) -> List[str]:
        """Validate percentage format in affected users and metrics."""
        errors = []
        percentage_pattern = re.compile(r'^\d+(\.\d+)?%$')
        
        # Check affected users percentages
        for affected in doc.findall(".//{*}affectedUsers"):
            if not percentage_pattern.match(affected.text):
                errors.append(f"Invalid percentage format in affectedUsers: {affected.text}")
        
        # Check metric percentages
        for metric in doc.findall(".//{*}metric"):
            if '%' in metric.text and not percentage_pattern.match(metric.text):
                errors.append(f"Invalid percentage format in metric: {metric.text}")
        
        return errors

    def _validate_metrics(self, doc: etree._ElementTree) -> List[str]:
        """Validate metric formats and consistency."""
        errors = []
        metric_patterns = {
            'percentage': re.compile(r'^[+-]?\d+(\.\d+)?%$'),
            'numeric': re.compile(r'^[+-]?\d+(\.\d+)?$'),
            'ratio': re.compile(r'^\d+:\d+$'),
            'duration': re.compile(r'^\d+(\.\d+)?(ms|s|min|h)$'),
            'boolean': re.compile(r'^(true|false)$', re.I)
        }
        
        seen_metrics: Dict[str, Set[str]] = {}
        
        for metric in doc.findall(".//{*}metric"):
            name = metric.get('name')
            value = metric.text
            
            # Check if any pattern matches
            valid_format = any(pattern.match(value) for pattern in metric_patterns.values())
            if not valid_format:
                errors.append(f"Invalid metric format: {name}={value}")
            
            # Check consistency of metric formats across items
            if name in seen_metrics:
                format_type = self._get_metric_format_type(value, metric_patterns)
                if format_type not in seen_metrics[name]:
                    errors.append(f"Inconsistent format for metric {name}: {value}")
            else:
                seen_metrics[name] = {self._get_metric_format_type(value, metric_patterns)}
        
        return errors

    def _get_metric_format_type(self, value: str, patterns: Dict[str, re.Pattern]) -> str:
        """Determine the format type of a metric value."""
        for format_type, pattern in patterns.items():
            if pattern.match(value):
                return format_type
        return 'unknown'

    def _validate_categories(self, doc: etree._ElementTree) -> List[str]:
        """Validate category names and usage."""
        errors = []
        categories_used = set()
        
        for category in doc.findall(".//{*}category"):
            cat_name = category.text.strip()
            categories_used.add(cat_name)
            
            # Check against standard categories
            if cat_name not in self.STANDARD_CATEGORIES:
                errors.append(f"Non-standard category used: {cat_name}")
            
            # Check category name format
            if not re.match(r'^[A-Z][a-zA-Z0-9 ]+$', cat_name):
                errors.append(f"Invalid category name format: {cat_name}")
        
        return errors

    def _validate_language(self, doc: etree._ElementTree) -> List[str]:
        """Validate language codes."""
        errors = []
        lang_elem = doc.find(".//{*}language")
        if lang_elem is not None and lang_elem.text not in self.ALLOWED_LANGUAGES:
            errors.append(f"Unsupported language code: {lang_elem.text}")
        return errors

    def _validate_retention(self, doc: etree._ElementTree) -> List[str]:
        """Validate feed history retention."""
        errors = []
        current_date = datetime.utcnow()
        
        # Get all publication dates
        pub_dates = []
        for date_elem in doc.findall(".//{*}pubDate"):
            try:
                pub_date = datetime.strptime(date_elem.text, "%Y-%m-%dT%H:%M:%SZ")
                pub_dates.append(pub_date)
            except ValueError:
                continue
        
        if pub_dates:
            oldest_date = min(pub_dates)
            days_retained = (current_date - oldest_date).days
            
            if days_retained < self.MIN_RETENTION_DAYS:
                errors.append(
                    f"Feed history retention ({days_retained} days) is less than "
                    f"required minimum ({self.MIN_RETENTION_DAYS} days)"
                )
        
        return errors

    def _validate_dates(self, doc: etree._ElementTree) -> List[str]:
        """Validate date formats and logical consistency."""
        errors = []
        current_date = datetime.utcnow()
        
        try:
            # Check lastBuildDate
            last_build = doc.find(".//{*}lastBuildDate")
            if last_build is not None:
                try:
                    last_build_date = datetime.strptime(last_build.text, "%Y-%m-%dT%H:%M:%SZ")
                    if last_build_date > current_date:
                        errors.append(f"lastBuildDate is in the future: {last_build.text}")
                except ValueError:
                    errors.append(f"Invalid lastBuildDate format: {last_build.text}")
            
            # Check pubDates
            for pub_date in doc.findall(".//{*}pubDate"):
                try:
                    pub_date_obj = datetime.strptime(pub_date.text, "%Y-%m-%dT%H:%M:%SZ")
                    if pub_date_obj > current_date:
                        errors.append(f"pubDate is in the future: {pub_date.text}")
                except ValueError:
                    errors.append(f"Invalid pubDate format: {pub_date.text}")
        
        except Exception as e:
            errors.append(f"Date validation error: {e}")
        
        return errors

    def _validate_uris(self, doc: etree._ElementTree) -> List[str]:
        """Validate URI formats and accessibility."""
        errors = []
        for link in doc.findall(".//{*}link"):
            url = link.text
            
            # Basic URL format validation
            if not url.startswith(('http://', 'https://')):
                errors.append(f"Invalid URI scheme: {url}")
                continue
            
            # Parse URL for additional validation
            try:
                parsed = urllib.parse.urlparse(url)
                if not all([parsed.scheme, parsed.netloc]):
                    errors.append(f"Invalid URI format: {url}")
                
                # Check for common issues
                if ' ' in url:
                    errors.append(f"URI contains spaces: {url}")
                if not parsed.netloc.count('.'):
                    errors.append(f"Invalid domain in URI: {url}")
                
            except Exception as e:
                errors.append(f"URI parsing error for {url}: {e}")
        
        return errors

def main():
    parser = argparse.ArgumentParser(description='Validate ATF XML files')
    parser.add_argument('xml_file', help='Path to the ATF XML file to validate')
    parser.add_argument('--schema', default='schema/atf-1.0.xsd',
                      help='Path to the ATF schema file')
    parser.add_argument('--verbose', action='store_true',
                      help='Show detailed validation messages')
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