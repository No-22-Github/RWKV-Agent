#!/usr/bin/env python3
"""Produce a reviewable per-case state comparison from original scored outputs."""
import argparse
import json
from pathlib import Path


def esc(value):
    return str(value).replace('|','\\|').replace('\n',' ')


def main():
    ap=argparse.ArgumentParser();ap.add_argument('comparison');ap.add_argument('output');args=ap.parse_args()
    data=json.loads(Path(args.comparison).read_text());runs=data['runs'];out=['# G1K state 逐题对照','', '以下沿用原始 case 判据；所有解释性摘录均不是重新判分。主表保留所有高并发观察值：† 表示整组原始 canary 指纹不稳定，未获严格比较有效性；这不把每一道题重新判为失败。具体 transport/effective-canary 状态见总报告与 state-comparison.json。','']
    arms=['zero-none','none-state','zero-fast','fast-state']
    for suite in ['workbank','boundary','bfcl']:
        suffix='-high-'+suite
        rs=[runs.get(arm+suffix) for arm in arms]
        ids=list(dict.fromkeys(c['id'] for r in rs if r for c in r['details']))
        if not ids:continue
        out+=['## '+suite,'','| Case | 零 state / none | none state | 零 state / fast 对齐 | fast state 对齐 |','|---|---|---|---|---|']
        for cid in ids:
            cells=[]
            for r in rs:
                cells.append('未完成' if not r else ('通过' if r['case_pass'].get(cid) else '失败')+('†' if not r['valid'] else ''))
            out+=['| '+cid+' | '+' | '.join(cells)+' |']
        out+=['']
        for cid in ids:
            out+=['### '+cid,'']
            for arm,r in zip(arms,rs):
                if not r:continue
                c=next((c for c in r['details'] if c['id']==cid),None)
                if not c:continue
                out+=['**'+arm+'：'+('通过' if c['passed'] else '失败')+('（整组严格指纹校验未通过）' if not r['valid'] else '')+'**','']
                if c['case_failures']:out+=['文件/执行验收：'+esc('；'.join(c['case_failures'])),'']
                if c['case_error']:out+=['Case 运行错误：'+esc(c['case_error']),'']
                for i,t in enumerate(c['turns'],1):
                    actions=['%s:%s%s'%(a['step'],a.get('tool') or a.get('action') or 'unparsed','[answer]' if a.get('stage')=='answer' else '') for a in t['actions']]
                    out+=['- 回合 '+str(i)+' 动作：`'+' → '.join(actions)+'`','- 强制收尾：`'+str(t['forced'] or '无')+'`','- 验收：'+esc('；'.join(t['failures']) or '本回合通过（仍需 case 层验收）'),'']
                    for a in t['actions']:
                        if a.get('protocol_error'):
                            out+=['- 第 '+str(a['step'])+' 步协议错误：'+esc(a['protocol_error']), '']
                            raw=a.get('model_output') or ''
                            out+=['````text',str(raw)[:600],'````','']
                    text=t['output'] or '（空输出）';out+=['````text',text[:700]+('…（截取）' if len(text)>700 else ''),'````','']
    out+=['## 复测逐题翻转','', '保留首次与复测的全部通过/失败翻转，不选择性替换首次分数。','']
    for c in data['comparisons']:
        if 'repeat' not in c['label']:continue
        out+=['### '+c['base']+' → '+c['variant'],'',
              '- 两组严格有效：'+str(c['valid']),
              '- 新通过：'+(', '.join(c['gains']) or '无'),
              '- 新失败：'+(', '.join(c['losses']) or '无'),'']
    Path(args.output).write_text('\n'.join(line.rstrip() for line in '\n'.join(out).splitlines()).rstrip()+'\n')

if __name__=='__main__':main()
