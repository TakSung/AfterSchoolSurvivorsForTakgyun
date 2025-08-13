from __future__ import annotations

import math


class Vector2:
    __slots__ = ('x', 'y')

    def __init__(self, x: float = 0.0, y: float = 0.0) -> None:
        self.x = float(x)
        self.y = float(y)

    def __repr__(self) -> str:
        return f'Vector2({self.x}, {self.y})'

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Vector2):
            return False
        return math.isclose(self.x, other.x) and math.isclose(self.y, other.y)

    def __add__(self, other: Vector2) -> Vector2:
        return Vector2(self.x + other.x, self.y + other.y)

    def __sub__(self, other: Vector2) -> Vector2:
        return Vector2(self.x - other.x, self.y - other.y)

    def __mul__(self, scalar: float | int) -> Vector2:
        return Vector2(self.x * scalar, self.y * scalar)

    def __rmul__(self, scalar: float | int) -> Vector2:
        return self.__mul__(scalar)

    def __truediv__(self, scalar: float | int) -> Vector2:
        if scalar == 0:
            raise ValueError('Cannot divide vector by zero')
        return Vector2(self.x / scalar, self.y / scalar)

    def __neg__(self) -> Vector2:
        return Vector2(-self.x, -self.y)

    def __hash__(self) -> int:
        return hash((self.x, self.y))

    @property
    def magnitude(self) -> float:
        return math.sqrt(self.x * self.x + self.y * self.y)

    @property
    def magnitude_squared(self) -> float:
        return self.x * self.x + self.y * self.y

    def distance_to(self, other: Vector2) -> float:
        return (self - other).magnitude

    def distance_squared_to(self, other: Vector2) -> float:
        return (self - other).magnitude_squared

    def normalize(self) -> Vector2:
        mag = self.magnitude
        if mag == 0:
            return Vector2(0, 0)
        return self / mag

    def normalized(self) -> Vector2:
        return self.normalize()

    def dot(self, other: Vector2) -> float:
        return self.x * other.x + self.y * other.y

    def cross(self, other: Vector2) -> float:
        return self.x * other.y - self.y * other.x

    def lerp(self, other: Vector2, t: float) -> Vector2:
        t = max(0.0, min(1.0, t))
        return self + (other - self) * t

    def rotate(self, angle_radians: float) -> Vector2:
        cos_angle = math.cos(angle_radians)
        sin_angle = math.sin(angle_radians)
        return Vector2(
            self.x * cos_angle - self.y * sin_angle,
            self.x * sin_angle + self.y * cos_angle,
        )

    def angle_to(self, other: Vector2) -> float:
        return math.atan2(other.y - self.y, other.x - self.x)

    def copy(self) -> Vector2:
        return Vector2(self.x, self.y)

    def to_tuple(self) -> tuple[float, float]:
        return (self.x, self.y)

    def int_tuple(self) -> tuple[int, int]:
        return (int(self.x), int(self.y))

    @classmethod
    def zero(cls) -> Vector2:
        return cls(0, 0)

    @classmethod
    def one(cls) -> Vector2:
        return cls(1, 1)

    @classmethod
    def up(cls) -> Vector2:
        return cls(0, -1)

    @classmethod
    def down(cls) -> Vector2:
        return cls(0, 1)

    @classmethod
    def left(cls) -> Vector2:
        return cls(-1, 0)

    @classmethod
    def right(cls) -> Vector2:
        return cls(1, 0)

    @classmethod
    def from_angle(
        cls, angle_radians: float, magnitude: float = 1.0
    ) -> Vector2:
        return cls(
            math.cos(angle_radians) * magnitude,
            math.sin(angle_radians) * magnitude,
        )

    @classmethod
    def from_tuple(cls, t: tuple[float, float]) -> Vector2:
        return cls(t[0], t[1])
