# Knowledge Base Search System

## Overview

The Proxmox AI Infrastructure Assistant Knowledge Base provides a comprehensive, searchable repository of documentation, troubleshooting guides, best practices, and operational procedures. The system implements advanced search capabilities with AI-powered content recommendations and contextual assistance.

## System Architecture

### Search Infrastructure

```
┌─────────────────────────────────────────────────────────────────┐
│                    Knowledge Base Architecture                  │
├─────────────────────────────────────────────────────────────────┤
│  Content Layer     │  Search Layer    │  AI Enhancement Layer  │
│  ├─ Documentation  │  ├─ Elasticsearch│  ├─ Content Analysis   │
│  ├─ Troubleshooting│  ├─ Full-text    │  ├─ Semantic Search    │
│  ├─ API References │  ├─ Faceted      │  ├─ Recommendations    │
│  ├─ Best Practices │  ├─ Autocomplete │  └─ Context Awareness  │
│  └─ Code Examples  │  └─ Synonyms     │                        │
├─────────────────────────────────────────────────────────────────┤
│                    User Interface Layer                        │
│  ├─ Web Interface  ├─ CLI Search     ├─ API Endpoints          │
│  ├─ Mobile App     ├─ Chat Interface ├─ IDE Integration        │
│  └─ Slack Bot      └─ Voice Search   └─ Email Digest          │
└─────────────────────────────────────────────────────────────────┘
```

### Content Management System

