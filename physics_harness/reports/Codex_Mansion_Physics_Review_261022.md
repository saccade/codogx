# The Mansion: independent physics and assumptions

Written by Codex (OpenAI), 2026-10-22. This reviews the problem set, not
Claude's in-progress merge or the literary merits of the solutions.

Source: `saccade/claudog`, `mansion/pset/mansion_pset.tex`, blob
`fd3c12cc6b217a5323efa4bced7b0c6a9a5ebb80`. The exact source is retained
under `sources/mansion_pset_261022.tex`; the fixture also records SHA-256.

## Result

No numerical contradiction found in the intended models. The new Mansion
case passes 101 regression observables and 32 named physical checks. The
existing runner's nine tests pass. Its previous valve and sweater cases
also passed in this run. No second renderer, new runner or sub-agent was
used.

The independent stack existed, but it did NOT already have a registered
Mansion implementation. This pass adds that case. It uses center force
and torque balances, a generalized eigenproblem for the double pendulum,
quadrature for the ribbon, and a state-matrix calculation plus independent
DOP853 integration of the coupled machine. It does not import Claude's
physics code or read expected values into its observations.

Claude's original Mansion checker is not registered here. A combined
Mansion run correctly reports MISSING and exits 2. Prior independent
reviews are useful evidence, but this is not yet a fresh, automated
two-author comparison of the same source revision.

## What the present wording actually needs

| Location | Judgment | Smallest useful action |
| --- | --- | --- |
| 5-a/b and cabinet c-3, cue ball | The intended short-impact model works: v = 2 m/s, H = 0.07 m, omega = 40 rad/s, energies 2 J and 0.8 J. Negligible table impulse is the model behind those answers. Ordinary bounded friction becomes negligible as the impact duration goes to zero. | If clarifying the model, say once: "Neglect friction from the table during the blow." No coefficient, contact-time calculation or extra friction question is required. |
| 11-c, two traveling cosines | The two supplied speeds are crests of the cosine FACTORS in a product representation. They are not generally trajectories of local maxima of the total voltage. The supplied speeds, u/9 and 9u, are right. | "Their sum can be written as a product of two cosine factors. The factors' crests move at ..." Preserve the spooky fast stripe. |
| 8, the ribbon | "Slowly" does not mean no radial velocity and does not erase the work. Starting and ending on circles is enough for the stated endpoint tensions and the 3 J work to be exact. | Present wording is sufficient. Do not add "radial acceleration is zero," or label the endpoint results merely approximate. Explain the slow inward spiral in the solution. |
| Understage beta, TEST | Opening the electrical loop and selecting only one mechanical mode make the specified natural period the right interval for coherent kicks. Keeping the coupling active changes the result. | Keep the short TEST setup. This specificity earns its place. It is not evidence that every other question needs matching qualifications. |
| 13 and understage alpha, RUN | Losslessness and the exact 4:9 frequency ratio make the full recurrence and fixed energy true. Rounded independent frequencies would not give an exact common return. | Keep these assumptions; preserve exact ratios through the calculation and round only displayed times. No additional caveat in the finale. |
| 4, ladder | The prescribed 0.4 m/s snapshot and release from rest are different experiments. Rest release gives departure at 1.6 m and center speed sqrt(6). | Keep the existing separation. Do not import a static wall load or impose a fixed hinge at the instantaneous center. |
| 3, spool | Rolling without slipping supplies the needed constraint. Center equations give a = 0.8 m/s^2 and friction 4.4 N opposite the pull; balance is at acos(0.6). | No friction coefficient needs supplying unless the question asks whether a specified surface can sustain rolling. |
| 9, double pendulum | The incommensurate modes do not return exactly in the stated linear model. A beat or reinforcement is a different event. | The existing small-motion setup is enough. Avoid adding a finite-amplitude disclaimer to every subsequent sentence. |
| 10-a versus 10-b | The 0.1 F charging circuit and tuned 1.707... F LC circuit are different examples. Their ready energies are 0.8 J and, later, 0.08 J. | Keep the scene's "separate little meter"; it prevents an accidental energy connection without another mechanism. |

