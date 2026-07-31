# Fast validation of the Julia port: at matched settings (N=192, amp=0.35, brink=0.5, nsteps=600)
# the Julia net displacement must equal the NumPy value in crossover_results.json, and the
# analytic Stokes/polymer split must make the Stokes displacement vanish to round-off.
#   run:  julia --startup-file=no --project=. -t auto smoke.jl
include("ViscoelasticSwimmer.jl")
using .ViscoelasticSwimmer
using Printf, JSON, Base.Threads

py = JSON.parsefile(joinpath(@__DIR__, "..", "viscoelastic", "crossover_results.json"))
pyget(lam, b1) = only(filter(x -> x["ok"] && isapprox(x["lam"], lam) &&
                                  isapprox(x["b1"], b1), py))["dx"]

cases = [(0.5, -0.5, "open"), (2.0, 0.5, "closed")]
out = Vector{Any}(undef, length(cases))
@threads for i in eachindex(cases)
    lam, b1, _ = cases[i]
    s = Swimmer(N=192, L=4π, brink=0.5, lam=lam, amp=0.35, stroke=warp_stroke(b1=b1, amp=0.35))
    r = run_cycles!(s, ncycles=6, nsteps=600)
    out[i] = (r[end][1], r[end][2])
end

println("── Julia vs NumPy (N=192, amp=0.35, brink=0.5, nsteps=600) ──")
@printf("%-16s %16s %16s %11s\n", "case", "Julia dx", "NumPy dx", "rel.diff")
for (i, (lam, b1, name)) in enumerate(cases)
    jl, _ = out[i]; p = pyget(lam, b1)
    @printf("De=%.1f %-9s % .7e  % .7e  %10.2e\n", lam, name, jl, p, abs(jl - p) / abs(p))
end
@printf("\nscallop residual  max |∮U_stokes| = %.1e   (want ~1e-15)\n",
        maximum(abs(o[2]) for o in out))
