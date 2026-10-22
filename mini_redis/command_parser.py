"""CLI 입력 문자열을 명령어와 인자 목록으로 파싱한다."""

import shlex
from typing import List


def parse_command(line: str) -> List[str]:
    """따옴표로 감싼 값과 공백 없는 값을 지원해 토큰 목록으로 반환한다.

    잘못된 따옴표가 입력되면 shlex가 ValueError를 발생시킨다.
    """
    return shlex.split(line, posix=True)