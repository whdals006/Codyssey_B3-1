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

## 3. 체이닝 방식의 해시맵

### 3-1. 해시맵의 동작 원리

### 3-2. 핵심 코드

1. ① 해시 함수 `_hash()`

    ```python
    value = (value * 31 + ord(character)) % len(self._buckets)
    ```

    각 문자의 유니코드 코드 포인트를 이용해 해시값을 계산한다.
    `31`은 다항식 해싱에 사용하는 상수.
    마지막에 버킷 개수로 나머지를 구해 유효한 인덱스를 만든다.

2. ② 충돌을 처리하는 `_find_node()`

    ```python
    current = bucket.head

    while current is not None:
        if current.data.key == key:
            return current

        current = current.next
    ```

    같은 버킷에 여러 키가 있으면 연결 리스트를 순회하며 키를 비교한다.
    따라서 해시 함수가 같은 위치를 반환해도 서로 다른 키의 값을 구분할 수 있다.

3. ③ 기존 키 덮어쓰기

    `put()`에서 키가 이미 존재하면 새 노드를 만들지 않고 기존 항목의 `value`만 변경한다.
    따라서 키가 중복 등록되지 않고, 항목 수도 증가하지 않는다.

4. ④ 버킷 확장 `_resize()`

버킷 개수가 변경되면 같은 키라도 새로운 인덱스가 나올 수 있다.
그러므로 기존 항목을 새 버킷 테이블에 다시 배치해야 하는데, 이를 `ReHashing` 이라고 한다.

해시맵의 `get()`, `put()`, `remove()`는 평균적으로 O(1)을 목표로 하지만, 특정 버킷에 충돌이 집중되면 최악의 경우 O(n)이 될 수 있다.

### 3-3. 기능 테스트

```bash
python3 - <<'PY'
from mini_redis.data_structures.hash_map import HashMap

# 1. 해시 충돌 테스트
hash_map = HashMap(initial_capacity=8)

# 'a'와 'i'는 현재 버킷 8개일 때 같은 인덱스에 배정된다.
assert hash_map._hash("a") == hash_map._hash("i")

hash_map.put("a", 100)
hash_map.put("i", 200)

assert hash_map.get("a") == 100
assert hash_map.get("i") == 200
assert hash_map.size() == 2

# 2. 기존 키 덮어쓰기 테스트
old_value = hash_map.put("a", 300)

assert old_value == 100
assert hash_map.get("a") == 300
assert hash_map.size() == 2

# 3. 존재 여부와 삭제 테스트
assert hash_map.contains("a") is True
assert hash_map.contains("missing") is False

removed_value = hash_map.remove("i")

assert removed_value == 200
assert hash_map.contains("i") is False
assert hash_map.size() == 1

# 존재하지 않는 키를 삭제하면 None
assert hash_map.remove("missing") is None

# 4. 로드 팩터 초과 시 버킷 확장 테스트
resizing_map = HashMap(initial_capacity=8)

for number in range(7):
    resizing_map.put(f"key-{number}", number)

# 7 / 8 = 0.875이므로 버킷이 8개에서 16개로 늘어나야 한다.
assert len(resizing_map._buckets) == 16

# 확장 이후에도 모든 항목이 유지되는지 확인한다.
for number in range(7):
    assert resizing_map.get(f"key-{number}") == number

assert resizing_map.size() == 7
assert len(resizing_map.keys()) == 7

print("모든 해시맵 테스트를 통과했습니다.")
PY
```

## 4. 최소 힙 (Min_Heap)

### 4-1. 최소 힙의 동작 원리

### 4-2. 최소 힙의 주요 연산

| 메서드 | 기능 | 시간 복잡도 |
| :--- | :--- | :--- |
| `push()` | 새 항목 추가 | O(log n) |
| `pop()` | 최소값 제거 및 반환 | O(log n) |
| `peek()` | 최소값 확인 | O(1) |
| `size()` | 항목 개수 반환 | O(1) |

`push()`와 `pop()`은 힙의 규칙을 유지하기 위해 부모,자식 노드를 비교하면서 위치를 조정한다.

### 4-3. 핵심 코드 이해하기

1. ① `push()`와 `_heapify_up()`

    새 항목을 배열 맨 끝에 추가한 뒤 부모와 비교한다.
    새 항목이 부모보다 작으면 두 항목의 위치를 바꾸는 과정을 반복

    ```python
    parent = (index - 1) // 2
    ```

    배열 인덱스가 `index`인 노드의 부모 인덱스를 계산하는 공식

2. ② `pop()`과 `_heapify_down()`

    최소값인 Root항목을 반환하고, 마지막 항목을 Root로 옮긴다. 그 후 자식 중 더 작은 항목과 비교하면서 Heap 규칙을 반복한다.

    왼쪽 자식과 오른쪽 자식의 인덱스는 아래와 같다.

    ```python
    left = index * 2 + 1
    right = index * 2 + 2
    ```

3. ③ 왜 배열로 구현할까?

    합은 완전 이진 트리 형태를 유지하므로, 포인터를 가진 트리 노드를 만들지 않고도 리스트 인덱스로 부모와 자식을 계산할 수 있다.

    여기서 리스트는 Heap 내부 항목을 저장하는 Array 역할을 한다.

### 4-4. 최소 힙 테스트

```bash
python3 - <<'PY'
from mini_redis.data_structures.min_heap import MinHeap

heap = MinHeap()

# 1. 빈 힙 확인
assert heap.size() == 0
assert heap.peek() is None
assert heap.pop() is None

# 2. 숫자 삽입 테스트
for number in [7, 3, 10, 1, 5]:
    heap.push(number)

assert heap.size() == 5
assert heap.peek() == 1

# 3. 최솟값 순서대로 꺼내지는지 확인
result = []

while heap.size() > 0:
    result.append(heap.pop())

assert result == [1, 3, 5, 7, 10]
assert heap.size() == 0

# 4. TTL 항목 테스트
ttl_heap = MinHeap()

ttl_heap.push((105.0, "user:1"))
ttl_heap.push((102.0, "user:2"))
ttl_heap.push((108.0, "user:3"))

assert ttl_heap.peek() == (102.0, "user:2")
assert ttl_heap.pop() == (102.0, "user:2")
assert ttl_heap.pop() == (105.0, "user:1")
assert ttl_heap.pop() == (108.0, "user:3")
assert ttl_heap.pop() is None

# 5. 만료 시각이 같은 경우 키 이름으로 비교되는지 확인
same_time_heap = MinHeap()

same_time_heap.push((200.0, "user:3"))
same_time_heap.push((200.0, "user:1"))
same_time_heap.push((200.0, "user:2"))

assert same_time_heap.pop() == (200.0, "user:1")
assert same_time_heap.pop() == (200.0, "user:2")
assert same_time_heap.pop() == (200.0, "user:3")

print("모든 최소 힙 테스트를 통과했습니다.")
PY
```

