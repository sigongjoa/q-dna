# Contributing Guidelines

## 1. 코드 컨벤션

### Python (Backend)
- **Style Guide**: PEP 8을 준수합니다.
- **Formatter**: `black`을 사용합니다.
- **Linter**: `flake8` 또는 `ruff`를 사용합니다.
- **Type Hinting**: 모든 함수 인자와 반환값에 타입을 명시해야 합니다.
  ```python
  def calculate_score(correct: int, total: int) -> float:
      ...
  ```

### TypeScript/React (Frontend)
- **Style Guide**: Airbnb Style Guide를 기반으로 합니다.
- **Formatter**: `Prettier`를 사용합니다.
- **Linter**: `ESLint`를 사용합니다.
- **Component Naming**: PascalCase (e.g., `QuestionCard.tsx`)
- **Hook Naming**: useCamelCase (e.g., `useAuth.ts`)

## 2. Git 워크플로우
본 프로젝트는 **Gitflow** 또는 **Feature Branch** 전략을 따릅니다.

### 브랜치 명명 규칙
- `main` : 배포 가능한 안정 버전 (Production)
- `develop` : 개발 중인 버전 (Staging)
- `feature/기능명` : 새로운 기능 개발 (e.g., `feature/login-page`)
- `bugfix/이슈명` : 버그 수정 (e.g., `bugfix/ocr-error`)
- `hotfix/이슈명` : 긴급 수정

### PR (Pull Request) 프로세스
1. Issue 생성 (작업 내용 정의)
2. Branch 생성 (`feature/...`)
3. 개발 및 테스트
4. PR 생성 (`develop` 브랜치로)
5. 코드 리뷰 (최소 1명 이상의 승인 필요)
6. Merge & Delete Branch

## 3. 커밋 메시지 규칙
Conventional Commits 규칙을 따릅니다.
- `feat`: 새로운 기능
- `fix`: 버그 수정
- `docs`: 문서 수정
- `style`: 코드 포맷팅 (로직 변경 없음)
- `refactor`: 리팩토링
- `test`: 테스트 코드
- `chore`: 빌드 업무 수정, 패키지 매니저 설정 등

예시: `feat: add user login API`
