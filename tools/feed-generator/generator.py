#!/usr/bin/env python3

import argparse
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
import xml.etree.ElementTree as ET
from xml.dom import minidom

class ATFGenerator:
    """Generator for Algorithmic Transparency Feed (ATF) files."""
    
    def __init__(self):
        """Initialize the ATF generator."""
        self.namespace = "https://www.algorithmictransparency.gov/atf"
        self.nsmap = {"": self.namespace}
        ET.register_namespace("", self.namespace)
    
    def create_feed(self, 
                   title: str,
                   link: str,
                   description: str,
                   language: str = "en-us") -> ET.Element:
        """Create a new ATF feed with basic channel information."""
        atf = ET.Element("atf", {"version": "1.0"})
        
        channel = ET.SubElement(atf, "channel")
        ET.SubElement(channel, "title").text = title
        ET.SubElement(channel, "link").text = link
        ET.SubElement(channel, "description").text = description
        ET.SubElement(channel, "lastBuildDate").text = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
        ET.SubElement(channel, "language").text = language
        
        return atf
    
    def add_item(self,
                 feed: ET.Element,
                 title: str,
                 link: str,
                 description: str,
                 categories: List[str],
                 impact_summary: str,
                 affected_users: str,
                 metrics: Optional[Dict[str, str]] = None,
                 pub_date: Optional[datetime] = None) -> None:
        """Add a new item to the feed."""
        if pub_date is None:
            pub_date = datetime.utcnow()
            
        item = ET.SubElement(feed, "item")
        
        ET.SubElement(item, "title").text = title
        ET.SubElement(item, "link").text = link
        ET.SubElement(item, "pubDate").text = pub_date.strftime("%Y-%m-%dT%H:%M:%SZ")
        ET.SubElement(item, "description").text = description
        
        # Add categories
        cats = ET.SubElement(item, "categories")
        for category in categories:
            ET.SubElement(cats, "category").text = category
        
        # Add impact assessment
        impact = ET.SubElement(item, "impactAssessment")
        ET.SubElement(impact, "summary").text = impact_summary
        ET.SubElement(impact, "affectedUsers").text = affected_users
        
        # Add metrics if provided
        if metrics:
            metrics_elem = ET.SubElement(impact, "metrics")
            for name, value in metrics.items():
                metric = ET.SubElement(metrics_elem, "metric", {"name": name})
                metric.text = value
    
    def save_feed(self, feed: ET.Element, output_path: Path) -> None:
        """Save the feed to a file with pretty printing."""
        rough_string = ET.tostring(feed, encoding='unicode')
        reparsed = minidom.parseString(rough_string)
        pretty_xml = reparsed.toprettyxml(indent="  ")
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(pretty_xml)

def main():
    parser = argparse.ArgumentParser(description='Generate ATF XML feeds')
    parser.add_argument('--config', type=str, help='Path to JSON configuration file')
    parser.add_argument('--output', type=str, default='feed.xml', help='Output file path')
    args = parser.parse_args()
    
    try:
        # Load configuration
        with open(args.config) as f:
            config = json.load(f)
        
        # Create generator and feed
        generator = ATFGenerator()
        feed = generator.create_feed(
            title=config['title'],
            link=config['link'],
            description=config['description'],
            language=config.get('language', 'en-us')
        )
        
        # Add items
        for item in config['items']:
            generator.add_item(
                feed=feed,
                title=item['title'],
                link=item['link'],
                description=item['description'],
                categories=item['categories'],
                impact_summary=item['impact_summary'],
                affected_users=item['affected_users'],
                metrics=item.get('metrics')
            )
        
        # Save feed
        generator.save_feed(feed, Path(args.output))
        print(f"Feed generated successfully: {args.output}")
        
    except Exception as e:
        print(f"Error generating feed: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    main()