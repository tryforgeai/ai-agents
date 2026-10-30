import fs from 'node:fs/promises';
import path from 'node:path';
import { Presentation, PresentationFile } from '@oai/artifact-tool';
import { resolvePresentationFont, finalizePresentation } from '/Users/soardulia/.codex/plugins/cache/openai-primary-runtime/presentations/26.1020.11618/skills/presentations/container_tools/artifact_tool_utils.mjs';
const ROOT='/Volumes/DOCK1TBFILES/AI/AI Agents/capstone/verifiable-commerce-agents/presentation';
const SKILL='/Users/soardulia/.codex/plugins/cache/openai-primary-runtime/presentations/26.1020.11618/skills/presentations';
const PY='/Users/soardulia/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3';
const P=Presentation.create({slideSize:{width:1280,height:720}});
const FONT=resolvePresentationFont();
console.log('Font:',FONT);
const C={navy:'#102B36',teal:'#007B78',cream:'#F7F5EF',white:'#FFFFFF',gray:'#50636A',light:'#E6ECE9',amber:'#9C481E'};
const BASE='https://github.com/sierra-research/tau2-bench/blob/122e2432b82d740e8f313f46f0a071729c404f39/';
const tableSlides=[];
function text(s,t,x,y,w,h,size=28,color=C.navy,bold=false){const a=s.shapes.add({geometry:'textbox',position:{left:x,top:y,width:w,height:h},fill:'none',line:{fill:'none',width:0}});a.text=t;a.text.style={typeface:FONT,fontSize:size,color,bold,autoFit:'none',insets:0,verticalAlignment:'top'};return a;}
function slide(title,sub='',dark=false){const s=P.slides.add();s.background.fill=dark?C.navy:C.cream;const n=P.slides.items.length;text(s,String(n).padStart(2,'0'),1174,661,45,24,16,dark?'#A9C9C5':C.gray);if(title)text(s,title,64,54,1140,92,44,dark?C.white:C.navy,true);if(sub)text(s,sub,66,145,1134,62,25,dark?'#B9D7D2':C.gray);return s;}
function note(s,body,sources=[]){s.speakerNotes.text=body+'\n\nSources:\n'+sources.map(v=>v.startsWith('http')?v:BASE+v).join('\n');}
function table(s,values,widths,{top=230,height=350,size=25}={}){const tb=s.tables.add({rows:values.length,columns:values[0].length,left:64,top,width:1152,height,columnWidths:widths,values});tb.borders.assign({fill:C.cream,width:2,style:'solid'});for(let r=0;r<values.length;r++){tb.rows[r].height=height/values.length;for(let c=0;c<values[0].length;c++){const cell=tb.getCell(r,c);cell.fill=r===0?C.navy:(r%2?C.white:C.light);cell.text.style={typeface:FONT,fontSize:size,color:r===0?C.white:C.navy,bold:r===0,insets:14,verticalAlignment:'middle'};}}tableSlides.push(P.slides.items.length);return tb;}
function item(s,num,title,body,y,{x=64,w=1120}={}){text(s,num,x,y,60,50,34,C.teal,true);text(s,title,x+78,y,w-78,45,30,C.navy,true);text(s,body,x+78,y+49,w-78,65,25,C.gray);}
let s=slide('', '',true);
text(s,'Verifiable Commerce\nAgents',64,150,1120,180,72,C.white,true);
text(s,'A capstone proposal for evaluating retail agents\nwith controlled tools and verifiable evidence',68,365,1050,110,32,'#B9D7D2');
text(s,'Rosso Han\nOctober 2026',68,590,500,65,23,'#B9D7D2');
note(s,'This presentation explains the proposed capstone and a source-based walkthrough of tau2-bench. The retail example comes from the base task collection at commit 122e2432b82d740e8f313f46f0a071729c404f39. The walkthrough is a source-code reconstruction, not a recorded model run. Proposed components and experiments are labeled throughout.',['README.md']);

