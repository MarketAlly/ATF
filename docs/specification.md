# Algorithmic Transparency Feed (ATF) Specification v1.0

## Overview

ATF is an XML-based format designed to help organizations comply with the Algorithmic Transparency and Accountability Act (ATAA). This specification defines the structure, elements, and requirements for creating valid ATF feeds.

## 1. Feed Structure

### 1.1 Root Element

The root element must be `<atf>` with the following attributes:
- `xmlns`: Must be "https://www.algorithmictransparency.gov/atf"
- `version`: Must be "1.0"

### 1.2 Channel Element

The `<channel>` element contains feed metadata with the following required sub-elements:

| Element | Description | Format | Required |
|---------|-------------|---------|----------|
| `title` | Feed title | String | Yes |
| `link` | Feed URL | Valid URL | Yes |
| `description` | Feed description | String | Yes |
| `lastBuildDate` | Last update time | ISO 8601 | Yes |
| `language` | Feed language | ISO 639-1 | Yes |

### 1.3 Item Elements

Each `<item>` element represents an algorithmic update with the following structure:

| Element | Description | Format | Required |
|---------|-------------|---------|----------|
| `title` | Update title | String | Yes |
| `link` | Update URL | Valid URL | Yes |
| `pubDate` | Publication date | ISO 8601 | Yes |
| `categories` | Category list | List of strings | Yes |
| `description` | Update description | String | Yes |
| `impactAssessment` | Impact details | Complex type | Yes |

### 1.4 Impact Assessment Structure

The `<impactAssessment>` element contains:

| Element | Description | Format | Required |
|---------|-------------|---------|----------|
| `summary` | Impact summary | String | Yes |
| `affectedUsers` | User impact | Percentage | Yes |
| `metrics` | Performance metrics | Complex type | No |

## 2. Data Types and Formats

### 2.1 Dates and Times
- All dates must use ISO 8601 format
- Example: `2025-01-19T10:00:00Z`
- Times must be in UTC (indicated by 'Z' suffix)

### 2.2 URLs
- Must be valid HTTP(S) URLs
- Must be absolute URLs
- Must be publicly accessible

### 2.3 Categories
- At least one category required per item
- Categories should be consistent within an organization
- Common categories include:
  - Ranking Algorithm
  - Content Moderation
  - Recommendation System
  - User Classification
  - Privacy Enhancement
  - Bias Mitigation

### 2.4 Metrics
- Name attribute required
- Value should be numeric with optional unit
- Common metrics include:
  - Accuracy
  - Fairness Score
  - Processing Time
  - User Engagement
  - Error Rate

## 3. Best Practices

### 3.1 Update Frequency
- Minimum: Monthly updates
- Recommended: Real-time or near-real-time for significant changes
- Retain historical entries for at least 12 months

### 3.2 Description Quality
- Use plain language
- Include specific, quantifiable changes
- Explain user impact clearly
- Avoid technical jargon when possible

### 3.3 Impact Assessment
- Provide concrete metrics where possible
- Include both positive and negative impacts
- Specify affected user demographics when relevant
- Detail mitigation strategies for negative impacts

### 3.4 Feed Management
- Maintain consistent URL structure
- Implement proper caching headers
- Provide API access when possible
- Include proper XML namespace declarations

## 4. Security Considerations

### 4.1 Feed Access
- HTTPS required for feed delivery
- Consider authentication for sensitive details
- Implement rate limiting if needed

### 4.2 Content Security
- Sanitize all text content
- Validate URLs before publishing
- Avoid including sensitive data

## 5. Validation

### 5.1 Schema Validation
- All feeds must validate against ATF XSD
- Use provided validator tool
- Check for well-formed XML

### 5.2 Content Validation
- Verify date formats
- Check URL accessibility
- Validate metric formats
- Ensure category consistency