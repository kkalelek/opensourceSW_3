# 강의실 가용성 조회 백엔드

## 프로젝트 개요

이 프로젝트는 CSV 시간표 파일을 읽어서 `IT융합대학` 강의실의 현재 사용 가능 여부와 특정 시간대 사용 가능 여부를 조회하는 `FastAPI` 백엔드입니다.

기본 시간표 조회는 계속 `backend/app/data/timetable_it.csv`를 직접 읽어서 계산합니다. MySQL은 시간표 전체를 저장하거나 조회하는 용도가 아니라, 관리자 계정과 관리자가 임시로 수정한 강의실 표시 상태만 저장하는 용도로 사용합니다.

색상 규칙은 기존과 동일하게 `white / yellow / green`만 사용합니다. 

## 현재 구현 범위

- `Python + FastAPI` 기반 백엔드
- CSV 파일 로딩 및 파싱
- 현재 시간 기준 강의실 상태 조회 API
- 특정 시간 구간 기준 사용 가능한 강의실 조회 API
- 현재 비어 있는 강의실이 몇 시까지 사용 가능한지 표시
- 관리자 로그인
- 관리자 강의실 실시간 상태 수정, 조회, 삭제
- `pytest` 기반 핵심 로직 테스트

아직 구현하지 않은 내용은 아래와 같습니다.

- 다른 건물 지원
- 일반 사용자 회원가입 / 로그인
- 프론트엔드 UI
- WebSocket 같은 별도 실시간 통신
- 시험, 행사, 공사 등 예외 일정 처리
- 강의실 수용 인원 / 장비 정보

## 담당 범위

### 백엔드 담당

- CSV 기반 기본 시간표 조회 로직 유지
- 관리자 로그인 API 제공
- 관리자 override 데이터를 MySQL에 저장하고 조회
- `available-now` 응답에서 CSV 기본 상태와 관리자 수정 최종 상태를 함께 반환

### 프론트엔드 담당

- 일반 사용자는 기존 조회 API를 호출
- 관리자는 로그인 후 발급받은 access token을 사용
- 화면 자동 갱신은 일정 시간마다 `available-now` API를 다시 호출하는 방식으로 구현
- 새 응답 필드인 `base_status`, `is_overridden`, `override_status`, `available_until`, `availability_message` 등을 화면에 반영

### DB 담당

- MySQL에 `empty_classroom` 데이터베이스 준비
- `database/admin_override_schema.sql` 실행
- `admins`, `room_status_overrides` 테이블과 컬럼 확인
- 실제 운영 `.env`에 사용할 DB 접속 계정 제공

## 폴더 구조

```text
backend/
  app/
    data/
      timetable_it.csv
    dependencies/
      admin.py
    repositories/
      admin_repository.py
      mysql_admin_repository.py
    routers/
      admin.py
      availability.py
    schemas/
      availability.py
    services/
      timetable_service.py
    utils/
      constants.py
      parsers.py
      security.py
      time_utils.py
    main.py
  scripts/
    create_admin.py
  tests/
    conftest.py
    test_admin_overrides.py
    test_parsers.py
    test_timetable_service.py
database/
  admin_override_schema.sql
frontend/
  public/
  src/
  package.json
  package-lock.json
.env.example
requirements.txt
README.md
```

## 설치 방법

프로젝트 루트에서 진행합니다.

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

`requirements.txt`에는 FastAPI 실행과 테스트에 필요한 패키지 외에 MySQL 접속용 `PyMySQL`이 포함되어 있습니다. 비밀번호 해시와 Bearer 토큰 생성은 Python 표준 라이브러리로 처리합니다.

## MySQL 테이블 생성

MySQL에 접속한 뒤 아래 SQL 파일을 실행합니다.

```powershell
mysql -u root -p < database/admin_override_schema.sql
```

생성 또는 확인해야 하는 테이블은 아래 두 개입니다.

### `admins`

- `id`: 관리자 고유 ID
- `username`: 관리자 로그인 ID, 중복 불가
- `password_hash`: 평문 비밀번호가 아닌 해시값
- `is_active`: 관리자 활성 여부
- `created_at`: 생성 시각

### `room_status_overrides`

- `id`: override 고유 ID
- `building`: 건물명, 현재는 `IT융합대학`
- `room`: `available-now` 응답에 나오는 원문 강의실 문자열
- `override_status`: `occupied` 또는 `available`
- `reason`: 관리자 입력 사유, 선택값
- `expires_at`: 관리자 수정 종료 시각, 선택값
- `updated_by`: 수정한 관리자 ID
- `created_at`: 생성 시각
- `updated_at`: 수정 시각

`building`, `room` 조합에는 하나의 override만 존재하도록 UNIQUE 제약이 있습니다.

## `.env` 설정