s=slide('The capstone goal','Evaluate interchangeable retail agents against explicit business rules');
text(s,'Did the agent complete the task?',66,235,1090,58,40,C.navy,true);
text(s,'Check the actual order, refund and inventory state.',66,303,1090,50,28,C.gray);
text(s,'Did it act within its authority?',66,400,1090,58,40,C.teal,true);
text(s,'Check confirmation, policy limits and approval evidence.',66,468,1090,60,28,C.gray);
text(s,'Planned scope: returns, exchanges and coupon rules in a synthetic store.',66,598,1110,50,24,C.gray);
note(s,'The project targets observable outcomes and process compliance. A successful-looking reply is insufficient. The proposal includes a synthetic store, controlled tools, a policy guard, prompt optimization and single-step reinforcement learning. This is a personal capstone project, not an employer deployment. Source: local capstone SCOPE.md and Proposal v2 dated October 24, 2026.');

s=slide('The tau2 evaluation architecture','A shared environment lets different agent implementations face the same task');
table(s,[['Component','Responsibility'],['Task + user simulator','Define the goal and simulate the customer'],['Agent','Choose a reply or request a tool call'],['Orchestrator / environment','Execute tools and record state changes'],['Evaluator','Check task criteria and calculate reward']],[380,772],{top:226,height:355,size:27});
text(s,'The standard agent interface separates decision-making from tool execution.',66,607,1110,45,25,C.teal,true);
note(s,'The agent receives policy, tool definitions and conversation/tool messages. The user simulator receives the user scenario. The orchestrator routes messages and tool requests. Standard adapters should not execute a write internally and then submit the same write to the orchestrator. In-process callable tools are not a security sandbox.',['src/tau2/agent/base_agent.py','src/tau2/orchestrator/orchestrator.py','src/tau2/environment/tool.py']);

s=slide('A concrete retail task','Base retail task 0: exchange two items in one delivered order');
text(s,'Customer request',66,230,500,44,30,C.teal,true);
text(s,'A clicky, full-size keyboard with RGB lighting.\n\nIf unavailable, accept no backlight.',66,292,510,215,31);
text(s,'A thermostat compatible with Google Home instead of Apple HomeKit.',666,292,510,215,31);
text(s,'Order #W2378156\nCustomer knows name and ZIP code, but has forgotten the email address.',66,553,1105,82,27,C.gray);
note(s,'Yusuf Rossi, ZIP 19122, wants a keyboard and thermostat exchange. The task asks the simulated customer to address everything in one go. The order is delivered. The customer requests Google Home compatibility, while the product data labels the target variant Google Assistant. This distinction is preserved in later slides.',['data/tau2/domains/retail/tasks.json','data/tau2/domains/retail/db.json']);

s=slide('Task definition and information boundaries','The customer scenario and the grading reference serve different roles');
table(s,[['Task field','Purpose in this example'],['user_scenario','Customer goal, identity details and fallback preference'],['initial_state = null','Use the initial domain database'],['evaluation_criteria.actions','Reference actions that produce the expected final state'],['reward_basis','DB and NL_ASSERTION for this base task']],[430,722],{top:229,height:350,size:26});
text(s,'A normal tested agent discovers the solution through dialogue and tools.',66,608,1110,44,25,C.teal,true);
note(s,'The reference actions are not a mandatory script. They identify the user, read the order, read two products and request one combined exchange. Normal LLMAgent behavior does not use the reference solution as its prompt. Ground-truth/debug agents are a separate condition and must not be presented as an ordinary baseline. Task 0 has null natural-language assertions.',['data/tau2/data_model/tasks.py'.replace('data/tau2/data_model','src/tau2/data_model'),'data/tau2/domains/retail/tasks.json','src/tau2/agent/llm_agent.py']);

