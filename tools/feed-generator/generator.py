#!/usr/bin/env python3

import json
import sys
import argparse
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Union, Set
import xml.etree.ElementTree as ET
from xml.dom import minidom
import logging
from dataclasses import dataclass, field
import copy

@dataclass
class UpdateTemplate:
    """Template for common update types."""
    name: str
    categories: List[str]
    description_template: str
    impact_template: str
    metrics: Dict[str, str] = field(default_factory=dict)
    required_fields: Set[str] = field(default_factory=set)

class EnhancedATFGenerator:
    """Enhanced generator for Algorithmic Transparency Feed (ATF) files."""
    
    # Standard categories
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
    
    # Common update templates
    DEFAULT_TEMPLATES = {
        'ranking_update': UpdateTemplate(
            name="Ranking Algorithm Update",
            categories=['Ranking Algorithm'],
            description_template="Updated {algorithm_name} ranking algorithm to improve {improvement_area}.",
            impact_template="Improved ranking performance for {affected_segment} of users.",
            metrics={
                'Relevance Score': '+{relevance_improvement}%',
                'Query Success Rate': '+{success_rate_improvement}%',
                'Processing Time': '{processing_time_change}%'
            },
            required_fields={'algorithm_name', 'improvement_area', 'affected_segment'}
        ),
        'privacy_enhancement': UpdateTemplate(
            name="Privacy Enhancement",
            categories=['Privacy Enhancement', 'Security'],
            description_template="Enhanced privacy protections in {system_name} using {technology}.",
            impact_template="Strengthened data protection while maintaining system functionality.",
            metrics={
                'Privacy Guarantee': 'ε={epsilon}',
                'Data Utility': '{utility}%',
                'Processing Overhead': '+{overhead}%'
            },
            required_fields={'system_name', 'technology', 'epsilon'}
        ),
        'content_moderation': UpdateTemplate(
            name="Content Moderation Update",
            categories=['Content Moderation', 'Machine Learning'],
            description_template="Updated content moderation system with improved {feature_type} detection.",
            impact_template="Enhanced detection accuracy while reducing false positives.",
            metrics={
                'Detection Accuracy': '+{accuracy_improvement}%',
                'False Positive Rate': '{false_positive_change}%',
                'Processing Latency': '{latency_change}%'
            },
            required_fields={'feature_type'}
        )
    }
    
    def __init__(self):
        """Initialize the ATF generator."""
        self.namespace = "https://www.algorithmictransparency.gov/atf"
        self.nsmap = {"": self.namespace}
        ET.register_namespace("", self.namespace)
        self.templates = copy.deepcopy(self.DEFAULT_TEMPLATES)
        self.logger = logging.getLogger(__name__)
    
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
    
    def add_template(self, name: str, template: UpdateTemplate):
        """Add a new template for updates."""
        self.templates[name] = template
    
    def get_template(self, name: str) -> Optional[UpdateTemplate]:
        """Get a template by name."""
        return self.templates.get(name)
    
    def standardize_category(self, category: str) -> str:
        """Standardize a category name or suggest the closest match."""
        if category in self.STANDARD_CATEGORIES:
            return category
        
        # Find closest match
        closest = None
        max_similarity = 0
        category_lower = category.lower()
        
        for std_category in self.STANDARD_CATEGORIES:
            similarity = self._calculate_similarity(category_lower, std_category.lower())
            if similarity > max_similarity:
                max_similarity = similarity
                closest = std_category
        
        if closest and max_similarity > 0.8:  # Threshold for suggestion
            self.logger.warning(f"Non-standard category '{category}' - using '{closest}' instead")
            return closest
        
        self.logger.warning(f"Using non-standard category: {category}")
        return category
    
    def _calculate_similarity(self, s1: str, s2: str) -> float:
        """Calculate string similarity for category matching."""
        # Simple Levenshtein distance-based similarity
        if len(s1) < len(s2):
            return self._calculate_similarity(s2, s1)
        
        if not s2:
            return 0
        
        previous_row = range(len(s2) + 1)
        for i, c1 in enumerate(s1):
            current_row = [i + 1]
            for j, c2 in enumerate(s2):
                insertions = previous_row[j + 1] + 1
                deletions = current_row[j] + 1
                substitutions = previous_row[j] + (c1 != c2)
                current_row.append(min(insertions, deletions, substitutions))
            previous_row = current_row
        
        return 1 - (previous_row[-1] / max(len(s1), len(s2)))
    
    def add_templated_item(self,
                          feed: ET.Element,
                          template_name: str,
                          template_data: Dict[str, str],
                          link: str,
                          affected_users: str,
                          pub_date: Optional[datetime] = None) -> None:
        """Add a new item using a template."""
        template = self.get_template(template_name)
        if not template:
            raise ValueError(f"Template not found: {template_name}")
        
        # Validate required fields
        missing_fields = template.required_fields - set(template_data.keys())
        if missing_fields:
            raise ValueError(f"Missing required fields for template: {missing_fields}")
        
        # Format description and impact summary
        description = template.description_template.format(**template_data)
        impact_summary = template.impact_template.format(**template_data)
        
        # Format metrics
        metrics = {}
        for metric_name, metric_template in template.metrics.items():
            try:
                metrics[metric_name] = metric_template.format(**template_data)
            except KeyError:
                # Skip optional metrics that don't have data
                continue
        
        # Standardize categories
        categories = [self.standardize_category(cat) for cat in template.categories]
        
        # Add the item
        self.add_item(
            feed=feed,
            title=template.name,
            link=link,
            description=description,
            categories=categories,
            impact_summary=impact_summary,
            affected_users=affected_users,
            metrics=metrics,
            pub_date=pub_date
        )
    
    def batch_update(self,
                    feed: ET.Element,
                    updates: List[Dict],
                    template_name: Optional[str] = None) -> None:
        """Process multiple updates in batch."""
        for update in updates:
            if template_name:
                self.add_templated_item(feed, template_name, update['data'], 
                                      update['link'], update['affected_users'],
                                      update.get('pub_date'))
            else:
                self.add_item(feed, **update)
    
    def merge_feeds(self, feeds: List[ET.Element]) -> ET.Element:
        """Merge multiple feeds into one, maintaining chronological order."""
        if not feeds:
            raise ValueError("No feeds to merge")
        
        # Create new feed with metadata from first feed
        first_feed = feeds[0]
        first_channel = first_feed.find("channel")
        merged = self.create_feed(
            title=first_channel.find("title").text,
            link=first_channel.find("link").text,
            description=first_channel.find("description").text,
            language=first_channel.find("language").text
        )
        
        # Collect all items
        all_items = []
        for feed in feeds:
            items = feed.findall("item")
            all_items.extend(items)
        
        # Sort items by publication date
        all_items.sort(
            key=lambda x: datetime.strptime(x.find("pubDate").text, "%Y-%m-%dT%H:%M:%SZ"),
            reverse=True
        )
        
        # Add items to merged feed
        for item in all_items:
            merged.append(copy.deepcopy(item))
        
        return merged
    
    def manage_history(self, 
                      feed: ET.Element,
                      max_age_days: Optional[int] = None,
                      max_items: Optional[int] = None) -> None:
        """Manage historical entries in the feed."""
        items = feed.findall("item")
        if not items:
            return
        
        current_time = datetime.utcnow()
        items_to_remove = set()
        
        # Identify items to remove based on age
        if max_age_days is not None:
            cutoff_date = current_time - timedelta(days=max_age_days)
            for item in items:
                pub_date = datetime.strptime(item.find("pubDate").text, "%Y-%m-%dT%H:%M:%SZ")
                if pub_date < cutoff_date:
                    items_to_remove.add(item)
        
        # Identify items to remove based on count
        if max_items is not None and len(items) > max_items:
            # Sort by date, newest first
            sorted_items = sorted(
                items,
                key=lambda x: datetime.strptime(x.find("pubDate").text, "%Y-%m-%dT%H:%M:%SZ"),
                reverse=True
            )
            items_to_remove.update(sorted_items[max_items:])
        
        # Remove identified items
        for item in items_to_remove:
            feed.remove(item)
    
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
    parser.add_argument('--template', type=str, help='Template name to use')
    parser.add_argument('--output', type=str, default='feed.xml', help='Output file path')
    parser.add_argument('--merge', nargs='+', help='Paths to feeds to merge')
    parser.add_argument('--max-age', type=int, help='Maximum age of entries in days')
    parser.add_argument('--max-items', type=int, help='Maximum number of items to keep')
    args = parser.parse_args()
    
    try:
        generator = EnhancedATFGenerator()
        
        if args.merge:
            # Merge multiple feeds
            feeds = []
            for feed_path in args.merge:
                tree = ET.parse(feed_path)
                feeds.append(tree.getroot())
            merged_feed = generator.merge_feeds(feeds)
            generator.save_feed(merged_feed, Path(args.output))
            
        elif args.config:
            # Generate from config
            with open(args.config) as f:
                config = json.load(f)
            
            feed = generator.create_feed(
                title=config['title'],
                link=config['link'],
                description=config['description'],
                language=config.get('language', 'en-us')
            )
            
            if args.template:
                generator.batch_update(feed, config['items'], args.template)
            else:
                generator.batch_update(feed, config['items'])
            
            if args.max_age or args.max_items:
                generator.manage_history(feed, args.max_age, args.max_items)
            
            generator.save_feed(feed, Path(args.output))
        
        print(f"Feed generated successfully: {args.output}")
        
    except Exception as e:
        print(f"Error generating feed: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    main()