#!/usr/bin/env python3

import json
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Union
import xml.etree.ElementTree as ET
from xml.dom import minidom
import git
import logging
from dataclasses import dataclass
import difflib
import hashlib

@dataclass
class FeedDiff:
    """Represents differences between two feed versions."""
    added_items: List[str]
    removed_items: List[str]
    modified_items: List[Dict]
    
@dataclass
class ImpactAssessment:
    """Template for impact assessments."""
    summary: str
    affected_users: str
    metrics: Dict[str, str]
    risks: List[str]
    mitigations: List[str]

class FeedManager:
    """Manages ATF feed archiving, versioning, and comparison."""
    
    def __init__(self, workspace_dir: Union[str, Path]):
        """Initialize the feed manager."""
        self.workspace = Path(workspace_dir)
        self.archive_dir = self.workspace / "archives"
        self.git_dir = self.workspace / "git"
        self.archive_dir.mkdir(parents=True, exist_ok=True)
        self.git_dir.mkdir(parents=True, exist_ok=True)
        self.logger = logging.getLogger(__name__)
        
        # Initialize git repository if needed
        if not (self.git_dir / ".git").exists():
            self.repo = git.Repo.init(self.git_dir)
        else:
            self.repo = git.Repo(self.git_dir)
    
    def archive_feed(self, feed_path: Union[str, Path], version: str) -> Path:
        """Archive a feed file with version information."""
        feed_path = Path(feed_path)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        archive_name = f"feed_v{version}_{timestamp}.xml"
        archive_path = self.archive_dir / archive_name
        
        # Copy file to archive
        shutil.copy2(feed_path, archive_path)
        
        # Create metadata
        metadata = {
            "version": version,
            "timestamp": timestamp,
            "original_file": str(feed_path),
            "checksum": self._calculate_checksum(feed_path)
        }
        
        # Save metadata
        metadata_path = archive_path.with_suffix(".json")
        with open(metadata_path, "w") as f:
            json.dump(metadata, f, indent=2)
            
        self.logger.info(f"Archived feed version {version} to {archive_path}")
        return archive_path
    
    def version_control(self, feed_path: Union[str, Path], message: str) -> str:
        """Add feed to version control with commit message."""
        feed_path = Path(feed_path)
        target_path = self.git_dir / feed_path.name
        
        # Copy file to git directory
        shutil.copy2(feed_path, target_path)
        
        # Add and commit
        self.repo.index.add([target_path])
        commit = self.repo.index.commit(message)
        
        self.logger.info(f"Committed feed to version control: {commit.hexsha}")
        return commit.hexsha
    
    def compare_feeds(self, feed1_path: Union[str, Path], feed2_path: Union[str, Path]) -> FeedDiff:
        """Compare two feed files and return differences."""
        feed1 = ET.parse(feed1_path)
        feed2 = ET.parse(feed2_path)
        
        items1 = self._extract_items(feed1)
        items2 = self._extract_items(feed2)
        
        # Find differences
        added = []
        removed = []
        modified = []
        
        for item_id, item in items2.items():
            if item_id not in items1:
                added.append(item["title"])
            elif items1[item_id] != item:
                modified.append({
                    "title": item["title"],
                    "changes": self._diff_items(items1[item_id], item)
                })
        
        for item_id, item in items1.items():
            if item_id not in items2:
                removed.append(item["title"])
        
        return FeedDiff(added, removed, modified)
    
    def create_impact_assessment(self, 
                               template_name: str, 
                               params: Dict) -> ImpactAssessment:
        """Create an impact assessment from a template."""
        templates = {
            "ranking_change": {
                "summary": "Updated {algorithm} ranking algorithm to improve {aspect}",
                "affected_users": "{percentage}%",
                "metrics": {
                    "accuracy": "+{accuracy_improvement}%",
                    "latency": "{latency_change}%"
                },
                "risks": [
                    "Temporary degradation during deployment",
                    "Potential learning period for new algorithm",
                    "May affect historical comparisons"
                ],
                "mitigations": [
                    "Phased rollout",
                    "A/B testing",
                    "Monitoring and alerts",
                    "Rollback plan"
                ]
            },
            "privacy_enhancement": {
                "summary": "Enhanced privacy protections for {feature}",
                "affected_users": "100%",
                "metrics": {
                    "privacy_score": "ε={epsilon}",
                    "performance_impact": "{perf_impact}%"
                },
                "risks": [
                    "Potential impact on system performance",
                    "Changes to data access patterns",
                    "Integration with existing systems"
                ],
                "mitigations": [
                    "Performance optimization",
                    "Clear documentation",
                    "User communication",
                    "Gradual rollout"
                ]
            }
        }
        
        template = templates.get(template_name)
        if not template:
            raise ValueError(f"Unknown template: {template_name}")
        
        return ImpactAssessment(
            summary=template["summary"].format(**params),
            affected_users=template["affected_users"].format(**params),
            metrics={k: v.format(**params) for k, v in template["metrics"].items()},
            risks=template["risks"],
            mitigations=template["mitigations"]
        )
    
    def automate_update(self, feed_path: Union[str, Path], 
                       updates: List[Dict], 
                       version: str) -> Path:
        """Automate feed updates with version control and archiving."""
        tree = ET.parse(feed_path)
        root = tree.getroot()
        
        # Apply updates
        for update in updates:
            if update.get("type") == "add":
                self._add_item(root, update["data"])
            elif update.get("type") == "modify":
                self._modify_item(root, update["item_id"], update["data"])
            elif update.get("type") == "remove":
                self._remove_item(root, update["item_id"])
        
        # Save updated feed
        updated_path = Path(feed_path).with_name(f"feed_v{version}.xml")
        self._save_xml(tree, updated_path)
        
        # Version control
        commit_msg = f"Update feed to version {version}"
        self.version_control(updated_path, commit_msg)
        
        # Archive
        self.archive_feed(updated_path, version)
        
        return updated_path
    
    def _calculate_checksum(self, file_path: Path) -> str:
        """Calculate SHA-256 checksum of a file."""
        sha256 = hashlib.sha256()
        with open(file_path, "rb") as f:
            for block in iter(lambda: f.read(4096), b""):
                sha256.update(block)
        return sha256.hexdigest()
    
    def _extract_items(self, tree: ET.ElementTree) -> Dict:
        """Extract items from feed with their IDs."""
        items = {}
        for item in tree.findall(".//item"):
            item_id = item.find("link").text
            items[item_id] = {
                "title": item.find("title").text,
                "description": item.find("description").text,
                "pubDate": item.find("pubDate").text
            }
        return items
    
    def _diff_items(self, item1: Dict, item2: Dict) -> Dict:
        """Generate detailed diff between two items."""
        diffs = {}
        for key in item1:
            if item1[key] != item2[key]:
                diffs[key] = {
                    "old": item1[key],
                    "new": item2[key],
                    "diff": list(difflib.ndiff(
                        item1[key].splitlines(),
                        item2[key].splitlines()
                    ))
                }
        return diffs
    
    def _save_xml(self, tree: ET.ElementTree, path: Path):
        """Save XML tree with pretty printing."""
        rough_string = ET.tostring(tree.getroot(), encoding='unicode')
        reparsed = minidom.parseString(rough_string)
        with open(path, "w", encoding="utf-8") as f:
            f.write(reparsed.toprettyxml(indent="  "))

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="ATF Feed Management Tools")
    parser.add_argument("--workspace", required=True, help="Workspace directory")
    
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")
    
    # Archive command
    archive_parser = subparsers.add_parser("archive", help="Archive a feed")
    archive_parser.add_argument("feed", help="Feed file to archive")
    archive_parser.add_argument("version", help="Version number")
    
    # Compare command
    compare_parser = subparsers.add_parser("compare", help="Compare two feeds")
    compare_parser.add_argument("feed1", help="First feed file")
    compare_parser.add_argument("feed2", help="Second feed file")
    
    # Update command
    update_parser = subparsers.add_parser("update", help="Automated feed update")
    update_parser.add_argument("feed", help="Feed file to update")
    update_parser.add_argument("updates", help="JSON file containing updates")
    update_parser.add_argument("version", help="New version number")
    
    args = parser.parse_args()
    
    manager = FeedManager(args.workspace)
    
    if args.command == "archive":
        manager.archive_feed(args.feed, args.version)
    elif args.command == "compare":
        diff = manager.compare_feeds(args.feed1, args.feed2)
        print(f"Added items: {diff.added_items}")
        print(f"Removed items: {diff.removed_items}")
        print("Modified items:")
        for item in diff.modified_items:
            print(f"  - {item['title']}")
            for field, changes in item['changes'].items():
                print(f"    {field}: {changes['old']} -> {changes['new']}")
    elif args.command == "update":
        with open(args.updates) as f:
            updates = json.load(f)
        manager.automate_update(args.feed, updates, args.version)

if __name__ == "__main__":
    main()