s=slide('The interaction loop','Each tool result becomes evidence for the next agent decision');
item(s,'01','Receive a customer message','The agent combines the message with policy, tools and conversation history.',224);
item(s,'02','Return a reply or a tool request','The model proposes an action. It has not changed the database yet.',354);
item(s,'03','Execute and record the result','The orchestrator calls the environment and sends the tool result back.',484);
note(s,'LLMAgent.generate_next_message appends the incoming message and calls generate with model, tools and message history. Orchestrator.step routes ordinary replies to the user and tool calls to the environment. _execute_tool_calls calls environment.get_response. The trajectory retains requests and results. This cycle repeats until the conversation stops or a limit/error ends the run.',['src/tau2/agent/llm_agent.py#L115','src/tau2/orchestrator/orchestrator.py#L327','src/tau2/environment/environment.py#L473']);

s=slide('Product lookup determines the replacement','The preferred RGB keyboard exists, but it is unavailable');
table(s,[['Item','Original','Available replacement','Difference'],['Keyboard','Linear, RGB\n$272.33','Clicky, no backlight\n$269.16','−$3.17'],['Thermostat','Apple HomeKit\n$262.47','Google Assistant\n$249.01','−$13.46']],[185,300,430,237],{top:244,height:260,size:27});
text(s,'Combined price difference: −$16.63',66,546,1100,55,37,C.teal,true);
text(s,'The agent should explain both replacements and obtain confirmation.',66,615,1100,38,24,C.gray);
note(s,'Keyboard old item 1151293680 maps to new item 7706410293. Thermostat old item 4983901480 maps to new item 7747408585. The clicky RGB full-size keyboard has available=false. The accepted fallback is clicky, no backlight, full-size. Arithmetic: 269.16 - 272.33 + 249.01 - 262.47 = -16.63. The negative difference records the exchange price difference, not completed bank settlement.',['data/tau2/domains/retail/db.json','data/tau2/domains/retail/policy.md']);

s=slide('The exchange tool call','One request includes both items and their corresponding replacements');
text(s,'exchange_delivered_order_items',66,231,1120,58,36,C.teal,true);
text(s,'order_id:  #W2378156\nitem_ids:  [1151293680, 4983901480]\nnew_item_ids:  [7706410293, 7747408585]\npayment_method_id:  credit_card_9513926',66,311,1120,200,30);
text(s,'The tool checks order status, item membership, replacement availability\nand the payment method before changing state.',66,555,1120,85,27,C.gray);
note(s,'This slide shows an abbreviated tool-call payload. Actual identifiers are strings, including item IDs. The function requires delivered status, checks item multiplicities and matching list lengths, resolves each new variant within the old product, checks availability and validates payment. A gift-card payment must cover a positive price difference. The function does not receive a user-confirmation token.',['src/tau2/domains/retail/tools.py#L240','data/tau2/domains/retail/tasks.json']);

s=slide('The environment records an exchange request','The write changes order fields rather than completing fulfillment');
table(s,[['Field','Before','After'],['status','delivered','exchange requested'],['exchange_items /\nexchange_new_items','Not set','Both original and replacement item IDs'],['exchange_payment_method_id','Not set','credit_card_9513926'],['exchange_price_difference','Not set','−16.63']],[450,230,472],{top:224,height:350,size:25});
text(s,'A second exchange call fails the delivered-status check.',66,606,1100,47,29,C.teal,true);
note(s,'The tool mutates the in-memory Order model in the retail environment. It records sorted item lists, payment method and the price difference. It does not replace order.items, ship products or settle a bank refund in this function. Since status becomes exchange requested, splitting the two exchanges into separate calls would cause the later call to fail the delivered-status requirement.',['src/tau2/domains/retail/tools.py#L270']);

