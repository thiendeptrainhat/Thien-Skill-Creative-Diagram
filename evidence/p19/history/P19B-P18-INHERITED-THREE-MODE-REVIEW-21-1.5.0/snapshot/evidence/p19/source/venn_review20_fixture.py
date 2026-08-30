"""Original D-100 three-set product-balance Venn fixture."""
from semantic_fixtures import finalize, g, n


SETS = (
    ("set-desirable", "Đáng mong muốn", "Người dùng cần", "member-desirable"),
    ("set-feasible", "Khả thi", "Đội ngũ xây được", "member-feasible"),
    ("set-viable", "Bền vững", "Mô hình duy trì được", "member-viable"),
)
CORE_MEMBER = "member-ready"


def venn_fixture():
    nodes = [
        n("member-desirable", "exclusive-member", "Người dùng cần"),
        n("member-feasible", "exclusive-member", "Đội ngũ xây được"),
        n("member-viable", "exclusive-member", "Mô hình duy trì được"),
        n(CORE_MEMBER, "triple-intersection", "Sẵn sàng triển khai"),
    ]
    groups = [
        g(set_id, label, [member_id, CORE_MEMBER])
        for set_id, label, _subtitle, member_id in SETS
    ]
    ir = finalize("venn", nodes=nodes, groups=groups)
    ir["diagram"].update({
        "title": "Điểm cân bằng để triển khai",
        "detail": "faithful",
        "audience": "mixed",
    })
    ir["accessibility"].update({
        "name": "Ba điều kiện để sẵn sàng triển khai",
        "description": (
            "Ba tập Đáng mong muốn, Khả thi và Bền vững giao nhau tại vùng "
            "Sẵn sàng triển khai; mỗi tập có một tiêu chí riêng và cùng chứa tiêu chí trung tâm."
        ),
        "reading_order": [
            "set-desirable", "set-feasible", "set-viable",
            "member-desirable", "member-feasible", "member-viable", CORE_MEMBER,
        ],
    })
    for item in ir["source_items"]:
        item["locator"] = item["locator"].replace("fixture:", "D-100-original-illustrative:")
    return ir
