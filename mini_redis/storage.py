"""해시맵, 이중 연결 리스트, 최소 힙을 결합한 메모리 저장소."""

import time
from typing import List, Optional, Tuple

from mini_redis.data_structures.doubly_linked_list import (
    DoublyLinkedList,
    Node,
)
from mini_redis.data_structures.hash_map import HashMap
from mini_redis.data_structures.min_heap import MinHeap


class StoredEntry:
    """저장된 문자열 값과 메모리/TTL/LRU 메타데이터를 보관한다."""

    __slots__ = ("value", "size_bytes", "expire_at", "lru_node")

    def __init__(self, value: str, size_bytes: int) -> None:
        self.value = value
        self.size_bytes = size_bytes
        self.expire_at: Optional[float] = None
        self.lru_node: Optional[Node] = None


class MiniRedisStore:
    """키-값 데이터, LRU 제거, TTL 만료, 사용 메모리를 관리한다."""

    def __init__(self) -> None:
        self._data = HashMap()
        self._lru = DoublyLinkedList()
        self._expiry_heap = MinHeap()

        self.used_memory = 0
        self.maxmemory = 0
        self.evicted_keys = 0

    @staticmethod
    def _utf8_size(text: str) -> int:
        """문자열의 UTF-8 인코딩 바이트 수를 반환한다."""
        return len(text.encode("utf-8"))

    def _purge_expired(self, now: Optional[float] = None) -> None:
        """현재 시각까지 만료된 실제 키를 힙을 통해 제거한다."""
        if now is None:
            now = time.time()

        while True:
            item = self._expiry_heap.peek()

            if item is None or item[0] > now:
                break

            expire_at, key = self._expiry_heap.pop()
            entry = self._data.get(key)

            # 삭제되었거나 TTL이 재설정된 오래된 힙 항목은 무시한다.
            if entry is None or entry.expire_at != expire_at:
                continue

            self._remove_entry(key, evicted=False)

    def _remove_entry(self, key: str, evicted: bool) -> bool:
        """데이터, LRU 목록, 메모리 사용량을 한 번에 정리한다."""
        entry = self._data.remove(key)

        if entry is None:
            return False

        if entry.lru_node is not None:
            self._lru.remove_node(entry.lru_node)

        self.used_memory -= entry.size_bytes

        if evicted:
            self.evicted_keys += 1

        return True

    def set(self, key: str, value: str) -> bool:
        """키와 값을 저장한다. 메모리 제한으로 저장할 수 없으면 False다."""
        self._purge_expired()

        entry_size = self._utf8_size(key) + self._utf8_size(value)

        # 단일 항목만으로 제한을 넘으면 저장하지 않고 OOM 처리한다.
        if self.maxmemory > 0 and entry_size > self.maxmemory:
            return False

        existing = self._data.get(key)

        if existing is not None:
            self.used_memory -= existing.size_bytes

            existing.value = value
            existing.size_bytes = entry_size

            # SET으로 기존 값을 덮어쓰면 기존 TTL을 초기화한다.
            existing.expire_at = None

            self.used_memory += entry_size
            self._lru.move_to_front(existing.lru_node)

        else:
            new_entry = StoredEntry(value, entry_size)
            new_entry.lru_node = self._lru.insert_front(key)

            self._data.put(key, new_entry)
            self.used_memory += entry_size

        # 맨 앞은 최근 사용, 맨 뒤는 가장 오래 사용하지 않은 키다.
        while self.maxmemory > 0 and self.used_memory > self.maxmemory:
            oldest_node = self._lru.tail

            if oldest_node is None:
                break

            self._remove_entry(oldest_node.data, evicted=True)

        return True

    def get(self, key: str) -> Optional[str]:
        """값을 조회한다. 조회 성공 시 해당 키를 LRU 맨 앞으로 이동한다."""
        self._purge_expired()

        entry = self._data.get(key)

        if entry is None:
            return None

        self._lru.move_to_front(entry.lru_node)

        return entry.value

    def delete(self, key: str) -> bool:
        """키를 삭제한다. 존재하지 않거나 만료되었으면 False를 반환한다."""
        self._purge_expired()

        return self._remove_entry(key, evicted=False)

    def exists(self, key: str) -> bool:
        """만료 여부를 반영해 키 존재 여부를 반환한다."""
        self._purge_expired()

        return self._data.contains(key)

    def dbsize(self) -> int:
        """만료된 키를 정리한 뒤 현재 키 개수를 반환한다."""
        self._purge_expired()

        return self._data.size()

    def keys(self) -> List[str]:
        """만료된 키를 정리한 뒤 전체 키 목록을 반환한다."""
        self._purge_expired()

        return self._data.keys()

    def set_maxmemory(self, maxmemory: int) -> None:
        """최대 메모리 제한을 바이트 단위로 설정한다. 0은 무제한이다."""
        self.maxmemory = maxmemory

    def expire(self, key: str, seconds: int) -> bool:
        """키에 TTL을 설정한다. seconds가 0 이하이면 즉시 삭제한다."""
        self._purge_expired()

        entry = self._data.get(key)

        if entry is None:
            return False

        if seconds <= 0:
            self._remove_entry(key, evicted=False)
            return True

        expire_at = time.time() + seconds

        entry.expire_at = expire_at
        self._expiry_heap.push((expire_at, key))

        return True

    def ttl(self, key: str) -> int:
        """남은 TTL을 초 단위 정수로 반환한다. 없음은 -2, TTL 없음은 -1이다."""
        now = time.time()
        self._purge_expired(now)

        entry = self._data.get(key)

        if entry is None:
            return -2

        if entry.expire_at is None:
            return -1

        remaining = entry.expire_at - now

        if remaining <= 0:
            # 조회 직전에 만료 시각이 지난 경우도 없는 키로 처리한다.
            self._purge_expired(time.time())
            return -2

        return int(remaining)

    def info_memory(self) -> Tuple[int, int, int]:
        """(used_memory, maxmemory, evicted_keys)를 반환한다."""
        self._purge_expired()

        return self.used_memory, self.maxmemory, self.evicted_keys