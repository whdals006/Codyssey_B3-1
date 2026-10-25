# Mini Redis

Python으로 직접 구현한 CLI 기반 In-Memory Key-Value 저장소입니다.

Redis의 기본 String 명령어, LRU 메모리 관리, TTL 만료 처리를 구현하면서
해시맵, 이중 연결 리스트, 최소 힙의 동작 원리를 학습하는 프로젝트입니다.

## 개발 환경

- Python 3.12.3
- WSL Ubuntu
- Visual Studio Code

## 실행 방법

프로젝트 루트인 `B3-1` 디렉터리에서 실행합니다.

```bash
python3 -m mini_redis.main
```

프로그램을 종료하려면 `exit` 또는 `quit`을 입력합니다.

## 지원 명령어

### String 명령어

- `SET [key] [value]`: 키에 값을 저장합니다.
- `GET [key]`: 값을 조회합니다.
- `DEL [key]`: 키를 삭제합니다.
- `EXISTS [key]`: 키 존재 여부를 확인합니다.
- `DBSIZE`: 저장된 키 개수를 반환합니다.
- `KEYS`: 전체 키 목록을 반환합니다.

### 메모리 관리

- `CONFIG SET [maxmemory_bytes]`: 최대 메모리를 바이트 단위로 설정합니다.
- `INFO memory`: 메모리 사용량, 메모리 제한, 제거된 키 개수를 조회합니다.

    `maxmemory`가 0이면 메모리 제한이 없습니다.

### TTL 명령어

- `EXPIRE [key] [seconds]`: 키의 만료 시간을 설정합니다.
- `TTL [key]`: 남은 만료 시간을 조회합니다.

    TTL 명령어의 반환값은 다음과 같습니다.

    - `-2`: 키가 존재하지 않습니다.
    - `-1`: 키는 존재하지만 만료 시간이 없습니다.
    - `0` 이상: 남은 만료 시간을 초 단위 정수로 반환합니다.

### 주의사항

값에 공백이 포함되어 있다면 큰따옴표로 감쌉니다.

(예시)

```text
SET greeting "hello world"
GET greeting
```

## 프로젝트 구조

```text
B3-1/
├── .gitignore
├── README.md
└── mini_redis/
    ├── __init__.py
    ├── main.py
    ├── command_parser.py
    ├── command_processor.py
    ├── storage.py
    └── data_structures/
        ├── __init__.py
        ├── doubly_linked_list.py
        ├── hash_map.py
        └── min_heap.py
```

## 자료구조 설계

### 이중 연결 리스트

`doubly_linked_list.py`

- `prev`, `next`, `data`를 가진 노드를 구현합니다.
- 앞뒤 삽입, 삭제, 노드 이동을 지원합니다.
- LRU 추적 및 해시맵의 체이닝에 활용합니다.

### 해시맵

`hash_map.py`

- 직접 작성한 다항식 해시 함수를 사용합니다.
- 체이닝으로 해시 충돌을 처리합니다.
- 로드 팩터가 0.75를 초과하면 버킷을 두 배로 확장합니다.

### 최소 힙

`min_heap.py`

- 배열 기반 최소 힙을 구현합니다.
- `push`, `pop`, `peek`, `size`를 제공합니다.
- 가장 빠른 TTL 만료 시각을 확인하는 데 사용합니다.

### 저장소 엔진

`storage.py`

- 해시맵, 이중 연결 리스트, 최소 힙을 결합합니다.
- LRU 정책으로 메모리 제한을 관리합니다.
- TTL 만료 항목을 정리합니다.
- UTF-8 기준 키와 값의 바이트 수를 합산해 메모리 사용량을 계산합니다.

### 명령어 처리

- `command_parser.py`: 입력 문자열을 명령어와 인자로 분리합니다.
- `command_processor.py`: 명령어 검증, 저장소 호출, 결과 형식 생성을 담당합니다.
- `main.py`: 사용자 입력을 반복적으로 처리하는 CLI를 실행합니다.

## 메모리 관리

메모리 사용량은 다음 공식으로 계산합니다.

`used_memory = Σ(len(utf8(key)) + len(utf8(value)))`

자료구조의 노드, 포인터, 버킷 등은 계산하지 않습니다.

메모리 제한을 초과하면 가장 오래 사용하지 않은 키부터 제거합니다.
단일 항목 자체가 제한보다 크면 저장하지 않고 OOM 오류를 반환합니다.

## TTL 관리

최소 힙에는 `(expire_at, key)` 형태의 항목을 저장합니다.

만료 시각이 빠른 항목부터 확인하며, TTL이 재설정되거나 키가 삭제되어
더 이상 유효하지 않은 힙 항목은 실제 엔트리의 만료 시각과 비교해 무시합니다.

## 제약 사항

- Python 내장 `dict`, `set`, `collections`를 자료구조 구현에 사용하지 않습니다.
- 외부 Redis 서버와의 네트워크 통신을 구현하지 않습니다.
- 데이터 영속성은 제공하지 않습니다.
- Redis의 복잡 자료형 및 보너스 과제는 구현하지 않습니다.