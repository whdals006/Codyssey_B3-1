# Mini Redis 만들기

## 1. 프로젝트 기본 구조 만들기

### 1-1. 전체 프로젝트 구조

```md
/B3-1
└── mini_redis/
    ├── __init__.py
    ├── command_parser.py
    ├── command_processor.py
    ├── storage.py
    └── data_structures/
        ├── __init__.py
        ├── doubly_linked_list.py
        ├── hash_map.py
        └── min_heap.py
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
## 5. 저장소 엔진 구현

* `해시맵`: key를 이용해 데이터를 조회하고 저장
* `이중 연결 리스트`: 최근 사용 순서를 추적해 LRU 제거
* `최소 힙`: 만료 시각이 빠른 TTL 항목을 확인

위 세가지 자료구조를 결합해 Mini Redis의 핵심인 저장소 엔진을 구현한다.

### 5-1. 저장소 엔진의 구조 이해하기

### 5-2. 중요 코드 이해하기

1. ① 메모리 사용량 계산

    ```python
    entry_size = self._utf8_size(key) + self._utf8_size(value)
    ```

    메모리 사용량은 key와 value의 UTF-8 byte 수를 합산해서 계산한다.

    예를 들어 아래의 데이터라면,

    ```
    key = "a"
    value = "한"
    ```

    * `"a"`는 UFT-8 기준 1 Byte
    * `"한"`는 UTF-8 기준 3 Byte
    * 총 사용량은 4 Byte

    Python의 `len("한")`은 문자 수인 `1`을 반환하지만, `len("한".encode("utf-8"))`은 Byte 수인 `3`을 반환한다.

2. ② LRU 추적

    새 key를 저장할 때는 LRU 목록의 맨 앞에 넣는다.

    ```python
    new_entry.lru_node = self._lru.insert_front(key)
    ```

    GET이 성공했을 때도 해당 Node를 맨 앞으로 이동시킨다.

    ```python
    self._lru.move_to_front(entry.lru_node)
    ```

    따라서 LRU 목록의 맨 앞은 가장 최근에 사용한 key이고, 맨 뒤에 `tail`은 가장 오랫동안 사용하지 않은 key가 된다.

    메모리 제한을 초과하면 다음 코드가 `tail`부터 제거한다.

    ```python
    oldest_node = self._lru.tail
    self._remove_entry(oldest_node.data, evicted=True)
    ```

3. ③ TTL 만료 처리

    `expire()`는 현재 시각에 만료까지 남은 초를 더해 만료 시각을 만들고, 최소 heap에 `(expire_at, key)` 형태로 넣는다.

    ```python
    expire_at = time.time() + seconds
    entry.expire_at = expire_at
    self._expiry_heap.push((expire_at, key))
    ```

    `_pruge_expired()`는 heap의 root에서 만료 시각이 지난 항목을 확인한다.
    단, 이전 TTL이 heap에 남아 있더라도 현재 엔트리의 만료 시각과 다르면 무시한다. 따라서 TTL을 재설정하거나 key를 삭제한 뒤에도 오래된 heap 항목이 새 데이터를 잘못 삭제하지 않는다.

4. ④ 공통 삭제 처리

    `_remove_entry()`는 데이터만 제거하는 것이 아니라, 아래의 작업도 함께 수행한다.

    * Hash Map에서 key 삭제
    * LRU 목록에서 Node 삭제
    * `used_memory` 감소
    * LRU로 제거한 경우에만 `evicted_keys` 증가

    이 공통 함수를 사용하는 이유는 삭제 경로마다 메모리나 LRU 정보가 서로 다르게 남는 오류를 방지하기 위해서이다.

### 5-3. 저장소 엔진 테스트

```bash
python3 - <<'PY'
import time

from mini_redis.storage import MiniRedisStore

# 1. 기본 저장 및 조회, UTF-8 메모리 계산
store = MiniRedisStore()

assert store.set("한", "글") is True
assert store.get("한") == "글"

# "한" 3바이트 + "글" 3바이트
assert store.used_memory == 6
assert store.dbsize() == 1

# 2. 삭제 시 메모리 사용량 갱신
assert store.delete("한") is True
assert store.used_memory == 0
assert store.dbsize() == 0

# 3. LRU 제거 테스트
store.set_maxmemory(7)

assert store.set("a", "1") is True   # 2바이트
assert store.set("b", "22") is True  # 3바이트

