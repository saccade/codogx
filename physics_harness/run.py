#!/usr/bin/env python3
"""One runner; independent physics implementations. Standard library only."""
import argparse
import hashlib
import importlib.metadata
import json
import math
import os
from pathlib import Path
import platform
import subprocess
import sys
import tempfile
from datetime import datetime, timezone

ROOT=Path(__file__).resolve().parent

def read_json(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))

def digest(data):
    return hashlib.sha256(data).hexdigest()

def environment():
    versions={}
    for name in ('numpy','scipy','sympy'):
        try: versions[name]=importlib.metadata.version(name)
        except importlib.metadata.PackageNotFoundError: versions[name]=None
    return {'python':platform.python_version(),'executable':sys.executable,
            'platform':platform.platform(),'packages':versions}

def validate(payload,case,implementation):
    if not isinstance(payload,dict): return ['Output JSON must be an object.']
    errors=[]
    if payload.get('schema_version')!=1: errors.append('Expected schema_version 1.')
    if payload.get('case_id')!=case['case_id']: errors.append('Wrong case_id.')
    if payload.get('implementation')!=implementation: errors.append('Wrong implementation identity.')
    values=payload.get('observations')
    if not isinstance(values,dict): return errors+['observations must be an object.']
    for name, rule in case['observables'].items():
        value=values.get(name)
        if isinstance(value,bool) or not isinstance(value,(int,float)) or not math.isfinite(value):
            errors.append(f'{name}: missing or non-finite numeric value.')
            continue
        if not math.isclose(value,rule['expected'],rel_tol=rule['rtol'],abs_tol=rule['atol']):
            errors.append(f"{name}: {value} {rule['unit']}; expected {rule['expected']}.")
    checks=payload.get('checks')
    if not isinstance(checks,dict) or not checks:
        errors.append('At least one named physical check is required.')
    elif any(value is not True for value in checks.values()):
        errors.append('An implementation check failed or did not return a boolean.')
    return errors

def run_entry(entry,env,no_cache=False,timeout=60):
    source=(ROOT/entry['entrypoint']).resolve()
    if ROOT not in source.parents:
        raise ValueError('Implementation paths must remain in the harness directory.')
    case_path=ROOT/'cases'/f"{entry['case']}.json"
    case=read_json(case_path)
    result={'case':entry['case'],'case_id':case['case_id'],
            'implementation':entry['implementation'],'provenance':entry['provenance']}
    if entry.get('status')!='available' or not source.is_file():
        return dict(result,status='missing',cached=False,
                    reason='Original implementation is not registered and available.')
    fingerprint={'source_sha256':digest(source.read_bytes()),
        'case_sha256':digest(case_path.read_bytes()),
        'runner_sha256':digest(Path(__file__).read_bytes()),
        'registry_entry':entry,'environment':env}
    # Declare helper files in the registry if an implementation imports local code.
    fingerprint['dependencies']={p:digest((ROOT/p).read_bytes()) for p in entry.get('sources',[])}
    key=digest(json.dumps(fingerprint,sort_keys=True).encode())
    cache=ROOT/'.cache'/f'{key}.json'
    if not no_cache and cache.is_file():
        try:
            saved=read_json(cache)
            errors=validate(saved.get('payload'),case,entry['implementation'])
        except (json.JSONDecodeError,AttributeError,OSError):
            errors=['Invalid cache; rerun.']
        if not errors:
            return dict(result,status='passed',cached=True,payload=saved['payload'],fingerprint=fingerprint)
    child_env=os.environ.copy()
    child_env.pop('PYTHONOPTIMIZE',None)
    child_env['PYTHONDONTWRITEBYTECODE']='1'
    try:
        # Each implementation runs alone. Its stdout is the JSON contract.
        with tempfile.TemporaryDirectory(prefix='physics-check-') as workdir:
            proc=subprocess.run([sys.executable,str(source),str(case_path)],
                cwd=workdir,env=child_env,capture_output=True,text=True,timeout=timeout)
        if proc.returncode:
            return dict(result,status='failed',cached=False,
                reason=f'Implementation exited {proc.returncode}.',stdout=proc.stdout,stderr=proc.stderr)
        payload=json.loads(proc.stdout)
        errors=validate(payload,case,entry['implementation'])
        if errors:
            return dict(result,status='failed',cached=False,errors=errors,payload=payload,stderr=proc.stderr)
    except (subprocess.TimeoutExpired,json.JSONDecodeError,OSError) as exc:
        return dict(result,status='failed',cached=False,reason=str(exc))
    cache.parent.mkdir(exist_ok=True)
    cache.write_text(json.dumps({'payload':payload,'fingerprint':fingerprint},indent=2)+'\n')
    return dict(result,status='passed',cached=False,payload=payload,fingerprint=fingerprint)

