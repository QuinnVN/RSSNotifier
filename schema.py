from rss_parser.models.rss import RSS
from rss_parser.models import XMLBaseModel
from rss_parser.models.types import Tag


class DataSchema(RSS, XMLBaseModel):
    channel: None = None
    title: Tag[str]
    link: Tag[str]
    pubDate: Tag[str]
