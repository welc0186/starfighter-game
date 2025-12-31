from typing import Iterator, Tuple, Any
import esper

def get_components_with_subclasses(*component_types) -> Iterator[Tuple[int, Tuple[Any, ...]]]:
    """
    Get entities with components, including subclasses of the specified types.
    
    This function wraps esper.get_components() to support querying for
    component subclasses without modifying the esper module.
    
    Args:
        *component_types: Component classes to search for (including subclasses)
        
    Yields:
        Tuples of (entity_id, component_tuple) where components match the
        requested types or their subclasses
    """
    # Get all registered component types from esper's internal data
    # In esper 3.x, components are stored in _current_world._components
    world_data = esper._current_world
    
    # Build a set of all component types that match (including subclasses)
    matching_types = set()
    for registered_type in esper._components.keys():
        if any(issubclass(registered_type, comp_type) for comp_type in component_types):
            matching_types.add(registered_type)
    
    # For each entity, check if it has matching components
    seen_entities = set()
    for comp_type in matching_types:
        # Get entities that have this specific component type
        if comp_type in esper._components:
            for entity in esper._components[comp_type]:
                if entity not in seen_entities:
                    # Check if entity has all required component types (or subclasses)
                    entity_components = []
                    has_all = True
                    
                    for requested_type in component_types:
                        found = None
                        # Look for a component that is a subclass of requested_type
                        for ent_comp_type in esper._entities[entity]:
                            if issubclass(ent_comp_type, requested_type):
                                found = esper._entities[entity][ent_comp_type]
                                break
                        
                        if found is None:
                            has_all = False
                            break
                        entity_components.append(found)
                    
                    if has_all:
                        seen_entities.add(entity)
                        yield (entity, tuple(entity_components))