s=slide('Final-state scoring','The evaluator builds an actual state and a reference state independently');
item(s,'01','Reconstruct the actual state','Create a fresh environment and replay recorded state-changing calls.',224);
item(s,'02','Construct the reference state','Create another fresh environment and execute the reference actions.',354);
item(s,'03','Compare database hashes','For task 0, empty NL assertions contribute 1. Normal completion leaves DB as the deciding score.',484);
note(s,'EnvironmentEvaluator applies initialization data and actions, reconstructs predicted state from the full trajectory, and constructs gold state from initial history plus reference actions. It compares both agent and user DB hashes. set_state skips non-mutating calls and rejected calls and checks replay output in strict mode. Task 0 basis is DB + NL_ASSERTION, but nl_assertions is null, yielding neutral 1. Premature termination produces 0 before component evaluation. This is task-specific, not a claim that all tau2 tasks use DB-only grading.',['src/tau2/evaluator/evaluator_env.py','src/tau2/environment/environment.py#L293','src/tau2/evaluator/evaluator_nl_assertions.py','src/tau2/evaluator/evaluator.py']);

s=slide('A correct final state can hide a process violation','Hypothetical comparison: identical final states, different confirmation behavior');
table(s,[['Evidence','Agent A','Agent B'],['Correct exchange request','Yes','Yes'],['Explicit customer confirmation','Yes','Skipped'],['Final database matches','Yes','Yes'],['Task 0 reward, if normally completed','1','1']],[640,256,256],{top:227,height:350,size:27});
text(s,'Proposed addition: verify a trusted confirmation event before the write.',66,608,1120,50,27,C.teal,true);
note(s,'This comparison is a hypothetical source-based counterexample, not a measured model result. Assume both traces execute identical valid exchange calls and terminate normally. The tool has no confirmation credential argument, the DB comparison cannot prove confirmation, and this task has no nonempty NL assertion. Other tau2 tasks or added evaluators may check dialogue requirements. A proposed deterministic confirmation check must rely on trusted evidence bound to the action, rather than an agent-supplied confirmed=true claim.',['data/tau2/domains/retail/tasks.json','src/tau2/domains/retail/tools.py#L240','src/tau2/evaluator/evaluator_nl_assertions.py']);

s=slide('Proposed commerce evaluation system','Reuse tau2 concepts and add domain-specific evidence checks');
table(s,[['Layer','Planned responsibility'],['Agent adapter','Normalize decisions from scripts, LLMs or LangGraph'],['Tool gateway + optional guard','Control writes and record attempted, blocked and executed actions'],['Commerce environment','Model return windows, coupon rules and idempotent operations'],['Independent verifier','Check task completion, event order and rule violations']],[400,752],{top:223,height:350,size:26});
text(s,'Report agent violations separately from violations the guard prevents.',66,608,1120,48,27,C.teal,true);
note(s,'This slide describes a proposed architecture, not completed integration. Original retail lacks delivered-date and coupon models needed by the capstone. A custom commerce domain is a candidate. Existing FinePrint includes SQLite data, policy logic and an independent final-state verifier, but event-level approval and authorization checks need further work. External MCP calls require a controlled gateway and trustworthy state/log collection. Tool-call logging alone does not guarantee reproducible replay. Source: capstone SCOPE.md, tau2-learning-notes.zh.md, and FinePrint verify.py.',['src/tau2/domains/retail/data_model.py','src/tau2/environment/environment.py']);

s=slide('Agent comparison and evaluation plan','Planned conditions share tasks, tools and scoring rules');
table(s,[['Condition','What changes'],['Small model + handwritten prompt','Baseline behavior'],['Small model + GEPA / MIPROv2','Two prompt-optimization conditions'],['Small model + GRPO','Decision policy learned from verifiable rewards'],['Frontier model','Reference condition using a stronger model']],[630,522],{top:223,height:300,size:26});
text(s,'150 held-out decision points\n30 complete tasks, 4 trials each',66,557,600,78,30,C.teal,true);
text(s,'Report completion, violations, cost,\nlatency and pass^1 through pass^4.',710,557,510,78,26,C.gray);
note(s,'These are proposal targets, not completed evaluations. There are five conditions: handwritten baseline, GEPA, MIPROv2, GRPO and frontier reference. Preserve task and rule-combination splits, tool access, observation boundaries and budgets. Include do-nothing, always-ask and always-escalate controls and Guard on/off. pass^k estimates all k trials succeeding: C(c,k)/C(n,k), then averages per task. It does not establish production readiness. Report paired uncertainty and human review of simulated conversations. Source: capstone SCOPE.md.',['src/tau2/metrics/agent_metrics.py']);

