import json,html,collections,subprocess
from pathlib import Path
R=Path('/private/tmp/rosso-tau2-study'); D=R/'data/tau2'; OUT=Path(__file__).parent
load=lambda p:json.loads(p.read_text())
esc=lambda x:html.escape(str(x))
pretty=lambda x:esc(json.dumps(x,ensure_ascii=False,indent=2))
base=load(D/'domains/retail/tasks.json'); split=load(D/'domains/retail/split_tasks.json'); subset=load(D/'task_subsets/retail_50.json')['task_ids']; voice=load(D/'domains/retail/tasks_voice.json')['configs']
sha=subprocess.check_output(['git','-C',str(R),'rev-parse','HEAD'],text=True).strip(); link='https://github.com/sierra-research/tau2-bench/blob/'+sha+'/'
labels={'cancel_pending_order':'取消待处理订单','exchange_delivered_order_items':'已送达订单换货','return_delivered_order_items':'已送达订单退货','modify_pending_order_items':'修改待处理订单商品','modify_pending_order_address':'修改订单收货地址','modify_pending_order_payment':'修改订单付款方式','modify_user_address':'修改用户默认地址','transfer_to_human_agents':'转人工'}
writes=set(labels)-{'transfer_to_human_agents'}
effects={'cancel_pending_order':'订单变为 cancelled，记录取消原因及退款交易；礼品卡退款还影响余额。','exchange_delivered_order_items':'订单变为 exchange requested；记录原商品、新商品、付款方式和差价。这里记录换货申请，不完成真实物流或退款结算。','return_delivered_order_items':'订单变为 return requested；记录退货商品列表和退款方式。这里记录退货申请。','modify_pending_order_items':'替换商品，记录差价交易及相关礼品卡余额变化，订单变为 pending (item modified)。具体终态以该版本工具代码执行结果为准。','modify_pending_order_address':'更新该订单的地址字段，不自动等同于修改用户默认地址。','modify_user_address':'更新用户默认地址，不自动等同于修改已有订单地址。','modify_pending_order_payment':'更新订单付款相关交易记录，并处理相关礼品卡余额。'}
sets=[('base','基础题库','data/tau2/domains/retail/tasks.json',base,load(D/'domains/retail/db.json'))]
sets.append(('en','多语言英语版','data/tau2/multilingual/en/retail_tasks_en.json',load(D/'multilingual/en/retail_tasks_en.json'),load(D/'domains/retail/db.json')))
for lang in ['zh','es','pt','hi','ko']:
 p=D/f'multilingual/{lang}/regional/retail.json';d=load(p);sets.append((lang,f'{lang} 区域化版',str(p.relative_to(R)),d['tasks'],d['database']))
issues=collections.defaultdict(list)
for p in (D/'domains/retail/task_issues').glob('*.json'):
 d=load(p);issues[str(d['task_id'])].append((str(p.relative_to(R)),d))
counts=collections.Counter()
for t in base:
 for n in set(a['name'] for a in t['evaluation_criteria']['actions']):
  if n in labels:counts[labels[n]]+=1
