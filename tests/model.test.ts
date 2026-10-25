import { describe, it, expect } from 'vitest';
import { BASE_BANK, SUBJECTS, validateQuestion, fingerprint, createExam, grade, emptyStore, answerExam, submitExam, restoreStore, startPractice, checkPractice, nextPractice, importQuestions, parseCsv, STORAGE_KEY } from '../src/model';
import { PROFILE } from '../src/qualification';
import { readFileSync } from 'node:fs';
import { execFileSync } from 'node:child_process';
const near=(a:number,b:number)=>expect(a).toBeCloseTo(b,6);
describe('independent inverse checks of every numerical variant',()=>{
 for(const q of BASE_BANK) it(q.id,()=>{
  validateQuestion(q);
  const c=q.calculation!; const [a,b]=c.values;
  const selected=Number(q.choices[q.answer-1].split(' ')[0]);
  near(selected,c.result); expect(new Set(q.choices).size).toBe(4);
  expect(q.year).toBeNull(); expect(q.session).toBeNull();
  // Reverse equations, rather than importing the generator's functions.
  switch(c.kind){
   case 'frequency': near(selected*b/1e6,a); break;
   case 'severity': near(selected*b/1e3,a); break;
   case 'education': case 'rest': case 'water': case 'strain': near(selected*b/100,a); break;
   case 'reduction': near(b*(1-selected/100),a); break;
   case 'risk': case 'moment': case 'volume': case 'swell': near(selected/b,a); break;
   case 'parallel': near(selected/100/b,a); break;
   case 'density': case 'stress': case 'productivity': case 'duration': case 'factor': case 'pressure': case 'rope': near(selected*b,a); break;
   case 'energy': near(selected/10/b,a); break;
   default: throw new Error('unchecked family');
  }
 });
});
it('counts, exact duplicates, families and subject coverage',()=>{
 expect(BASE_BANK).toHaveLength(1000); expect(new Set(BASE_BANK.map(q=>q.id)).size).toBe(1000);
 expect(new Set(BASE_BANK.map(fingerprint)).size).toBe(1000);
 expect(new Set(BASE_BANK.map(q=>q.family)).size).toBe(20);
 for(const s of SUBJECTS)expect(BASE_BANK.filter(q=>q.subject===s)).toHaveLength(200);
 expect(BASE_BANK.every(q=>q.type==='original' && q.verificationStatus==='reviewed')).toBe(true);
});
it('reproducible generator preserves JSON bytes',()=>{
 const source=readFileSync('src/data/questions-main.json','utf8');execFileSync('python3',['scripts/generate-bank.py']);expect(readFileSync('src/data/questions-main.json','utf8')).toBe(source);
});
it('exam selection, duration, unique IDs, pending exclusion',()=>{
 const e=createExam([...BASE_BANK,{...BASE_BANK[0],id:'PENDING',verificationStatus:'pending'}],'main',100);
 expect(e.questions).toHaveLength(PROFILE.questionCount); expect(e.deadline-100).toBe(9000000);
 expect(new Set(e.questions.map(q=>q.id)).size).toBe(100);
 for(const s of SUBJECTS)expect(e.questions.filter(q=>q.subject===s)).toHaveLength(20);
 expect(e.questions.some(q=>q.id==='PENDING')).toBe(false);
});
function withCounts(counts:number[]){const e=createExam(BASE_BANK,'main');for(const [i,s] of SUBJECTS.entries())for(const q of e.questions.filter(q=>q.subject===s).slice(0,counts[i]))e.answers[q.id]=q.answer;return e;}
it.each([
 [[12,12,12,12,12],true,60], [[11,12,12,12,12],false,59],
 [[7,20,20,20,20],false,87], [[8,13,13,13,13],true,60],
 [[0,0,0,0,0],false,0], [[20,20,20,20,20],true,100],
] as [number[],boolean,number][] )('grade %j', (counts,passed,score)=>{const g=grade(withCounts(counts));expect(g.passed).toBe(passed);expect(g.score).toBe(score);});
it('answer changes, expired answers, duplicate submission and restore',()=>{
 let s=emptyStore();s.exam=createExam(BASE_BANK,'main',1000);const q=s.exam.questions[0];
 s=answerExam(s,q.id,1,1001);s=answerExam(s,q.id,2,1002);expect(s.exam!.answers[q.id]).toBe(2);
 const restored=restoreStore(JSON.stringify(s));expect(restored.exam!.deadline).toBe(9001000);
 s=answerExam(s,q.id,3,9001000);expect(s.exam).toBeNull();expect(s.results[0].answers[q.id]).toBe(2);
 expect(submitExam(s).results).toHaveLength(1);expect(s.attempts).toHaveLength(100);
});
it('practice once per answer, wrong cleared, nonrepeating traversal',()=>{
 let s=emptyStore();s.practice=startPractice(BASE_BANK,'main');const q=BASE_BANK.find(q=>q.id===s.practice!.currentId)!;
 s.practice!.selected=q.answer;s=checkPractice(s,BASE_BANK);const n=s.attempts.length;s=checkPractice(s,BASE_BANK);expect(s.attempts).toHaveLength(n);
 let p=s.practice!;const seen=new Set([p.currentId]);for(let i=0;i<100;i++){p=nextPractice(p,BASE_BANK);expect(seen.has(p.currentId)).toBe(false);seen.add(p.currentId);}
});
it('imports are atomic, duplicates include reordered choices, templates validate',()=>{
 const q=BASE_BANK[0]; expect(importQuestions([{...q,id:'COPY',choices:[...q.choices].reverse()}],BASE_BANK).duplicates).toBe(1);
 expect(()=>importQuestions([{...q,id:'NEW',question:'new'},{}],BASE_BANK)).toThrow();
 const added=importQuestions([{...q,id:'NEW',question:'new'}],BASE_BANK).added;expect(added[0].verificationStatus).toBe('pending');
 expect(parseCsv(readFileSync('public/templates/questions.csv','utf8')).map(validateQuestion)).toHaveLength(1);
});
it('corruption throws, storage is isolated',()=>{expect(()=>restoreStore('{bad')).toThrow();expect(STORAGE_KEY).toBe('construction-safety-cbt:v1');});
