import { test, expect } from '@playwright/test';
for (const size of [{width:390,height:480},{width:740,height:360},{width:390,height:480,largeText:true}]) {
 for(const method of ['wheel','touch']) test(`menu ${size.width}x${size.height} ${"largeText" in size ? "large-text" : "normal"} ${method}`, async ({page,browserName})=>{
  await page.setViewportSize(size); await page.goto('');
  if ('largeText' in size) await page.addStyleTag({content:'.sidebar nav button,.sidebar .text-button {font-size:20px} .sidebar-disclaimer {font-size:16px}'});
  await page.getByRole('button',{name:'메뉴 열기'}).click();await page.waitForTimeout(400);
  const menu=page.locator('.sidebar'); const before=await page.evaluate(()=>window.scrollY);
  const session=method==='touch'?await page.context().newCDPSession(page):null;
  async function input(down:boolean){
   if(method==='wheel'){await page.mouse.move(140,size.height/2);await page.mouse.wheel(0,down?600:-600);}
   else {
    const start=down?size.height-60:80,end=down?80:size.height-60;
    await session!.send('Input.dispatchTouchEvent',{type:'touchStart',touchPoints:[{x:140,y:start}]});
    for(let n=1;n<=12;n++){
     await session!.send('Input.dispatchTouchEvent',{type:'touchMove',touchPoints:[{x:140,y:start+(end-start)*n/12}]});
     await page.waitForTimeout(20);
    }
    await session!.send('Input.dispatchTouchEvent',{type:'touchEnd',touchPoints:[]});
   }
   await page.waitForTimeout(200);
  }
  for(let n=0;n<5;n++) await input(true);
  expect(await menu.evaluate(el=>el.scrollTop)).toBeGreaterThan(0);
  await expect(page.getByRole('button',{name:'학습 기록 백업',exact:true})).toBeInViewport();
  await expect(page.getByRole('button',{name:'데이터 초기화',exact:true})).toBeInViewport();
  const downloaded=page.waitForEvent('download');await page.getByRole('button',{name:'학습 기록 백업',exact:true}).click();await downloaded;
  await page.getByRole('button',{name:'데이터 초기화',exact:true}).click();await expect(page.getByRole('dialog')).toBeVisible();
  await page.getByRole('button',{name:'돌아가기',exact:true}).click();
  for(let n=0;n<5;n++) await input(false);
  await expect(page.getByRole('navigation').getByRole('button',{name:'학습 대시보드',exact:true})).toBeInViewport();
  await page.getByRole('navigation').getByRole('button',{name:'학습 대시보드',exact:true}).click();
  await expect(page.getByRole('heading',{name:'건설안전기사 필기 CBT',exact:true})).toBeVisible();
  expect(await page.evaluate(()=>window.scrollY)).toBe(before);
 });
}
test('no permanent banners; storage write errors stay visible',async({page})=>{
 await page.addInitScript(()=>{Storage.prototype.setItem=()=>{throw new DOMException('quota','QuotaExceededError')}});
 await page.goto(''); await expect(page.locator('.criteria-note')).toHaveCount(0);
 await expect(page.getByRole('alert')).toBeVisible();
});
