#!/usr/bin/env python3
"""Tovli Plan: init / validate / render. Standard-library renderer; optional jsonschema validation."""
from __future__ import annotations
import argparse
import json
import html
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / 'assets'
SCHEMA = ROOT / 'references' / 'plan.schema.json'


def read_json(path: Path) -> dict:
    try:
        data = json.loads(path.read_text(encoding='utf-8-sig'))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f'Cannot read JSON {path}: {exc}') from exc
    if not isinstance(data, dict):
        raise ValueError('Plan root must be a JSON object.')
    return data


def err(errors: list[str], where: str, message: str) -> None:
    errors.append(f'{where}: {message}')


def validate(plan: dict) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    # A full JSON Schema validation is run when jsonschema is available.
    try:
        import jsonschema  # type: ignore
    except ImportError:
        warnings.append('Install jsonschema for full type/format validation: python -m pip install jsonschema')
        required = {'schema_version', 'metadata', 'overview', 'plan_now', 'decide', 'steps', 'history'}
        for k in sorted(required):
            if k not in plan:
                err(errors, '/', f'missing required key {k}')
    else:
        from jsonschema import Draft202012Validator, FormatChecker
        schema = read_json(SCHEMA)
        checker = FormatChecker()
        for e in sorted(Draft202012Validator(schema, format_checker=checker).iter_errors(plan), key=lambda x: str(list(x.path))):
            loc = '/'+ '/'.join(str(x) for x in e.path)
            err(errors, loc, e.message)
    md = plan.get('metadata') or {}
    dec = plan.get('decide') or {}
    st = plan.get('steps') or {}
    hist = plan.get('history') or {}
    pn = plan.get('plan_now') or {}
    questions = dec.get('questions') or []
    defaults = dec.get('defaults') or []
    direct = dec.get('direct_decisions') or []
    out = dec.get('out_this_round') or []
    phases = st.get('phases') or []
    diagrams = plan.get('diagrams') or []
    all_items: list[tuple[str, str]] = []
    def collect(items: list[dict], loc: str) -> None:
        for i, item in enumerate(items):
            if not isinstance(item, dict):
                continue
            ident = item.get('id')
            if ident:
                all_items.append((str(ident), f'{loc}[{i}]'))
    for loc, arr in [('decide.questions', questions), ('decide.defaults', defaults),
        ('decide.direct_decisions', direct), ('decide.out_this_round', out),
        ('steps.phases', phases), ('steps.risks', st.get('risks') or []),
        ('history.events', hist.get('events') or []),
        ('plan_now.visual_examples', pn.get('visual_examples') or []),
        ('plan_now.success_measures', pn.get('success_measures') or []),
        ('plan_now.assumptions', pn.get('assumptions') or []), ('diagrams', diagrams)]:
        collect(arr, loc)
    occurrences: dict[str, str] = {}
    for identifier, location in all_items:
        if identifier in occurrences:
            err(errors, location, f'duplicate ID {identifier!r}, first seen in {occurrences[identifier]}')
        else:
            occurrences[identifier] = location
    step_ids = {x.get('id') for x in phases if isinstance(x, dict)}
    decision_ids = {x.get('id') for a in (questions, defaults, direct) for x in a if isinstance(x, dict)}
    other_ids = set(occurrences)
    for i, q in enumerate(questions):
        if not isinstance(q,dict): continue
        opts = [o.get('id') for o in q.get('options', []) if isinstance(o, dict)]
        if len(opts) != len(set(opts)):
            err(errors,f'decide.questions[{i}]','duplicate option IDs')
        for key in ('my_pick_option_id','selected_option_id'):
            x = q.get(key)
            if x and x not in opts:
                err(errors,f'decide.questions[{i}]',f'{key}={x!r} does not identify an option')
        if q.get('status')=='settled':
            if not q.get('selected_option_id') and not (q.get('note') or '').strip():
                err(errors,f'decide.questions[{i}]','settled question has neither a selected option nor a recorded answer in note')
            if not q.get('decided_by') or not q.get('decided_at'):
                warnings.append(f'decide.questions[{i}]: settled decision lacks who/when provenance')
        if q.get('status')=='open' and q.get('selected_option_id'):
            warnings.append(f'decide.questions[{i}]: choice recorded but question remains open; verify its status')
        for sid in q.get('related_step_ids',[]):
            if sid not in step_ids:
                err(errors,f'decide.questions[{i}]',f'unknown related step {sid!r}')
    for i, d in enumerate(defaults):
        if not isinstance(d,dict): continue
        opts = {o.get('id') for o in d.get('options',[]) if isinstance(o,dict)}
        for key in ('default_option_id','selected_option_id'):
            x=d.get(key)
            if x and x not in opts:
                err(errors,f'decide.defaults[{i}]',f'{key}={x!r} does not identify an option')
        if d.get('status') == 'proposed' and d.get('selected_option_id'):
            warnings.append(f'decide.defaults[{i}]: selected option exists but default still proposed')
        if d.get('status') in ('implicitly_accepted','explicitly_accepted','overridden'):
            if not d.get('accepted_by') or not d.get('accepted_at'):
                warnings.append(f'decide.defaults[{i}]: accepted default needs who/when provenance')
            if d.get('status')=='implicitly_accepted':
                warnings.append(f'decide.defaults[{i}]: implicit acceptance requires an explicitly agreed rule documented in history')
            if d.get('status')=='overridden' and d.get('selected_option_id')==d.get('default_option_id'):
                warnings.append(f'decide.defaults[{i}]: override equals default; check status')
    graph: dict[str,list[str]]={x:[] for x in step_ids if x}
    for i,s in enumerate(phases):
        if not isinstance(s,dict): continue
        sid=s.get('id')
        for dep in s.get('depends_on',[]):
            if dep not in step_ids:
                err(errors,f'steps.phases[{i}]',f'unknown prerequisite step {dep!r}')
            elif dep==sid:
                err(errors,f'steps.phases[{i}]','step depends on itself')
            else: graph[sid].append(dep)
        for d in s.get('decision_ids',[]):
            if d not in decision_ids:
                err(errors,f'steps.phases[{i}]',f'unknown decision reference {d!r}')
        if s.get('status')=='done' and not (s.get('done_when') or '').strip():
            warnings.append(f'steps.phases[{i}]: done step has no completion criterion')
        if s.get('status') in ('in_progress','done') and s.get('commitment_status') == 'proposed':
            warnings.append(f'steps.phases[{i}]: execution status indicates work, but step is only proposed')
        if s.get('commitment_status')=='committed' and not s.get('owner'):
            warnings.append(f'steps.phases[{i}]: committed step has no accountable owner')
    visited: dict[str,int]={}
    def visit(n: str):
        v=visited.get(n,0)
        if v==1: raise ValueError(n)
        if v==2: return
        visited[n]=1
        for child in graph.get(n,[]): visit(child)
        visited[n]=2
    try:
        for step in graph: visit(step)
    except ValueError as exc:
        err(errors,'steps.phases',f'cycle in dependencies involving {exc}')
    for i,diag in enumerate(diagrams):
        if not isinstance(diag,dict): continue
        nds={n.get('id') for n in diag.get('nodes',[]) if isinstance(n,dict)}
        if len(nds)!=len(diag.get('nodes',[])):
            err(errors,f'diagrams[{i}]','missing or duplicate node IDs')
        for edge in diag.get('edges',[]):
            for key in ('from','to'):
                if edge.get(key) not in nds:
                    err(errors,f'diagrams[{i}]',f'{key}={edge.get(key)!r} not in nodes')
        for d in diag.get('related_decision_ids',[]):
            if d not in decision_ids: err(errors,f'diagrams[{i}]',f'unknown decision {d!r}')
    for i,vis in enumerate(pn.get('visual_examples') or []):
        for ann in vis.get('decision_annotations') or []:
            if ann.get('decision_id') not in decision_ids:
                err(errors,f'plan_now.visual_examples[{i}]',f'unknown decision annotation {ann.get("decision_id")!r}')
    for i,j in enumerate(pn.get('user_journey') or []):
        for d in j.get('linked_decision_ids') or []:
            if d not in decision_ids: err(errors,f'plan_now.user_journey[{i}]',f'unknown decision {d!r}')
    for i,r in enumerate(st.get('risks') or []):
        for s in r.get('linked_step_ids') or []:
            if s not in step_ids: err(errors,f'steps.risks[{i}]',f'unknown step {s!r}')
    ask=md.get('immediate_ask') or {}
    if ask.get('status')=='none' and any(q.get('status')=='open' and q.get('blocking',True) for q in questions):
        warnings.append('metadata.immediate_ask: says none, but one or more blocking decisions remain open')
    for ref in ask.get('linked_ids',[]):
        if ref not in other_ids: warnings.append(f'metadata.immediate_ask: linked ID {ref!r} is not defined')
    versions=hist.get('versions') or []
    if versions and md.get('version')!=versions[-1].get('version'):
        err(errors,'metadata.version',f"{md.get('version')!r} disagrees with latest recorded version {versions[-1].get('version')!r}")
    return errors,warnings


