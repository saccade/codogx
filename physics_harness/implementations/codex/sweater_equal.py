# Codex: the calculation block extracted from write_explanation.py.
# It is no longer necessary to regenerate the document to run these checks.
import math, sys, json
case=json.load(open(sys.argv[1],encoding='utf-8'))
# Check the exact model balances with centered finite differences.
def f(n):return 1-(1+n)*math.exp(-n)
def d(n):return 1-math.exp(-n)
h=1e-5
errors=[]
for n in (.01,.1,.5,1,2,5):
 fp=(f(n+h)-f(n-h))/(2*h)
 dp=(d(n+h)-d(n-h))/(2*h)
 errors.extend((abs(fp-(d(n)-f(n))), abs(dp-(1-d(n)))))
assert max(errors)<1e-8
assert abs(f(.001)/(.001**2/2)-1)<.001
assert 50*30==500*3

observations={}
for t in case['inputs']['times_s']:
 n=t/case['inputs']['lag_s']
 observations[f'cold_{t}_fraction']=f(n)
 observations[f'hot_{t}_fraction']=d(n)
observations['balance_residual']=max(errors)
print(json.dumps({'schema_version':1,'case_id':case['case_id'],
 'implementation':'codex','observations':observations,
 'checks':{'original_assertions_passed':True}}))
