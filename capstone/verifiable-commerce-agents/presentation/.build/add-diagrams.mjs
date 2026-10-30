import fs from 'node:fs/promises';
import path from 'node:path';
import {FileBlob,PresentationFile} from '@oai/artifact-tool';
import {finalizePresentation} from '/Users/soardulia/.codex/plugins/cache/openai-primary-runtime/presentations/26.1020.11618/skills/presentations/container_tools/artifact_tool_utils.mjs';
const ROOT='/Volumes/DOCK1TBFILES/AI/AI Agents/capstone/verifiable-commerce-agents/presentation';
const SKILL='/Users/soardulia/.codex/plugins/cache/openai-primary-runtime/presentations/26.1020.11618/skills/presentations';
const P=await PresentationFile.importPptx(await FileBlob.load(path.join(ROOT,'output','Tau2_Bench_Overview_EN.pptx')));
const snap=await P.inspect({kind:'slide,textbox,shape,table',maxChars:160000});
const recs=snap.ndjson.trim().split('\n').map(l=>JSON.parse(l));
const C={navy:'#102B36',teal:'#007B78',cream:'#F7F5EF',gray:'#50636A',light:'#E6ECE9',amber:'#9C481E'};
function clear(i){const ids=recs.filter(r=>r.slideIndex===i-1&&['textbox','shape','table'].includes(r.kind)&&r.position?.top>=200&&r.position?.top<650).map(r=>r.id);P.delete([...new Set(ids)]);return P.slides.items[i-1];}
function change(old,t){const r=recs.find(r=>r.kind==='textbox'&&r.text===old);P.resolve(r.id).text.replace(old,t);}
function text(s,t,x,y,w,h,size=24,color=C.gray,bold=false,align='left'){const a=s.shapes.add({geometry:'textbox',position:{left:x,top:y,width:w,height:h},fill:'none',line:{fill:'none',width:0}});a.text=t;a.text.style={typeface:'Helvetica Neue',fontSize:size,color,bold,alignment:align,insets:0,autoFit:'none'};return a;}
function box(s,t,x,y,w,h,dark=false){const a=s.shapes.add({geometry:'roundRect',position:{left:x,top:y,width:w,height:h},borderRadius:9,fill:dark?C.navy:C.light,line:{fill:dark?C.navy:C.teal,width:1.7}});a.text=t;a.text.style={typeface:'Helvetica Neue',fontSize:26,color:dark?'#FFFFFF':C.navy,bold:false,alignment:'center',verticalAlignment:'middle',insets:12,autoFit:'none'};return a;}
function connect(s,a,b,fromSide,toSide,{both=false,dashed=false}={}){return s.shapes.connect(a,b,{fromSide,toSide,kind:fromSide==='right'&&toSide==='left'?'straight':'elbow',line:{fill:dashed?C.amber:C.teal,width:2.5,style:dashed?'dashed':'solid'},head:both?{type:'triangle',width:'sm',length:'sm'}:{type:'none'},tail:{type:'triangle',width:'sm',length:'sm'}});}
function arrow(s,x1,x2,y,label){s.shapes.add({geometry:'connector',kind:'straight',position:{left:Math.min(x1,x2),top:y,width:Math.abs(x2-x1),height:0},line:{fill:C.teal,width:2.4},...(x2>x1?{tail:{type:'triangle',width:'sm',length:'sm'}}:{head:{type:'triangle',width:'sm',length:'sm'}})});text(s,label,Math.min(x1,x2)+12,y-29,Math.abs(x2-x1)-24,28,21,C.navy,false,'center');}
const B='https://github.com/sierra-research/tau2-bench/blob/122e2432b82d740e8f313f46f0a071729c404f39/';
let s=clear(3);
change('A shared environment lets different agent implementations face the same task','Runtime interactions and post-conversation evaluation');
const user=box(s,'User simulator\nCustomer goal + persona',64,255,260,120);
const orch=box(s,'Orchestrator\nRoute + execute + record',480,255,300,120,true);
const agent=box(s,'Agent\nPolicy + tool schemas',940,255,275,120);
const tools=box(s,'Tool environment\nTools + mutable database',480,505,300,110);
const judge=box(s,'Evaluator\nReplay + task checks',940,505,275,110);
connect(s,user,orch,'right','left',{both:true});
connect(s,orch,agent,'right','left',{both:true});
connect(s,orch,tools,'bottom','top',{both:true});
for(const [x,y,w,h,last] of [[780,350,75,0,false],[855,350,0,210,false],[855,560,85,0,true]]) s.shapes.add({geometry:'connector',kind:'straight',position:{left:x,top:y,width:w,height:h},line:{fill:C.amber,width:2.5,style:'dashed'},...(last?{tail:{type:'triangle',width:'sm',length:'sm'}}:{})});
text(s,'Dialogue',333,275,140,34,23,C.teal,false,'center');
text(s,'Messages /\naction requests',787,218,145,80,20,C.teal,false,'center');
text(s,'Tool calls\nand results',650,414,185,65,24,C.teal);
text(s,'Recorded trajectory\nafter the conversation',880,413,335,67,23,C.amber);
text(s,'Runtime\nSolid arrows',64,493,285,58,25,C.teal,true);
text(s,'Post-run scoring\nDashed arrow',64,568,285,58,25,C.amber,true);
s.speakerNotes.text='Solid bidirectional arrows show runtime message exchanges. The orchestrator routes customer dialogue to the agent and sends tool calls to the environment. The tool environment holds mutable domain state. The orchestrator records the trajectory. The dashed arrow shows post-run evaluation, not an online decision maker. The evaluator also uses task criteria and fresh environments to reconstruct actual and reference states. The evaluation/replay diagram later makes those inputs explicit.\n\nSources:\n'+B+'src/tau2/orchestrator/orchestrator.py\n'+B+'src/tau2/evaluator/evaluator.py\n'+B+'src/tau2/evaluator/evaluator_env.py';