no_write=sum(not any(a['name'] in writes for a in t['evaluation_criteria']['actions']) for t in base)
parts=['''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>tau2 retail 全部任务与评分条件</title><style>body{margin:0;background:#f5f6f2;color:#183139;font:16px/1.75 system-ui,-apple-system,sans-serif}main{max-width:1120px;margin:auto;padding:40px 28px}h1{font-size:36px}h2{margin-top:38px}h3{margin:0}a{color:#007773}article,section{background:white;padding:24px;border:1px solid #dce4df;border-radius:12px;margin:16px 0}summary{cursor:pointer;font-weight:650}pre{white-space:pre-wrap;overflow-wrap:anywhere;background:#f1f4f3;padding:14px;border-radius:7px;font:13px/1.65 ui-monospace,monospace}table{width:100%;border-collapse:collapse}td,th{border-bottom:1px solid #dde4e1;padding:9px;text-align:left;vertical-align:top}.tag{display:inline-block;padding:3px 9px;background:#e1efeb;border-radius:5px;margin:5px;font-size:13px}.warn{border-left:4px solid #b47920;padding:10px 16px;background:#fff8e8}.bar{position:sticky;top:0;background:#f5f6f2;padding:12px 0;z-index:1}input,select,button{font:inherit;padding:9px;border:1px solid #aebfbb;border-radius:6px}input{width:45%}.muted{color:#607077}.goal{font-size:17px}li{margin:5px 0}@media print{.bar{display:none}body{background:white}article{break-inside:avoid}main{max-width:none;padding:0}details:not([open]){display:none}}</style><main><h1>tau2 retail 全部任务与评分条件</h1>''']
parts.append(f'<p>以此前学习和 PPT 使用的同一版本为准：<code>{sha}</code>。本文件收录基础题库全部 114 道题，以及英语、多语言区域化的 300 条任务定义。后者是变体，不应合计宣称为 414 个独立业务场景。题目保留仓库原文；分类、状态判定和评分说明用中文整理。可以搜索订单号、商品、工具名、断言或任务 ID。</p>')
parts.append('''<section><h2>先理解实际如何判分</h2><ol><li>用户模拟器读取 user_scenario；agent 通过对话获取需求，不能把隐藏的参考操作当作输入答案。</li><li>DB 检查：从相同初态分别重放实际轨迹和任务参考操作，比较数据库状态哈希。相同为 1，否则为 0。参考查询动作的存在，不等于必须按同一顺序调用全部查询工具。</li><li>NL_ASSERTION 检查：LLM 根据轨迹判断逐条自然语言断言，全部满足才得 1。断言为空时此项为 1。</li><li>在默认 ALL 评分模式下，最终得分按 reward_basis 选取组件相乘；提前异常终止直接为 0。更换 evaluation_type（例如强制 ACTION）会改变评分含义。</li></ol><p class="warn">基础 114 题：112 题的 basis 是 DB + NL_ASSERTION，2 题（33、34）只有 DB；40 题有非空 NL 断言，72 题配置了 NL 但断言为空。因此正常结束后，74 题实际上主要依赖 DB 检查。没有任何基础题把 ACTION 或 COMMUNICATE 放入 reward_basis。日志中出现 action_checks，或题目有 communicate_info，都不代表它们参与最终得分。</p><p>没有参考写操作时，DB 目标通常是保持初态；若又没有有效 NL 断言，最终状态检查对回答质量的约束很弱。身份验证、用户确认、隐私和政策合规仍是 policy 要求，但不保证每题均有对应评分断言。通过测试不等于全面合规。</p></section>''')
parts.append('<section><h2>题库与任务类型</h2><p>基础题库：train 74 / test 40；base 是全部 114 题的划分。retail_50 是按写操作特征分层抽样的 50 题子集，不能当成额外 50 道新题。语音配置覆盖 114 个基础 ID，改变音频和交互条件，不是新的业务标准答案。</p><table><tr><th>参考操作分类（可重叠）</th><th>题数</th></tr>')
for k,v in counts.items():parts.append(f'<tr><td>{k}</td><td>{v}</td></tr>')
parts.append(f'<tr><td>无参考数据库写操作（含查询或转人工）</td><td>{no_write}</td></tr></table><p>区域化版本包含本地姓名、地址、商品及金额等变化，应使用该版本的数据库和参考参数，不能直接套用基础题答案。默认只显示基础 114 题，切换下方菜单可查看全部变体。</p></section>')
parts.append('''<section><h2>共同业务规则与评分边界</h2><ul><li>先用邮箱或姓名与邮编定位用户；只处理该用户的信息。</li><li>任何数据库更新前，应说明操作细节并取得明确确认。换货和修改商品应先收齐同一订单的所有变更。</li><li>取消及修改针对 pending 订单；退换货针对 delivered 订单。商品替换须为同一产品的可用变体。</li><li>取消原因限定 no longer needed 或 ordered by mistake；退款或补差价需符合付款方式及礼品卡余额约束。</li><li>订单收货地址与用户默认地址是两个不同状态。换货申请、退货申请也不同于真实履约完成。</li></ul><p>下面“预期状态变化”是阅读工具代码后的说明；真正 DB 判定比较的是整份环境终态，而不是仅检查所列字段。额外错误修改也可能导致失败。这里没有运行被测模型，不是成绩报告。</p></section>''')
parts.append('<div class="bar"><input id="q" placeholder="搜索任务、订单、工具、商品、断言…"><select id="set"><option value="base">基础题库 114</option value="all">全部定义 414</option value="en">英语变体 50</option value="zh">中文区域化 50</option value="es">西语区域化 50</option value="pt">葡语区域化 50</option value="hi">印地语区域化 50</option value="ko">韩语区域化 50</option></select> <select id="grade"><option value="all">所有评分类型</option><option value="nl">有 NL 断言</option><option value="db">无有效 NL 断言</option></select><span id="count"></span></div><div id="tasks">')
for key,label,source,tasks,db in sets:
 products=db.get('products',{}); itemmap={iid:(p['name'],v) for p in products.values() for iid,v in p.get('variants',{}).items()}
 for t in tasks:
  tid=str(t['id']);e=t.get('evaluation_criteria') or {};acts=e.get('actions') or [];nl=e.get('nl_assertions') or [];basis=e.get('reward_basis',[]);ws=[a for a in acts if a['name'] in writes];cats=list(dict.fromkeys(labels[a['name']] for a in acts if a['name'] in labels)) or ['查询与信息答复'];title=' / '.join(cats);inst=t['user_scenario']['instructions'];cid=tid.split('_')[0]
  parts.append(f'<article data-set="{key}" data-nl="{"nl" if nl else "db"}" id="{key}-{tid}"><h3>{esc(label)} · Task {esc(tid)} · {esc(title)}</h3>')
  tags=[str(x) for x in basis]
  if key=='base':tags += [('train' if tid in split['train'] else 'test'),('retail_50 子集' if tid in subset else '不在 retail_50')]
  parts.append(''.join(f'<span class="tag">{esc(x)}</span>' for x in tags))
  if isinstance(inst,dict):
   parts.append(f'<h4>题目与用户目标（仓库原文）</h4><p class="goal">{esc(inst.get("reason_for_call",""))}</p>')
   for field,cn in [('task_instructions','交互要求'),('known_info','已知身份与信息'),('unknown_info','未知信息')]:
    if inst.get(field):parts.append(f'<p><b>{cn}：</b>{esc(inst[field])}</p>')
  else:parts.append(f'<p>{esc(inst)}</p>')
  if t['user_scenario'].get('persona'):parts.append(f'<p>Persona：{esc(t["user_scenario"]["persona"])}</p>')
  parts.append('<h4>这道题如何判断</h4>')
  if not ws:parts.append('<p>参考操作没有数据库写操作：DB 目标是参考流程得到的未修改状态。不能据此认定回答内容已经被验证。</p>')
  else:
   parts.append('<ol>')
   for a in ws:
    args=a['arguments'];target=args.get('order_id') or args.get('user_id','');parts.append(f'<li><b>{labels[a["name"]]} {esc(target)}</b>：{effects[a["name"]]}<pre>{pretty(args)}</pre>')
    desc=[]
    for field in ['item_ids','new_item_ids']:
     for iid in args.get(field,[]):
      if iid in itemmap:
       name,v=itemmap[iid];desc.append(f'{field}: {iid} → {name}；选项 {json.dumps(v.get("options"),ensure_ascii=False)}；目录价 {v.get("price")}')
    if desc:parts.append('<p class="muted">'+'<br>'.join(map(esc,desc))+'<br>目录价仅帮助识别变体；历史订单购买价可能不同，不能直接当作退款金额。</p>')
    parts.append('</li>')
   parts.append('</ol>')
  if nl:parts.append('<p><b>必须满足的自然语言断言：</b></p><ol>'+''.join('<li>'+esc(n)+'</li>' for n in nl)+'</ol>')
  else:parts.append('<p><b>自然语言断言：</b>未配置非空断言；若 basis 含 NL_ASSERTION，此项按 1 处理。</p>')
  parts.append('<p><b>默认 ALL 模式判分：</b>'+('DB 通过，并且上述所有 NL 断言通过，正常结束才得 1。' if nl and 'NL_ASSERTION' in basis else '正常结束且 DB 终态与参考终态一致则得 1（按本题所选 basis）。')+'</p>')
  if e.get('communicate_info'):parts.append('<p><b>communicate_info 原值：</b>'+esc(json.dumps(e['communicate_info'],ensure_ascii=False))+'。'+('COMMUNICATE 已计入 basis。' if 'COMMUNICATE' in basis else '本题未把 COMMUNICATE 放入 basis，不能把此列表自动视为独立必过检查。')+'</p>')
  parts.append('<details><summary>完整参考工具调用（含查询；不代表唯一合法调用顺序）</summary><ol>')
  for a in acts:parts.append(f'<li><code>{esc(a["name"])}</code><pre>{pretty(a["arguments"])}</pre></li>')
  parts.append('</ol></details>')
  if key=='base' and cid in issues:
   parts.append('<details><summary>仓库中的历史 task issue 记录</summary>')
   for p,d in issues[cid]:parts.append(f'<p><a href="{link+p}">{esc(p.split("/")[-1])}</a>：记录得分 {esc(d.get("reward_info",{}).get("reward"))}。这是历史运行记录，不等于所有版本必现的缺陷。</p>')
   parts.append('</details>')
  parts.append(f'<details><summary>完整任务定义（含初始状态与原始评分配置）</summary><pre>{pretty(t)}</pre></details><p class="muted"><a href="{link+source}">源文件</a> · 文件内查找 ID {esc(tid)}</p></article>')
