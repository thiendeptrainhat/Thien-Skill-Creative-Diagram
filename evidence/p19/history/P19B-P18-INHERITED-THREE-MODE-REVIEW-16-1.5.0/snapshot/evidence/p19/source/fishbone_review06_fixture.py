"""D-086 original QA-only detailed Fishbone example, not P-19A input."""
from semantic_fixtures import finalize, n, e, g


def fishbone_fixture():
    categories = [
        ('people', 'Con người', [('handover', 'Bàn giao ca thiếu ngữ cảnh'), ('assignment', 'Chậm phân công người xử lý')]),
        ('process', 'Quy trình', [('intake-check', 'Bỏ qua bước kiểm tra đầu vào'), ('review-sla', 'SLA rà soát chưa rõ trách nhiệm')]),
        ('technology', 'Công nghệ', [('alert-delay', 'Cảnh báo được tổng hợp quá trễ'), ('retry-queue', 'Hàng đợi retry bị nghẽn')]),
        ('data', 'Dữ liệu', [('required-field', 'Thiếu trường dữ liệu bắt buộc'), ('status-map', 'Mapping trạng thái không nhất quán')]),
        ('monitoring', 'Giám sát', [('sample-window', 'Dashboard lấy mẫu mỗi 15 phút'), ('duration-alert', 'Chưa có cảnh báo thời gian xử lý')]),
    ]
    effect_id = 'effect-delay'
    nodes, edges, groups = [], [], []
    for category_id, label, causes in categories:
        member_ids = []
        for cause_id, cause_label in causes:
            key = f'cause-{cause_id}'
            member_ids.append(key)
            nodes.append(n(key, 'cause', cause_label))
            edges.append(e(f'relation-{cause_id}', key, effect_id, 'cause'))
        groups.append(g(f'category-{category_id}', label, member_ids, cause_category=label))
    nodes.append(n(effect_id, 'effect', 'Hồ sơ xử lý trễ'))
    ir = finalize('fishbone', nodes=nodes, edges=edges, groups=groups)
    ir['diagram']['title'] = 'Phân tích nguyên nhân hồ sơ xử lý trễ'
    ir['accessibility'].update(
        name=ir['diagram']['title'], data_representation_required=True,
        description='Dữ liệu minh họa: năm nhóm nguyên nhân, mỗi nhóm có hai nguyên nhân chi tiết, cùng hội tụ vào hệ quả Hồ sơ xử lý trễ. Sơ đồ tổ chức giả thuyết phân tích, không chứng minh quan hệ nhân quả.')
    for item in ir['source_items']:
        item['locator'] = 'D-086:original-illustrative-fishbone:' + item['id']
    return ir