s=clear(6);
change('The interaction loop','A tool-use cycle');
change('Each tool result becomes evidence for the next agent decision','Example sequence: a customer asks about an order');
const xs=[170,480,790,1100];
['User simulator','Orchestrator','Agent','Tool environment'].forEach((label,i)=>{const h=box(s,label,xs[i]-108,206,216,53,i===1);h.text.style={typeface:'Helvetica Neue',fontSize:22,color:i===1?'#FFFFFF':C.navy,alignment:'center',verticalAlignment:'middle',insets:4,autoFit:'none'};s.shapes.add({geometry:'line',position:{left:xs[i],top:265,width:0,height:370},line:{fill:'#A8B7B6',width:1.3,style:'dashed'}});});
arrow(s,170,480,295,'1  Customer message');
arrow(s,480,790,339,'2  Forward message');
arrow(s,790,480,383,'3  Tool call request');
arrow(s,480,1100,427,'4  Execute get_order_details(order_id)');
arrow(s,1100,480,471,'5  Return order data');
arrow(s,480,790,515,'6  Deliver tool result');
arrow(s,790,480,559,'7  Generate a reply');
arrow(s,480,170,603,'8  Deliver reply');
s.speakerNotes.text='Read downward in time. This illustrative cycle shows an order lookup, not a measured run. The agent may request further tools instead of replying after step 6, so the tool-use cycle can repeat. User and agent do not exchange messages directly. All arrows pass through the orchestrator. The environment changes state only for mutating calls; get_order_details is read-only. All messages and tool results enter the trajectory for later evaluation.\n\nSources:\n'+B+'src/tau2/orchestrator/orchestrator.py#L847\n'+B+'src/tau2/agent/llm_agent.py#L115\n'+B+'src/tau2/domains/retail/tools.py';

s=clear(10);
change('Final-state scoring','Evaluation through replay');
change('The evaluator builds an actual state and a reference state independently','The evaluator reconstructs two states from the same starting point');
text(s,'ACTUAL TRAJECTORY',64,214,600,36,22,C.teal,true);
text(s,'REFERENCE ACTIONS',64,410,600,36,22,C.teal,true);
const a1=box(s,'Fresh environment\nInitial state',64,266,220,100);
const a2=box(s,'Replay recorded\nstate-changing calls',360,266,300,100);
const a3=box(s,'Predicted\nDB state',745,266,230,100);
const b1=box(s,'Fresh environment\nInitial state',64,460,220,100);
const b2=box(s,'Execute task\nreference actions',360,460,300,100);
const b3=box(s,'Gold\nDB state',745,460,230,100);
const cmp=box(s,'Hash match?\nDB = 1 or 0',1040,363,185,100,true);
connect(s,a1,a2,'right','left');connect(s,a2,a3,'right','left');
connect(s,b1,b2,'right','left');connect(s,b2,b3,'right','left');
connect(s,a3,cmp,'right','top');connect(s,b3,cmp,'right','bottom');
text(s,'Task 0: reward = DB × 1 for empty NL assertions, after normal termination.',64,606,1152,44,25,C.teal,true);
s.speakerNotes.text='The same evaluator coordinates both lanes. Both environments apply task initialization. Predicted state comes from the recorded trajectory; reference state comes from initial history plus reference actions. Current replay skips non-mutating and rejected calls and validates mutating tool outputs in strict mode. EnvironmentEvaluator compares agent and user database hashes. Other reward components depend on reward_basis. In base retail task 0, NL assertions are empty and contribute a neutral 1. Premature termination gives zero before this comparison.\n\nSources:\n'+B+'src/tau2/evaluator/evaluator_env.py\n'+B+'src/tau2/environment/environment.py#L293\n'+B+'data/tau2/domains/retail/tasks.json\n'+B+'src/tau2/evaluator/evaluator.py';
await fs.mkdir(path.join(ROOT,'.build','diagram-renders'),{recursive:true});
for(let i=0;i<P.slides.items.length;i++){const b=await P.export({slide:P.slides.items[i],format:'png',scale:1});await fs.writeFile(path.join(ROOT,'.build','diagram-renders',`slide-${String(i+1).padStart(2,'0')}.png`),new Uint8Array(await b.arrayBuffer()));}
const candidatePath=path.join(ROOT,'.build','diagram-candidate.pptx');await(await PresentationFile.exportPptx(P)).save(candidatePath);
const owners=[5,7,9,11,12,13];
const result=await finalizePresentation({workspaceDir:ROOT,candidatePath,finalPath:path.join(ROOT,'output','Tau2_Bench_Overview_EN_Diagrams_Final.pptx'),pythonExecutable:'/Users/soardulia/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3',integrityValidatorPath:path.join(SKILL,'container_tools/inspect_presentation_package_integrity.py'),layoutValidatorPath:path.join(SKILL,'container_tools/inspect_presentation_layout_geometry.py'),layoutArgs:['--expected-slide-size-emu','12192000,6858000','--validate-bullet-geometry','--validate-heading-fit',...owners.flatMap(n=>['--require-native-table-slide',String(n)])],requiredNativeTableOwnerSlides:owners,explicitTotalSlideCount:15,fontPolicy:{basis:'design',families:['Helvetica Neue']},verifyArtifactToolImport:true,receiptPath:path.join(ROOT,'.build','diagram-validation-final.json')});console.log(JSON.stringify(result));
