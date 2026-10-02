from pathlib import Path
from datetime import datetime
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"13_MANAGEMENT"/"MONTHLY"; OUT.mkdir(parents=True,exist_ok=True)
out=OUT/f"monthly_quality_management_{datetime.now().strftime('%Y%m')}.md"
out.write_text(f"""# 월간 품질·생산 관리 보고

- 작성월: {datetime.now().strftime('%Y-%m')}

## 1. 목표 PPM 대비 실적
데이터 입력 필요

## 2. 고객사별 PPM
데이터 입력 필요

## 3. 차종/품번별 주요 불량
데이터 입력 필요

## 4. 전월 대비 증감
데이터 입력 필요

## 5. 개선과제 진행률
데이터 입력 필요

## 6. 담당자 / 완료일
데이터 입력 필요

## 7. 임원 결정 필요사항
데이터 입력 필요
""",encoding="utf-8")
print(out)