def render(plan: dict, target: Path):
    template=(ASSETS/'plan-viewer.html').read_text(encoding='utf-8')
    if template.count('__PLAN_DATA__')!=1:
        raise ValueError('HTML template must contain exactly one __PLAN_DATA__ placeholder')
    # JSON in a script[type=application/json] requires escaping HTML-significant bytes.
    embedded=json.dumps(plan,ensure_ascii=False,separators=(',',':'))
    embedded=(embedded.replace('&','\\u0026').replace('<','\\u003c')
              .replace('>','\\u003e').replace('\u2028','\\u2028').replace('\u2029','\\u2029'))
    rendered=template.replace('__PLAN_DATA__',embedded)
    title=plan.get('metadata',{}).get('title') or 'Work plan'
    rendered=rendered.replace('<title>Tovli Plan</title>',
        '<title>'+html.escape(str(title))+' | Planning Canvas</title>',1)
    target.parent.mkdir(parents=True,exist_ok=True)
    target.write_text(rendered,encoding='utf-8')
    return target


def report(errors,warnings):
    for issue in errors: print('ERROR: '+issue,file=sys.stderr)
    for issue in warnings: print('WARNING: '+issue,file=sys.stderr)
    if not errors: print(f'Validated: 0 errors, {len(warnings)} warning(s).')


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    cmds=parser.add_subparsers(dest='command',required=True)
    init=cmds.add_parser('init',help='Create a blank plan.json and matching plan.html')
    init.add_argument('path',type=Path,help='Destination JSON path, e.g. my-project/planning/plan.json')
    init.add_argument('--title',default='Untitled work plan')
    init.add_argument('--id',default='PLAN-NEW')
    init.add_argument('--date',default=date.today().isoformat())
    init.add_argument('--force',action='store_true')
    v=cmds.add_parser('validate',help='Validate a plan JSON file')
    v.add_argument('path',type=Path)
    v.add_argument('--strict',action='store_true',help='Warnings also make validation fail')
    r=cmds.add_parser('render',help='Generate the standalone HTML viewer for a plan JSON file')
    r.add_argument('path',type=Path)
    r.add_argument('--out',type=Path,help='HTML destination (default: next to JSON as plan.html)')
    r.add_argument('--strict',action='store_true')
    args=parser.parse_args(argv)
    try:
        if args.command=='init':
            if args.path.exists() and not args.force:
                raise ValueError(f'{args.path} already exists (use --force to replace)')
            data=read_json(ASSETS/'plan.template.json')
            data['metadata']['id']=args.id
            data['metadata']['title']=args.title
            data['metadata']['as_of']=args.date
            data['plan_now']['as_of']=args.date
            data['history']['versions']=[{'version':'v1','date':args.date,'stage':'Discovering','change_summary':'Initialized blank planning template'}]
            args.path.parent.mkdir(parents=True,exist_ok=True)
            args.path.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
            errors,warnings=validate(data);report(errors,warnings)
            if errors: return 1
            out=args.path.with_suffix('.html');render(data,out)
            print(f'Created {args.path} and {out}')
        else:
            plan=read_json(args.path)
            errors,warnings=validate(plan);report(errors,warnings)
            if errors or (args.strict and warnings): return 1
            if args.command=='render':
                out=args.out or args.path.with_suffix('.html')
                render(plan,out)
                print(f'Rendered {out}')
    except (ValueError,OSError) as exc:
        print(f'ERROR: {exc}',file=sys.stderr)
        return 2
    return 0

if __name__=='__main__':
    sys.exit(main())
