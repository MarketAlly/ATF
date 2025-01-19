# docs/getting-started.md
# Getting Started with ATF

## Overview
The Algorithmic Transparency Feed (ATF) format is designed to help organizations comply with the Algorithmic Transparency and Accountability Act (ATAA). This guide will help you get started with implementing ATF in your organization.

## Quick Start

1. **Installation**
```bash
git clone https://github.com/yourusername/atf.git
cd atf
pip install -r validator/requirements.txt
```

2. **Creating Your First ATF Feed**
```xml
<?xml version="1.0" encoding="UTF-8"?>
<atf xmlns="https://www.algorithmictransparency.gov/atf" version="1.0">
  <!-- Add your feed content here -->
</atf>
```

3. **Validating Your Feed**
```bash
python validator/validator.py your_feed.xml
```

## Best Practices

1. **Regular Updates**
   - Update your feed at least monthly
   - Include all significant algorithmic changes
   - Maintain historical entries

2. **Clear Descriptions**
   - Use plain language
   - Include specific metrics
   - Detail impact assessments

3. **Accessibility**
   - Host feed on a public URL
   - Provide stable, permanent links
   - Include proper documentation

---

# docs/specification.md
# ATF Technical Specification

## 1. Format Overview

The Algorithmic Transparency Feed (ATF) is an XML-based format designed for publishing algorithmic transparency data. It follows similar principles to RSS while adding specific elements for algorithmic transparency.

### 1.1 Namespace

The ATF namespace is: `https://www.algorithmictransparency.gov/atf`

### 1.2 Version

Current version: 1.0

## 2. Elements

### 2.1 Required Elements

#### Channel
- `<title>`: Feed title
- `<link>`: Feed URL
- `<description>`: Feed description
- `<lastBuildDate>`: Last update timestamp
- `<language>`: Feed language

#### Items
- `<title>`: Update title
- `<link>`: Update URL
- `<pubDate>`: Publication date
- `<categories>`: Category list
- `<description>`: Update description
- `<impactAssessment>`: Impact details

### 2.2 Optional Elements

#### Impact Assessment
- `<metrics>`: Quantitative metrics
- `<affectedUsers>`: User impact percentage

## 3. Data Types

- Dates: ISO 8601 format
- URLs: Valid HTTP(S) URLs
- Percentages: Numeric values with % symbol

## 4. Validation

See `validator/validator.py` for implementation details.

---

# docs/examples.md
# ATF Examples

## Basic Feed Example

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
    <!-- Example item content -->
  </item>
</atf>
```

## Common Use Cases

1. **Ranking Algorithm Updates**
2. **Content Moderation Changes**
3. **Recommendation System Updates**
4. **User Classification Changes**

See `examples/` directory for more detailed examples.