"""Original D-090 article-domain ER data-model fixture."""
from semantic_fixtures import e, finalize, member, n


def _field(item_id, name, data_type, *constraints):
    return member(item_id, "attribute", name, data_type=data_type, constraints=list(constraints))


def er_data_model_fixture():
    entities = [
        n("entity-author", "entity", "Author", members=[
            _field("field-author-id", "id", "uuid", "primary-key"),
            _field("field-author-handle", "handle", "text", "unique"),
            _field("field-author-name", "display_name", "text"),
            _field("field-author-bio", "bio", "text"),
            _field("field-author-profile", "profile_url", "text · url"),
        ]),
        n("entity-article", "entity", "Article", members=[
            _field("field-article-id", "id", "uuid", "primary-key"),
            _field("field-article-title", "title", "text"),
            _field("field-article-slug", "slug", "text · unique", "unique"),
            _field("field-article-body", "body_mdx", "text"),
            _field("field-article-published", "published_at", "timestamp"),
            _field("field-article-author", "author_id", "uuid", "foreign-key"),
            _field("field-article-status", "status", "enum"),
            _field("field-article-cover", "cover_url", "text · url"),
        ]),
        n("entity-tag", "entity", "Tag", members=[
            _field("field-tag-id", "id", "uuid", "primary-key"),
            _field("field-tag-slug", "slug", "text · unique", "unique"),
            _field("field-tag-name", "name", "text"),
            _field("field-tag-description", "description", "text"),
        ]),
        n("entity-article-tag", "associative-entity", "ArticleTag", members=[
            _field("field-article-tag-article", "article_id", "uuid", "foreign-key"),
            _field("field-article-tag-tag", "tag_id", "uuid", "foreign-key"),
        ]),
    ]
    relationships = [
        e("relation-author-writes-article", "entity-author", "entity-article", "one-to-many", source_multiplicity="1", target_multiplicity="N"),
        e("relation-article-tagged-via", "entity-article", "entity-article-tag", "one-to-many", source_multiplicity="1", target_multiplicity="N"),
        e("relation-tag-used-by", "entity-tag", "entity-article-tag", "one-to-many", source_multiplicity="1", target_multiplicity="N"),
    ]
    ir = finalize("er-data-model", nodes=entities, edges=relationships)
    ir["diagram"].update({
        "title": "Mô hình dữ liệu nội dung",
        "detail": "faithful",
        "audience": "mixed",
    })
    ir["accessibility"].update({
        "name": "Mô hình dữ liệu Author, Article, Tag và ArticleTag",
        "description": "Bốn entity với mười chín trường dữ liệu; Article là aggregate root, ArticleTag là associative entity, và ba quan hệ một-nhiều hiển thị cardinality tại từng đầu nối.",
        "reading_order": [
            "entity-author", "field-author-id", "field-author-handle", "field-author-name", "field-author-bio", "field-author-profile",
            "entity-article", "field-article-id", "field-article-title", "field-article-slug", "field-article-body", "field-article-published", "field-article-author", "field-article-status", "field-article-cover",
            "entity-tag", "field-tag-id", "field-tag-slug", "field-tag-name", "field-tag-description",
            "entity-article-tag", "field-article-tag-article", "field-article-tag-tag",
            "relation-author-writes-article", "relation-article-tagged-via", "relation-tag-used-by",
        ],
    })
    for item in ir["source_items"]:
        item["locator"] = item["locator"].replace("fixture:", "D-090-original-illustrative:")
    return ir
