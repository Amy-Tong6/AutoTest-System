#!/usr/bin/env python3
"""PR 时由 CI 调用的占位脚本，后续可替换为真实检查逻辑。"""

from __future__ import annotations

import random
import sys


def main() -> None:
    print("[pr-check] start")
    ok = random.random() < 0.5
    if ok:
        print("[pr-check] result=PASS")
        sys.exit(0)
    print("[pr-check] result=FAIL", file=sys.stderr)
    sys.exit(1)


if __name__ == "__main__":
    main()
