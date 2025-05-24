"""
Data models for HotCRP submissions
"""

from dataclasses import dataclass
from typing import List, Dict, Optional, Any
from jinja2 import Template
import html
import re


def strip_html_tags(text: str) -> str:
    """Strip HTML tags from text and convert HTML entities to their corresponding characters."""
    if not text:
        return ""
    # First convert HTML entities
    text = html.unescape(text)
    # Then remove HTML tags
    text = re.sub(r'<[^>]+>', '', text)
    # Replace <br> with newlines
    text = text.replace('<br>', '\n')
    return text.strip()


@dataclass
class Author:
    email: str = ""
    first: str = ""
    last: str = ""
    affiliation: str = ""
    contact: bool = False


@dataclass
class Tag:
    tag: str = ""
    value: int = 0


@dataclass
class Talk:
    object: str = ""
    pid: int = 0
    title: str = ""
    authors: List[Author] = None
    track_intent: str = ""
    proposal_length: str = ""
    long_description_program_committee: str = ""
    session_outline: str = ""
    audience_take_aways: str = ""
    would_like_help_rehearsing_your_talk: str = ""
    region_will_coming_from_order_present: str = ""
    pc_conflicts: Dict[str, str] = None
    status: str = ""
    submitted: bool = False
    submitted_at: int = 0
    modified_at: int = 0
    tags: List[Tag] = None
    other_notes_program_committee_chairs: Optional[str] = None
    any_other_comments_regarding_factors_would_affect_your_presentation_plans: Optional[str] = None

    def __post_init__(self):
        if self.authors is None:
            self.authors = []
        if self.pc_conflicts is None:
            self.pc_conflicts = {}
        if self.tags is None:
            self.tags = []

    @classmethod
    def from_record(cls, record: Dict[str, Any]) -> 'Talk':
        """Create a Talk instance from a HotCRP JSON record."""
        # Convert authors to Author objects
        authors = [
            Author(
                email=a.get('email', ''),
                first=a.get('first', ''),
                last=a.get('last', ''),
                affiliation=a.get('affiliation', ''),
                contact=a.get('contact', False)
            ) for a in record.get('authors', [])
        ]
        
        # Convert tags to Tag objects
        tags = [
            Tag(
                tag=t.get('tag', ''),
                value=t.get('value', 0)
            ) for t in record.get('tags', [])
        ]
        
        # Create Talk instance with all fields
        return cls(
            object=record.get('object', ''),
            pid=record.get('pid', 0),
            title=record.get('title', ''),
            authors=authors,
            track_intent=record.get('track_intent', ''),
            proposal_length=record.get('proposal_length', ''),
            long_description_program_committee=record.get('long_description_program_committee', ''),
            session_outline=record.get('session_outline', ''),
            audience_take_aways=record.get('audience_take_aways', ''),
            would_like_help_rehearsing_your_talk=record.get('would_like_help_rehearsing_your_talk?', ''),
            region_will_coming_from_order_present=record.get('region_will_coming_from_order_present?', ''),
            pc_conflicts=record.get('pc_conflicts', {}),
            status=record.get('status', ''),
            submitted=record.get('submitted', False),
            submitted_at=record.get('submitted_at', 0),
            modified_at=record.get('modified_at', 0),
            tags=tags,
            other_notes_program_committee_chairs=record.get('other_notes_program_committee_chairs'),
            any_other_comments_regarding_factors_would_affect_your_presentation_plans=record.get('any_other_comments_regarding_factors_would_affect_your_presentation_plans')
        )

    def render_markdown(self, include_authors=True) -> str:
        """Render the talk as markdown text using Jinja2 templating."""
        template = Template("""# #{{ pid }} {{ title }}

{% if include_authors %}
## Speakers
{% for author in authors %}
* {{ author.first }} {{ author.last }}{% if author.affiliation %} ({{ author.affiliation }}){% endif %}
{% endfor %}
{% endif %}

{% if proposal_length %}
## Duration
*{{ proposal_length }}*
{% endif %}

{% if tags %}
## Tags
{% for tag in tags %}`{{ tag.tag }}`{% if not loop.last %}, {% endif %}{% endfor %}
{% endif %}

{% if long_description_program_committee %}
## Description
{{ long_description_program_committee }}
{% endif %}

{% if session_outline %}
## Session Outline
{{ session_outline }}
{% endif %}

{% if audience_take_aways %}
## Audience Take-aways
{{ audience_take_aways }}
{% endif %}

{% if other_notes_program_committee_chairs %}
## Program Committee Notes
{{ other_notes_program_committee_chairs }}
{% endif %}

---

""")
        # Prepare the data for the template, stripping HTML from text fields
        data = {
            'pid': self.pid,
            'title': strip_html_tags(self.title),
            'authors': self.authors,
            'proposal_length': strip_html_tags(self.proposal_length),
            'long_description_program_committee': strip_html_tags(self.long_description_program_committee),
            'session_outline': strip_html_tags(self.session_outline),
            'audience_take_aways': strip_html_tags(self.audience_take_aways),
            'other_notes_program_committee_chairs': strip_html_tags(self.other_notes_program_committee_chairs),
            'tags': self.tags,
            'include_authors': include_authors
        }
        
        return template.render(**data).strip() 