# NEOCODE 홈페이지

NEOCODE의 한국어·영어 정적 홈페이지입니다. 빌드 과정 없이 `index.html`에서 시작합니다.

## 로컬 실행

```sh
python -m http.server 4173
```

브라우저에서 `http://localhost:4173/`을 엽니다.

## 구성

- `index.html`: 화면 구성과 한국어·영어 문구
- `style.css`, `dark.css`, `redesign.css`: 반응형 다크 테마
- `app.js`: 언어 전환, 모바일 메뉴, 문의 폼
- `motion.js`: 스크롤 페이드인 효과
- `media/`: 시연용 주식 차트 영상과 포스터
- `make_chart_video.py`: 차트 영상 생성 스크립트

문의 폼은 FormSubmit을 통해 `neocode.kr@gmail.com`으로 전송합니다. 영상의 차트는 시연용이며 실제 시장 데이터가 아닙니다.
