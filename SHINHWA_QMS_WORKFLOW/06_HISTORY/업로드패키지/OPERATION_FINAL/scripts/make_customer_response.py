from pathlib import Path
from datetime import datetime
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"15_CUSTOMER_RESPONSE"; OUT.mkdir(parents=True,exist_ok=True)
pkg=OUT/f"HANON_RESPONSE_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
pkg.mkdir(parents=True,exist_ok=True)
(pkg/"CUSTOMER_RESPONSE_TEMPLATE.md").write_text("""# 고객사 품질 대응자료

고객사: 한온시스템

## 1. 문제현상
입력 필요

## 2. 대상 품번 / LOT
입력 필요

## 3. LOT 추적 결과
입력 필요

## 4. 원인분석
입력 필요

## 5. 임시조치
입력 필요

## 6. 영구대책
입력 필요

## 7. 재발방지
입력 필요

## 8. 증빙자료
첨부 필요

## 9. 담당자 / 완료일
입력 필요
""",encoding="utf-8")
print(pkg)
