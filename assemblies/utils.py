from typing import Iterable, Dict, List

from assemblies.assembly_fun import Projectable, Assembly
from brain import Brain, Area, Stimulus


def fire_many(brain: Brain, projectables: Iterable[Projectable], area: Area):
    """
    params:
    -the relevant brain object, as project is dependent on the brain instance.
    -a list of object which are projectable (Stimuli, Areas...) which will be projected
    -the target area's name.

    This function works by creating a "Parent tree", (Which is actually a directed acyclic graph) first,
    and then by going from the top layer, which will consist of stimuli, and traversing down the tree
    while firing each layer to areas its relevant descendant inhibit.

    For example, "firing" an assembly, we will first climb up its parent tree (Assemblies of course may have
    multiple parents, such as results of merge. Then we iterate over the resulting list in reverse, while firing
    each layer to the relevant areas, which are saved in a dictionary format:
    The thing we will project: areas to project it to
    """

    # TODO: Add inline documentation
    layers: List[Dict[Projectable, List[Area]]] = [{projectable: [area] for projectable in projectables}]
    while any(isinstance(projectable, Assembly) for projectable in layers[-1]):
        prev_layer: Iterable[Assembly] = (ass for ass in layers[-1].keys() if not isinstance(ass, Stimulus))
        current_layer: Dict[Projectable, List[Area]] = {}
        for ass in prev_layer:
            for parent in ass.parents:
                current_layer[parent] = current_layer.get(ass, []) + [ass.area]

        layers.append(current_layer)

    layers = layers[::-1]
    for layer in layers:
        stimuli_mappings: Dict[Stimulus, List[Area]] = {stim: areas
                                                        for stim, areas in
                                                        layer.items() if isinstance(stim, Stimulus)}

        assembly_mapping: Dict[Area, List[Area]] = {}
        for ass, areas in filter(lambda t: (lambda assembly, _: isinstance(assembly, Assembly))(*t), layer.items()):
            assembly_mapping[ass.area] = assembly_mapping.get(ass.area, []) + areas

        mapping = {**stimuli_mappings, **assembly_mapping}
        brain.next_round(mapping)
