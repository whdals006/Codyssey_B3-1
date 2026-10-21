#

## 1. 프로젝트 기본 구조 만들기

### 1-1. 전체 프로젝트 구조

```md
/B3-1
└── mini_redis/
    └── data_structures/
```

## 2. 이중 연결 리스트

### 2-1. 이중 연결 리스트의 원리

### 2-2. 코드에서 기억할 부분

| 코드 | 의미 |
| :--- | :--- |
| `head` | 첫 번째 노드 |
| `tail` | 마지막 노드 |
| `prev` | 이전 노드 참조 |
| `next` | 다음 노드 참조 |
| `_size` | 현재 노드 개수 |
| `insert_front()` | 맨 앞 삽입 |
| `insert_back()` | 맨 뒤 삽입 |
| `remove_node()` | 특정 노드 삭제 |
| `move_to_front()` | 기존 노드를 맨 앞으로 이동 |

`__slots__`는 노드에서 사용할 속성을 제한해 주는 Python 기능이다. 이번 미션에서는 각 노드에 필요한 세 속성을 명확하게 나타내기 위해 사용.

`move_to_front()`에서는 `_size`를 수정하지 않는다. 노드를 삭제하거나 추가하는 게 아니라 기존 노드의 연결만 바꾸는 작업이기 때문이다.

### 2-3. 코드 직접 테스트 하기

```bash
python3 - <<'PY'
from mini_redis.data_structures.doubly_linked_list import DoublyLinkedList

linked_list = DoublyLinkedList()

# 1. 빈 리스트 확인
assert len(linked_list) == 0
assert linked_list.remove_front() is None
assert linked_list.remove_back() is None

# 2. 뒤쪽에 삽입
a = linked_list.insert_back("A")
b = linked_list.insert_back("B")
c = linked_list.insert_back("C")

assert list(linked_list) == ["A", "B", "C"]
assert linked_list.head is a
assert linked_list.tail is c

# 3. 맨 앞 이동
linked_list.move_to_front(c)
assert list(linked_list) == ["C", "A", "B"]
assert linked_list.head is c
assert linked_list.tail is b

# 4. 중간 노드 이동
linked_list.move_to_front(a)
assert list(linked_list) == ["A", "C", "B"]

# 5. 특정 노드 삭제
removed = linked_list.remove_node(c)
assert removed == "C"
assert list(linked_list) == ["A", "B"]
assert c.prev is None
assert c.next is None

# 6. 양 끝 노드 삭제
assert linked_list.remove_front() == "A"
assert linked_list.remove_back() == "B"

assert len(linked_list) == 0
assert linked_list.head is None
assert linked_list.tail is None

print("모든 테스트를 통과했습니다.")
PY
```