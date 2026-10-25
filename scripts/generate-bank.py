"""Deterministic, internally reviewed teaching models; no historical exam claims.
20 explicitly simplified calculation families × 50 condition sets. No legal limits.
"""
import json
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
SUBJECTS = ['산업재해 예방 및 안전보건교육','인간공학 및 위험성 평가·관리','건설재료','건설시공','건설공사 안전관리']
# kind, subject, topic, question template, formula text, unit, inputs+result
FAMILIES = [
('frequency',0,'재해지표','총 근로시간이 {b}시간이고 재해 건수가 {a}건이다. 100만 근로시간당 재해 건수로 정의한 도수율은?','도수율 = 재해 건수 × 1,000,000 / 총 근로시간','',lambda i:(i+1,1000000,(i+1))),
('severity',0,'재해지표','총 근로시간이 {b}시간이고 근로손실일수가 {a}일이다. 1,000 근로시간당 손실일수로 정의한 강도율은?','강도율 = 손실일수 × 1,000 / 총 근로시간','',lambda i:((i+1)*10,100000,(i+1)/10)),
('education',0,'교육 이수율','교육 대상자가 {b}명이고 이수자가 {a}명이다. 이수율은 몇 %인가?','이수율 = 이수자 / 대상자 × 100','%',lambda i:((i+1)*2,200,i+1)),
('reduction',0,'예방 성과','동일한 노출 조건에서 개선 전 사고가 {b}건, 개선 후 사고가 {a}건이다. 사고 건수 감소율은?','감소율 = (개선 전 − 개선 후) / 개선 전 × 100','%',lambda i:(100-(i+1),100,i+1)),
('risk',1,'위험성 추정','이 학습 모형에서는 위험도를 가능성 점수 × 중대성 점수로 정의한다. 가능성이 {a}, 중대성이 {b}이면 위험도는?','위험도 = 가능성 × 중대성. 법정 점수 체계를 뜻하지 않는다.','점',lambda i:(i+1,3,(i+1)*3)),
('moment',1,'정적 부하','수평 팔에 수직으로 작용하는 힘이 {a} N이고 회전축에서 작용점까지 거리가 {b} m이다. 축에 대한 모멘트 크기는?','모멘트 = 수직 힘 × 수평 거리','N·m',lambda i:((i+1)*10,0.5,(i+1)*5)),
('rest',1,'작업 시간 배분','한 주기의 총 시간이 {b}분이고 휴식이 {a}분이다. 이 주기에서 휴식 시간이 차지하는 비율은?','휴식 비율 = 휴식 시간 / 총 주기 시간 × 100','%',lambda i:(i+1,100,i+1)),
('parallel',1,'신호 인지 모형','독립인 두 감지 장치가 각각 위험 신호를 놓칠 확률이 {a} 및 {b}이다. 두 장치가 모두 놓칠 확률을 %로 나타내면?','독립 사건의 동시 누락 확률 = 두 누락 확률의 곱. 백분율로 바꾸려면 100을 곱한다.','%',lambda i:((i+1)/100,0.2,(i+1)/5)),
('density',2,'밀도','균질한 건설재료 시료의 질량이 {a} kg, 부피가 {b} m³이다. 밀도는?','밀도 = 질량 / 부피','kg/m³',lambda i:((i+1)*20,0.5,(i+1)*40)),
('stress',2,'압축응력','균일 압축하중 {a} N이 단면적 {b} mm²에 작용한다. 평균 압축응력은?','응력 = 하중 / 단면적. 1 N/mm² = 1 MPa.','MPa',lambda i:((i+1)*1000,100,(i+1)*10)),
('water',2,'물 결합재비','혼합물의 물 질량은 {a} kg, 결합재 질량은 {b} kg이다. 질량 기준 물 결합재비는?','물 결합재비 = 물 질량 / 결합재 질량 × 100','%',lambda i:(50+i,200,(50+i)/2)),
('strain',2,'축변형률','원래 길이가 {b} mm인 시험편이 {a} mm 늘었다. 공학적 변형률을 %로 표시하면?','공학적 변형률 = 길이 변화 / 원래 길이 × 100','%',lambda i:(i+1,10000,(i+1)/100)),
('volume',3,'콘크리트 물량','일정한 직사각형 단면 부재의 단면적은 {a} m²이고 길이는 {b} m이다. 손실을 무시한 콘크리트 부피는?','부피 = 일정한 단면적 × 길이','m³',lambda i:((i+1)/10,10,i+1)),
('productivity',3,'시공 생산성','일정한 작업 속도로 {a} m³를 {b}시간 동안 시공했다. 시간당 평균 시공량은?','평균 생산성 = 시공량 / 작업 시간','m³/h',lambda i:((i+1)*8,8,i+1)),
('duration',3,'공정 소요시간','총 작업량은 {a} m³이고 일정 생산성이 {b} m³/h이다. 중단 없는 작업의 소요시간은?','소요시간 = 총 작업량 / 시간당 생산성','h',lambda i:((i+1)*12,12,i+1)),
('swell',3,'토공 물량','자연 상태 토량은 {a} m³이고, 굴착 후 부피/자연 상태 부피로 정의한 팽창계수는 {b}이다. 굴착 후 부피는?','굴착 후 부피 = 자연 상태 부피 × 팽창계수','m³',lambda i:((i+1)*10,1.2,(i+1)*12)),
('factor',4,'안정 검토 모형','단순 학습 모형에서 저항력은 {a} kN, 작용력은 {b} kN이다. 저항력/작용력으로 정의한 안전율은?','안전율 = 저항력 / 작용력. 계산값만으로 법정 적합 여부를 판단하지 않는다.','',lambda i:((i+1)*30,20,(i+1)*1.5)),
('pressure',4,'지반 접지압','수직 하중이 {a} kN이고 균일 접촉 면적이 {b} m²이다. 편심을 무시한 평균 접지압은?','평균 접지압 = 수직 하중 / 접촉 면적. 1 kN/m² = 1 kPa.','kPa',lambda i:((i+1)*40,4,(i+1)*10)),
('energy',4,'낙하 에너지','질량 {a} kg의 물체가 높이 {b} m에서 정지 상태로 낙하한다. g=10 m/s², 저항 무시 시 낙하 직전 운동에너지는?','위치에너지 mgh가 운동에너지로 전환된다. E = 질량 × 10 × 높이. 실제 충격력은 정지거리 등 추가 조건이 필요하다.','J',lambda i:(i+1,5,(i+1)*50)),
('rope',4,'인양 분담 모형','총 수직 하중이 {a} kN이다. 수직이고 동일하게 하중을 분담하는 줄 {b}가닥 각각의 장력은? 줄 무게와 동적 효과는 무시한다.','줄당 장력 = 총 하중 / 수직 줄 수. 경사 줄에는 이 식을 그대로 적용하지 않는다.','kN',lambda i:((i+1)*4,4,i+1)),
]
def fmt(x): return f'{x:.6f}'.rstrip('0').rstrip('.') if isinstance(x,float) else str(x)
bank=[]
for fi,(kind,si,topic,stem,formula,unit,make) in enumerate(FAMILIES):
 for i in range(50):
  a,b,result=make(i); result=round(result,6)
  vals=[result,round(result+1,6),round(result+2,6),round(result+3,6)]
  shift=(i+fi)%4; vals=vals[shift:]+vals[:shift]
  answer=vals.index(result)+1
  q={'id':f'CS-{kind}-{i+1:03}', 'subject':SUBJECTS[si], 'topic':topic,
   'question':stem.format(a=fmt(a),b=fmt(b)), 'choices':[f'{fmt(v)} {unit}'.strip() for v in vals],
   'answer':answer,'explanation':f'조건: a={fmt(a)}, b={fmt(b)}. {formula} 계산 결과는 {fmt(result)} {unit}이다. 명시된 이상화 조건에 한정한 자체 제작 계산 변형이다.',
   'difficulty':'하','year':None,'session':None,'type':'original',
   'sourceUrl':'https://github.com/YunSangYeong/Engineer-Construction-Safety-CBT/blob/main/scripts/generate-bank.py',
   'verificationStatus':'reviewed','reviewNote':'AI 일반 지식의 기초 공식으로 자체 작성. 20개 템플릿의 조건·단위·해설을 내부 검토하고 별도 역산 테스트로 수치·정답·보기를 검증. 외부 자료 대조·전문가 검수·공식 출제기준 대조는 미완료. URL은 작성 위치이며 외부 정답 증빙이 아님.',
   'version':'main','rights':'자체 제작 원고: CC BY 4.0, Engineer-Construction-Safety-CBT contributors. 외부 기출을 복제하지 않음.',
   'family':kind,'calculation':{'kind':kind,'values':[a,b],'result':result,'unit':unit}}
  bank.append(q)
(ROOT/'src/data/questions-main.json').write_text(json.dumps(bank,ensure_ascii=False,indent=2)+'\n')
(ROOT/'public/templates/questions.json').write_text(json.dumps([{**bank[0],'id':'LOCAL-EXAMPLE','verificationStatus':'pending'}],ensure_ascii=False,indent=2)+'\n')
import csv
q=bank[0]; fields=[k for k in q if k not in ['choices','calculation','family']]; fields[fields.index('answer'):fields.index('answer')]=['choice1','choice2','choice3','choice4']
with (ROOT/'public/templates/questions.csv').open('w',newline='') as f:
 w=csv.DictWriter(f,fieldnames=fields,lineterminator="\n");w.writeheader();w.writerow({**{k:q[k] for k in fields if k in q},**{f'choice{i+1}':v for i,v in enumerate(q['choices'])},'verificationStatus':'pending','id':'LOCAL-CSV-EXAMPLE','question':'등록 양식 예시: 근로시간 100만 시간에 재해가 1건이면 도수율은?'})
print(f'{len(bank)} questions / {len(FAMILIES)} families / 50 conditions each')
