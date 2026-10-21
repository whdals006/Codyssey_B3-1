"""O(1) 삽입, 삭제, 이동 연산을 제공하는 이중 연결 리스트."""

from typing import Any, Iterator, Optional


class Node:
    """이중 연결 리스트의 노드. 앞/뒤 노드와 데이터를 보관한다."""

    __slots__ = ("prev", "next", "data")

    def __init__(self, data: Any) -> None:
        self.prev: Optional[Node] = None
        self.next: Optional[Node] = None
        self.data = data


class DoublyLinkedList:
    """양방향 포인터를 사용해 노드 삽입과 삭제를 O(1)에 수행한다."""

    def __init__(self) -> None:
        self.head: Optional[Node] = None
        self.tail: Optional[Node] = None
        self._size = 0

    def insert_front(self, data: Any) -> Node:
        """데이터를 맨 앞에 삽입하고 새 노드를 반환한다."""
        node = Node(data)

        if self.head is None:
            self.head = self.tail = node
        else:
            node.next = self.head
            self.head.prev = node
            self.head = node

        self._size += 1
        return node

    def insert_back(self, data: Any) -> Node:
        """데이터를 맨 뒤에 삽입하고 새 노드를 반환한다."""
        node = Node(data)

        if self.tail is None:
            self.head = self.tail = node
        else:
            node.prev = self.tail
            self.tail.next = node
            self.tail = node

        self._size += 1
        return node

    def remove_front(self) -> Any:
        """맨 앞 데이터를 제거해 반환한다. 비어 있으면 None을 반환한다."""
        if self.head is None:
            return None

        return self.remove_node(self.head)

    def remove_back(self) -> Any:
        """맨 뒤 데이터를 제거해 반환한다. 비어 있으면 None을 반환한다."""
        if self.tail is None:
            return None

        return self.remove_node(self.tail)

    def remove_node(self, node: Node) -> Any:
        """리스트에 속한 특정 노드를 O(1)에 제거하고 데이터를 반환한다."""
        if node.prev is None:
            self.head = node.next
        else:
            node.prev.next = node.next

        if node.next is None:
            self.tail = node.prev
        else:
            node.next.prev = node.prev

        data = node.data

        # 제거한 노드가 다른 노드를 계속 참조하지 않도록 정리한다.
        node.prev = None
        node.next = None

        self._size -= 1
        return data

    def move_to_front(self, node: Optional[Node]) -> None:
        """기존 노드를 맨 앞으로 이동한다. 노드를 새로 만들지 않는다."""
        if node is None or node is self.head:
            return

        # 현재 위치에서 노드를 분리한다.
        if node.prev is None:
            self.head = node.next
        else:
            node.prev.next = node.next

        if node.next is None:
            self.tail = node.prev
        else:
            node.next.prev = node.prev

        # 기존 노드를 리스트의 맨 앞으로 연결한다.
        node.prev = None
        node.next = self.head

        if self.head is not None:
            self.head.prev = node

        self.head = node

        if self.tail is None:
            self.tail = node

    def size(self) -> int:
        """현재 노드 개수를 반환한다."""
        return self._size

    def __len__(self) -> int:
        return self._size

    def __iter__(self) -> Iterator[Any]:
        """리스트를 앞에서 뒤로 순회할 수 있게 한다."""
        current = self.head

        while current is not None:
            yield current.data
            current = current.next