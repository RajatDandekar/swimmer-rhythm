# Discovered coefficient #1: the amplitude-scaling exponent.
# A reciprocal swimmer in a viscoelastic fluid moves because elasticity breaks the scallop theorem;
# the leading response is quadratic in the stroke amplitude. We sweep the amplitude of the plain
# sinusoidal stroke and fit  |Δx| ∝ amp^p , recovering p ≈ 2 from the solver alone.
#   run:  julia --startup-file=no --project=. -t auto amp_scaling.jl
include("ViscoelasticSwimmer.jl")
using .ViscoelasticSwimmer
using Printf, JSON, Statistics, Base.Threads

const N = 128; const L = 4π; const BRINK = 0.5; const DE = 1.0
const AMPS = [0.06, 0.08, 0.11, 0.14, 0.18, 0.23, 0.30]

res = Vector{Any}(undef, length(AMPS))
@threads for i in eachindex(AMPS)
    a = AMPS[i]
    s = Swimmer(N=N, L=L, brink=BRINK, lam=DE, amp=a, stroke=warp_stroke(b1=0.0, amp=a))
    r = run_cycles!(s, ncycles=6, nsteps=500)
    res[i] = Dict("amp" => a, "dx" => abs(r[end][1]))
end
amps = [r["amp"] for r in res]; dxs = [r["dx"] for r in res]

# least-squares slope of log|Δx| vs log(amp)
X = log.(amps); Y = log.(dxs)
p = (mean(X .* Y) - mean(X) * mean(Y)) / (mean(X .^ 2) - mean(X)^2)
c = mean(Y) - p * mean(X)
@printf("amplitude exponent  p = %.4f   (theory: 2.000)\n", p)

JSON.print(open(joinpath(@__DIR__, "julia_amp.json"), "w"),
           Dict("amps" => amps, "dx" => dxs, "exponent" => p, "logintercept" => c,
                "De" => DE, "N" => N), 1)
println("wrote julia_amp.json")
