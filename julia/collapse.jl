# Discovered coefficient #2: a dimensionless constant that governs the reversal.
# The critical Deborah number depends on how strongly the rhythm is modulated (b1). We measure
# De_c(b1) for several rhythm strengths and test whether  De_c · <θ̇²> = K  is constant, where
# <θ̇²> = 1 + b1²/2 for θ = t + b1 sin t. A constant product is a genuine dimensionless law, and K
# is the discovered coefficient.
#   run:  julia --startup-file=no --project=. -t auto collapse.jl
include("ViscoelasticSwimmer.jl")
using .ViscoelasticSwimmer
using Printf, JSON, Statistics, Base.Threads

const N = 128; const L = 4π; const BRINK = 0.5; const AMP = 0.35
const B1S = [0.30, 0.40, 0.50, 0.60]
const DES = [0.70, 0.80, 0.90, 1.00]   # brackets every De_c(b1) in [0.77, 0.87]

jobs = [(b1, De, sgn) for b1 in B1S for De in DES for sgn in (-1.0, 1.0)]
res = Dict{Tuple{Float64,Float64,Float64},Float64}()
lk = ReentrantLock()
println("collapse: $(length(jobs)) runs on $(nthreads()) thread(s)"); flush(stdout)
@threads for j in jobs
    b1, De, sgn = j
    s = Swimmer(N=N, L=L, brink=BRINK, lam=De, amp=AMP, stroke=warp_stroke(b1=sgn * b1, amp=AMP))
    r = run_cycles!(s, ncycles=6, nsteps=400)
    lock(lk) do; res[j] = abs(r[end][1]); end
end

out = Any[]
println("\n  b1    <θ̇²>    De_c    De_c·<θ̇²>")
for b1 in B1S
    ratio = [res[(b1, De, 1.0)] / res[(b1, De, -1.0)] for De in DES]   # |closed|/|open|
    Dec = NaN
    for i in 2:length(DES)
        if (ratio[i-1] - 1) * (ratio[i] - 1) <= 0
            Dec = DES[i-1] + (1 - ratio[i-1]) * (DES[i] - DES[i-1]) / (ratio[i] - ratio[i-1]); break
        end
    end
    thetadot2 = 1 + b1^2 / 2
    K = Dec * thetadot2
    @printf("  %.2f  %.4f  %.4f   %.4f\n", b1, thetadot2, Dec, K)
    push!(out, Dict("b1" => b1, "thetadot2" => thetadot2, "De_c" => Dec, "K" => K,
                    "De" => DES, "ratio" => ratio))
end
Ks = [o["K"] for o in out]
@printf("\n  discovered constant  K = %.4f ± %.4f   (spread %.2f%%)\n",
        mean(Ks), std(Ks), 100 * (maximum(Ks) - minimum(Ks)) / mean(Ks))

JSON.print(open(joinpath(@__DIR__, "julia_collapse.json"), "w"),
           Dict("rows" => out, "K_mean" => mean(Ks), "K_std" => std(Ks), "N" => N), 1)
println("wrote julia_collapse.json")
