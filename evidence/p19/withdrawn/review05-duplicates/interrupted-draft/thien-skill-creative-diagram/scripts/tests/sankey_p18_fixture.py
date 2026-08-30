"""Gallery-only approved Sankey source; the historical minimal fixture is unchanged."""
from semantic_fixtures import finalize
from sankey_p18_v15 import approved_material

def sankey_fixture():
    material=approved_material()
    ir=finalize('sankey',nodes=material['nodes'],edges=material['edges'])
    ir['diagram']['title']=material['title']
    ir['accessibility'].update(name=material['title'],description=material['description'],data_representation_required=True)
    for item in ir['source_items']:
        item['locator']='D-084:P18R6-review17-Sankey:'+item['id']
    return ir
