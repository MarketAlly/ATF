# ATF Usage Examples

This document provides practical examples of ATF implementations for various common scenarios.

## 1. Basic Feed Example

### 1.1 Minimal Valid Feed

```xml
<?xml version="1.0" encoding="UTF-8"?>
<atf xmlns="https://www.algorithmictransparency.gov/atf" version="1.0">
  <channel>
    <title>Example Corp ATF</title>
    <link>https://example.com/atf</link>
    <description>Algorithm updates for Example Corp</description>
    <lastBuildDate>2025-01-19T10:00:00Z</lastBuildDate>
    <language>en-us</language>
  </channel>
  <item>
    <title>Search Ranking Update</title>
    <link>https://example.com/updates/search-2025-01</link>
    <pubDate>2025-01-19T09:00:00Z</pubDate>
    <categories>
      <category>Search Algorithm</category>
      <category>Ranking</category>
    </categories>
    <description>Updated search ranking to improve local result relevance.</description>
    <impactAssessment>
      <summary>Improved local search results for 15% of queries.</summary>
      <affectedUsers>25%</affectedUsers>
    </impactAssessment>
  </item>
</atf>
```

## 2. Common Use Cases

### 2.1 Recommendation System Update

```xml
<item>
  <title>Product Recommendation Enhancement</title>
  <link>https://example.com/updates/rec-2025-01</link>
  <pubDate>2025-01-15T14:30:00Z</pubDate>
  <categories>
    <category>Recommendation System</category>
    <category>Personalization</category>
  </categories>
  <description>
    Enhanced product recommendations to better balance personalization and diversity.
    The update introduces collaborative filtering improvements and diversity metrics.
  </description>
  <impactAssessment>
    <summary>
      Increased recommendation diversity while maintaining personalization accuracy.
      Testing shows improved user satisfaction and product discovery.
    </summary>
    <affectedUsers>60%</affectedUsers>
    <metrics>
      <metric name="Diversity Score">+25%</metric>
      <metric name="User Satisfaction">+12%</metric>
      <metric name="Click-through Rate">+8%</metric>
      <metric name="Long-tail Product Views">+15%</metric>
    </metrics>
  </impactAssessment>
</item>
```

### 2.2 Content Moderation Update

```xml
<item>
  <title>Enhanced Hate Speech Detection</title>
  <link>https://example.com/updates/moderation-2025-01</link>
  <pubDate>2025-01-10T09:15:00Z</pubDate>
  <categories>
    <category>Content Moderation</category>
    <category>Safety</category>
    <category>Machine Learning</category>
  </categories>
  <description>
    Deployed improved hate speech detection models with enhanced
    contextual understanding and reduced false positive rates.
  </description>
  <impactAssessment>
    <summary>
      New models show significant improvement in accuracy while
      reducing false positives for legitimate content.
    </summary>
    <affectedUsers>30%</affectedUsers>
    <metrics>
      <metric name="Detection Accuracy">+15%</metric>
      <metric name="False Positive Rate">-40%</metric>
      <metric name="Processing Latency">-20%</metric>
    </metrics>
  </impactAssessment>
</item>
```

### 2.3 Privacy Enhancement

```xml
<item>
  <title>User Data Anonymization Update</title>
  <link>https://example.com/updates/privacy-2025-01</link>
  <pubDate>2025-01-05T16:45:00Z</pubDate>
  <categories>
    <category>Privacy</category>
    <category>Data Protection</category>
  </categories>
  <description>
    Implemented enhanced data anonymization techniques for user behavior analysis.
  </description>
  <impactAssessment>
    <summary>
      Improved privacy guarantees while maintaining analytical capabilities.
      Implemented differential privacy with ε=2.0.
    </summary>
    <affectedUsers>100%</affectedUsers>
    <metrics>
      <metric name="Privacy Guarantee">ε=2.0</metric>
      <metric name="Analysis Accuracy">-3%</metric>
      <metric name="Data Utility">95%</metric>
    </metrics>
  </impactAssessment>
</item>
```

## 3. Using the Generator Tool

### 3.1 Example Configuration File

```json
{
  "title": "Example Corp ATF",
  "link": "https://example.com/transparency",
  "description": "Algorithmic system updates for Example Corp",
  "language": "en-us",
  "items": [
    {
      "title": "Search Ranking Update Q1 2025",
      "link": "https://example.com/updates/search-2025-q1",
      "description": "Quarterly update to search ranking algorithm",
      "categories": ["Search", "Ranking"],
      "impact_summary": "Improved search relevance for technical queries",
      "affected_users": "35%",
      "metrics": {
        "Relevance Score": "+10%",
        "Query Success Rate": "+15%"
      }
    }
  ]
}
```

### 3.2 Command Line Usage

Generate a feed:
```bash
python tools/feed-generator/generator.py --config examples/config.json --output feed.xml
```

Validate the feed:
```bash
python validator/validator.py feed.xml
```

Read the feed:
```bash
python tools/feed-reader/reader.py feed.xml
```

## 4. Integration Examples

### 4.1 Automated Generation Script

```python
from atf.generator import ATFGenerator

def generate_weekly_feed():
    generator = ATFGenerator()
    feed = generator.create_feed(
        title="Weekly Algorithm Updates",
        link="https://example.com/weekly-updates",
        description="Weekly algorithmic system changes"
    )
    
    # Add recent updates
    generator.add_item(
        feed=feed,
        title="Weekly Update 2025-W03",
        link="https://example.com/updates/2025-w03",
        description="Regular weekly update with minor improvements",
        categories=["Maintenance", "Performance"],
        impact_summary="Routine optimization with minimal user impact",
        affected_users="5%",
        metrics={"System Latency": "-5%"}
    )
    
    # Save feed
    generator.save_feed(feed, "weekly_feed.xml")
```

### 4.2 CI/CD Integration

```yaml
name: Generate ATF Feed
on:
  schedule:
    - cron: '0 0 * * MON'  # Weekly on Monday
  workflow_dispatch:

jobs:
  generate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
      - name: Generate Feed
        run: python tools/feed-generator/generator.py --config config.json --output feed.xml
      - name: Validate Feed
        run: python validator/validator.py feed.xml
      - name: Deploy Feed
        run: # Deploy to your web server
```