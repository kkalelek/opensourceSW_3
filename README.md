# 강의실 가용성 조회 백엔드

## 프로젝트 개요

이 프로젝트는 CSV 시간표 파일을 읽어서 `IT융합대학`의 강의실 사용 가능 여부를 조회하는 `FastAPI` 백엔드입니다.

현재는 백엔드만 구현되어 있으며, 아래 기능을 지원합니다.

- 현재 시간 기준 강의실 상태 조회
- 특정 시간 구간 기준 사용 가능한 강의실 조회
- 강의실 상태를 `white`, `yellow`, `green`으로 분류

이 프로젝트는 `database`를 사용하지 않고, 제공된 CSV 파일만 데이터 소스로 사용합니다.

## 현재 구현 범위

현재 구현된 내용은 아래와 같습니다.

- `Python + FastAPI` 기반 백엔드
- CSV 파일 로딩 및 파싱
- `시간` 컬럼 파싱을 통한 요일, 시작 시간, 종료 시간, 장소 추출
- 장소 문자열에 `IT융합대학`이 포함된 항목만 사용
- 현재 시간 기준 강의실 상태 조회 API
- 특정 시간 구간 기준 사용 가능한 강의실 조회 API
- `pytest` 기반 핵심 로직 테스트

아직 구현하지 않은 내용은 아래와 같습니다.

- 다른 건물 지원
- 로그인 / 인증
- 프론트엔드 UI
- 시험, 행사, 공사 등 예외 일정 처리
- 강의실 수용 인원 / 장비 정보

## 폴더 구조

```text
backend/
  app/
    data/
      timetable_it.csv
    routers/
      availability.py
    schemas/
      availability.py
    services/
      timetable_service.py
    utils/
      constants.py
      parsers.py
      time_utils.py
    main.py
  tests/
    conftest.py
    test_parsers.py
    test_timetable_service.py
requirements.txt
README.md
```

## 설치 방법

아래 순서대로 진행하면 됩니다.

### 1. 프로젝트 폴더로 이동

```powershell
cd C:\Users\skary\Desktop\project
```

### 2. 가상환경 생성

```powershell
python -m venv .venv
```

### 3. 가상환경 활성화

```powershell
.\.venv\Scripts\Activate.ps1
```

### 4. `pip` 업그레이드

```powershell
python -m pip install --upgrade pip
```

### 5. 필요한 패키지 설치

```powershell
python -m pip install -r requirements.txt
```

## 서버 실행 방법

프로젝트 루트에서 아래 명령어를 실행합니다.

```powershell
python -m uvicorn app.main:app --reload --app-dir backend
```

서버가 실행되면 기본 주소는 아래와 같습니다.

- `http://127.0.0.1:8000`
- Swagger 문서: `http://127.0.0.1:8000/docs`

## 테스트 실행 방법

프로젝트 루트에서 아래 명령어를 실행합니다.

```powershell
python -m pytest backend/tests
```

특정 테스트 파일만 실행하고 싶다면 아래처럼 실행할 수 있습니다.

```powershell
python -m pytest backend/tests/test_timetable_service.py
```

## API 설명

### 1. 서버 확인

- Method: `GET`
- Path: `/`
- 설명: 서버가 정상 실행 중인지 확인합니다.

### 2. CSV 파싱 요약 확인

- Method: `GET`
- Path: `/api/availability/summary`
- 설명: CSV에서 파싱된 엔트리 수와 샘플 데이터를 확인합니다.

### 3. 현재 시간 기준 강의실 상태 조회

- Method: `GET`
- Path: `/api/buildings/{building}/available-now`
- 설명: 현재 시각 기준으로 각 공간의 상태를 반환합니다.

상태 기준은 아래와 같습니다.

- `white`: 현재 수업 중
- `yellow`: 현재 수업은 없지만 다음 수업까지 60분 미만
- `green`: 현재 수업이 없고 다음 수업까지 60분 이상이거나 오늘 더 이상 수업이 없음

### 4. 특정 시간 구간 기준 사용 가능한 강의실 조회

- Method: `GET`
- Path: `/api/buildings/{building}/available-range`
- Query:
  - `day=MON`
  - `start=14:00`
  - `end=16:00`
- 설명: 요청한 시간 구간과 겹치는 수업이 없는 공간만 반환합니다.

## 예시 요청/응답

### 현재 시간 기준 조회 예시

요청:

```http
GET /api/buildings/IT융합대학/available-now
```

응답 예시:

```json
{
  "building": "IT융합대학",
  "day": "MON",
  "query_time": "14:30",
  "rooms": [
    {
      "room": "IT융합대학-공용PC실1(3208)",
      "status": "yellow",
      "current_course_name": null,
      "current_class_end": null,
      "next_course_name": "객체지향프로그래밍",
      "next_class_start": "15:00"
    },
    {
      "room": "IT융합대학3224 강의실",
      "status": "white",
      "current_course_name": "AI디지털미디어",
      "current_class_end": "15:00",
      "next_course_name": null,
      "next_class_start": null
    }
  ]
}
```

### 특정 시간 구간 조회 예시

요청:

```http
GET /api/buildings/IT융합대학/available-range?day=MON&start=14:00&end=16:00
```

응답 예시:

```json
{
  "building": "IT융합대학",
  "day": "MON",
  "start": "14:00",
  "end": "16:00",
  "rooms": [
    {
      "room": "IT융합대학-공용PC실2(3210)"
    },
    {
      "room": "IT융합대학-SW융합교육원 PC 1실(1209)"
    }
  ]
}
```

### 잘못된 요청 예시

요청:

```http
GET /api/buildings/본관/available-range?day=MON&start=14:00&end=16:00
```

응답 예시:

```json
{
  "detail": "Only IT융합대학 is supported."
}
```

## 현재 한계점

현재 버전의 한계는 아래와 같습니다.

- `IT융합대학`만 지원합니다.
- CSV 파일에 있는 정보만 사용합니다.
- `강의실` 컬럼은 비어 있으므로 사용하지 않고, `시간` 컬럼을 파싱해서 처리합니다.
- 시험, 행사, 공사 같은 예외 상황은 반영하지 않습니다.
- 현재 시간 기준 조회는 `Asia/Seoul` 시간대를 기준으로 동작합니다.
- 프론트엔드는 포함되어 있지 않습니다.

## 참고 사항

- 시간 비교는 문자열 비교가 아니라 `Python datetime/time` 기반으로 처리합니다.
- 장소 문자열은 응답에서 원문을 최대한 유지합니다.
- 현재 지원하는 `building` 값은 `IT융합대학` 하나뿐입니다.
