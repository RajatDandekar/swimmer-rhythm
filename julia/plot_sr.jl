# Draw the symbolic-regression result: the discovered closed form against the solver data,
# crossing unity at the critical Deborah number.  julia_sr.json -> julia_sr.png
using JSON, Plots, Printf
gr()

d = JSON.parsefile(joinpath(@__DIR__, "julia_sr.json"))
Ded  = Float64.(d["De_data"]);  rd = Float64.(d["ratio_data"])
grid = Float64.(d["De_grid"]);  rp = Float64.(d["ratio_pred"])
Dec  = d["De_c_formula"];        eq = d["equation"]

jpurple = RGB(0.54, 0.31, 0.69); jgreen = RGB(0.22, 0.59, 0.16); jred = RGB(0.76, 0.21, 0.17)
ink = RGB(0.09, 0.075, 0.05)

plt = plot(grid, rp, xscale=:log10, lw=3, color=jgreen, label="SymbolicRegression.jl formula",
           xlabel="Deborah number  De", ylabel="speed ratio   |Δx|closed / |Δx|open",
           legend=:topleft, grid=false, framestyle=:box, size=(860, 480), dpi=200,
           left_margin=6Plots.mm, bottom_margin=5Plots.mm)
scatter!(plt, Ded, rd, ms=6, color=ink, markerstrokewidth=0, label="spectral solver")
hline!(plt, [1.0], color=RGB(0.6, 0.6, 0.6), ls=:dash, lw=1, label="")
vline!(plt, [Dec], color=jred, ls=:dot, lw=1.8, label="")
annotate!(plt, Dec*1.05, 0.965, text("De_c ≈ $(round(Dec, digits=2))", 10, jred, :left))
annotate!(plt, Ded[2], maximum(rd)-0.03, text("open wins  ↓", 9, jpurple, :left))
annotate!(plt, Ded[end-1], 1.03, text("↑  closed wins", 9, jred, :right))
title!(plt, "A closed-form law for the reversal, found by symbolic regression")
savefig(plt, joinpath(@__DIR__, "julia_sr.png"))
println("wrote julia_sr.png   formula: r(De) = $eq   (De_c ≈ $(round(Dec, digits=3)))")
