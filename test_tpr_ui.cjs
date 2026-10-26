const vm=require('node:vm'), fs=require('node:fs'), assert=require('node:assert');
const content={innerHTML:''};const nav={};const context={console,Set,document:{querySelector:s=>s==='#content'?content:nav},fetch:()=>Promise.reject(Error('not used')),setTimeout,clearTimeout};
vm.createContext(context);let src=fs.readFileSync('static/main.js','utf8');src=src.slice(0,src.indexOf('refresh().then'))+src.slice(src.indexOf("let tprData="));vm.runInContext(src,context);
const data={nodes:JSON.parse(fs.readFileSync('reference/data/nodes.json')),cases:JSON.parse(fs.readFileSync('reference/data/cases.json')),mappings:JSON.parse(fs.readFileSync('reference/data/mappings.json')),ttl:'fixture ttl'};
context.fixture=data;
(async()=>{await vm.runInContext("tprData=fixture; tprCase='A'; tprPage()",context);assert(content.innerHTML.includes('A-Control'));assert(content.innerHTML.includes('导出全部四场景实例 TTL'));await vm.runInContext("tprCase='C';tprPage()",context);assert(content.innerHTML.includes('未提供控制材料'));assert(!content.innerHTML.includes('A-Control'));console.log('TPR A/C rendering and export label checks passed');})().catch(e=>{console.error(e);process.exit(1)});