s=slide('Implementation milestones','The first deliverable is a verified task loop');
item(s,'01','One rule and three hand-checked tasks','Use a fixed date, isolated state and a scripted agent.',224);
item(s,'02','Outcome checks and process checks','Test missing confirmation, repeated writes and inappropriate refusal.',354);
item(s,'03','Model comparison and optimization','Freeze test cases before adding prompt optimization or GRPO.',484);
note(s,'Suggested sequence, not a claim of completed implementation. Start with a return-window rule and inside/outside/boundary cases, then adversarial traces. Inspect both attempted actions and actual state changes. After the environment and verifier are credible, connect LLM agents, compare conditions and investigate failures. Memory, seller A2A and retrieval are later extensions in the proposal. Source: capstone SCOPE.md and tau2-learning-notes.zh.md.');

s=slide('Sources and project status','Source review at commit 122e2432b82d740e8f313f46f0a071729c404f39');
text(s,'tau2-bench',66,231,1120,45,31,C.teal,true);
text(s,'Retail task 0 and database\nAgent interface and orchestrator\nRetail tools, replay and evaluators',66,292,1100,145,28);
const link=text(s,'github.com/sierra-research/tau2-bench',66,454,1110,45,26,C.teal);
link.text.get('github.com/sierra-research/tau2-bench').link={uri:'https://github.com/sierra-research/tau2-bench',isExternal:true};
text(s,'Capstone design: Proposal v2, October 24, 2026\nStatus: source review and prototype material. Integration and model experiments remain planned.',66,553,1120,91,25,C.gray);
note(s,'Technical claims use a pinned source revision. The walkthrough is based on the base retail task collection, not the separately frozen 50-task released benchmark. No model performance claims appear in this deck. Local project sources: SCOPE.md, PROGRESS.md, tau2-learning-notes.zh.md and FinePrint verify.py.',['data/tau2/domains/retail/tasks.json','data/tau2/domains/retail/db.json','src/tau2/agent/llm_agent.py','src/tau2/orchestrator/orchestrator.py','src/tau2/domains/retail/tools.py','src/tau2/evaluator/evaluator_env.py','src/tau2/evaluator/evaluator.py']);

await fs.mkdir(path.join(ROOT,'.build','renders'),{recursive:true});
await fs.writeFile(path.join(ROOT,'.build','deck.json'),JSON.stringify(P.toProto()));
for(let i=0;i<P.slides.items.length;i++){
 const blob=await P.export({slide:P.slides.items[i],format:'png',scale:1});
 await fs.writeFile(path.join(ROOT,'.build','renders',`slide-${String(i+1).padStart(2,'0')}.png`),new Uint8Array(await blob.arrayBuffer()));
 console.log('Rendered',i+1);
}
const candidatePath=path.join(ROOT,'.build','candidate.pptx');
await (await PresentationFile.exportPptx(P)).save(candidatePath);
const result=await finalizePresentation({workspaceDir:ROOT,candidatePath,finalPath:path.join(ROOT,'output','Verifiable_Commerce_Agents_Overview_EN.pptx'),pythonExecutable:PY,integrityValidatorPath:path.join(SKILL,'container_tools/inspect_presentation_package_integrity.py'),layoutValidatorPath:path.join(SKILL,'container_tools/inspect_presentation_layout_geometry.py'),layoutArgs:['--expected-slide-size-emu','12192000,6858000','--validate-bullet-geometry','--validate-heading-fit',...tableSlides.flatMap(n=>['--require-native-table-slide',String(n)])],requiredNativeTableOwnerSlides:tableSlides,explicitTotalSlideCount:15,fontPolicy:{basis:'design',families:[FONT]},verifyArtifactToolImport:true,receiptPath:path.join(ROOT,'.build','validation-v2.json')});
console.log(JSON.stringify(result));
