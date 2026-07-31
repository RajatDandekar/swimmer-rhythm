# One sweep point, for the Modal driver. Prints "dx stokes_res" for a single (De, b1, amp).
# ARGS: De  b1  amp  N  nsteps  ncyc
include(joinpath(@__DIR__, "ViscoelasticSwimmer.jl"))
using .ViscoelasticSwimmer
De  = parse(Float64, ARGS[1]); b1 = parse(Float64, ARGS[2]); amp = parse(Float64, ARGS[3])
N   = parse(Int, ARGS[4]); nsteps = parse(Int, ARGS[5]); ncyc = parse(Int, ARGS[6])
s = Swimmer(N=N, L=4π, brink=0.5, lam=De, amp=amp, stroke=warp_stroke(b1=b1, amp=amp))
r = run_cycles!(s, ncycles=ncyc, nsteps=nsteps)
println(r[end][1], " ", r[end][2])