# a를 최근 사용 키로 만든다.
assert store.get("a") == "1"

# c를 저장하면 총 9바이트가 되어 가장 오래된 b가 제거된다.
assert store.set("c", "333") is True

assert store.get("b") is None
assert store.get("a") == "1"
assert store.get("c") == "333"

assert store.used_memory == 6
assert store.evicted_keys == 1

# 4. 단일 항목이 메모리 제한보다 크면 OOM 처리
oom_store = MiniRedisStore()
oom_store.set_maxmemory(3)

assert oom_store.set("long", "x") is False
assert oom_store.dbsize() == 0
assert oom_store.used_memory == 0

# 5. TTL 없는 키와 존재하지 않는 키 확인
ttl_store = MiniRedisStore()

assert ttl_store.set("item", "old") is True
assert ttl_store.ttl("item") == -1
assert ttl_store.expire("missing", 10) is False

# 6. TTL 설정
assert ttl_store.expire("item", 30) is True

remaining = ttl_store.ttl("item")
assert 0 <= remaining <= 30

# 7. SET으로 덮어쓰면 TTL이 초기화된다.
assert ttl_store.set("item", "new") is True
assert ttl_store.ttl("item") == -1

# 이전 TTL 항목은 현재 엔트리를 삭제하면 안 된다.
ttl_store._purge_expired(now=time.time() + 60)
assert ttl_store.get("item") == "new"

# 8. 정상적인 TTL 만료 확인
assert ttl_store.set("temp", "v") is True
assert ttl_store.expire("temp", 10) is True

ttl_store._purge_expired(now=time.time() + 20)

assert ttl_store.get("temp") is None
assert ttl_store.ttl("temp") == -2

# 9. TTL 0은 즉시 삭제
assert ttl_store.expire("item", 0) is True
assert ttl_store.ttl("item") == -2

print("모든 저장소 엔진 테스트를 통과했습니다.")
PY
```

## 6. Redis 명령어 구현

### 6-1. `command_parser.py` 의 역할

- 입력 문자열을 명령어와 인자로 분리하는 역할

- `split()`을 사용하면 공백을 기준으로 분리되지만, `shlex.split()`은 따옴표를 고려해서 분리한다.

```bash
SET greeting "hello world"
```

를 `split()`으로 분리하면 `"hello`와 `world"`로 분리되지만,
`shlex.split()`으로 분리하면 따옴표를 고려해서 `"hello world"`로 분리된다.

### 6-2. `command_processor.py` 의 역할

명령어를 직접 파싱하는 대신, 파싱된 argument 목록을 받아 실행하는 역할.

예를 들어서,

```
SET user:` "Alice"
```

command_parser.py는 ["SET", "user:1", "Alice"]를 반환하고,

command_processor는 storage.py의 `set()` 메서드를 호출한다.

| 명령어 | storage method | 정상적인 응답 형식 |
| :--- | :--- | :--- |
| `SET` | `set()` | `OK` |
| `GET` | `get()` | `"Alice"` 또는 `(nil)` |
| `DEL` | `delete()` | `(integr) 1` 또는 `(integer) 0` |
| `EXISTS` | `exists()` | `(integer) 1` 또는 `(integer) 0` |
| `DBSIZE` | `dbsize()` | `(integer) N` |
| `KEYS` | `keys()` | key 목록 또는 `(emty array)` |
| `CONFIG SET maxmemory` | `set_maxmemory()` | `OK` 또는 오류 |
| `INFO memory` | `info_memory()` | 메모리 정보 |
| `EXPIRE` | `expire()` | `(integer) 1` 또는 `(integer) 0` |
| `TTL` | `ttl()` | 남은 초, `-1` 또는 `-2` |

`_parse_integer()`는 메모리 제한이나 만료 시간처럼 정수가 필요한 입력을 검증한다. 숫자가 아니거나 64비트 부호 정수 범위를 벗어난 입력은 지정된 오류 메세지로 처리한다.

### 6-3. 테스트

