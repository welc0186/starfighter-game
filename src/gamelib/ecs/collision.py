import esper
import pygame
from typing import Set, Callable, Optional

from gamelib.ecs.geometry import PositionComponent


class ColliderComponent:
    """Component for collision detection using pygame.Rect with filtering support.

    The rect automatically syncs with PositionComponent if present on the entity.

    Attributes:
        width: Width of the collider
        height: Height of the collider
        offset_x: X offset from PositionComponent (default 0)
        offset_y: Y offset from PositionComponent (default 0)
        tags: Set of tags for filtering (e.g., {'enemy', 'solid'})
        ignore_tags: Set of tags to ignore during collision detection
        on_collision: Optional callback function(entity, other_entity, tags)
        mask: Optional pygame.mask.Mask for pixel-perfect collision
        rect: pygame.Rect (automatically updated from PositionComponent)
    """

    def __init__(
        self,
        width: float,
        height: float,
        offset_x: int = 0,
        offset_y: int = 0,
        tags: Optional[Set[str]] = None,
        ignore_tags: Optional[Set[str]] = None,
        on_collision: Optional[Callable] = None,
        mask: Optional[pygame.mask.Mask] = None,
    ):
        self.width = width
        self.height = height
        self.offset_x = offset_x
        self.offset_y = offset_y
        self.tags = tags or set()
        self.ignore_tags = ignore_tags or set()
        self.on_collision = on_collision
        self.mask = mask
        self.rect = pygame.Rect(0, 0, width, height)

    @classmethod
    def from_surface(
        cls,
        surface: pygame.Surface,
        offset_x: int = 0,
        offset_y: int = 0,
        tags: Optional[Set[str]] = None,
        ignore_tags: Optional[Set[str]] = None,
        on_collision: Optional[Callable] = None,
        use_mask: bool = False,
    ):
        """Create ColliderComponent from pygame.Surface."""
        mask = pygame.mask.from_surface(surface) if use_mask else None
        return cls(
            surface.get_width(),
            surface.get_height(),
            offset_x,
            offset_y,
            tags,
            ignore_tags,
            on_collision,
            mask,
        )

    def update_from_position(self, position: PositionComponent):
        """Update rect position from PositionComponent."""
        self.rect.x = position.x + self.offset_x
        self.rect.y = position.y + self.offset_y

    def collides_with(
        self, other: "ColliderComponent", pixel_perfect: bool = False
    ) -> bool:
        """Check collision using pygame methods.

        Args:
            other: Other collider to check against
            pixel_perfect: Use mask collision if both colliders have masks
        """
        # First check rect collision (fast broad phase)
        if not self.rect.colliderect(other.rect):
            return False

        # If pixel-perfect requested and both have masks
        if pixel_perfect and self.mask and other.mask:
            offset = (other.rect.x - self.rect.x, other.rect.y - self.rect.y)
            return self.mask.overlap(other.mask, offset) is not None

        return True

    def should_collide_with(self, other: "ColliderComponent") -> bool:
        """Check if collision should occur based on tag filtering."""
        if self.ignore_tags & other.tags:
            return False
        if other.ignore_tags & self.tags:
            return False
        return True


class CollisionEvent:
    """Event triggered when a collision occurs."""

    def __init__(
        self,
        entity_a: int,
        entity_b: int,
        collider_a: ColliderComponent,
        collider_b: ColliderComponent,
        overlap_point: Optional[tuple] = None,
    ):
        self.entity_a = entity_a
        self.entity_b = entity_b
        self.collider_a = collider_a
        self.collider_b = collider_b
        self.overlap_point = overlap_point


