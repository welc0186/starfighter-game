from dataclasses import dataclass, field
from typing import List
from esper import Processor
import esper
import time


@dataclass
class ModifierContainer:
    """Component that holds all active modifiers for an entity"""

    modifiers: List["Modifier"] = field(default_factory=list)


class Modifier:
    """Base class for all modifiers (buffs/debuffs)"""

    def __init__(
        self, name: str, duration: float, stackable: bool = False, max_stacks: int = 1
    ):
        """
        Args:
            name: Display name of the modifier
            duration: Duration in seconds (-1 for permanent)
            stackable: Whether this modifier can stack
            max_stacks: Maximum number of stacks allowed
        """
        self.name = name
        self.duration = duration
        self.time_remaining = duration
        self.stackable = stackable
        self.max_stacks = max_stacks
        self.current_stacks = 1

    def on_apply(self, entity: int) -> None:
        """Called when modifier is first applied to an entity"""
        pass

    def on_update(self, entity: int, dt: float) -> bool:
        """
        Called every frame while modifier is active

        Args:
            entity: The entity ID
            dt: Delta time in seconds

        Returns:
            True to keep modifier active, False to remove it
        """
        if self.duration > 0:
            self.time_remaining -= dt
            return self.time_remaining > 0
        return True  # Permanent modifiers

    def on_remove(self, entity: int) -> None:
        """Called when modifier is removed from an entity"""
        pass

    def on_stack(self, entity: int) -> bool:
        """
        Called when trying to stack this modifier

        Returns:
            True if stacking succeeded, False otherwise
        """
        if self.stackable and self.current_stacks < self.max_stacks:
            self.current_stacks += 1
            return True
        return False


# ===== PROCESSOR =====


class ModifierProcessor(Processor):
    """Processes all active modifiers on entities"""

    def process(self, dt) -> None:
        for ent, container in esper.get_component(ModifierContainer):
            # Update all modifiers and filter out expired ones
            active_modifiers = []

            for modifier in container.modifiers:
                should_keep = modifier.on_update(ent, dt)

                if should_keep:
                    active_modifiers.append(modifier)
                else:
                    # Modifier expired
                    modifier.on_remove(ent)
                    print(f"[Entity {ent}] {modifier.name} expired")

            container.modifiers = active_modifiers


# ===== HELPER FUNCTIONS =====


def add_modifier(entity: int, modifier: Modifier) -> None:
    """
    Add a modifier to an entity

    Args:
        entity: The entity ID
        modifier: The modifier instance to add
    """
    # Ensure entity has ModifierContainer
    if not esper.has_component(entity, ModifierContainer):
        esper.add_component(entity, ModifierContainer())

    container = esper.component_for_entity(entity, ModifierContainer)

    # Check if modifier already exists and is stackable
    existing = next((m for m in container.modifiers if m.name == modifier.name), None)

    if existing:
        if existing.on_stack(entity):
            print(
                f"[Entity {entity}] {modifier.name} stacked ({existing.current_stacks}x)"
            )
            return
        else:
            # Refresh duration instead
            existing.time_remaining = existing.duration
            print(f"[Entity {entity}] {modifier.name} duration refreshed")
            return

    # Add new modifier
    container.modifiers.append(modifier)
    modifier.on_apply(entity)
    print(f"[Entity {entity}] {modifier.name} applied")


def remove_modifier(entity: int, modifier_name: str) -> None:
    """
    Remove a modifier from an entity by name

    Args:
        entity: The entity ID
        modifier_name: Name of the modifier to remove
    """
    if not esper.has_component(entity, ModifierContainer):
        return

    container = esper.component_for_entity(entity, ModifierContainer)

    for i, modifier in enumerate(container.modifiers):
        if modifier.name == modifier_name:
            modifier.on_remove(entity)
            container.modifiers.pop(i)
            print(f"[Entity {entity}] {modifier_name} removed")
            break


def get_active_modifiers(entity: int) -> List[dict]:
    """
    Get list of active modifiers on an entity

    Returns:
        List of dicts with modifier info (name, time_remaining, stacks)
    """
    if not esper.has_component(entity, ModifierContainer):
        return []

    container = esper.component_for_entity(entity, ModifierContainer)
    return [
        {"name": m.name, "time_remaining": m.time_remaining, "stacks": m.current_stacks}
        for m in container.modifiers
    ]
