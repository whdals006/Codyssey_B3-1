"""만료 시간이 가장 빠른 항목을 먼저 꺼내는 최소 힙."""

from typing import Any, List, Optional


class MinHeap:
    """리스트 기반 최소 힙. TTL 항목은 (expire_at, key) 튜플로 저장한다."""

    def __init__(self) -> None:
        self._items: List[Any] = []

    def push(self, item: Any) -> None:
        """항목을 추가하고 부모 방향으로 힙 속성을 복구한다."""
        self._items.append(item)
        self._heapify_up(len(self._items) - 1)

    def pop(self) -> Optional[Any]:
        """최솟값을 제거해 반환한다. 비어 있으면 None을 반환한다."""
        if not self._items:
            return None

        if len(self._items) == 1:
            return self._items.pop()

        smallest = self._items[0]

        self._items[0] = self._items.pop()
        self._heapify_down(0)

        return smallest

    def peek(self) -> Optional[Any]:
        """최솟값을 제거하지 않고 반환한다."""
        if not self._items:
            return None

        return self._items[0]

    def size(self) -> int:
        """힙에 저장된 항목 개수를 반환한다."""
        return len(self._items)

    def _heapify_up(self, index: int) -> None:
        """현재 항목이 부모보다 작으면 위로 이동한다."""
        while index > 0:
            parent = (index - 1) // 2

            if self._items[parent] <= self._items[index]:
                break

            self._items[parent], self._items[index] = (
                self._items[index],
                self._items[parent],
            )

            index = parent

    def _heapify_down(self, index: int) -> None:
        """현재 항목이 자식보다 크면 작은 자식 방향으로 이동한다."""
        length = len(self._items)

        while True:
            left = index * 2 + 1
            right = index * 2 + 2
            smallest = index

            if left < length and self._items[left] < self._items[smallest]:
                smallest = left

            if right < length and self._items[right] < self._items[smallest]:
                smallest = right

            if smallest == index:
                break

            self._items[index], self._items[smallest] = (
                self._items[smallest],
                self._items[index],
            )

            index = smallest