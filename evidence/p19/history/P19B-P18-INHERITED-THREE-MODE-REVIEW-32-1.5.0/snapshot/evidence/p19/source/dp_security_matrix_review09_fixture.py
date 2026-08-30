"""Original D-089 five-by-five data-platform security matrix fixture."""
from semantic_fixtures import finalize, n


ROLES = (
    ("data-engineer", "Kỹ sư dữ liệu", "GRP-DATA-ENG"),
    ("data-scientist", "Nhà khoa học dữ liệu", "GRP-DATA-SCI"),
    ("analyst", "Chuyên viên phân tích", "GRP-ANALYST"),
    ("administrator", "Quản trị nền tảng", "GRP-PLATFORM-ADMIN"),
    ("external-partner", "Đối tác bên ngoài", "GRP-PARTNER"),
)

COMPONENTS = (
    ("object-storage", "Kho đối tượng", "S3"),
    ("query-engine", "Dịch vụ truy vấn", "SQL"),
    ("notebooks", "Notebook", "PY"),
    ("bi-workspace", "Không gian BI", "DASH"),
    ("orchestrator", "Bộ điều phối", "DAG"),
)

PERMISSIONS = (
    ("Write", "Read", "None", "Admin", "None"),
    ("Write", "Read", "Read", "Admin", "Read"),
    ("Write", "Write", "None", "Admin", "None"),
    ("Write", "Read", "Write", "Admin", "Read · Dashboard được chia sẻ"),
    ("Write", "Read", "None", "Admin", "None"),
)


def dp_security_matrix_fixture():
    cells = []
    for component_index, (component_id, component_name, component_code) in enumerate(COMPONENTS):
        component = f"{component_name} · {component_code}"
        for role_index, (role_id, role_name, role_code) in enumerate(ROLES):
            role = f"{role_name} · {role_code}"
            label = PERMISSIONS[component_index][role_index]
            permission = label.split(" · ", 1)[0]
            state = "deny" if permission == "None" else "allow"
            cells.append(n(
                f"cell-{role_id}-{component_id}",
                "permission-cell",
                label,
                secondary_label=f"{role}|{component}",
                state=state,
            ))
    ir = finalize("dp-security-matrix", nodes=cells)
    ir["diagram"].update({
        "title": "Ma trận quyền truy cập nền tảng dữ liệu",
        "detail": "faithful",
        "audience": "mixed",
    })
    ir["accessibility"].update({
        "name": "Ma trận quyền truy cập nền tảng dữ liệu theo vai trò và thành phần",
        "description": "Ma trận năm vai trò và năm thành phần hiển thị đầy đủ quyền Admin, Write, Read hoặc None; quyền Read của đối tác tại Không gian BI được giới hạn ở dashboard được chia sẻ.",
        "reading_order": [cell["id"] for cell in cells],
        "data_representation_required": True,
    })
    for item in ir["source_items"]:
        item["locator"] = item["locator"].replace("fixture:", "D-089-original-illustrative:")
    return ir
