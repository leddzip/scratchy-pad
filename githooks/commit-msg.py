#!/usr/bin/env python3

import sys
import re

from dataclasses import dataclass


CONVENTIONAL_COMMIT_PATTERNS = {
    'revert': [],
    'chore': ['setup'],
    'fix': [],
    'feat': [],
    'docs': [],
    'style': [],
    'refactor': [],
    'test': [],
    'perf': [],
    'ci': [],
    'build': []
}


class InvalidScopeForTypeException(Exception):
    def __init__(self, message: str):
        super().__init__(message)
        self.message = message


def format_error(message: str) -> str:
    return f"\033[91m{message}\033[0m"


def format_success(message: str) -> str:
    return f"\033[92m{message}\033[0m"


@dataclass
class ConventionalCommit:
    commit_type: str
    scopes: list[str]

    @property
    def type_regex(self) -> re.Pattern:
        return re.compile(f'^{self.commit_type}\([\w_-]+\): .+$')

    @property
    def scope_regex(self) -> re.Pattern:
        scopes_formatted = '|'.join(self.scopes)
        return re.compile(f'^{self.commit_type}\(({scopes_formatted})\): .+$')

    @property
    def message_invalid_scope(self) -> str:
        return f'Invalid scope for {self.commit_type}. Valid scopes are: {", ".join(self.scopes)}'

    def _test_type(self, message_line: str) -> bool:
        return self.type_regex.match(message_line) is not None

    def _test_scope(self, message_line: str) -> bool:
        is_message_valid = self.scope_regex.match(message_line) is not None
        if is_message_valid:
            return True
        else:
            raise InvalidScopeForTypeException(self.message_invalid_scope)

    def test(self, message_line: str) -> bool:
        return self._test_type(message_line) and self._test_scope(message_line)


def scoped_conventional_commit_validator(pattern_map: dict[str, list[str]]) -> None:
    patterns = [ConventionalCommit(commit_type=commit_type, scopes=scopes) for commit_type, scopes in pattern_map.items()]
    message = sys.argv[1]

    with open(message, 'r') as f:
        message_lines = f.readlines()
        first_line = message_lines[0]

    try:
        pattern_evaluation = [pattern.test(first_line) for pattern in patterns]

        if any(pattern_evaluation):
            print(format_success("Commit message format is correct."))
        else:
            print(format_error("ERROR: Commit message does not follow the Conventional Commit format."))
            print(format_error("Please format your commit message as follows:"))
            print(format_error("  <type>(<scope>): <description>"))
            sys.exit(1)
    except InvalidScopeForTypeException as e:
        print(format_error("ERROR: Commit message does not follow the Conventional Commit format."))
        print(format_error(e.message))
        sys.exit(1)


if __name__ == '__main__':
    scoped_conventional_commit_validator(CONVENTIONAL_COMMIT_PATTERNS)