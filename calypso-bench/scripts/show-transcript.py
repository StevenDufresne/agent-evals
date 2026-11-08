import json,sys
sys.stdout.reconfigure(line_buffering=True)
for line in (open(sys.argv[1]) if len(sys.argv) > 1 else sys.stdin):
    try: e=json.loads(line)
    except: continue
    if e.get('type')=='assistant':
        for c in e['message'].get('content',[]):
            if c.get('type')=='text': print('💬',c['text'][:300].replace('\n',' '))
            elif c.get('type')=='tool_use':
                i=c['input']; d=i.get('command') or i.get('file_path') or i.get('pattern') or json.dumps(i)[:150]
                print('🔧',c['name'],':',str(d)[:180].replace('\n',' '))
    elif e.get('type')=='result':
        print('✅ result:', e.get('subtype'), 'turns=',e.get('num_turns'), 'cost=',e.get('total_cost_usd'), 'ms=',e.get('duration_ms'))