def compare(results):
    comparisons=[]
    for case_name in sorted({r['case'] for r in results}):
        good=[r for r in results if r['case']==case_name and r['status']=='passed']
        if len(good)<2:
            comparisons.append({'case':case_name,'status':'incomplete',
                'reason':'Fewer than two original implementations passed.'})
            continue
        fixture=read_json(ROOT/'cases'/f'{case_name}.json')
        differences=[]
        for name,rule in fixture['observables'].items():
            values={r['implementation']:r['payload']['observations'][name] for r in good}
            reference=next(iter(values.values()))
            if any(not math.isclose(reference,v,rel_tol=rule['rtol'],abs_tol=rule['atol']) for v in values.values()):
                differences.append({'observable':name,'values':values,'unit':rule['unit']})
        comparisons.append({'case':case_name,'status':'disagree' if differences else 'agree',
                            'differences':differences})
    return comparisons

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    sub=parser.add_subparsers(dest='command',required=True)
    sub.add_parser('list')
    check=sub.add_parser('check')
    check.add_argument('--case',action='append',help='Case name; repeat to select several.')
    check.add_argument('--implementation',action='append',help='Implementation identity; repeat if needed.')
    check.add_argument('--no-cache',action='store_true')
    check.add_argument('--timeout',type=float,default=60)
    check.add_argument('--report',type=Path,default=ROOT/'reports/latest.json')
    args=parser.parse_args()
    entries=read_json(ROOT/'registry.json')['entries']
    if args.command=='list':
        for e in entries: print(f"{e['case']:22s} {e['implementation']:8s} {e['status']}")
        return 0
    known_cases={e['case'] for e in entries}; known_impls={e['implementation'] for e in entries}
    if args.case and set(args.case)-known_cases: parser.error('Unknown case selection.')
    if args.implementation and set(args.implementation)-known_impls: parser.error('Unknown implementation selection.')
    selected=[e for e in entries if (not args.case or e['case'] in args.case)
              and (not args.implementation or e['implementation'] in args.implementation)]
    if not selected: parser.error('No implementation matches both selections.')
    env=environment()
    results=[run_entry(e,env,args.no_cache,args.timeout) for e in selected]
    comparisons=compare(results)
    report={'schema_version':1,'run_utc':datetime.now(timezone.utc).isoformat(),
        'environment':env,'results':results,'comparisons':comparisons}
    args.report.parent.mkdir(parents=True,exist_ok=True)
    args.report.write_text(json.dumps(report,indent=2)+'\n')
    for r in results:
        print(f"{r['status'].upper():7s} {r['case']:22s} {r['implementation']}"+
              (' (cached)' if r['cached'] else ''))
        for error in r.get('errors',[]): print('        '+error)
    print('Report: '+str(args.report))
    if any(r['status']=='failed' for r in results) or any(c['status']=='disagree' for c in comparisons): return 1
    if any(r['status']=='missing' for r in results): return 2
    return 0

if __name__=='__main__': raise SystemExit(main())