```python
python3 - <<'PY'
from mini_redis.command_parser import parse_command
from mini_redis.command_processor import CommandProcessor
from mini_redis.storage import MiniRedisStore

# 1. 따옴표와 공백이 포함된 값 파싱
assert parse_command('SET greeting "hello world"') == [
    "SET", "greeting", "hello world"
]

assert parse_command("GET greeting") == ["GET", "greeting"]

# 2. 잘못된 따옴표 처리
try:
    parse_command('SET key "unfinished')
except ValueError:
    pass
else:
    raise AssertionError("잘못된 따옴표가 감지되지 않았습니다.")

store = MiniRedisStore()
processor = CommandProcessor(store)

# 3. 기본 String 명령어
assert processor.execute(["SET", "name", "Alice Smith"]) == "OK"
assert processor.execute(["GET", "name"]) == '"Alice Smith"'
assert processor.execute(["EXISTS", "name"]) == "(integer) 1"
assert processor.execute(["DBSIZE"]) == "(integer) 1"
assert processor.execute(["KEYS"]) == '1) "name"'

assert processor.execute(["GET", "missing"]) == "(nil)"
assert processor.execute(["EXISTS", "missing"]) == "(integer) 0"
assert processor.execute(["DEL", "name"]) == "(integer) 1"
assert processor.execute(["DEL", "name"]) == "(integer) 0"
assert processor.execute(["DBSIZE"]) == "(integer) 0"
assert processor.execute(["KEYS"]) == "(empty array)"

# 4. 메모리 설정과 OOM 처리
assert processor.execute(
    ["CONFIG", "SET", "maxmemory", "4"]
) == "OK"

assert processor.execute(["SET", "long", "x"]) == (
    "(error) OOM command not allowed when used_memory > 'maxmemory'"
)

assert processor.execute(
    ["CONFIG", "SET", "maxmemory", "abc"]
) == "(error) ERR value is not an integer or out of range"

assert processor.execute(
    ["CONFIG", "SET", "maxmemory", "-1"]
) == "(error) ERR value is not an integer or out of range"

# 5. TTL 설정과 SET 덮어쓰기 시 초기화
assert processor.execute(
    ["CONFIG", "SET", "maxmemory", "20"]
) == "OK"

assert processor.execute(["SET", "temp", "x"]) == "OK"
assert processor.execute(["EXPIRE", "temp", "30"]) == "(integer) 1"

ttl_result = int(processor.execute(["TTL", "temp"]).split()[-1])
assert 0 <= ttl_result <= 30

assert processor.execute(["EXPIRE", "missing", "30"]) == "(integer) 0"
assert processor.execute(["SET", "temp", "new"]) == "OK"
assert processor.execute(["TTL", "temp"]) == "(integer) -1"

# 6. INFO memory
info = processor.execute(["INFO", "memory"])
assert "used_memory:7" in info
assert "maxmemory:20" in info
assert "evicted_keys:0" in info

# 7. 오류 처리
assert processor.execute(["GET"]) == (
    "(error) ERR wrong number of arguments for 'get' command"
)
assert processor.execute(["HELLO"]) == (
    "(error) ERR unknown command 'HELLO'"
)
assert processor.execute(["EXPIRE", "temp", "abc"]) == (
    "(error) ERR value is not an integer or out of range"
)

print("모든 명령어 처리 테스트를 통과했습니다.")
PY
```

## 7. CLI 완성

### 7-1. main.py 의 역할

- CLI의 시작점

### 7-2. 전체 테스트

```bash
python3 -m mini_redis.main <<'EOF'
CONFIG SET maxmemory 30
SET user:1 "Alice"
SET user:2 "Bob"
GET user:1
SET user:3 "Charlie"
INFO memory
EXISTS user:2
KEYS
EXPIRE user:1 0
GET user:1
TTL user:1
SET oversize abcdefghijklmnopqrstuvwxyz
GET
HELLO
quit
EOF
```

* 결과 확인

| 테스트 | 기대 결과 |
| :--- | :--- |
| `CONFIG SET maxmemory 30` | `OK` |
| `SET user:1 "Alice"` | `OK` |
| `GET user:1` | `"Alice"` |
| `SET user:3 "Charlie"` 이후	| LRU에 따라 `user:2` 제거 |
| `INFO memory` | `used_memory:24`, `maxmemory:30`, `evicted_keys:1` |
| `EXISTS user:2` | `(integer) 0` |
| `EXPIRE user:1 0` | `(integer) 1` |
| `GET user:1` | `(nil)` |
| `TTL user:1` | `(integer) -2` |
| 단일 항목 OOM	| `(error) OOM command not allowed when used_memory > 'maxmemory'` |
| 인자 없는 `GET` | 인자 개수 오류 |
| `HELLO`	| 알 수 없는 명령어 오류 |