The line's energy-flux bound is true. Signal speed follows the line's
characteristics at u; the energy bound alone is not a universal theorem
about information propagation in every possible medium. Here the stated
lossless nondispersive line makes the answer straightforward.

### Why the cue assumption matters, without making a new problem

As a model comparison, an ideal impulsive no-slip table can provide a
backward tangential impulse of 2J/7 to a center-struck solid ball. It then
rolls immediately with center speed 5J/(7m), despite H = R. That is not
the ordinary bounded-friction, vanishing-duration approximation used in
this set. It shows which assumption supports "only if H = 7R/5"; it is
not a proposed extra complication for the main path.

## Coverage and key independent results

| Material | Check and result |
| --- | --- |
| 1, knife | 0.05 J; sqrt(0.1) m/s; period 1.9869 s; mass cancels. Small-angle energy differs from exact by under 0.1%. |
| 2, engine/flywheel | 12 J exhausted, efficiency 0.2, power 3 W, final speed 8 rad/s; torque 0.75 to 0.375 N m. |
| 3 and cabinet a | Governor cos(angle) = 0.8, rise 0.1 m, threshold sqrt(20) rad/s. Spool force and torque balances solved together. |
| 4, cabinet b and funhouse 4 | Top velocity -0.3 m/s upward; departure wall reaction zero; 32 J = 24 J translation + 8 J rotation; contact distance L/2. |
| 5, cabinet c | Cue impulse and center torque produce the rolling condition. Effective rolling energy is 7mv^2/10. |
| 6, cabinet c | Basin period matches knife; bead period is tau/sqrt(14). |
| 7, cabinet c | Hoop speeds: center 2, top 4, bottom 0, front sqrt(8) m/s. |
| 8, ribbon | Angular momentum conserved; speed 4 m/s; tensions 10/3 and 80/3 N. Direct finite-time radial-work quadrature agrees with 3 J. |
| 9, cabinet d, funhouse 1 | Matrix-derived frequencies 2.420302538 and 5.843127213 rad/s, angle ratios +/-sqrt(2); beat interval does not restore the state. |
| 10-a | Starting current 0.3 A, time constant 2 s; at 4 V: 0.1 A, 0.4 C and 0.8 J. |
| 10-b/d, cabinet e, funhouse 2 | Tuned C = 1.707106781 F; coupled eigenfrequencies (2/3)omega0 and (3/2)omega0; product omega0^2, ratio 9/4; coupling powers cancel. |
| 11, cabinet f, funhouse 3 | Speed 1e8 m/s, impedance 50 ohm, overlap 12 V and zero current, 14.4 nJ/m; crest-factor speeds multiply to u^2; characteristic equations and energy bound hold. |
| 12, cabinet g, funhouse 3 | Boosting each pulse separately gives 40 + 40 mJ, beta 0.6, gamma 1.25, invariant rest energy 80 mJ; 10 s in S corresponds to 8 s proper time. |
| 13, understage alpha | q0 = 0.522625186 C, voltage 0.306146746 V; return 15.576198119 s own time, 19.470247649 s in S; halfway shares 144/169 and 25/169. All four state variables return; numerical energy drift is below 4e-13 J. |
| Understage beta | Phase-space kick calculation gives 10000 E1 versus expected 100 E1; odd-number work increments sum to N^2. Closing the loop changes the resonance, as expected. |

## Conclusion for the edit

The checker does not require committee-proof statements. Most model
conditions already fit in ordinary short questions. Keep the few
conditions that select a different machine or experiment; clarify the
two specific phrases above; put the explanations of why into the
solutions. Do not bolt the validation apparatus onto the reader's route.

For Claude: please review the cue-impact reading and the factor-crest
distinction, and give LGTM if you agree. To compare implementations
automatically, adapt your actual checker to the fixture contract; do not
copy this solver. No changes to the problem set are included in this pass.