`.env.example`을 참고해서 프로젝트 루트에 `.env` 파일을 만듭니다. 실제 비밀번호와 실제 토큰 secret은 README에 적지 않습니다.

```powershell
Copy-Item .env.example .env
```

예시 형식:

```env
MYSQL_HOST=127.0.0.1
MYSQL_PORT=3306
MYSQL_USER=empty_classroom_user
MYSQL_PASSWORD=change-this-password
MYSQL_DATABASE=empty_classroom

ADMIN_TOKEN_SECRET=replace-with-a-long-random-secret
ADMIN_TOKEN_EXPIRE_MINUTES=120

FRONTEND_ORIGINS=http://localhost:5173
```

`.env` 파일은 `.gitignore`에 포함되어 있으므로 Git에 올리지 않습니다.

`MYSQL_USER=empty_classroom_user`를 그대로 사용할 경우 DB 담당자가 MySQL에서 해당 사용자와 권한을 만들어야 합니다. 개발 중에는 본인이 사용할 수 있는 MySQL 계정을 `.env`에 설정해도 됩니다.

`FRONTEND_ORIGINS`는 브라우저 CORS 요청을 허용할 프론트엔드 주소입니다. 개발 기본 예시는 Vite 개발 서버인 `http://localhost:5173`입니다. 여러 개를 허용하려면 쉼표로 구분합니다.

```env
FRONTEND_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
```

공유하거나 압축 파일에 포함하지 않아야 하는 항목:

- `.env`
- `.venv/`
- `.pytest_cache/`
- `__pycache__/`
- `frontend/node_modules/`
- `frontend/node_modules.zip`

루트의 `tests/` 폴더는 사용하지 않습니다. 테스트는 `backend/tests/`에만 두어 전체 `pytest` 실행 시 중복 수집 충돌이 나지 않게 관리합니다.

## 최초 관리자 계정 생성

MySQL 테이블 생성과 `.env` 설정을 마친 뒤 실행합니다.

```powershell
python backend/scripts/create_admin.py --username admin
```

비밀번호는 프롬프트에 입력합니다. 자동화가 꼭 필요할 때만 아래처럼 명령행 인자로 전달할 수 있습니다.

```powershell
python backend/scripts/create_admin.py --username admin --password 임시비밀번호
```

비밀번호는 DB에 평문이 아니라 PBKDF2 기반 해시값으로 저장됩니다.

## 서버 실행 방법

```powershell
python -m uvicorn app.main:app --reload --app-dir backend
```

서버 주소:

- `http://127.0.0.1:8000`
- Swagger 문서: `http://127.0.0.1:8000/docs`

## 테스트 실행 방법

```powershell
python -m pytest backend/tests
```

테스트는 실제 MySQL 데이터를 오염시키지 않도록 fake repository를 사용합니다.

## Swagger에서 관리자 기능 확인 순서

1. `POST /api/admin/login`으로 관리자 로그인
2. 응답의 `access_token` 복사
3. Swagger 우측 상단 `Authorize` 클릭
4. Swagger 입력칸에는 `access_token` 값만 붙여넣기
5. `PUT /api/admin/room-status-override`로 강의실 상태 수정
6. `GET /api/buildings/IT융합대학/available-now`를 호출해서 일반 사용자 조회 결과에 override가 반영되는지 확인
7. 필요하면 `DELETE /api/admin/room-status-override`로 관리자 수정을 취소

직접 HTTP 요청을 작성할 때만 아래처럼 `Bearer` 형식을 사용합니다.

```http
Authorization: Bearer <access_token>
```

## API 설명

### 서버 확인

- Method: `GET`
- Path: `/`

응답:

```json
{
  "message": "Classroom Availability API is running."
}
```

### CSV 파싱 요약 확인

- Method: `GET`
- Path: `/api/availability/summary`

### 현재 시간 기준 강의실 상태 조회

- Method: `GET`
- Path: `/api/buildings/{building}/available-now`
- 인증: 필요 없음

상태 기준:

- `white`: 시간표상 현재 수업 중인 강의실 또는 관리자 override가 `occupied`
- `yellow`: 현재 비어 있고 다음 수업까지 1시간 미만
- `green`: 현재 비어 있고 다음 수업까지 1시간 이상, 오늘 남은 수업 없음, 또는 관리자 override가 `available`

응답 예시:

```json
{
  "building": "IT융합대학",
  "day": "MON",
  "query_time": "14:30",
  "rooms": [
    {
      "room": "IT융합대학-공용PC실1(3208)",
      "status": "green",
      "base_status": "white",
      "current_course_name": "객체지향프로그래밍",
      "current_class_end": "15:00",
      "next_course_name": null,
      "next_class_start": null,
      "available_until": "17:00",
      "availability_message": "17:00까지 사용 가능 (관리자 수정)",
      "is_overridden": true,
      "override_status": "available",
      "override_reason": "수업 취소",
      "override_expires_at": "2099-05-18T17:00:00"
    }
  ]
}
```

