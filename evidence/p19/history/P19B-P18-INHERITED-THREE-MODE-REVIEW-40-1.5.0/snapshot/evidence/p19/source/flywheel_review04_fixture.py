"""D-083 original QA-only continuous-improvement example, not P-19A input."""
from semantic_fixtures import finalize, n, e, annotation

def flywheel_fixture():
    steps = [
        ('receive', 'Ghi nhận nhu cầu', 'Tập hợp phản hồi mới'),
        ('assess', 'Đánh giá tác động', 'Đối chiếu các bằng chứng'),
        ('choose', 'Chốt ưu tiên', 'Người phụ trách phê duyệt'),
        ('deliver', 'Thử nghiệm cải tiến', 'Áp dụng trong phạm vi nhỏ'),
        ('observe', 'Kiểm tra hiệu quả', 'Ghi lại kết quả thực tế'),
        ('refine', 'Chuẩn hóa bài học', 'Điều chỉnh hướng dẫn'),
    ]
    memory = 'knowledge'
    nodes = [n(key, 'station', label, state='decision' if key=='choose' else 'normal') for key,label,_ in steps]
    nodes.append(n(memory, 'shared-state', 'Tri thức chung'))
    edges = [e('cycle-'+key, key, steps[(i+1)%len(steps)][0], 'cycle') for i,(key,_,_) in enumerate(steps)]
    annotations = [annotation('detail-'+key, detail, [key]) for key,_,detail in steps]
    annotations.append(annotation('detail-knowledge', 'Lưu vết qua mỗi vòng cải tiến', [memory]))
    # Directed contribution is explicit prose attached to both objects, not another
    # cycle edge. This uses the existing annotation schema without changing P-19A.
    annotations.extend(annotation('contribution-'+key, 'Góp vào Tri thức chung: '+detail, [key,memory]) for key,_,detail in steps)
    ir = finalize('loop-flywheel', nodes=nodes, edges=edges, annotations=annotations)
    ir['diagram']['title'] = 'Vòng cải tiến từ phản hồi'
    ir['accessibility'].update(name=ir['diagram']['title'], data_representation_required=True,
        description='Dữ liệu minh họa: sáu bước tạo một vòng theo chiều kim đồng hồ. Mỗi bước đóng góp vào Tri thức chung qua nhánh nét đứt; ô trung tâm không phải bước thứ bảy. Chốt ưu tiên là bước phê duyệt.')
    for item in ir['source_items']:
        item['locator'] = 'D-083:original-illustrative-flywheel:'+item['id']
    return ir
