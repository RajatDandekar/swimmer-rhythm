# Reproduce the central result in Julia: the optimal stroke rhythm of a reciprocal microswimmer
# REVERSES at a critical Deborah number. We sweep the Deborah number for the two mirror rhythms
# (linger-open b1=-0.5, linger-closed b1=+0.5) and find where the faster of the two flips.
#
#   run with:  julia --startup-file=no --project=. -t auto reversal.jl
#
include("ViscoelasticSwimmer.jl")
using .ViscoelasticSwimmer
using Printf, JSON, Base.Threads

const N      = 192
const L      = 4π
const BRINK  = 0.5
const AMP    = 0.35
const NSTEPS = parse(Int, get(ENV, "NSTEPS", "600"))
const NCYC   = parse(Int, get(ENV, "NCYC", "6"))
# De values chosen to bracket the crossover and to coincide with the NumPy run for comparison
const DES    = [0.50, 0.60, 0.70, 0.80, 0.90, 1.00, 1.20, 1.50, 2.00]

# NumPy reference (same physics, other language) for a side-by-side check
const PY = JSON.parsefile(joinpath(@__DIR__, "..", "viscoelastic", "crossover_results.json"))
pyget(lam, b1) = only(filter(x -> x["ok"] && isapprox(x["lam"], lam) &&
                                  isapprox(x["b1"], b1), PY))["dx"]

jobs = [(lam, b1) for lam in DES for b1 in (-0.5, 0.5)]
results = Vector{Any}(undef, length(jobs))
println("running $(length(jobs)) jobs on $(nthreads()) thread(s)  " *
        "(N=$N, brink=$BRINK, amp=$AMP, nsteps=$NSTEPS, ncyc=$NCYC)")
flush(stdout)

@threads for i in eachindex(jobs)
    lam, b1 = jobs[i]
    s = Swimmer(N=N, L=L, brink=BRINK, lam=lam, amp=AMP, stroke=warp_stroke(b1=b1, amp=AMP))
    r = run_cycles!(s, ncycles=NCYC, nsteps=NSTEPS)
    results[i] = Dict("lam" => lam, "b1" => b1, "dx" => r[end][1],
                      "stokes_res" => r[end][2], "per_cycle" => [x[1] for x in r])
    @printf("  done  De=%.2f  b1=%+.1f   dx=% .4e\n", lam, b1, r[end][1]); flush(stdout)
end

open_dx   = Dict(r["lam"] => r["dx"] for r in results if r["b1"] == -0.5)
closed_dx = Dict(r["lam"] => r["dx"] for r in results if r["b1"] == +0.5)

println("\n  De     open (b1=-0.5)  closed (b1=+0.5)  ratio|c|/|o|  winner   maxΔ vs NumPy")
println("  " * "-"^76)
Dec = nothing; prevr = nothing; prevDe = nothing; maxpy = 0.0
for De in DES
    o = abs(open_dx[De]); c = abs(closed_dx[De]); ratio = c / o
    dpy = max(abs(open_dx[De] - pyget(De, -0.5)) / abs(pyget(De, -0.5)),
              abs(closed_dx[De] - pyget(De, +0.5)) / abs(pyget(De, +0.5)))
    global maxpy = max(maxpy, dpy)
    @printf("  %4.2f  % .4e    % .4e    %7.4f   %-6s   %.1e\n",
            De, open_dx[De], closed_dx[De], ratio, o > c ? "OPEN" : "CLOSED", dpy)
    if prevr !== nothing && (prevr - 1) * (ratio - 1) < 0        # ratio crosses unity
        global Dec = prevDe + (1 - prevr) * (De - prevDe) / (ratio - prevr)
    end
    global prevr = ratio; global prevDe = De
end
@printf("\n  ⇒ crossover  De_c ≈ %.3f   (independent NumPy search gave 0.81)\n", Dec)
@printf("  agreement with NumPy: max relative difference over all points = %.1e\n", maxpy)
@printf("  scallop residual across all runs: max |∮U_stokes| = %.1e\n",
        maximum(abs(r["stokes_res"]) for r in results))

JSON.print(open(joinpath(@__DIR__, "julia_crossover.json"), "w"),
           Dict("params" => Dict("N" => N, "L" => L, "brink" => BRINK, "amp" => AMP,
                                 "nsteps" => NSTEPS, "ncyc" => NCYC),
                "De_c" => Dec, "results" => results), 2)
println("\n  wrote julia_crossover.json")
