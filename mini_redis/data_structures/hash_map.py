"""내장 dict 없이 체이닝으로 구현한 해시맵."""

from typing import Any, List, Optional

from mini_redis.data_structures.doubly_linked_list import (
    DoublyLinkedList,
    Node,
)


class HashEntry:
    """해시 버킷에 저장되는 키-값 항목."""

    __slots__ = ("key", "value")

    def __init__(self, key: str, value: Any) -> None:
        self.key = key
        self.value = value


class HashMap:
    """체이닝, 직접 작성한 해시 함수, 동적 리사이징을 제공한다."""

    def __init__(self, initial_capacity: int = 8) -> None:
        if initial_capacity < 1:
            raise ValueError("initial_capacity must be positive")

        self._buckets: List[DoublyLinkedList] = [
            DoublyLinkedList() for _ in range(initial_capacity)
        ]

        self._size = 0
        self._max_load_factor = 0.75

    def _hash(self, key: str) -> int:
        """문자 코드에 다항식 해싱을 적용해 현재 버킷 인덱스를 계산한다."""
        value = 0

        for character in key:
            value = (value * 31 + ord(character)) % len(self._buckets)

        return value

    def _find_node(
        self,
        bucket: DoublyLinkedList,
        key: str,
    ) -> Optional[Node]:
        """버킷의 연결 리스트를 순회하며 키에 해당하는 노드를 찾는다."""
        current = bucket.head

        while current is not None:
            if current.data.key == key:
                return current

            current = current.next

        return None

    def put(self, key: str, value: Any) -> Optional[Any]:
        """키를 저장한다. 덮어쓴 경우 이전 값을, 새 키면 None을 반환한다."""
        bucket = self._buckets[self._hash(key)]
        node = self._find_node(bucket, key)

        if node is not None:
            old_value = node.data.value
            node.data.value = value
            return old_value

        bucket.insert_back(HashEntry(key, value))
        self._size += 1

        # 로드 팩터가 0.75를 초과하면 버킷을 두 배로 늘린다.
        if self._size / len(self._buckets) > self._max_load_factor:
            self._resize(len(self._buckets) * 2)

        return None

    def get(self, key: str) -> Optional[Any]:
        """키에 대응하는 값을 반환한다. 키가 없으면 None을 반환한다."""
        bucket = self._buckets[self._hash(key)]
        node = self._find_node(bucket, key)

        if node is None:
            return None

        return node.data.value

    def remove(self, key: str) -> Optional[Any]:
        """키를 제거하고 기존 값을 반환한다. 키가 없으면 None을 반환한다."""
        bucket = self._buckets[self._hash(key)]
        node = self._find_node(bucket, key)

        if node is None:
            return None

        entry = bucket.remove_node(node)
        self._size -= 1

        return entry.value

    def contains(self, key: str) -> bool:
        """키가 존재하는지 반환한다."""
        bucket = self._buckets[self._hash(key)]

        return self._find_node(bucket, key) is not None

    def keys(self) -> List[str]:
        """현재 저장된 모든 키를 리스트로 반환한다."""
        result: List[str] = []

        for bucket in self._buckets:
            current = bucket.head

            while current is not None:
                result.append(current.data.key)
                current = current.next

        return result

    def size(self) -> int:
        """현재 저장된 키 개수를 반환한다."""
        return self._size

    def _resize(self, new_capacity: int) -> None:
        """버킷 수를 늘리고 모든 항목의 버킷 위치를 다시 계산한다."""
        old_buckets = self._buckets

        self._buckets = [
            DoublyLinkedList() for _ in range(new_capacity)
        ]

        for bucket in old_buckets:
            current = bucket.head

            while current is not None:
                entry = current.data

                # 변경된 버킷 수를 기준으로 해시 위치를 다시 계산한다.
                self._buckets[self._hash(entry.key)].insert_back(entry)

                current = current.next