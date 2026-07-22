# tech-doc-kr

한국어 기술 문서에서 번역투와 기계 생성 신호를 걷어내는 Claude Code 스킬.

A Claude Code skill that removes translationese and AI-tells from Korean tech writing (PRs, READMEs, docs, blog posts).

## 무엇을 하나

AI와 함께 기술 문서를 쓰면 이런 문장이 생긴다:

> "모든 sink가 내던 **세금** 두 개" (tax)
> "Sendable 판정은 **움직이는 과녁**이다" (moving target)
> "이 문으로 들어간 작업은 **고아**가 된다" (orphan)

영어 기술 문서에서는 자연스러운 관용구인데, 한국어로 직역하면 아무도 안 쓰는 말이 된다.
이 스킬은 실제 문서 교정에서 독자 피드백으로 검증된 규칙으로 이런 표현을 찾아 고친다.

**6대 규칙** (상세: [rules.md](.claude/skills/tech-doc-kr/references/rules.md))

1. **영어 관용구 직역 금지** - 판별 기준: "한국 개발자가 실제로 입에 올리는 말인가?" ([블랙리스트](.claude/skills/tech-doc-kr/references/calque-blacklist.md))
2. **개념어는 영어 그대로** - 한국어 명사를 발명하지 않는다 (single-flight를 "단일 비행"으로 옮기지 않는다). 첫 등장에만 한국어 풀이
3. **역할 별명 대신 코드 실명** - "엔진"이 아니라 `NetworkSession`. 문서 어휘 = 코드 어휘
4. **형식** - 비키보드 특수문자 0, 문답/면접 프레임 금지, 압축 명사구 제목 금지
5. **구조** - 본문과 겹치는 절 삭제, 문서 밖 참조 금지
6. **검증 루프** - 지적 1곳 = 같은 패턴 전수 검색. 교정 후 기계 검증(특수문자/마커/링크/코드펜스)

기술 스택과 무관하게 적용된다 - iOS, 웹, 백엔드 어디든 같은 규칙이다.

## 설치

```
claude
/plugin marketplace add Jeon0976/tech-doc-kr
/plugin install tech-doc-kr@tech-doc-kr
```

## 사용

```
/tech-doc-kr docs/notes/my-note.md
```

또는 자연어로: "이 README 번역투 잡아줘", "PR 본문 정리해줘".

- **파이프라인 모드 (기본)**: 탐지(tell-detector) -> 교정(doc-rewriter) -> 검증(doc-verifier) 에이전트 분업. 긴 문서/문서군에 적합
- **경량 모드**: 본체가 직접 수행. 짧은 입력(PR 본문 등)이나 재교정에 적합. 시작할 때 물어본다

## 불변 조건

- 의미/사실/수치는 한 글자도 바꾸지 않는다 - 표현만 고친다
- 코드블록/표/링크 보존. 레포 실코드 인용은 특수문자까지 소스와 일치 유지
- 문체(반말/존댓말) 유지

## 검증 스크립트 단독 사용

```bash
python3 scripts/verify.py docs/*.md            # 특수문자/마커/링크 검사
python3 scripts/verify.py --scan docs/*.md     # 비키보드 문자 빈도표
python3 scripts/verify.py --baseline old.md new.md   # 코드펜스 훼손 검사
```

표준 라이브러리만 사용한다.

## License

MIT
