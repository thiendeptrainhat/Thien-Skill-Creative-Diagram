"""D-082 original illustrative data; QA only, not a frozen P-19A fixture."""
from semantic_fixtures import finalize, g, n

def gantt_fixture():
    schedule = [
        ('review-docs', 'Rà soát tài liệu', '2026-09-01', '2026-09-16', 'task'),
        ('interview-users', 'Phỏng vấn nhóm dùng', '2026-09-09', '2026-09-24', 'task'),
        ('design-structure', 'Thiết kế cấu trúc', '2026-09-24', '2026-10-09', 'task'),
        ('test-prototype', 'Thử nghiệm mẫu', '2026-10-01', '2026-10-17', 'task'),
        ('approve-direction', 'Chốt phương án', '2026-10-17', '2026-10-24', 'gate'),
        ('configure-portal', 'Cấu hình cổng tri thức', '2026-10-24', '2026-11-20', 'task'),
        ('internal-pilot', 'Chạy thử nội bộ', '2026-11-12', '2026-11-28', 'task'),
    ]
    ir = finalize('gantt', nodes=[n(key, 'task', label, state=state,
        start=start+'T00:00:00+07:00', end=end+'T00:00:00+07:00')
        for key, label, start, end, state in schedule], groups=[
        g('phase-discovery', 'KHỞI TẠO', ['review-docs', 'interview-users']),
        g('phase-design', 'THIẾT KẾ', ['design-structure', 'test-prototype', 'approve-direction']),
        g('phase-rollout', 'TRIỂN KHAI', ['configure-portal', 'internal-pilot']),
    ])
    ir['diagram']['title'] = 'Triển khai cổng tri thức nội bộ'
    ir['accessibility'].update(name=ir['diagram']['title'], data_representation_required=True,
        description='Dữ liệu minh họa: ba giai đoạn, sáu công việc và một cửa sổ duyệt (GATE), tháng 9–11/2026, UTC+07:00. Khoảng thời gian [bắt đầu, kết thúc), không tính thời điểm kết thúc. Không khai báo quan hệ phụ thuộc.')
    for item in ir['source_items']:
        item['locator'] = 'D-082:original-illustrative-schedule:'+item['id']
    return ir