parts.append('</div><section><h2>源码索引与可复核范围</h2><ul>')
for p in ['data/tau2/domains/retail/tasks.json','data/tau2/domains/retail/split_tasks.json','data/tau2/domains/retail/policy.md','data/tau2/task_subsets/retail_50.json','data/tau2/domains/retail/tasks_voice.json','src/tau2/domains/retail/tools.py','src/tau2/evaluator/evaluator.py','src/tau2/evaluator/evaluator_env.py','src/tau2/evaluator/evaluator_nl_assertions.py']:
 parts.append(f'<li><a href="{link+p}">{p}</a></li>')
parts.append('</ul><p>上述范围是仓库 retail 业务 benchmark 题目；不把框架的 Python 单元测试、历史模型成绩、语音扰动配置当作额外业务题目。数据按固定 commit 整理，未声称为未来最新版。</p></section></main><script>const cards=[...document.querySelectorAll("article")];function filter(){let q=document.querySelector("#q").value.toLowerCase(),s=document.querySelector("#set").value,g=document.querySelector("#grade").value,n=0;cards.forEach(c=>{let show=(s==="all"||c.dataset.set===s)&&(g==="all"||c.dataset.nl===g)&&c.textContent.toLowerCase().includes(q);c.hidden=!show;if(show)n++});document.querySelector("#count").textContent=" 显示 "+n+" 条"}document.querySelectorAll("input,select").forEach(e=>e.addEventListener("input",filter));filter();</script></html>')
out=OUT/'tau2-retail-all-tasks-and-grading.zh.html';out.write_text('\n'.join(parts));assert len(base)==114 and len(set(t['id'] for t in base))==114;assert sum(len(x[3]) for x in sets)==414
print(json.dumps({'file':str(out.resolve()),'base':len(base),'all_definitions':sum(len(x[3]) for x in sets),'nonempty_nl':sum(bool(t['evaluation_criteria'].get('nl_assertions')) for t in base),'bytes':out.stat().st_size,'categories':counts},ensure_ascii=False,indent=2))
