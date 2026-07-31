# A denser Deborah-number sweep for smooth curves + symbolic-regression training data.
# Both mirror rhythms, N=192, over De in [0.3, 3.0]. Writes julia_dense.json.
#   run:  julia --startup-file=no --project=. -t auto dense.jl
include("ViscoelasticSwimmer.jl")
using .ViscoelasticSwimmer
using Printf, JSON, Base.Threads

const N = 192; const L = 4π; const BRINK = 0.5; const AMP = 0.35
const NSTEPS = 600; const NCYC = 6                     # NumPy-grade accuracy, matched settings
# 18 Deborah numbers over 0.3–3.0, dense through the crossover for a precise De_c and a smooth law
const DES = [0.30, 0.40, 0.50, 0.60, 0.70, 0.80, 0.85, 0.90, 0.95,
             1.00, 1.10, 1.25, 1.45, 1.70, 2.00, 2.35, 2.70, 3.00]

jobs = [(lam, b1) for lam in DES for b1 in (-0.5, 0.5)]
res = Vector{Any}(undef, length(jobs))
println("dense sweep: $(length(jobs)) jobs on $(nthreads()) thread(s) (N=$N, nsteps=$NSTEPS)")
flush(stdout)
@threads for i in eachindex(jobs)
    lam, b1 = jobs[i]
    s = Swimmer(N=N, L=L, brink=BRINK, lam=lam, amp=AMP, stroke=warp_stroke(b1=b1, amp=AMP))
    r = run_cycles!(s, ncycles=NCYC, nsteps=NSTEPS)
    res[i] = Dict("lam" => lam, "b1" => b1, "dx" => r[end][1])
    @printf("  done De=%.2f b1=%+.1f\n", lam, b1); flush(stdout)
end
JSON.print(open(joinpath(@__DIR__, "julia_dense.json"), "w"),
           Dict("params" => Dict("N" => N, "nsteps" => NSTEPS, "ncyc" => NCYC,
                                 "brink" => BRINK, "amp" => AMP), "results" => res), 1)
println("wrote julia_dense.json")
