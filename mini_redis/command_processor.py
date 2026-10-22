"""Mini Redis 명령어를 검증하고 Redis 스타일로 출력한다."""

from typing import List, Optional

from mini_redis.storage import MiniRedisStore


class CommandProcessor:
    """파싱된 인자 목록을 받아 명령을 실행하고 출력 문자열을 생성한다."""

    _MIN_INTEGER = -(2**63)
    _MAX_INTEGER = 2**63 - 1

    _OOM_MESSAGE = (
        "(error) OOM command not allowed when used_memory > 'maxmemory'"
    )

    _INTEGER_ERROR = (
        "(error) ERR value is not an integer or out of range"
    )

    def __init__(self, store: MiniRedisStore) -> None:
        self.store = store

    @staticmethod
    def _wrong_number(command: str) -> str:
        """명령어의 인자 개수가 잘못됐을 때 오류 문자열을 만든다."""
        return (
            "(error) ERR wrong number of arguments for '{}' command"
        ).format(command.lower())

    @classmethod
    def _parse_integer(cls, text: str) -> Optional[int]:
        """64비트 부호 정수 범위의 입력만 정수로 반환한다."""
        try:
            value = int(text, 10)
        except ValueError:
            return None

        if value < cls._MIN_INTEGER or value > cls._MAX_INTEGER:
            return None

        return value

    @staticmethod
    def _quote(value: str) -> str:
        """CLI에서 문자열 값과 키를 큰따옴표 형태로 출력한다."""
        escaped = value.replace("\\", "\\\\")
        escaped = escaped.replace('"', '\\"')
        escaped = escaped.replace("\r", "\\r").replace("\n", "\\n")

        return '"{}"'.format(escaped)

    def execute(self, args: List[str]) -> str:
        """명령을 실행하고 사용자가 볼 결과 문자열을 반환한다."""
        if not args:
            return ""

        original_command = args[0]
        command = original_command.upper()

        if command == "SET":
            if len(args) != 3:
                return self._wrong_number("SET")

            if not self.store.set(args[1], args[2]):
                return self._OOM_MESSAGE

            return "OK"

        if command == "GET":
            if len(args) != 2:
                return self._wrong_number("GET")

            value = self.store.get(args[1])

            if value is None:
                return "(nil)"

            return self._quote(value)

        if command == "DEL":
            if len(args) != 2:
                return self._wrong_number("DEL")

            deleted = self.store.delete(args[1])

            return "(integer) {}".format(1 if deleted else 0)

        if command == "EXISTS":
            if len(args) != 2:
                return self._wrong_number("EXISTS")

            exists = self.store.exists(args[1])

            return "(integer) {}".format(1 if exists else 0)

        if command == "DBSIZE":
            if len(args) != 1:
                return self._wrong_number("DBSIZE")

            return "(integer) {}".format(self.store.dbsize())

        if command == "KEYS":
            if len(args) != 1:
                return self._wrong_number("KEYS")

            keys = self.store.keys()

            if not keys:
                return "(empty array)"

            return "\n".join(
                "{}) {}".format(index, self._quote(key))
                for index, key in enumerate(keys, start=1)
            )

        if command == "CONFIG":
            if len(args) != 4:
                return self._wrong_number("CONFIG")

            if args[1].upper() != "SET" or args[2].lower() != "maxmemory":
                return "(error) ERR syntax error"

            maxmemory = self._parse_integer(args[3])

            if maxmemory is None or maxmemory < 0:
                return self._INTEGER_ERROR

            self.store.set_maxmemory(maxmemory)

            return "OK"

        if command == "INFO":
            if len(args) != 2:
                return self._wrong_number("INFO")

            if args[1].lower() != "memory":
                return "(error) ERR unknown subcommand '{}'".format(args[1])

            used_memory, maxmemory, evicted_keys = (
                self.store.info_memory()
            )

            return (
                "used_memory:{}\n"
                "maxmemory:{}\n"
                "evicted_keys:{}"
            ).format(used_memory, maxmemory, evicted_keys)

        if command == "EXPIRE":
            if len(args) != 3:
                return self._wrong_number("EXPIRE")

            seconds = self._parse_integer(args[2])

            if seconds is None:
                return self._INTEGER_ERROR

            success = self.store.expire(args[1], seconds)

            return "(integer) {}".format(1 if success else 0)

        if command == "TTL":
            if len(args) != 2:
                return self._wrong_number("TTL")

            return "(integer) {}".format(self.store.ttl(args[1]))

        return "(error) ERR unknown command '{}'".format(original_command)