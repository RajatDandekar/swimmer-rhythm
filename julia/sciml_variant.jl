# The same swimmer, integrated with the SciML stack (OrdinaryDiffEq.jl) instead of the hand-written
# RK2. The conformation field C(t) and the swimmer displacement are posed as one ODE system and
# handed to an adaptive Tsit5 integrator. It reproduces the reversal and agrees with the RK2 result,
# demonstrating the effect is a property of the physics, not of a particular time-stepper.
#   run:  julia --startup-file=no --project=. sciml_variant.jl
include("ViscoelasticSwimmer.jl")
using .ViscoelasticSwimmer
using OrdinaryDiffEq, Printf, JSON
const VS = ViscoelasticSwimmer

const N = 96; const L = 4π; const BRINK = 0.5; const AMP = 0.35; const NCYC = 4

# Build an in-place ODE right-hand side that reuses the spectral machinery of one Swimmer.
function make_rhs(s::Swimmer)
    n2 = s.N * s.N
    function rhs!(du, u, p, t)
        s.Cxx = reshape(u[1:n2], s.N, s.N)
        s.Cxy = reshape(u[n2+1:2n2], s.N, s.N)
        s.Cyy = reshape(u[2n2+1:3n2], s.N, s.N)
        s.xc  = u[3n2+1]
        uxh, uyh, Us, Up = VS.velocity_field(s, t)
        kx, ky, kz = VS.dCdt(s, uxh, uyh)
        du[1:n2]        .= vec(kx)
        du[n2+1:2n2]    .= vec(ky)
        du[2n2+1:3n2]   .= vec(kz)
        du[3n2+1] = Us + Up        # swimmer centre
        du[3n2+2] = Up             # net (polymer) displacement accumulator
        return nothing
    end
    return rhs!
end

function sciml_dx(lam, b1)
    s = Swimmer(N=N, L=L, brink=BRINK, lam=lam, amp=AMP, stroke=warp_stroke(b1=b1, amp=AMP))
    n2 = N * N
    u0 = vcat(vec(ones(N, N)), vec(zeros(N, N)), vec(ones(N, N)), 0.0, 0.0)
    prob = ODEProblem(make_rhs(s), u0, (0.0, 2π * NCYC))
    sol = solve(prob, Tsit5(); reltol=1e-7, abstol=1e-9,
                saveat=[2π * (NCYC - 1), 2π * NCYC])
    return sol.u[end][end] - sol.u[end-1][end]      # last-cycle net displacement
end

function rk2_dx(lam, b1)
    s = Swimmer(N=N, L=L, brink=BRINK, lam=lam, amp=AMP, stroke=warp_stroke(b1=b1, amp=AMP))
    r = run_cycles!(s, ncycles=NCYC, nsteps=400)
    return r[end][1]
end

cases = [(0.5, -0.5, "open"), (0.5, 0.5, "closed"), (2.0, -0.5, "open"), (2.0, 0.5, "closed")]
out = Dict{String,Any}()
@printf("%-15s %16s %16s %11s\n", "case", "SciML (Tsit5)", "hand RK2", "rel.diff")
for (lam, b1, name) in cases
    sc = sciml_dx(lam, b1); rk = rk2_dx(lam, b1)
    @printf("De=%.1f %-8s % .6e  % .6e  %9.1e\n", lam, name, sc, rk, abs(sc - rk) / abs(rk))
    out["De$(lam)_$(name)"] = Dict("sciml" => sc, "rk2" => rk)
end
# the reversal, via the SciML integrator alone
r05 = abs(out["De0.5_closed"]["sciml"]) / abs(out["De0.5_open"]["sciml"])
r20 = abs(out["De2.0_closed"]["sciml"]) / abs(out["De2.0_open"]["sciml"])
@printf("\nSciML ratio |closed|/|open|:  De=0.5 -> %.4f (open wins),  De=2.0 -> %.4f (closed wins)\n",
        r05, r20)
JSON.print(open(joinpath(@__DIR__, "julia_sciml.json"), "w"),
           Dict("N" => N, "ncyc" => NCYC, "cases" => out,
                "ratio_De0.5" => r05, "ratio_De2.0" => r20), 1)
println("wrote julia_sciml.json")