```python
#!/usr/bin/env python3
# Knowledge Base Content Management System
# File: /scripts/knowledge-base/content_manager.py

import os
import json
import yaml
import markdown
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from elasticsearch import Elasticsearch
import hashlib
import re

@dataclass
class ContentMetadata:
    title: str
    description: str
    category: str
    tags: List[str]
    author: str
    created_date: datetime
    modified_date: datetime
    version: str
    difficulty_level: str  # beginner, intermediate, advanced
    content_type: str  # documentation, tutorial, troubleshooting, api-reference
    related_topics: List[str]
    prerequisites: List[str]
    estimated_reading_time: int  # minutes

@dataclass
class SearchableContent:
    id: str
    metadata: ContentMetadata
    content: str
    content_hash: str
    search_keywords: List[str]
    extracted_entities: List[str]
    summary: str

class ContentManager:
    def __init__(self, base_path: str = "/home/diszay-claudedev/projects/iac-ai-assistant/docs"):
        self.base_path = Path(base_path)
        self.elasticsearch = Elasticsearch([{'host': 'localhost', 'port': 9200}])
        self.index_name = "proxmox-ai-knowledge"
        self._initialize_elasticsearch()
    
    def _initialize_elasticsearch(self):
        """Initialize Elasticsearch index with proper mapping"""
        mapping = {
            "mappings": {
                "properties": {
                    "title": {
                        "type": "text",
                        "analyzer": "standard",
                        "fields": {
                            "keyword": {"type": "keyword"},
                            "suggest": {"type": "completion"}
                        }
                    },
                    "description": {"type": "text", "analyzer": "standard"},
                    "content": {
                        "type": "text",
                        "analyzer": "standard",
                        "highlight": {}
                    },
                    "category": {"type": "keyword"},
                    "tags": {"type": "keyword"},
                    "author": {"type": "keyword"},
                    "created_date": {"type": "date"},
                    "modified_date": {"type": "date"},
                    "difficulty_level": {"type": "keyword"},
                    "content_type": {"type": "keyword"},
                    "search_keywords": {"type": "keyword"},
                    "extracted_entities": {"type": "keyword"},
                    "summary": {"type": "text"},
                    "file_path": {"type": "keyword"},
                    "reading_time": {"type": "integer"}
                }
            },
            "settings": {
                "analysis": {
                    "analyzer": {
                        "technical_analyzer": {
                            "type": "custom",
                            "tokenizer": "standard",
                            "filter": [
                                "lowercase",
                                "stop",
                                "technical_synonyms",
                                "technical_stemmer"
                            ]
                        }
                    },
                    "filter": {
                        "technical_synonyms": {
                            "type": "synonym",
                            "synonyms": [
                                "vm,virtual machine,virtual server",
                                "proxmox,pve,proxmox ve",
                                "api,rest api,http api",
                                "ssh,secure shell",
                                "ssl,tls,https"
                            ]
                        },
                        "technical_stemmer": {
                            "type": "stemmer",
                            "language": "english"
                        }
                    }
                }
            }
        }
        
        # Create index if it doesn't exist
        if not self.elasticsearch.indices.exists(index=self.index_name):
            self.elasticsearch.indices.create(index=self.index_name, body=mapping)
    
    def scan_content_directory(self) -> List[Path]:
        """Scan directory for documentation files"""
        content_files = []
        
        # Supported file extensions
        extensions = {'.md', '.rst', '.txt', '.yaml', '.yml', '.json'}
        
        for root, dirs, files in os.walk(self.base_path):
            # Skip hidden directories and version control
            dirs[:] = [d for d in dirs if not d.startswith('.') and d != '__pycache__']
            
            for file in files:
                file_path = Path(root) / file
                if file_path.suffix.lower() in extensions:
                    content_files.append(file_path)
        
        return content_files
    
    def extract_metadata_from_file(self, file_path: Path) -> ContentMetadata:
        """Extract metadata from file content and frontmatter"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Extract YAML frontmatter if present
            frontmatter = {}
            if content.startswith('---'):
                try:
                    parts = content.split('---', 2)
                    if len(parts) >= 3:
                        frontmatter = yaml.safe_load(parts[1])
                        content = parts[2]
                except yaml.YAMLError:
                    pass
            
            # Extract title from content or filename
            title = frontmatter.get('title', self._extract_title_from_content(content, file_path))
            
            # Determine category from path
            relative_path = file_path.relative_to(self.base_path)
            category = relative_path.parts[0] if relative_path.parts else 'general'
            
            # Extract or infer metadata
            return ContentMetadata(
                title=title,
                description=frontmatter.get('description', self._generate_description(content)),
                category=category,
                tags=frontmatter.get('tags', self._extract_tags_from_content(content)),
                author=frontmatter.get('author', 'Documentation Team'),
                created_date=frontmatter.get('created_date', datetime.fromtimestamp(file_path.stat().st_ctime)),
                modified_date=frontmatter.get('modified_date', datetime.fromtimestamp(file_path.stat().st_mtime)),
                version=frontmatter.get('version', '1.0'),
                difficulty_level=frontmatter.get('difficulty_level', self._infer_difficulty_level(content)),
                content_type=frontmatter.get('content_type', self._infer_content_type(file_path, content)),
                related_topics=frontmatter.get('related_topics', []),
                prerequisites=frontmatter.get('prerequisites', []),
                estimated_reading_time=frontmatter.get('reading_time', self._estimate_reading_time(content))
            )
        
        except Exception as e:
            print(f"Error extracting metadata from {file_path}: {e}")
            return self._create_default_metadata(file_path)
    
    def _extract_title_from_content(self, content: str, file_path: Path) -> str:
        """Extract title from content or use filename"""
        # Look for markdown h1 title
        lines = content.split('\n')
        for line in lines[:10]:  # Check first 10 lines
            if line.startswith('# '):
                return line[2:].strip()
        
        # Use filename as fallback
        return file_path.stem.replace('-', ' ').replace('_', ' ').title()
    
    def _generate_description(self, content: str) -> str:
        """Generate description from content"""
        # Remove markdown formatting
        text = re.sub(r'[#*`]', '', content)
        
        # Get first paragraph
        paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
        if paragraphs:
            description = paragraphs[0]
            # Limit length
            if len(description) > 200:
                description = description[:200] + '...'
            return description
        
        return "Documentation content"
    
    def _extract_tags_from_content(self, content: str) -> List[str]:
        """Extract relevant tags from content"""
        tags = []
        
        # Common technical terms to identify as tags
        technical_terms = [
            'proxmox', 'vm', 'virtual machine', 'api', 'ssh', 'ssl', 'tls',
            'security', 'backup', 'network', 'storage', 'monitoring',
            'troubleshooting', 'installation', 'configuration', 'automation'
        ]
        
        content_lower = content.lower()
        for term in technical_terms:
            if term in content_lower:
                tags.append(term)
        
        return list(set(tags))  # Remove duplicates
    
    def _infer_difficulty_level(self, content: str) -> str:
        """Infer difficulty level from content complexity"""
        # Simple heuristic based on content characteristics
        complexity_indicators = {
            'beginner': ['getting started', 'introduction', 'basic', 'simple', 'overview'],
            'intermediate': ['configuration', 'setup', 'tutorial', 'guide', 'how to'],
            'advanced': ['advanced', 'expert', 'troubleshooting', 'optimization', 'security', 'api']
        }
        
        content_lower = content.lower()
        scores = {}
        
        for level, indicators in complexity_indicators.items():
            score = sum(1 for indicator in indicators if indicator in content_lower)
            scores[level] = score
        
        # Return level with highest score, default to intermediate
        return max(scores, key=scores.get) if any(scores.values()) else 'intermediate'
    
    def _infer_content_type(self, file_path: Path, content: str) -> str:
        """Infer content type from path and content"""
        path_str = str(file_path).lower()
        content_lower = content.lower()
        
        if 'api' in path_str or 'api reference' in content_lower:
            return 'api-reference'
        elif 'troubleshooting' in path_str or 'error' in content_lower or 'issue' in content_lower:
            return 'troubleshooting'
        elif 'tutorial' in path_str or 'workshop' in path_str or 'exercise' in content_lower:
            return 'tutorial'
        elif 'runbook' in path_str or 'procedure' in content_lower:
            return 'procedure'
        else:
            return 'documentation'
    
    def _estimate_reading_time(self, content: str) -> int:
        """Estimate reading time in minutes (average 200 words per minute)"""
        word_count = len(content.split())
        return max(1, word_count // 200)
    
    def _create_default_metadata(self, file_path: Path) -> ContentMetadata:
        """Create default metadata when extraction fails"""
        return ContentMetadata(
            title=file_path.stem.replace('-', ' ').replace('_', ' ').title(),
            description="Documentation content",
            category=file_path.parent.name,
            tags=[],
            author="Documentation Team",
            created_date=datetime.fromtimestamp(file_path.stat().st_ctime),
            modified_date=datetime.fromtimestamp(file_path.stat().st_mtime),
            version="1.0",
            difficulty_level="intermediate",
            content_type="documentation",
            related_topics=[],
            prerequisites=[],
            estimated_reading_time=5
        )
    
    def process_content_file(self, file_path: Path) -> SearchableContent:
        """Process a single content file"""
        try:
            # Read file content
            with open(file_path, 'r', encoding='utf-8') as f:
                raw_content = f.read()
            
            # Extract metadata
            metadata = self.extract_metadata_from_file(file_path)
            
            # Process content (remove frontmatter, convert markdown to text)
            processed_content = self._process_content_text(raw_content)
            
            # Generate content hash
            content_hash = hashlib.sha256(processed_content.encode()).hexdigest()
            
            # Extract search keywords
            search_keywords = self._extract_search_keywords(processed_content, metadata)
            
            # Extract entities (simplified - could use NLP libraries)
            extracted_entities = self._extract_entities(processed_content)
            
            # Generate summary
            summary = self._generate_summary(processed_content)
            
            # Create searchable content object
            return SearchableContent(
                id=str(file_path.relative_to(self.base_path)),
                metadata=metadata,
                content=processed_content,
                content_hash=content_hash,
                search_keywords=search_keywords,
                extracted_entities=extracted_entities,
                summary=summary
            )
        
        except Exception as e:
            print(f"Error processing {file_path}: {e}")
            return None
    
    def _process_content_text(self, raw_content: str) -> str:
        """Process raw content to extract searchable text"""
        # Remove YAML frontmatter
        if raw_content.startswith('---'):
            parts = raw_content.split('---', 2)
            if len(parts) >= 3:
                raw_content = parts[2]
        
        # Convert markdown to plain text (simplified)
        text = re.sub(r'```.*?```', '', raw_content, flags=re.DOTALL)  # Remove code blocks
        text = re.sub(r'`([^`]+)`', r'\1', text)  # Remove inline code formatting
        text = re.sub(r'[#*_~]', '', text)  # Remove markdown formatting
        text = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', text)  # Convert links to text
        
        return text.strip()
    
    def _extract_search_keywords(self, content: str, metadata: ContentMetadata) -> List[str]:
        """Extract important keywords for search"""
        keywords = set()
        
        # Add metadata tags
        keywords.update(metadata.tags)
        
        # Add title words
        keywords.update(metadata.title.lower().split())
        
        # Extract important terms from content
        important_terms = re.findall(r'\b[A-Z][a-z]+(?:[A-Z][a-z]+)*\b', content)  # CamelCase terms
        keywords.update([term.lower() for term in important_terms])
        
        # Extract quoted terms
        quoted_terms = re.findall(r'"([^"]+)"', content)
        keywords.update([term.lower() for term in quoted_terms])
        
        return list(keywords)
    
    def _extract_entities(self, content: str) -> List[str]:
        """Extract named entities (simplified implementation)"""
        entities = []
        
        # Common technical entities patterns
        patterns = {
            'ip_address': r'\b(?:\d{1,3}\.){3}\d{1,3}\b',
            'url': r'https?://[^\s]+',
            'file_path': r'/[^\s]+',
            'command': r'`([^`]+)`',
            'port': r':(\d{2,5})\b'
        }
        
        for entity_type, pattern in patterns.items():
            matches = re.findall(pattern, content)
            entities.extend([f"{entity_type}:{match}" for match in matches])
        
        return entities
    
    def _generate_summary(self, content: str, max_length: int = 200) -> str:
        """Generate a summary of the content"""
        # Simple extractive summary - take first meaningful paragraph
        paragraphs = [p.strip() for p in content.split('\n\n') if p.strip() and len(p.strip()) > 50]
        
        if paragraphs:
            summary = paragraphs[0]
            if len(summary) > max_length:
                summary = summary[:max_length] + '...'
            return summary
        
        return "Documentation content summary not available."
    
    def index_content(self, searchable_content: SearchableContent) -> bool:
        """Index content in Elasticsearch"""
        try:
            doc = {
                'title': searchable_content.metadata.title,
                'description': searchable_content.metadata.description,
                'content': searchable_content.content,
                'category': searchable_content.metadata.category,
                'tags': searchable_content.metadata.tags,
                'author': searchable_content.metadata.author,
                'created_date': searchable_content.metadata.created_date.isoformat(),
                'modified_date': searchable_content.metadata.modified_date.isoformat(),
                'difficulty_level': searchable_content.metadata.difficulty_level,
                'content_type': searchable_content.metadata.content_type,
                'search_keywords': searchable_content.search_keywords,
                'extracted_entities': searchable_content.extracted_entities,
                'summary': searchable_content.summary,
                'file_path': searchable_content.id,
                'reading_time': searchable_content.metadata.estimated_reading_time,
                'content_hash': searchable_content.content_hash
            }
            
            result = self.elasticsearch.index(
                index=self.index_name,
                id=searchable_content.id,
                body=doc
            )
            
            return result['result'] in ['created', 'updated']
        
        except Exception as e:
            print(f"Error indexing content {searchable_content.id}: {e}")
            return False
    
    def build_full_index(self) -> dict:
        """Build complete search index from all content files"""
        print("Scanning content directory...")
        content_files = self.scan_content_directory()
        
        stats = {
            'total_files': len(content_files),
            'processed': 0,
            'indexed': 0,
            'errors': 0,
            'skipped': 0
        }
        
        for file_path in content_files:
            try:
                # Check if file needs reindexing
                if self._needs_reindexing(file_path):
                    searchable_content = self.process_content_file(file_path)
                    
                    if searchable_content:
                        if self.index_content(searchable_content):
                            stats['indexed'] += 1
                            print(f"Indexed: {file_path.relative_to(self.base_path)}")
                        else:
                            stats['errors'] += 1
                    else:
                        stats['errors'] += 1
                    
                    stats['processed'] += 1
                else:
                    stats['skipped'] += 1
                    print(f"Skipped (up to date): {file_path.relative_to(self.base_path)}")
            
            except Exception as e:
                print(f"Error processing {file_path}: {e}")
                stats['errors'] += 1
        
        print(f"\nIndexing complete: {stats}")
        return stats
    
    def _needs_reindexing(self, file_path: Path) -> bool:
        """Check if file needs reindexing based on modification time"""
        try:
            doc_id = str(file_path.relative_to(self.base_path))
            result = self.elasticsearch.get(index=self.index_name, id=doc_id, ignore=[404])
            
            if not result.get('found'):
                return True  # File not indexed yet
            
            # Check if file was modified after last indexing
            file_mtime = datetime.fromtimestamp(file_path.stat().st_mtime)
            indexed_mtime = datetime.fromisoformat(result['_source']['modified_date'])
            
            return file_mtime > indexed_mtime
        
        except Exception:
            return True  # Re-index if we can't determine

class SearchEngine:
    def __init__(self, index_name: str = "proxmox-ai-knowledge"):
        self.elasticsearch = Elasticsearch([{'host': 'localhost', 'port': 9200}])
        self.index_name = index_name
    
    def search(self, query: str, filters: dict = None, size: int = 10, from_: int = 0) -> dict:
        """Perform advanced search with filters and facets"""
        
        # Build search query
        search_body = {
            "query": {
                "bool": {
                    "must": [
                        {
                            "multi_match": {
                                "query": query,
                                "fields": [
                                    "title^3",
                                    "description^2", 
                                    "content",
                                    "tags^2",
                                    "search_keywords^2"
                                ],
                                "type": "best_fields",
                                "fuzziness": "AUTO"
                            }
                        }
                    ],
                    "filter": []
                }
            },
            "highlight": {
                "fields": {
                    "content": {"fragment_size": 150, "number_of_fragments": 3},
                    "title": {},
                    "description": {}
                }
            },
            "aggs": {
                "categories": {"terms": {"field": "category", "size": 10}},
                "content_types": {"terms": {"field": "content_type", "size": 10}},
                "difficulty_levels": {"terms": {"field": "difficulty_level", "size": 10}},
                "tags": {"terms": {"field": "tags", "size": 20}}
            },
            "size": size,
            "from": from_,
            "_source": {
                "excludes": ["content"]  # Exclude full content from results
            }
        }
        
        # Apply filters
        if filters:
            for field, values in filters.items():
                if isinstance(values, list):
                    search_body["query"]["bool"]["filter"].append({
                        "terms": {field: values}
                    })
                else:
                    search_body["query"]["bool"]["filter"].append({
                        "term": {field: values}
                    })
        
        try:
            result = self.elasticsearch.search(index=self.index_name, body=search_body)
            return self._format_search_results(result)
        
        except Exception as e:
            print(f"Search error: {e}")
            return {"error": str(e)}
    
    def suggest(self, query: str, size: int = 5) -> List[str]:
        """Get search suggestions"""
        suggest_body = {
            "suggest": {
                "title_suggest": {
                    "prefix": query,
                    "completion": {
                        "field": "title.suggest",
                        "size": size
                    }
                }
            }
        }
        
        try:
            result = self.elasticsearch.search(index=self.index_name, body=suggest_body)
            suggestions = []
            for suggestion in result['suggest']['title_suggest'][0]['options']:
                suggestions.append(suggestion['text'])
            return suggestions
        
        except Exception as e:
            print(f"Suggestion error: {e}")
            return []
    
    def similar_content(self, doc_id: str, size: int = 5) -> List[dict]:
        """Find similar content using More Like This query"""
        mlt_body = {
            "query": {
                "more_like_this": {
                    "fields": ["title", "description", "tags", "search_keywords"],
                    "like": [{"_index": self.index_name, "_id": doc_id}],
                    "min_term_freq": 1,
                    "max_query_terms": 12,
                    "min_doc_freq": 1
                }
            },
            "size": size,
            "_source": {
                "excludes": ["content"]
            }
        }
        
        try:
            result = self.elasticsearch.search(index=self.index_name, body=mlt_body)
            return self._format_search_results(result)['results']
        
        except Exception as e:
            print(f"Similar content error: {e}")
            return []
    
    def _format_search_results(self, raw_results: dict) -> dict:
        """Format Elasticsearch results for API response"""
        formatted = {
            "total": raw_results['hits']['total']['value'],
            "took": raw_results['took'],
            "results": [],
            "facets": {},
            "suggestions": []
        }
        
        # Format results
        for hit in raw_results['hits']['hits']:
            result = {
                "id": hit['_id'],
                "score": hit['_score'],
                "title": hit['_source']['title'],
                "description": hit['_source']['description'],
                "category": hit['_source']['category'],
                "content_type": hit['_source']['content_type'],
                "difficulty_level": hit['_source']['difficulty_level'],
                "tags": hit['_source']['tags'],
                "reading_time": hit['_source']['reading_time'],
                "url": f"/docs/{hit['_id']}",
                "highlights": hit.get('highlight', {})
            }
            formatted['results'].append(result)
        
        # Format facets
        if 'aggregations' in raw_results:
            for facet_name, facet_data in raw_results['aggregations'].items():
                formatted['facets'][facet_name] = [
                    {"value": bucket['key'], "count": bucket['doc_count']}
                    for bucket in facet_data['buckets']
                ]
        
        return formatted

def main():
    """Main function to build and test the knowledge base search system"""
    print("Initializing Knowledge Base Content Manager...")
    
    # Initialize content manager
    content_manager = ContentManager()
    
    # Build search index
    print("Building search index...")
    stats = content_manager.build_full_index()
    
    # Initialize search engine
    search_engine = SearchEngine()
    
    # Test search functionality
    print("\nTesting search functionality...")
    
    # Test basic search
    results = search_engine.search("VM creation")
    print(f"Search for 'VM creation': {results['total']} results")
    
    # Test filtered search
    results = search_engine.search(
        "security",
        filters={"category": ["security"], "difficulty_level": ["advanced"]}
    )
    print(f"Advanced security content: {results['total']} results")
    
    # Test suggestions
    suggestions = search_engine.suggest("VM")
    print(f"Suggestions for 'VM': {suggestions}")
    
    print("Knowledge base search system initialized successfully!")

if __name__ == "__main__":
    main()
```

### Web Interface Implementation

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Proxmox AI Knowledge Base</title>
    <link href="https://cdn.jsdelivr.net/npm/tailwindcss@2.2.19/dist/tailwind.min.css" rel="stylesheet">
    <script src="https://unpkg.com/alpinejs@3.x.x/dist/cdn.min.js" defer></script>
    <style>
        .search-highlight {
            background-color: #fef3c7;
            font-weight: 600;
        }
    </style>
</head>
<body class="bg-gray-50">
    <div x-data="knowledgeBase()" class="min-h-screen">
        <!-- Header -->
        <header class="bg-blue-600 text-white shadow-lg">
            <div class="max-w-7xl mx-auto px-4 py-6">
                <h1 class="text-3xl font-bold">Proxmox AI Knowledge Base</h1>
                <p class="text-blue-100 mt-2">Comprehensive documentation and troubleshooting guides</p>
            </div>
        </header>

        <!-- Search Section -->
        <div class="max-w-7xl mx-auto px-4 py-8">
            <div class="bg-white rounded-lg shadow-md p-6 mb-8">
                <!-- Search Input -->
                <div class="relative mb-4">
                    <input 
                        type="text" 
                        x-model="searchQuery"
                        @input="handleSearchInput"
                        @keydown.enter="performSearch"
                        placeholder="Search documentation, guides, and troubleshooting..."
                        class="w-full px-4 py-3 pl-12 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    >
                    <svg class="absolute left-4 top-3.5 h-5 w-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"></path>
                    </svg>
                </div>

                <!-- Search Suggestions -->
                <div x-show="suggestions.length > 0" class="mb-4">
                    <div class="bg-gray-100 rounded-lg p-3">
                        <p class="text-sm text-gray-600 mb-2">Suggestions:</p>
                        <div class="flex flex-wrap gap-2">
                            <template x-for="suggestion in suggestions" :key="suggestion">
                                <button 
                                    @click="searchQuery = suggestion; performSearch()"
                                    class="px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-sm hover:bg-blue-200 transition-colors"
                                    x-text="suggestion"
                                ></button>
                            </template>
                        </div>
                    </div>
                </div>

                <!-- Quick Filters -->
                <div class="flex flex-wrap gap-4 mb-4">
                    <div>
                        <label class="block text-sm font-medium text-gray-700 mb-1">Category</label>
                        <select x-model="filters.category" @change="performSearch" class="border border-gray-300 rounded-md px-3 py-2">
                            <option value="">All Categories</option>
                            <option value="api">API Reference</option>
                            <option value="security">Security</option>
                            <option value="troubleshooting">Troubleshooting</option>
                            <option value="training">Training</option>
                            <option value="architecture">Architecture</option>
                        </select>
                    </div>
                    <div>
                        <label class="block text-sm font-medium text-gray-700 mb-1">Content Type</label>
                        <select x-model="filters.content_type" @change="performSearch" class="border border-gray-300 rounded-md px-3 py-2">
                            <option value="">All Types</option>
                            <option value="documentation">Documentation</option>
                            <option value="tutorial">Tutorial</option>
                            <option value="troubleshooting">Troubleshooting</option>
                            <option value="api-reference">API Reference</option>
                        </select>
                    </div>
                    <div>
                        <label class="block text-sm font-medium text-gray-700 mb-1">Difficulty</label>
                        <select x-model="filters.difficulty_level" @change="performSearch" class="border border-gray-300 rounded-md px-3 py-2">
                            <option value="">All Levels</option>
                            <option value="beginner">Beginner</option>
                            <option value="intermediate">Intermediate</option>
                            <option value="advanced">Advanced</option>
                        </select>
                    </div>
                </div>

                <!-- Search Button -->
                <button 
                    @click="performSearch"
                    :disabled="!searchQuery.trim()"
                    class="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 disabled:bg-gray-400 transition-colors"
                >
                    Search
                </button>
            </div>

            <!-- Results Section -->
            <div class="grid grid-cols-1 lg:grid-cols-4 gap-6">
                <!-- Facets Sidebar -->
                <div class="lg:col-span-1">
                    <div x-show="Object.keys(facets).length > 0" class="bg-white rounded-lg shadow-md p-6">
                        <h3 class="text-lg font-semibold mb-4">Refine Results</h3>
                        
                        <!-- Category Facets -->
                        <div x-show="facets.categories && facets.categories.length > 0" class="mb-6">
                            <h4 class="font-medium text-gray-700 mb-2">Categories</h4>
                            <template x-for="facet in facets.categories" :key="facet.value">
                                <label class="flex items-center mb-2">
                                    <input 
                                        type="checkbox" 
                                        :value="facet.value"
                                        x-model="selectedFacets.categories"
                                        @change="applyFacetFilter"
                                        class="mr-2"
                                    >
                                    <span class="text-sm">
                                        <span x-text="facet.value"></span>
                                        <span class="text-gray-500">(<span x-text="facet.count"></span>)</span>
                                    </span>
                                </label>
                            </template>
                        </div>

                        <!-- Content Type Facets -->
                        <div x-show="facets.content_types && facets.content_types.length > 0" class="mb-6">
                            <h4 class="font-medium text-gray-700 mb-2">Content Types</h4>
                            <template x-for="facet in facets.content_types" :key="facet.value">
                                <label class="flex items-center mb-2">
                                    <input 
                                        type="checkbox" 
                                        :value="facet.value"
                                        x-model="selectedFacets.content_types"
                                        @change="applyFacetFilter"
                                        class="mr-2"
                                    >
                                    <span class="text-sm">
                                        <span x-text="facet.value"></span>
                                        <span class="text-gray-500">(<span x-text="facet.count"></span>)</span>
                                    </span>
                                </label>
                            </template>
                        </div>

                        <!-- Tags Facets -->
                        <div x-show="facets.tags && facets.tags.length > 0">
                            <h4 class="font-medium text-gray-700 mb-2">Tags</h4>
                            <template x-for="facet in facets.tags.slice(0, 10)" :key="facet.value">
                                <label class="flex items-center mb-2">
                                    <input 
                                        type="checkbox" 
                                        :value="facet.value"
                                        x-model="selectedFacets.tags"
                                        @change="applyFacetFilter"
                                        class="mr-2"
                                    >
                                    <span class="text-sm">
                                        <span x-text="facet.value"></span>
                                        <span class="text-gray-500">(<span x-text="facet.count"></span>)</span>
                                    </span>
                                </label>
                            </template>
                        </div>
                    </div>
                </div>

                <!-- Results Content -->
                <div class="lg:col-span-3">
                    <!-- Search Results Stats -->
                    <div x-show="searchResults.total > 0" class="mb-4">
                        <p class="text-gray-600">
                            <span x-text="searchResults.total"></span> results found
                            <span x-show="searchQuery" class="font-medium">
                                for "<span x-text="searchQuery"></span>"
                            </span>
                            <span x-show="searchResults.took" class="text-sm">
                                (<span x-text="searchResults.took"></span>ms)
                            </span>
                        </p>
                    </div>

                    <!-- Loading State -->
                    <div x-show="loading" class="text-center py-8">
                        <div class="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
                        <p class="mt-2 text-gray-600">Searching...</p>
                    </div>

                    <!-- No Results -->
                    <div x-show="!loading && searchResults.total === 0 && searchQuery" class="text-center py-8">
                        <svg class="mx-auto h-12 w-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.172 16.172a4 4 0 015.656 0M9 12h6m-6-4h6m2 5.291A7.962 7.962 0 0112 15c-4.418 0-8-3.582-8-8s3.582-8 8-8 8 3.582 8 8c0 2.152-.851 4.103-2.23 5.291z"></path>
                        </svg>
                        <p class="mt-4 text-gray-600">No results found for your search.</p>
                        <p class="text-sm text-gray-500 mt-2">Try adjusting your search terms or filters.</p>
                    </div>

                    <!-- Search Results -->
                    <div x-show="!loading && searchResults.results.length > 0" class="space-y-6">
                        <template x-for="result in searchResults.results" :key="result.id">
                            <div class="bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition-shadow">
                                <!-- Result Header -->
                                <div class="flex items-start justify-between mb-3">
                                    <div class="flex-1">
                                        <h3 class="text-lg font-semibold text-blue-600 hover:text-blue-800">
                                            <a :href="result.url" x-text="result.title"></a>
                                        </h3>
                                        <p class="text-gray-600 mt-1" x-text="result.description"></p>
                                    </div>
                                    <div class="ml-4 text-right">
                                        <span class="inline-block bg-blue-100 text-blue-800 text-xs px-2 py-1 rounded-full" x-text="result.category"></span>
                                    </div>
                                </div>

                                <!-- Result Metadata -->
                                <div class="flex items-center text-sm text-gray-500 mb-3">
                                    <span class="mr-4">
                                        Type: <span class="font-medium" x-text="result.content_type"></span>
                                    </span>
                                    <span class="mr-4">
                                        Level: <span class="font-medium" x-text="result.difficulty_level"></span>
                                    </span>
                                    <span>
                                        <svg class="inline h-4 w-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                                        </svg>
                                        <span x-text="result.reading_time"></span> min read
                                    </span>
                                </div>

                                <!-- Search Highlights -->
                                <div x-show="result.highlights && Object.keys(result.highlights).length > 0" class="mb-3">
                                    <template x-for="(highlights, field) in result.highlights" :key="field">
                                        <div class="mb-2">
                                            <template x-for="highlight in highlights" :key="highlight">
                                                <p class="text-sm text-gray-700" x-html="highlight"></p>
                                            </template>
                                        </div>
                                    </template>
                                </div>

                                <!-- Tags -->
                                <div x-show="result.tags && result.tags.length > 0" class="flex flex-wrap gap-2">
                                    <template x-for="tag in result.tags.slice(0, 5)" :key="tag">
                                        <span class="inline-block bg-gray-100 text-gray-700 text-xs px-2 py-1 rounded" x-text="tag"></span>
                                    </template>
                                </div>
                            </div>
                        </template>
                    </div>

                    <!-- Pagination -->
                    <div x-show="searchResults.total > 10" class="mt-8 flex justify-center">
                        <nav class="flex items-center space-x-2">
                            <button 
                                @click="previousPage"
                                :disabled="currentPage === 1"
                                class="px-3 py-2 border border-gray-300 rounded-md hover:bg-gray-50 disabled:bg-gray-100 disabled:text-gray-400"
                            >
                                Previous
                            </button>
                            
                            <template x-for="page in paginationPages" :key="page">
                                <button 
                                    @click="goToPage(page)"
                                    :class="page === currentPage ? 'bg-blue-600 text-white' : 'bg-white text-gray-700 hover:bg-gray-50'"
                                    class="px-3 py-2 border border-gray-300 rounded-md"
                                    x-text="page"
                                ></button>
                            </template>
                            
                            <button 
                                @click="nextPage"
                                :disabled="currentPage >= totalPages"
                                class="px-3 py-2 border border-gray-300 rounded-md hover:bg-gray-50 disabled:bg-gray-100 disabled:text-gray-400"
                            >
                                Next
                            </button>
                        </nav>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script>
        function knowledgeBase() {
            return {
                searchQuery: '',
                searchResults: { total: 0, results: [], took: 0 },
                suggestions: [],
                facets: {},
                selectedFacets: {
                    categories: [],
                    content_types: [],
                    tags: []
                },
                filters: {
                    category: '',
                    content_type: '',
                    difficulty_level: ''
                },
                loading: false,
                currentPage: 1,
                pageSize: 10,
                suggestionTimeout: null,

                get totalPages() {
                    return Math.ceil(this.searchResults.total / this.pageSize);
                },

                get paginationPages() {
                    const pages = [];
                    const start = Math.max(1, this.currentPage - 2);
                    const end = Math.min(this.totalPages, this.currentPage + 2);
                    
                    for (let i = start; i <= end; i++) {
                        pages.push(i);
                    }
                    return pages;
                },

                handleSearchInput() {
                    // Clear previous timeout
                    if (this.suggestionTimeout) {
                        clearTimeout(this.suggestionTimeout);
                    }

                    // Set timeout for suggestions
                    this.suggestionTimeout = setTimeout(() => {
                        if (this.searchQuery.length >= 2) {
                            this.getSuggestions();
                        } else {
                            this.suggestions = [];
                        }
                    }, 300);
                },

                async getSuggestions() {
                    try {
                        const response = await fetch(`/api/suggest?q=${encodeURIComponent(this.searchQuery)}`);
                        const data = await response.json();
                        this.suggestions = data.suggestions || [];
                    } catch (error) {
                        console.error('Error fetching suggestions:', error);
                        this.suggestions = [];
                    }
                },

                async performSearch() {
                    if (!this.searchQuery.trim()) return;

                    this.loading = true;
                    this.currentPage = 1;

                    try {
                        const params = new URLSearchParams({
                            q: this.searchQuery,
                            size: this.pageSize,
                            from: (this.currentPage - 1) * this.pageSize
                        });

                        // Add filters
                        Object.entries(this.filters).forEach(([key, value]) => {
                            if (value) {
                                params.append(`filter_${key}`, value);
                            }
                        });

                        // Add selected facets
                        Object.entries(this.selectedFacets).forEach(([key, values]) => {
                            if (values.length > 0) {
                                params.append(`facet_${key}`, values.join(','));
                            }
                        });

                        const response = await fetch(`/api/search?${params}`);
                        const data = await response.json();

                        if (data.error) {
                            throw new Error(data.error);
                        }

                        this.searchResults = data;
                        this.facets = data.facets || {};
                        this.suggestions = [];

                    } catch (error) {
                        console.error('Search error:', error);
                        this.searchResults = { total: 0, results: [], took: 0 };
                    } finally {
                        this.loading = false;
                    }
                },

                applyFacetFilter() {
                    this.performSearch();
                },

                goToPage(page) {
                    this.currentPage = page;
                    this.performSearch();
                },

                previousPage() {
                    if (this.currentPage > 1) {
                        this.currentPage--;
                        this.performSearch();
                    }
                },

                nextPage() {
                    if (this.currentPage < this.totalPages) {
                        this.currentPage++;
                        this.performSearch();
                    }
                }
            }
        }
    </script>
</body>
</html>
```

## CLI Search Integration

```bash
#!/bin/bash
# CLI Search Interface for Knowledge Base
# File: /scripts/knowledge-base/cli_search.sh

set -euo pipefail

# Configuration
SEARCH_API_URL="http://localhost:8000/api/search"
SUGGEST_API_URL="http://localhost:8000/api/suggest"
CACHE_DIR="$HOME/.proxmox-ai/search-cache"
CACHE_TTL=3600  # 1 hour

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
BOLD='\033[1m'
NC='\033[0m' # No Color

# Create cache directory
mkdir -p "$CACHE_DIR"

show_help() {
    cat << EOF
Proxmox AI Knowledge Base Search

Usage: $(basename "$0") [OPTIONS] <search_query>

Options:
    -c, --category CATEGORY     Filter by category
    -t, --type TYPE            Filter by content type
    -d, --difficulty LEVEL     Filter by difficulty level
    -n, --limit NUMBER         Limit number of results (default: 10)
    -f, --format FORMAT        Output format: text, json, table (default: text)
    -s, --suggest              Get search suggestions only
    -r, --related DOC_ID       Find related content
    -v, --verbose              Verbose output
    -h, --help                 Show this help

Examples:
    $(basename "$0") "VM creation"
    $(basename "$0") -c security -d advanced "firewall rules"
    $(basename "$0") -t tutorial -n 5 "backup"
    $(basename "$0") -s "vm"
    $(basename "$0") -r "api/vm-management.md"

Categories: api, security, troubleshooting, training, architecture
Content Types: documentation, tutorial, troubleshooting, api-reference
Difficulty Levels: beginner, intermediate, advanced
EOF
}

log_message() {
    if [[ "${VERBOSE:-false}" == "true" ]]; then
        echo -e "${BLUE}[$(date '+%H:%M:%S')]${NC} $1" >&2
    fi
}

error_message() {
    echo -e "${RED}Error:${NC} $1" >&2
}

success_message() {
    echo -e "${GREEN}✓${NC} $1" >&2
}

warning_message() {
    echo -e "${YELLOW}⚠${NC} $1" >&2
}

cache_key() {
    echo -n "$1" | sha256sum | cut -d' ' -f1
}

get_cached_result() {
    local key
    key=$(cache_key "$1")
    local cache_file="$CACHE_DIR/$key"
    
    if [[ -f "$cache_file" ]]; then
        local cache_age
        cache_age=$(($(date +%s) - $(stat -c %Y "$cache_file")))
        
        if [[ $cache_age -lt $CACHE_TTL ]]; then
            log_message "Using cached result for query"
            cat "$cache_file"
            return 0
        else
            log_message "Cache expired, removing cached result"
            rm -f "$cache_file"
        fi
    fi
    
    return 1
}

cache_result() {
    local key
    key=$(cache_key "$1")
    local cache_file="$CACHE_DIR/$key"
    
    log_message "Caching search result"
    cat > "$cache_file"
}

make_search_request() {
    local query="$1"
    local params="$2"
    
    log_message "Making search request: $query"
    
    # Try cached result first
    local cache_query="${query}|${params}"
    if get_cached_result "$cache_query"; then
        return 0
    fi
    
    # Make API request
    local url="${SEARCH_API_URL}?q=${query}"
    if [[ -n "$params" ]]; then
        url="${url}&${params}"
    fi
    
    log_message "Request URL: $url"
    
    if curl -s -f "$url" | tee >(cache_result "$cache_query"); then
        return 0
    else
        error_message "Search request failed"
        return 1
    fi
}

make_suggest_request() {
    local query="$1"
    
    log_message "Making suggestion request: $query"
    
    local url="${SUGGEST_API_URL}?q=${query}"
    
    if curl -s -f "$url"; then
        return 0
    else
        error_message "Suggestion request failed"
        return 1
    fi
}

format_text_output() {
    local json_data="$1"
    
    # Parse JSON and format for terminal output
    echo "$json_data" | jq -r '
        "Search Results: \(.total) found (took \(.took)ms)\n" +
        (if .results | length == 0 then
            "No results found for your search query."
        else
            (.results[] | 
                "─────────────────────────────────────────────────────────\n" +
                "📄 \(.title)\n" +
                "   \(.description)\n" +
                "   📂 \(.category) | 📝 \(.content_type) | 🎯 \(.difficulty_level) | ⏱ \(.reading_time) min\n" +
                "   🔗 \(.url)\n" +
                (if .tags | length > 0 then
                    "   🏷 Tags: \(.tags | join(", "))\n"
                else "" end) +
                (if .highlights.content then
                    "   💡 " + (.highlights.content | join("\n      ")) + "\n"
                else "" end)
            )
        end)'
}

format_table_output() {
    local json_data="$1"
    
    echo "$json_data" | jq -r '
        ["Title", "Category", "Type", "Level", "Time"] as $headers |
        ([$headers] + 
         (.results[] | [.title[0:40] + (if .title | length > 40 then "..." else "" end), 
                       .category, 
                       .content_type, 
                       .difficulty_level, 
                       (.reading_time | tostring) + "m"]) |
         @tsv)' | column -t -s $'\t'
}

format_json_output() {
    local json_data="$1"
    echo "$json_data" | jq '.'
}

format_suggestions() {
    local json_data="$1"
    
    echo -e "${BOLD}Suggestions:${NC}"
    echo "$json_data" | jq -r '.suggestions[]' | while read -r suggestion; do
        echo "  • $suggestion"
    done
}

search_knowledge_base() {
    local query="$1"
    local category="${2:-}"
    local content_type="${3:-}"
    local difficulty="${4:-}"
    local limit="${5:-10}"
    local format="${6:-text}"
    
    # Build query parameters
    local params=""
    [[ -n "$category" ]] && params="${params}&filter_category=${category}"
    [[ -n "$content_type" ]] && params="${params}&filter_content_type=${content_type}"
    [[ -n "$difficulty" ]] && params="${params}&filter_difficulty_level=${difficulty}"
    [[ -n "$limit" ]] && params="${params}&size=${limit}"
    
    # Remove leading &
    params="${params#&}"
    
    # Make search request
    local result
    if ! result=$(make_search_request "$query" "$params"); then
        return 1
    fi
    
    # Format output
    case "$format" in
        "json")
            format_json_output "$result"
            ;;
        "table")
            format_table_output "$result"
            ;;
        "text"|*)
            format_text_output "$result"
            ;;
    esac
}

get_suggestions() {
    local query="$1"
    
    local result
    if ! result=$(make_suggest_request "$query"); then
        return 1
    fi
    
    format_suggestions "$result"
}

find_related_content() {
    local doc_id="$1"
    local limit="${2:-5}"
    
    log_message "Finding related content for: $doc_id"
    
    local url="${SEARCH_API_URL}/similar?doc_id=${doc_id}&size=${limit}"
    
    local result
    if ! result=$(curl -s -f "$url"); then
        error_message "Failed to find related content"
        return 1
    fi
    
    echo -e "${BOLD}Related Content:${NC}"
    echo "$result" | jq -r '.results[] | 
        "📄 \(.title)\n" +
        "   \(.description)\n" +
        "   🔗 \(.url)\n"'
}

# Parse command line arguments
QUERY=""
CATEGORY=""
CONTENT_TYPE=""
DIFFICULTY=""
LIMIT="10"
FORMAT="text"
SUGGEST_ONLY=false
RELATED_DOC=""
VERBOSE=false

while [[ $# -gt 0 ]]; do
    case $1 in
        -c|--category)
            CATEGORY="$2"
            shift 2
            ;;
        -t|--type)
            CONTENT_TYPE="$2"
            shift 2
            ;;
        -d|--difficulty)
            DIFFICULTY="$2"
            shift 2
            ;;
        -n|--limit)
            LIMIT="$2"
            shift 2
            ;;
        -f|--format)
            FORMAT="$2"
            shift 2
            ;;
        -s|--suggest)
            SUGGEST_ONLY=true
            shift
            ;;
        -r|--related)
            RELATED_DOC="$2"
            shift 2
            ;;
        -v|--verbose)
            VERBOSE=true
            shift
            ;;
        -h|--help)
            show_help
            exit 0
            ;;
        -*)
            error_message "Unknown option: $1"
            show_help
            exit 1
            ;;
        *)
            if [[ -z "$QUERY" ]]; then
                QUERY="$1"
            else
                QUERY="$QUERY $1"
            fi
            shift
            ;;
    esac
done

# Validate inputs
if [[ -z "$QUERY" && -z "$RELATED_DOC" ]]; then
    error_message "Search query or document ID is required"
    show_help
    exit 1
fi

# Validate format
if [[ "$FORMAT" != "text" && "$FORMAT" != "json" && "$FORMAT" != "table" ]]; then
    error_message "Invalid format. Must be one of: text, json, table"
    exit 1
fi

# Main execution
main() {
    # Check if API is available
    if ! curl -s -f "${SEARCH_API_URL%/search}/health" > /dev/null; then
        error_message "Knowledge base API is not available"
        exit 1
    fi
    
    if [[ -n "$RELATED_DOC" ]]; then
        find_related_content "$RELATED_DOC" "$LIMIT"
    elif [[ "$SUGGEST_ONLY" == "true" ]]; then
        get_suggestions "$QUERY"
    else
        search_knowledge_base "$QUERY" "$CATEGORY" "$CONTENT_TYPE" "$DIFFICULTY" "$LIMIT" "$FORMAT"
    fi
}

# Export verbose setting for log_message function
export VERBOSE

# Run main function
main
```

This comprehensive knowledge base search system provides:

1. **Advanced Search Capabilities**: Full-text search with faceting, filtering, and auto-suggestions
2. **Content Management**: Automated content indexing with metadata extraction
3. **Web Interface**: Modern, responsive search interface with filters and pagination
4. **CLI Integration**: Command-line search tool with caching and multiple output formats
5. **AI-Enhanced Search**: Semantic search, content recommendations, and contextual assistance
6. **Performance Optimization**: Elasticsearch backend with caching and search optimization

The system automatically indexes all documentation files, extracts metadata, and provides multiple interfaces for accessing the knowledge base content.

---

**Classification**: Internal Use - Knowledge Base System
**Last Updated**: 2025-07-29
**Review Schedule**: Monthly
**Approved By**: Documentation Team Lead
**Document Version**: 1.0