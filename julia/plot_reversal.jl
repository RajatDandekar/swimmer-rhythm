# Draw the reversal from the Julia sweep (julia_crossover.json) -> julia_reversal.png
using JSON, Plots
gr()

d   = JSON.parsefile(joinpath(@__DIR__, "julia_crossover.json"))
res = d["results"]
Dec = d["De_c"]
DES = sort(unique(Float64(r["lam"]) for r in res))
pick(De, b1) = only(filter(x -> isapprox(x["lam"], De) && x["b1"] == b1, res))["dx"]
op  = [abs(pick(De, -0.5)) for De in DES]
cl  = [abs(pick(De, +0.5)) for De in DES]
rat = cl ./ op

teal = RGB(0.10, 0.44, 0.69); orange = RGB(0.75, 0.37, 0.09)
ink  = RGB(0.09, 0.075, 0.05); mag = RGB(0.70, 0.0, 0.42)

p1 = plot(DES, op, xscale=:log10, lw=2.6, color=teal, marker=:circle, ms=4,
          label="linger open  (b₁ = −0.5)", legend=:topleft,
          xlabel="Deborah number  De", ylabel="net displacement per cycle  |Δx|",
          title="(a)  the two rhythms", titlelocation=:left, grid=false, framestyle=:box)
plot!(p1, DES, cl, lw=2.6, color=orange, marker=:diamond, ms=4,
      label="linger closed  (b₁ = +0.5)")

p2 = plot(DES, rat, xscale=:log10, lw=2.8, color=ink, marker=:circle, ms=4,
          label="", xlabel="Deborah number  De",
          ylabel="speed ratio   |Δx|closed / |Δx|open",
          title="(b)  the optimum reverses", titlelocation=:left, grid=false, framestyle=:box)
hline!(p2, [1.0], color=RGB(0.6,0.6,0.6), ls=:dash, lw=1, label="")
vline!(p2, [Dec], color=mag, ls=:dot, lw=1.6, label="")
annotate!(p2, Dec*1.03, minimum(rat)+0.02, text("De_c ≈ $(round(Dec, digits=2))", 9, mag, :left))
annotate!(p2, DES[2], 1.012, text("open wins", 8, teal, :left))
annotate!(p2, DES[end-1], maximum(rat)-0.02, text("closed wins", 8, orange, :right))

plt = plot(p1, p2, layout=(1, 2), size=(960, 400), dpi=200,
           left_margin=6Plots.mm, bottom_margin=6Plots.mm,
           plot_title="Reproduced in Julia — the optimal rhythm reverses at De_c",
           plot_titlefontsize=12)
savefig(plt, joinpath(@__DIR__, "julia_reversal.png"))
println("wrote julia_reversal.png   (De_c ≈ $(round(Dec, digits=3)))")
