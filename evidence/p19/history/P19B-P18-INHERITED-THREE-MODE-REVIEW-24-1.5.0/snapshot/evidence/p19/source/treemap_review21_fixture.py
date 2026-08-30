"""Original D-101 continent-share Treemap fixture derived from owner reference data."""
from semantic_fixtures import finalize, g, n


CONTINENTS = (
    ("continent-asia", "Châu Á", 4780),
    ("continent-africa", "Châu Phi", 1480),
    ("continent-europe", "Châu Âu", 750),
    ("continent-north-america", "Bắc Mỹ", 610),
    ("continent-south-america", "Nam Mỹ", 430),
    ("continent-oceania", "Châu Đại Dương", 50),
)
TOTAL = sum(value for _item_id, _label, value in CONTINENTS)


def treemap_fixture():
    leaf_ids = [item_id for item_id, _label, _value in CONTINENTS]
    nodes = [
        n(item_id, "continent", label, value=value, unit="triệu người", parent_group_id="group-world")
        for item_id, label, value in CONTINENTS
    ]
    groups = [
        g("group-root", "Dân số thế giới", ["group-world"], parent_group_id=None, declared_total=TOTAL, unit="triệu người"),
        g("group-world", "Các châu lục", leaf_ids, parent_group_id="group-root", declared_total=TOTAL, unit="triệu người"),
    ]
    ir = finalize("treemap", nodes=nodes, groups=groups)
    ir["diagram"].update({
        "title": "Tỷ trọng dân số theo châu lục",
        "detail": "faithful",
        "audience": "mixed",
    })
    ir["accessibility"].update({
        "name": "Treemap tỷ trọng dân số theo châu lục",
        "description": (
            "Diện tích của sáu ô tỷ lệ trực tiếp với dân số làm tròn trong ảnh tham chiếu; "
            "Châu Á là phần lớn nhất và được đánh dấu làm tiêu điểm, Châu Đại Dương quá nhỏ để đặt nhãn đầy đủ trong ô."
        ),
        "reading_order": ["group-root", "group-world", *leaf_ids],
    })
    for item in ir["source_items"]:
        item["locator"] = item["locator"].replace("fixture:", "D-101-owner-reference-illustrative:")
    return ir
