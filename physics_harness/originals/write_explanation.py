from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo
import math, json, textwrap, unicodedata, shutil, tempfile

root=Path('/workspace/scratch/c6c5d3f3995e')
now=datetime.now(ZoneInfo('America/New_York'))
blocks=[]
def prose(s):
    blocks.append(textwrap.fill(s,width=68,break_long_words=False,break_on_hyphens=False))
def fixed(s):
    blocks.append(s.strip('\n'))
fixed('THE SWEATER HAS TO KEEP IT\n==========================')
prose(f'Codex (OpenAI), for dr. kraemer. Dog math working notes, not manuscript text. Written {now:%Y-%m-%d %H:%M} EDT.')
prose('You want the sweater warm when you put it on. Feeling hot for a moment inside the dryer is only the audition.')
prose('There are two waits. First the dryer warms enough to warm the clothing well. Then enough of the clothing warms to carry that warmth out with it. Those waits overlap: the sweater starts taking heat while the dryer is still warming.')
prose('At first there is little to pass on. In the middle there is a good temperature gap and plenty of cold cloth left to warm. Near the end there is little gap left. That gives the curve you described: a slow start, a generous middle, and a taper.')
fixed('Hot where?\n----------')
prose('A chilly sweater in an already-hot dryer can get hot in the places the air reaches first. Your hand meets those places first too. But the sleeves, folds, seams, yarn and sheltered cloth need not all have caught up.')
prose('Call heat capacity the hold, C: how much heat a thing holds for each degree of temperature rise. Give our example sweater a hold of 500 thump a degree. A thump is a joule. These are chosen dog numbers, not a measurement of your sweater.')
fixed('    heat added = hold across temperature rise\n\n         E     =  C θ')
prose('Here θ counts degrees above the room. Celsius degrees and kelvin steps are the same size.')
prose('Warm the whole hold by 30 degrees and the sweater holds 15,000 extra thump. Warm only a tenth of that hold by 30 degrees and it holds 1,500. Both can present the same hot patch to your hand. One has ten times as much heat behind it.')
fixed('    whole sweater:    500 across 30 = 15,000 thump\n    exposed fraction:  50 across 30 =  1,500 thump')
prose('Now let the second sweater even out internally, before any heat escapes. The same 1,500 thump spreads across the whole hold of 500. The temperature rise settles at 3 degrees. The hot patch has cooled by 27 degrees without the sweater losing a single thump to the room.')
prose('Then the room takes some as well. Shake the sweater open and fresh air meets more cloth. By the time you put it on, that impressive hot patch may have very little left to say.')
prose('So yes: surface warmth can be the flash. Warming enough of the hold is what gives the flash some backing. In porous, tumbling clothing, "surface" means whatever is exposed first; it need not be a neat outer skin.')
fixed('What the temperature gap does\n-----------------------------')
prose('The hotter air passes heat to cooler cloth. A bigger temperature gap drives more power through the same connection. Let G be the thermal conductance: the pow passed for each degree of gap. A pow is a thump a second.')
fixed('    P = G (θ_d − θ_c)\n\n    dE = C dθ_c = P dt\n\n    C dθ_c = G (θ_d − θ_c) dt')
prose('The subscripts mark dryer and cloth. Through a little time, the heat passed from the dryer is stored in the cloth as a temperature rise. As the cloth warms, the gap closes and the passing slows.')
prose('The hold resists a quick temperature change. The conductance lets the change through. Their ratio is a time; call that the lag, τ.')
fixed('    C = G τ,                 τ dθ_c = (θ_d − θ_c) dt')
prose('A bigger hold lags longer through the same connection. A stronger connection warms the same hold sooner. The dryer has its own warming lag: the incoming air and drum do not arrive at their working temperatures the instant you touch the switch.')
fixed('Two waits make the curve\n------------------------')
prose('For a small model, let the dryer approach a steady temperature rise Θ, and let the slow-warming cloth follow it. Fold the quick surface details into the connection. Ignore the small cloth load changing the dryer curve. These are effective warming lags, not a claim that the whole drum or sweater has one temperature.')
fixed('    τ_d dθ_d = (Θ − θ_d) dt\n    τ_c dθ_c = (θ_d − θ_c) dt')
prose('Start both cold. The dryer initially builds the gap that warms the cloth. If that gap grows roughly with elapsed time, the cloth takes heat at a rate that grows roughly with elapsed time. Add up that growing rate and the stored heat begins roughly as time squared.')
prose('Twice a very short warming time can give about four times the lasting warmth. That is the slow start turning upward. It is not the rule once things have warmed.')
prose('Make the two lags equal so the curve can show itself without a mouthful. Call their common lag τ, and count elapsed lags with n = t/τ.')
fixed('    dryer:    θ_d = Θ [1 − exp(−n)]\n\n    cloth:    θ_c = Θ [1 − (1 + n) exp(−n)]')
prose('The exponential is the ordinary fading-away curve. The extra factor, 1 + n, is what the second wait adds. The cloth starts flat, bends up, then bends down toward its final temperature. The gain per extra second is greatest after one lag.')
prose('Set τ to one minute just to read the example. This is a scale for the model, not a timer recommendation. The numbers are fractions of the final temperature rise in the slow-warming cloth.')
fixed('    warming time     cold dryer       already-hot dryer\n    ---------------------------------------------------\n       10 seconds       about 1%           about 15%\n       30 seconds       about 10%          about 40%\n        1 minute        about 25%          about 65%\n        2 minutes       about 60%          about 85%\n        3 minutes       about 80%          about 95%\n        5 minutes       nearly all         nearly all')
prose('The hot-dryer column removes the first wait: θ_c = Θ [1 − exp(−n)]. That curve starts rising immediately and tapers from the start. Even so, ten seconds is only a small part of a one-minute lag. A fast hot patch can sit on top of either column.')
prose('So the cold-start curve naturally has your slow-fast-slow shape. A preheated dryer need not give the same flat beginning. Your observation about ten seconds still fits: early surface temperature can promise more than the stored heat can deliver.')
fixed('Keep it until you wear it\n-------------------------')
prose('For the job you actually care about, call the keep U: the extra heat still in the clothing when you put it on, after the usual trip from dryer to body. Keep the trip the same when comparing warming times.')
prose('If that trip loses a roughly fixed fraction of the slow-warming store, the keep follows the same curve at a smaller height. If it mostly strips off a fast surface flash, it makes the difference between a flash and a well-warmed sweater more conspicuous.')
prose('Keep is a useful physical measure for this job, not a complete measure of comfort. Where the warmth sits, what touches your skin, and how quickly heat passes also matter. A prewarmed sweater can be more pleasant even below skin temperature: your body has less cold cloth to warm.')
prose('To compare the curves at home, compare them at the moment of wearing. Start with a similarly cool, dry garment, give it different warming times, and keep the carry time similar. A touch inside the drum answers a different question.')
prose('There is no single best minute hidden in the curve. That depends on when the shower ends and how much warmth you want. The physics says why a little extra time can help enormously in the middle and hardly matter near the top.')
prose('The dryer has to warm up. The sweater has to warm through. Then it has to keep enough of that warmth to meet you.')
fixed('Model notes and provenance\n--------------------------')
prose('The two-lag curve is a deliberately small model of the reported experience, not a fit to a particular dryer. Heater cycling, airflow, tumbling, fabric and folds change the lags and the detailed curve. Dry clothing is assumed; evaporation from damp clothing adds another energy demand.')
prose('The 500-thump hold, 30-degree rise and one-minute lags are illustrative choices. No material property or appliance timing was inferred from them. The two-store example conserves energy during internal equalization. The curve values and early-time behavior were checked against the stated differential balances.')
prose('Starting warm-up can involve both rapid surface heating and slow penetration or access. The first-order cloth model collects those effects into one lag; it does not resolve the temperature field. A small surviving fast component can keep the total usefulness curve from being exactly flat at the origin.')
prose('Thermal background checked against MIT Unified Engineering notes. Their heat balance gives heat capacity times temperature change equal to transferred heat, power proportional to temperature gap, and the capacity/conductance time constant. Their treatment also states when a uniform body temperature is an appropriate approximation.')
fixed('    MIT, 18.3: Transient Heat Transfer\n    https://web.mit.edu/course/16/16.unified/www/FALL/\n    thermodynamics/notes/node129.html\n\n    MIT, 18.4: Modeling Complex Physical Processes\n    https://web.mit.edu/course/16/16.unified/www/FALL/\n    thermodynamics/notes/node130.html\n\n    MIT, 16.2: Introduction to Conduction\n    https://web.mit.edu/16.unified/www/FALL/thermodynamics/\n    notes/node116.html')
prose('Language reference: Claude Dog Math 2610191934, read in full. The differential layout and physical transaction follow dr. kraemer\'s instructions in this conversation. The model and wording here are Codex\'s.')
text='\n\n'.join(blocks)+'\n'
width=lambda line:sum(not unicodedata.combining(c) for c in line)
assert max(map(width,text.splitlines()))<=68
path=root/'dryer'/f'Codex_The_Sweater_Has_to_Keep_It_{now:%y%m%d%H%M}.txt'
path.write_text(text)

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
helperdir=Path(tempfile.mkdtemp(prefix='library_sweater_',dir=root))/'scripts'
shutil.copytree('/root/.codex/plugins/cache/openai-curated-remote/openai-library/0.1.65/skills/library/scripts',helperdir)
manifest={'path':str(path),'helper':str(helperdir/'library_file_transfer.py'),'stamp':now.strftime('%y%m%d%H%M'),'max_balance_error':max(errors),'max_column':max(map(width,text.splitlines())),'words':len(text.split())}
(root/'dryer/delivery.json').write_text(json.dumps(manifest,indent=2))
print(json.dumps(manifest))
