# Figures for the discovered coefficients and the SciML check:
#   julia_amp.png       amplitude scaling exponent (~2)
#   julia_collapse.png  the dimensionless constant K = De_c·<θ̇²>
#   julia_sciml.png     hand-RK2 vs OrdinaryDiffEq.jl agreement
using JSON, Plots, Printf, Statistics
gr()
jpurple = RGB(0.54, 0.31, 0.69); jgreen = RGB(0.22, 0.59, 0.16)
jred = RGB(0.76, 0.21, 0.17); ink = RGB(0.09, 0.075, 0.05)
here(f) = joinpath(@__DIR__, f)

# --- amplitude scaling: |Δx| ∝ A^p ---
a = JSON.parsefile(here("julia_amp.json"))
amps = Float64.(a["amps"]); dxs = Float64.(a["dx"]); p = a["exponent"]; c = a["logintercept"]
xf = 10 .^ range(log10(minimum(amps) * 0.9), log10(maximum(amps) * 1.06), length=100)
p1 = scatter(amps, dxs, xscale=:log10, yscale=:log10, ms=7, color=ink, label="spectral solver",
             xlabel="stroke amplitude  A", ylabel="net displacement per cycle  |Δx|",
             legend=:topleft, grid=false, framestyle=:box, size=(760, 470), dpi=200,
             left_margin=6Plots.mm, bottom_margin=5Plots.mm)
plot!(p1, xf, exp(c) .* xf .^ p, color=jgreen, lw=2.6, label=@sprintf("fit:  |Δx| ∝ A^{%.3f}", p))
title!(p1, @sprintf("Amplitude scaling — the discovered exponent is %.3f", p))
savefig(p1, here("julia_amp.png")); println("wrote julia_amp.png (p=$(round(p,digits=4)))")

# --- collapse: De_c·<θ̇²> = K ---
co = JSON.parsefile(here("julia_collapse.json"))
rows = co["rows"]; b1s = Float64.([r["b1"] for r in rows])
Dec = Float64.([r["De_c"] for r in rows]); K = Float64.([r["K"] for r in rows])
Kbar = co["K_mean"]; th2 = [1 + b^2 / 2 for b in b1s]
p2a = scatter(b1s, Dec, ms=8, color=jpurple, label="measured De_c",
              xlabel="rhythm strength  b₁", ylabel="critical Deborah number  De_c",
              legend=:topright, grid=false, framestyle=:box, title="(a)  De_c depends on the rhythm")
bg = range(minimum(b1s), maximum(b1s), length=60)
plot!(p2a, bg, Kbar ./ (1 .+ bg .^ 2 ./ 2), color=jgreen, lw=2.2, ls=:dash,
      label="K / (1 + b₁²/2)")
p2b = scatter(b1s, K, ms=8, color=jred, label="", xlabel="rhythm strength  b₁",
              ylabel="De_c · ⟨θ̇²⟩", grid=false, framestyle=:box,
              title="(b)  the product is constant")
hline!(p2b, [Kbar], color=ink, ls=:dash, lw=1.5, label="")
annotate!(p2b, b1s[1] + 0.02, Kbar + 0.012, text("K ≈ $(round(Kbar, digits=3))", 11, ink, :left))
ylims!(p2b, Kbar - 0.06, Kbar + 0.06)
p2 = plot(p2a, p2b, layout=(1, 2), size=(970, 410), dpi=200,
          left_margin=6Plots.mm, bottom_margin=6Plots.mm,
          plot_title="A dimensionless law for the reversal:  De_c·⟨θ̇²⟩ = K", plot_titlefontsize=12)
savefig(p2, here("julia_collapse.png")); println("wrote julia_collapse.png (K=$(round(Kbar,digits=4)))")

# --- SciML agreement (optional) ---
if isfile(here("julia_sciml.json"))
    sc = JSON.parsefile(here("julia_sciml.json"))
    cs = sc["cases"]
    labs = ["De0.5_open", "De0.5_closed", "De2.0_open", "De2.0_closed"]
    rk = [abs(cs[l]["rk2"]) for l in labs]; sm = [abs(cs[l]["sciml"]) for l in labs]
    reld = maximum(abs.(sm .- rk) ./ rk)
    lo, hi = minimum([rk; sm]) * 0.97, maximum([rk; sm]) * 1.03
    p3 = plot([lo, hi], [lo, hi], color=ink, ls=:dash, lw=1.5, label="y = x",
              xlabel="hand-written RK2    |Δx|", ylabel="OrdinaryDiffEq.jl / Tsit5    |Δx|",
              grid=false, framestyle=:box, size=(720, 470), dpi=200, legend=:topleft,
              left_margin=6Plots.mm, bottom_margin=5Plots.mm)
    scatter!(p3, rk, sm, ms=9, color=jpurple, markerstrokewidth=0,
             label="2 fluids × 2 rhythms")
    title!(p3, @sprintf("Two integrators, one answer  (agree to %.0e)", reld))
    savefig(p3, here("julia_sciml.png")); println("wrote julia_sciml.png (reld=$reld)")
end
