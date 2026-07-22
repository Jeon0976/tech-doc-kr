#!/usr/bin/env python3
"""tech-doc-kr 기계 검증기 - 표준 라이브러리만 사용.

검사 항목
  1. 비키보드 문자: ASCII/한글(음절+자모) 밖의 문자를 위치와 함께 리포트
  2. 피드백 마커: {한글 ...} 형태의 교정 요청 마커 잔존
  3. 상대링크: 마크다운 링크 대상 파일 존재 여부
  4. 코드펜스: --baseline 파일 대비 코드 블록 내용 해시 비교 (교정 전후 훼손 검사)

사용법
  verify.py FILE [FILE ...]              # 1~3 검사 (기본)
  verify.py --scan FILE ...              # 1번만, 문자 빈도표로 (교정 전 전수 조사용)
  verify.py --baseline OLD.md NEW.md     # 4번: OLD 대비 NEW의 코드펜스 훼손 검사
종료 코드: 문제 0건이면 0, 있으면 1
"""
import sys, re, os, hashlib, collections

def is_keyboard(ch: str) -> bool:
    o = ord(ch)
    if o < 128:
        return True                      # ASCII
    if 0xAC00 <= o <= 0xD7A3:
        return True                      # 한글 음절
    if 0x3131 <= o <= 0x318E:
        return True                      # 호환 자모 (ㅋㅋㅋ 등)
    return False

def iter_lines(path):
    with open(path, encoding="utf-8") as f:
        yield from enumerate(f, 1)

def check_chars(path, counter=None):
    problems = []
    for i, line in iter_lines(path):
        for ch in line:
            if not is_keyboard(ch) and ch != "﻿":
                if counter is not None:
                    counter[ch] += 1
                else:
                    problems.append(f"{path}:{i}: 비키보드 문자 {ch!r} (U+{ord(ch):04X})")
    return problems

MARKER = re.compile(r"\{[가-힣][^`{}]*\}|\{ [가-힣][^`{}]*\}")

def check_markers(path):
    out = []
    in_fence = False
    for i, line in iter_lines(path):
        if line.lstrip().startswith("```"):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        for m in MARKER.finditer(line):
            out.append(f"{path}:{i}: 피드백 마커 잔존 {m.group(0)[:40]!r}")
    return out

LINK = re.compile(r"\]\(([^)#\s]+?)(?:#[^)]*)?\)")

def check_links(path):
    out = []
    base = os.path.dirname(os.path.abspath(path))
    text = open(path, encoding="utf-8").read()
    for m in LINK.finditer(text):
        target = m.group(1)
        if target.startswith(("http://", "https://", "mailto:")):
            continue
        if not os.path.exists(os.path.normpath(os.path.join(base, target))):
            out.append(f"{path}: 깨진 상대링크 -> {target}")
    return out

def fence_hashes(path):
    """(언어, 내용해시) 목록. 순서 보존."""
    hashes, buf, lang, in_fence = [], [], "", False
    for _, line in iter_lines(path):
        stripped = line.lstrip()
        if stripped.startswith("```"):
            if in_fence:
                joined = "".join(buf)
                hashes.append((lang, hashlib.md5(joined.encode()).hexdigest()[:12]))
                buf, in_fence = [], False
            else:
                lang, in_fence = stripped[3:].strip(), True
            continue
        if in_fence:
            buf.append(line)
    return hashes

def check_baseline(old, new):
    a, b = fence_hashes(old), fence_hashes(new)
    out = []
    if len(a) != len(b):
        out.append(f"코드펜스 개수 변화: {len(a)} -> {len(b)} (의도한 삭제/추가인지 확인)")
    for idx, (x, y) in enumerate(zip(a, b), 1):
        if x != y:
            out.append(f"코드펜스 #{idx} 내용 변경: {x} -> {y} (실코드 인용이면 소스와 재대조)")
    return out

def main(argv):
    args = [a for a in argv if not a.startswith("--")]
    if "--baseline" in argv:
        if len(args) != 2:
            print(__doc__); return 2
        problems = check_baseline(*args)
    elif "--scan" in argv:
        counter = collections.Counter()
        for p in args:
            check_chars(p, counter)
        for ch, n in counter.most_common():
            print(f"{ch!r}  {n:4d}  U+{ord(ch):04X}")
        return 0
    else:
        if not args:
            print(__doc__); return 2
        problems = []
        for p in args:
            problems += check_chars(p) + check_markers(p) + check_links(p)
    for line in problems:
        print(line)
    print(f"-- 문제 {len(problems)}건")
    return 1 if problems else 0

if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