관리자 수정이 없으면 `base_status`와 `status`는 같습니다.

### 특정 시간 구간 기준 사용 가능한 강의실 조회

- Method: `GET`
- Path: `/api/buildings/{building}/available-range`
- 인증: 필요 없음
- Query:
  - `day=MON`
  - `start=14:00`
  - `end=16:00`

이 API는 CSV 시간표 기준으로 동작하며, 관리자 override 로직을 적용하지 않습니다.

### 관리자 로그인

- Method: `POST`
- Path: `/api/admin/login`

요청:

```json
{
  "username": "admin",
  "password": "관리자비밀번호"
}
```

응답:

```json
{
  "access_token": "발급된토큰",
  "token_type": "bearer"
}
```

### 관리자 override 목록 조회

- Method: `GET`
- Path: `/api/admin/room-status-overrides`
- 인증: 관리자 Bearer 토큰 필요

응답:

```json
{
  "overrides": [
    {
      "id": 1,
      "building": "IT융합대학",
      "room": "IT융합대학-공용PC실1(3208)",
      "override_status": "occupied",
      "reason": "동아리 사용",
      "expires_at": null,
      "updated_by": 1,
      "created_at": "2026-05-18T14:00:00",
      "updated_at": "2026-05-18T14:00:00"
    }
  ]
}
```

### 관리자 override 생성 또는 수정

- Method: `PUT`
- Path: `/api/admin/room-status-override`
- 인증: 관리자 Bearer 토큰 필요

요청:

```json
{
  "building": "IT융합대학",
  "room": "IT융합대학-공용PC실1(3208)",
  "override_status": "available",
  "reason": "수업 취소",
  "expires_at": "2099-05-18T17:00:00"
}
```

`override_status`는 `occupied` 또는 `available`만 가능합니다.
`room`은 `available-now` 응답에 나오는 원문 강의실 문자열과 정확히 일치해야 합니다. CSV에서 파싱된 IT융합대학 강의실 목록에 없는 값이면 요청이 실패합니다.
`expires_at`은 Asia/Seoul 기준입니다. timezone 정보가 없는 값은 Seoul 현지 시간으로 해석하고, timezone 정보가 있는 값은 저장 전에 Seoul 시간으로 정규화합니다. 이미 지난 시간은 새 override로 저장할 수 없습니다.

### 관리자 override 삭제

- Method: `DELETE`
- Path: `/api/admin/room-status-override`
- 인증: 관리자 Bearer 토큰 필요

요청:

```json
{
  "building": "IT융합대학",
  "room": "IT융합대학-공용PC실1(3208)"
}
```

응답:

```json
{
  "deleted": true
}
```

삭제 후에는 기존 CSV 시간표 계산 상태가 그대로 반환됩니다.

## 프론트엔드 담당자가 사용할 필드

- `base_status`: CSV 시간표 기준 원래 상태
- `status`: 화면에 최종 표시할 상태
- `is_overridden`: 관리자 수정 적용 여부
- `override_status`: `occupied`, `available`, 또는 `null`
- `override_reason`: 관리자 입력 사유 또는 `null`
- `override_expires_at`: 관리자 수정 종료 시각 또는 `null`
- `available_until`: 현재 비어 있는 강의실의 사용 가능 종료 시간 또는 `null`
- `availability_message`: 화면에 바로 표시할 안내 문구

관리자 override가 `occupied`이면 최종 `status`는 `white`이고, `availability_message`는 `"관리자에 의해 사용 중으로 변경됨"`입니다.

관리자 override가 `available`이고 `expires_at`이 있으면 최종 `status`는 `green`, `available_until`은 종료 시간의 `HH:MM`, `availability_message`는 `"HH:MM까지 사용 가능 (관리자 수정)"`입니다.

관리자 override가 `available`이고 `expires_at`이 없으면 최종 `status`는 `green`, `availability_message`는 `"관리자에 의해 사용 가능으로 변경됨"`입니다.

`override_expires_at`은 Asia/Seoul 기준으로 반환됩니다. 요청에 timezone이 포함되어 있으면 Seoul 시간으로 변환된 값이 저장되고, timezone이 없으면 처음부터 Seoul 시간으로 입력한 것으로 봅니다.

## 현재 한계점

- `IT융합대학`만 지원합니다.
- 기본 시간표는 CSV 파일에 있는 정보만 사용합니다.
- 관리자 override는 일반 사용자 조회 API 중 `available-now`에만 반영됩니다.
- `available-range`는 기존 CSV 기준 동작을 유지합니다.
- 프론트엔드 자동 갱신은 백엔드가 아니라 프론트엔드에서 주기적으로 조회하는 방식으로 처리합니다.
