"""Mini Redis REPL의 시작점."""

from mini_redis.command_parser import parse_command
from mini_redis.command_processor import CommandProcessor
from mini_redis.storage import MiniRedisStore


def main() -> None:
    """입력을 반복해 파싱하고 명령을 실행하는 CLI 루프를 시작한다."""
    store = MiniRedisStore()
    processor = CommandProcessor(store)

    while True:
        try:
            line = input("mini-redis> ")
        except EOFError:
            break
        except KeyboardInterrupt:
            print("\n프로그램을 종료합니다.")
            break

        try:
            args = parse_command(line)
        except ValueError:
            print("(error) ERR syntax error")
            continue

        if not args:
            continue

        command = args[0].upper()

        if command in ("EXIT", "QUIT"):
            if len(args) == 1:
                break

            print(
                "(error) ERR wrong number of arguments for '{}' command"
                .format(command.lower())
            )
            continue

        output = processor.execute(args)

        if output:
            print(output)


if __name__ == "__main__":
    main()