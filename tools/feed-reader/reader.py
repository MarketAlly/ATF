#!/usr/bin/env python3

import argparse
import sys
from pathlib import Path
from typing import Dict, List
import xml.etree.ElementTree as ET
from datetime import datetime
import json

class ATFReader:
    """Reader for Algorithmic Transparency Feed (ATF) files."""
    
    def __init__(self):
        """Initialize the ATF reader."""
        self.namespace = {"atf": "https://www.algorithmictransparency.gov/atf"}
    
    def read_feed(self, file_path: Path) -> Dict:
        """Read and parse an ATF feed file."""
        tree = ET.parse(file_path)
        root = tree.getroot()
        
        # Parse channel information
        channel = root.find("atf:channel", self.namespace)
        feed_info = {
            "title": self._get_text(channel, "atf:title"),
            "link": self._get_text(channel, "atf:link"),
            "description": self._get_text(channel, "atf:description"),
            "lastBuildDate": self._get_text(channel, "atf:lastBuildDate"),
            "language": self._get_text(channel, "atf:language"),
            "items": []
        }
        
        # Parse items
        for item in root.findall("atf:item", self.namespace):
            feed_info["items"].append(self._parse_item(item))
        
        return feed_info
    
    def _get_text(self, element: ET.Element, xpath: str) -> str:
        """Get text content from an element using xpath."""
        elem = element.find(xpath, self.namespace)
        return elem.text if elem is not None else ""
    
    def _parse_item(self, item: ET.Element) -> Dict:
        """Parse an individual feed item."""
        # Parse categories
        categories = []
        cats_elem = item.find("atf:categories", self.namespace)
        if cats_elem is not None:
            categories = [cat.text for cat in cats_elem.findall("atf:category", self.namespace)]
        
        # Parse impact assessment
        impact = item.find("atf:impactAssessment", self.namespace)
        impact_data = {
            "summary": self._get_text(impact, "atf:summary"),
            "affectedUsers": self._get_text(impact, "atf:affectedUsers"),
            "metrics": {}
        }
        
        # Parse metrics
        metrics_elem = impact.find("atf:metrics", self.namespace)
        if metrics_elem is not None:
            for metric in metrics_elem.findall("atf:metric", self.namespace):
                impact_data["metrics"][metric.get("name")] = metric.text
        
        return {
            "title": self._get_text(item, "atf:title"),
            "link": self._get_text(item, "atf:link"),
            "pubDate": self._get_text(item, "atf:pubDate"),
            "description": self._get_text(item, "atf:description"),
            "categories": categories,
            "impactAssessment": impact_data
        }
    
    def print_feed(self, feed_info: Dict, format: str = "text"):
        """Print feed information in specified format."""
        if format == "json":
            print(json.dumps(feed_info, indent=2))
            return
        
        # Print in text format
        print(f"Feed: {feed_info['title']}")
        print(f"URL: {feed_info['link']}")
        print(f"Description: {feed_info['description']}")
        print(f"Last Updated: {feed_info['lastBuildDate']}")
        print(f"Language: {feed_info['language']}")
        print("\nItems:")
        for idx, item in enumerate(feed_info['items'], 1):
            print(f"\n{idx}. {item['title']}")
            print(f"   Published: {item['pubDate']}")
            print(f"   Link: {item['link']}")
            print(f"   Categories: {', '.join(item['categories'])}")
            print(f"   Description: {item['description']}")
            print("\n   Impact Assessment:")
            print(f"   - Summary: {item['impactAssessment']['summary']}")
            print(f"   - Affected Users: {item['impactAssessment']['affectedUsers']}")
            if item['impactAssessment']['metrics']:
                print("   - Metrics:")
                for name, value in item['impactAssessment']['metrics'].items():
                    print(f"     * {name}: {value}")

def main():
    parser = argparse.ArgumentParser(description='Read and display ATF feeds')
    parser.add_argument('file', type=str, help='Path to ATF XML file')
    parser.add_argument('--format', choices=['text', 'json'], default='text',
                      help='Output format (default: text)')
    args = parser.parse_args()
    
    try:
        reader = ATFReader()
        feed_info = reader.read_feed(Path(args.file))
        reader.print_feed(feed_info, args.format)
    
    except Exception as e:
        print(f"Error reading feed: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    main()