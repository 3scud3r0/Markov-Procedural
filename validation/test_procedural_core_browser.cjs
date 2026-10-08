/* STUDIO_URL selects local/public Studio; verifies standalone core inside Pyodide. */
const {chromium}=require('playwright');
const assert=require('assert');
(async()=>{
 const browser=await chromium.launch({executablePath:process.env.STUDIO_CHROMIUM||'/usr/bin/chromium',headless:true,args:['--no-sandbox','--disable-webgl']});
 try{
  const page=await browser.newPage({ignoreHTTPSErrors:true});
  await page.goto(process.env.STUDIO_URL||'http://127.0.0.1:8765/');
  await page.waitForFunction(()=>typeof lastResult!=='undefined'&&lastResult?.ok,{},{timeout:120000});
  const source=`from procedural import Procedural, RewriteRule\nengine = Procedural(42)\n@engine.generator("building")\ndef building(ctx):\n    return {"height": ctx.randint(2, 8), "material": ctx.choose(["wood", "stone"])}\ncity = [engine.generate("building", key=i) for i in range(5)]\nfor i, item in enumerate(city):\n    box(size=[1, item["height"], 1], position=[i*2, item["height"]/2, 0])\ntext = engine.generate("grammar", rules={"start": "City of {name}", "name": ["Eden", "Vale"]})\nterrain = engine.generate("terrain")\nrewritten = engine.context.rewrite("aa", [RewriteRule(("a", "a"), ("b",))])\nprint("CORE_READY", len(city), text, rewritten)\nemit("core.json", {"city": city, "terrain": terrain, "text": text})`;
  await page.locator('.cm-content').click();await page.keyboard.press('Control+KeyA');await page.keyboard.insertText(source);
  async function run(){const id=await page.evaluate(()=>requestId);await page.locator('#run').click();await page.waitForFunction(old=>requestId>old&&!running&&lastResult!==null,id,{timeout:60000});const result=await page.evaluate(()=>lastResult);assert(result.ok,JSON.stringify(result.error));return result;}
  const first=await run(),second=await run();
  assert.equal(first.scene.objects.length,5);assert(first.stdout.includes('CORE_READY 5'));
  assert.deepStrictEqual(first.files,second.files);
  assert.equal(await page.evaluate(()=>viewport.backend),'Canvas 2D / CPU');
  console.log(JSON.stringify({ok:true,url:page.url(),checks:['standalone core import in Pyodide','custom generator and actual scene geometry','grammar, terrain and token rewriting','repeatable exported data','CPU rendering without WebGL']},null,2));
 }finally{await browser.close();}
})().catch(error=>{console.error(error);process.exit(1)});
