import sys, os
import eng, gen, specs13, clips13
which = sys.argv[1:] or list(specs13.V.keys())
for k in which:
    wd = eng.S + f"/w13/{k}"
    eng.KNOTS[:] = [(0.0, 0.0)]
    for sc, c in zip(specs13.V[k]['scenes'], clips13.C[k]): sc['clip'] = c
    try:
        d = gen.run(k, specs13.V[k], wd)
        print("OK", k, round(d, 1), flush=True)
    except Exception as e:
        import traceback; traceback.print_exc(); print("FAIL", k, e, flush=True)
