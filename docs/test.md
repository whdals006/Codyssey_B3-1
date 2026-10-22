# 테스트

## 1. Mini Redis 실행하기

```bash
python3 -m mini_redis.main
```

## 2. 기본 명령어 6개

1. `SET` — 데이터 저장

    ```bash
    SET [key] [value]
    ```

    - 내부적으로 Hash Map에 데이터를 저장하고, Double Linked List의 LRU 목록 맨 앞에 key를 추가한다.

2. `GET` — 데이터 조회

    ```bash
    GET [key]
    ```

    - key의 value값을 반환
    - key가 없으면 `(nil)`을 반환

3. `EXISTS` — key 존재 여부 확인

    ```bash
    EXISTS [key]
    ```

    - key가 존재하면 `(integer) 1`, 없으면 `(integer) 0`을 반환한다.

4. `DBSIZE` — 전체 key 개수 확인

    ```bash
    DBSIZE
    ```

    - 현재 저장된 key의 총 개수를 반환

5. `KEYS` — 전체 key 목록 확인

    ```bash
    KEYS
    ```

    - 저장된 모든 key를 출력

6. `DEL` — 데이터 삭제

    ```bash
    DEL [key]
    ```

    - 정상적으로 삭제되면 `(integer) 1`을 반환.
    - 이미 key가 없으면 `(integer) 0`을 반환.

## 3. 메모리 관리 명령어 2개

7. `CONFIG SET maxmemory` — 최대 메모리 제한 설정

    ```bash
    CONFIG SET maxmemory [byte수]
    ```

    - `0`으로 설정하면 무제한으로 동작

8. `INFO memory` — 메모리 사용량 확인

    ```bash
    INFO memory
    ```

    - 3가지 정보를 확인 할 수 있다.

        | 항목 | 의미 |
        | :--- | :--- |
        | `used_memory` | key와 value의 UTF-8 byte 수 합계 |
        | `maxmemory` | 최대 메모리 제한 |
        | `evicted keys` | 메모리 부족으로 제거된 key의 누적 개수 |

## 4. TTL 관리 명령어 2개

9. `EXPIRE` — 만료 시간 설정

    ```bash
    EXPIRE [key] [만료시간_초]
    ```

    - 존재하는 key에 설정하면 `(integer) 1`을 반환.
    - 존재하지 않는 key에 설정하면 `(integer) 0`을 반환.

10. `TTL` — 남은 만료 시간 조회

```bash
TTL [key]
```

- TTL 반환값의 3가지 경우

    | 반환값 | 의미 |
    | :--- | :--- |
    | `(integer) N` | 남은 만료 시간(초) |
    | `(integer) -1` | key는 존재하지만 만료 시간이 설정되지 않음 |
    | `(integer) -2` | key가 존재하지 않음 |

## 예외 처리

1. 메모리 부족 (OOM)

    ```
    mini-redis> CONFIG SET maxmemory 4
    OK
    mini-redis> SET longkey "value"
    (error) OOM command not allowed when used_memory > 'maxmemory'
    ```

2. 잘못된 명령어와 인자

    - ① 지원하지 않는 명령어를 적었을 때

    ```
    mini-redis> HELLO
    (error) ERR unknown command 'HELLO'
    ```

    - ② 명령어 형식을 잘못 적었을 때

    ```
    mini-redis> GET
    (error) ERR wrong number of arguments for 'get' command
    ```

    - ③ 옵션 값을 잘못 적었을 때

    ```
    mini-redis> CONFIG SET maxmemory abc
    (error) ERR value is not an integer or out of range
    ```

## 문자 종류에 따른 바이트 계산

문자열을 UTF-8로 인코딩 했을 때의 바이트 수로 계산

| 문자 종류 | 개수 | UTF-8 바이트 수 |
| 영어 | 알파벳 1개 | 1 byte |
| 숫자 | 숫자 1개 | 1 byte |
| 한글 | 한글자 | 3 byte |
| 공백 | 1개 | 1 byte |
| 이모지 | 종류에 따라 다름 | - |


storage.py 에서 코드 확인 가능

```python
@staticmethod
def _utf8_size(text: str) -> int:
    """문자열의 UTF-8 인코딩 바이트 수를 반환한다."""
    return len(text.encode("utf-8"))
```

`set()` 에서 key와 value의 byte수를 더한다.

```python
entry_size = self._utf8_size(key) + self._utf8_size(value)
```