class CollisionProcessor(esper.Processor):
    """System that processes collisions using pygame collision detection.

    Automatically syncs ColliderComponent rects with PositionComponent before
    checking collisions.

    Usage:
        world = esper.World()
        collision_processor = CollisionProcessor(pixel_perfect=False)
        world.add_processor(collision_processor)

        # Listen for collision events
        @collision_processor.on_collision
        def handle_collision(event):
            print(f"Collision between {event.entity_a} and {event.entity_b}")
    """

    def __init__(self, pixel_perfect: bool = False):
        super().__init__()
        self.collision_listeners = []
        self.pixel_perfect = pixel_perfect

    def on_collision(self, func: Callable):
        """Decorator to register collision event listeners."""
        self.collision_listeners.append(func)
        return func

    def add_listener(self, func: Callable):
        """Add a collision event listener."""
        self.collision_listeners.append(func)

    def process(self, dt):
        """Check for collisions between all entities with ColliderComponents."""
        # First, sync all collider rects with their PositionComponents
        for entity, (collider, position) in esper.get_components(
            ColliderComponent, PositionComponent
        ):
            collider.update_from_position(position)

        # Get all entities with colliders
        entities = esper.get_component(ColliderComponent)
        entity_list = list(entities)

        # Check all pairs of entities for collision
        for i in range(len(entity_list)):
            entity_a, collider_a = entity_list[i]

            for j in range(i + 1, len(entity_list)):
                entity_b, collider_b = entity_list[j]

                # Check if they should collide based on filters
                if not collider_a.should_collide_with(collider_b):
                    continue

                # Check collision using pygame methods
                if collider_a.collides_with(collider_b, self.pixel_perfect):
                    # Get overlap point if using masks
                    overlap_point = None
                    if self.pixel_perfect and collider_a.mask and collider_b.mask:
                        offset = (
                            collider_b.rect.x - collider_a.rect.x,
                            collider_b.rect.y - collider_a.rect.y,
                        )
                        overlap_point = collider_a.mask.overlap(collider_b.mask, offset)

                    event = CollisionEvent(
                        entity_a, entity_b, collider_a, collider_b, overlap_point
                    )

                    # Call component-specific callbacks
                    if collider_a.on_collision:
                        collider_a.on_collision(entity_a, entity_b, collider_b.tags)
                    if collider_b.on_collision:
                        collider_b.on_collision(entity_b, entity_a, collider_a.tags)

                    # Notify all registered listeners
                    for listener in self.collision_listeners:
                        listener(event)


class SpatialHashProcessor(esper.Processor):
    """Optimized collision processor using spatial hashing for better performance.

    Automatically syncs ColliderComponent rects with PositionComponent before
    checking collisions. More efficient for games with many entities.
    """

    def __init__(self, cell_size: int = 64, pixel_perfect: bool = False):
        super().__init__()
        self.collision_listeners = []
        self.pixel_perfect = pixel_perfect
        self.cell_size = cell_size

    def on_collision(self, func: Callable):
        """Decorator to register collision event listeners."""
        self.collision_listeners.append(func)
        return func

    def add_listener(self, func: Callable):
        """Add a collision event listener."""
        self.collision_listeners.append(func)

    def _get_cells(self, rect: pygame.Rect) -> Set[tuple]:
        """Get all grid cells that this rect occupies."""
        cells = set()
        left = rect.left // self.cell_size
        right = rect.right // self.cell_size
        top = rect.top // self.cell_size
        bottom = rect.bottom // self.cell_size

        for x in range(left, right + 1):
            for y in range(top, bottom + 1):
                cells.add((x, y))
        return cells

    def process(self):
        """Check for collisions using spatial hashing."""
        # First, sync all collider rects with their PositionComponents
        for entity, (collider, position) in esper.get_components(
            ColliderComponent, PositionComponent
        ):
            collider.update_from_position(position)

        # Build spatial hash
        spatial_hash = {}
        entities = list(esper.get_component(ColliderComponent))

        for entity, collider in entities:
            cells = self._get_cells(collider.rect)
            for cell in cells:
                if cell not in spatial_hash:
                    spatial_hash[cell] = []
                spatial_hash[cell].append((entity, collider))

        # Check collisions only within same cells
        checked_pairs = set()

        for cell, cell_entities in spatial_hash.items():
            for i in range(len(cell_entities)):
                entity_a, collider_a = cell_entities[i]

                for j in range(i + 1, len(cell_entities)):
                    entity_b, collider_b = cell_entities[j]

                    # Avoid checking same pair twice
                    pair = tuple(sorted([entity_a, entity_b]))
                    if pair in checked_pairs:
                        continue
                    checked_pairs.add(pair)

                    # Check filtering
                    if not collider_a.should_collide_with(collider_b):
                        continue

                    # Check collision
                    if collider_a.collides_with(collider_b, self.pixel_perfect):
                        overlap_point = None
                        if self.pixel_perfect and collider_a.mask and collider_b.mask:
                            offset = (
                                collider_b.rect.x - collider_a.rect.x,
                                collider_b.rect.y - collider_a.rect.y,
                            )
                            overlap_point = collider_a.mask.overlap(
                                collider_b.mask, offset
                            )

                        event = CollisionEvent(
                            entity_a, entity_b, collider_a, collider_b, overlap_point
                        )

                        # Call callbacks
                        if collider_a.on_collision:
                            collider_a.on_collision(entity_a, entity_b, collider_b.tags)
                        if collider_b.on_collision:
                            collider_b.on_collision(entity_b, entity_a, collider_a.tags)

                        # Notify listeners
                        for listener in self.collision_listeners:
                            listener(event)
