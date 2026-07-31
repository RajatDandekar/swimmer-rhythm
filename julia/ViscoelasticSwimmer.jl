"""
    ViscoelasticSwimmer

A from-scratch spectral Stokes/Brinkman–Oldroyd-B solver for a two-bead reciprocal
microswimmer, written in pure Julia (only FFTW). This is a faithful line-by-line port of the
NumPy solver (`solver2.py`) behind the paper *"The optimal stroke rhythm of a reciprocal
microswimmer reverses with fluid memory"* (Dandekar, Dandekar & Panat, Vizuara Research 2026).

The physics: an asymmetric dumbbell (two regularised point forces of radii `eps1 ≠ eps2` at
separation `d(t)`) is immersed in an Oldroyd-B fluid under mild Brinkman confinement. The polymer
conformation `C` obeys the upper-convected Maxwell equation; the force-free swimmer velocity is
split analytically into a Stokes part (which integrates to zero over a closed stroke — the scallop
theorem, recovered here to round-off) and a polymer part (the net motion).

The point of the port: reproduce, in a second language and FFT library, the reversal of the
optimal stroke rhythm at the critical Deborah number `De_c ≈ 0.81`.

FFT conventions match NumPy exactly: Julia `fft`  ≡ `np.fft.fft2` (unnormalised forward),
Julia `ifft` ≡ `np.fft.ifft2` (normalised by 1/N²).
"""
module ViscoelasticSwimmer

using FFTW

export Swimmer, run_cycles!, reset!, warp_stroke, sinusoid_stroke

mutable struct Swimmer
    N::Int
    L::Float64
    eta_s::Float64
    eta_p::Float64
    lam::Float64
    eps_s::Float64
    eps1::Float64
    eps2::Float64
    d0::Float64
    amp::Float64
    brink::Union{Nothing,Float64}      # Brinkman screening length; nothing = pure Stokes
    stroke::Function                   # t -> (d, ddot)
    KX::Matrix{Float64}
    KY::Matrix{Float64}
    K2::Matrix{Float64}
    K2inv::Matrix{Float64}
    mask::Matrix{Float64}              # 2/3 dealiasing mask (as 0/1 floats)
    zero::Matrix{ComplexF64}
    Cxx::Matrix{Float64}
    Cxy::Matrix{Float64}
    Cyy::Matrix{Float64}
    xc::Float64
    acc_poly::Float64                  # ∮ U_poly dt  -> the net displacement
    acc_stokes::Float64                # ∮ U_stokes dt -> must be round-off
    Pf::Any                            # forward FFT plan
    Pi::Any                            # inverse FFT plan (normalised)
end

sinusoid_stroke(; d0=1.0, amp=0.30) = (t -> (d0 + amp*cos(t), -amp*sin(t)))

"""
    warp_stroke(; b1, d0, amp, ks, bs, phis)

The rhythm control on the θ-reparametrisation axis:
`θ(t) = t + Σ b_k sin(k t + φ_k)`, `d(t) = d0 + amp·cos θ`. Every choice of `{b_k, φ_k}` has the
*same* excursion, path and period; only the rhythm changes. `b1 > 0` lingers CLOSED, `b1 < 0`
lingers OPEN. Matches the NumPy `make_stroke` used to build `crossover_results.json`.
"""
function warp_stroke(; b1=0.0, d0=1.0, amp=0.35, ks=(1.0, 2.0, 3.0),
                     bs=nothing, phis=nothing)
    b = bs === nothing ? (b1, 0.0, 0.0) : bs
    ph = phis === nothing ? (0.0, 0.0, 0.0) : phis
    function stroke(t)
        θ  = t + sum(b[i]*sin(ks[i]*t + ph[i]) for i in 1:3)
        dθ = 1.0 + sum(b[i]*ks[i]*cos(ks[i]*t + ph[i]) for i in 1:3)
        return (d0 + amp*cos(θ), -amp*sin(θ)*dθ)
    end
    return stroke
end

function Swimmer(; N=128, L=2π, eta_s=1.0, eta_p=1.0, lam=1.0, eps_s=2e-3,
                 eps1=0.14, eps2=0.26, d0=1.0, amp=0.30, stroke=nothing, brink=nothing)
    m  = vcat(0:div(N, 2)-1, -div(N, 2):-1)          # np.fft.fftfreq ordering
    k1 = (2π / L) .* m
    KX = repeat(reshape(k1, N, 1), 1, N)             # meshgrid(indexing="ij")
    KY = repeat(reshape(k1, 1, N), N, 1)
    K2 = KX .^ 2 .+ KY .^ 2
    K2inv = [k > 0 ? 1.0 / k : 0.0 for k in K2]
    kmax = maximum(abs.(k1))
    mask = Float64.((abs.(KX) .<= (2 / 3) * kmax) .& (abs.(KY) .<= (2 / 3) * kmax))
    strokef = stroke === nothing ? sinusoid_stroke(; d0=d0, amp=amp) : stroke
    Pf = plan_fft(Matrix{ComplexF64}(undef, N, N))
    Pi = plan_ifft(Matrix{ComplexF64}(undef, N, N))
    Swimmer(N, L, eta_s, eta_p, lam, eps_s, eps1, eps2, d0, amp, brink, strokef,
            KX, KY, K2, K2inv, mask, zeros(ComplexF64, N, N),
            ones(N, N), zeros(N, N), ones(N, N), 0.0, 0.0, 0.0, Pf, Pi)
end

function reset!(s::Swimmer)
    fill!(s.Cxx, 1.0); fill!(s.Cxy, 0.0); fill!(s.Cyy, 1.0)
    s.xc = 0.0; s.acc_poly = 0.0; s.acc_stokes = 0.0
    return s
end

# ----------------------------------------------------------------- spectral operators
function stokes(s::Swimmer, fxh, fyh)
    dot = s.KX .* fxh .+ s.KY .* fyh
    px = fxh .- s.KX .* dot .* s.K2inv
    py = fyh .- s.KY .* dot .* s.K2inv
    if s.brink === nothing
        return px .* s.K2inv ./ s.eta_s, py .* s.K2inv ./ s.eta_s
    end
    inv = 1.0 ./ (s.K2 .+ 1.0 / s.brink^2)           # Brinkman: k²+1/ℓ²
    return px .* inv ./ s.eta_s, py .* inv ./ s.eta_s
end

spread_hat(s::Swimmer, Fx, xb, eps) =
    Fx .* exp.(-1im .* (s.KX .* xb .+ s.KY .* (s.L / 2))) .* exp.(-0.5 * eps^2 .* s.K2)

interp(s::Swimmer, uh, xb, eps) =
    real(sum(uh .* exp.(1im .* (s.KX .* xb .+ s.KY .* (s.L / 2))) .*
             exp.(-0.5 * eps^2 .* s.K2))) / s.N^2

function polymer_force_hat(s::Swimmer)
    c = s.eta_p / s.lam
    txxh = c .* (s.Pf * complex.(s.Cxx .- 1.0))
    txyh = c .* (s.Pf * complex.(s.Cxy))
    tyyh = c .* (s.Pf * complex.(s.Cyy .- 1.0))
    return 1im .* (s.KX .* txxh .+ s.KY .* txyh), 1im .* (s.KX .* txyh .+ s.KY .* tyyh)
end

# --------------------------------------------------------------------------- step
function velocity_field(s::Swimmer, t)
    d, dd = s.stroke(t)
    x1 = s.xc - d / 2; x2 = s.xc + d / 2

    pxh, pyh = polymer_force_hat(s)
    upxh, _ = stokes(s, pxh, pyh)
    up1 = interp(s, upxh, x1, s.eps1); up2 = interp(s, upxh, x2, s.eps2)

    u1h, _ = stokes(s, spread_hat(s, 1.0, x1, s.eps1), s.zero)
    u2h, _ = stokes(s, spread_hat(s, 1.0, x2, s.eps2), s.zero)
    M11 = interp(s, u1h, x1, s.eps1); M21 = interp(s, u1h, x2, s.eps2)
    M12 = interp(s, u2h, x1, s.eps1); M22 = interp(s, u2h, x2, s.eps2)
    SumM = M11 + M22 - M12 - M21; dM = M22 - M11

    # analytic split: the Stokes part integrates to zero over a closed stroke
    U_stokes = (dd / SumM) * dM / 2.0
    U_poly = (-(up2 - up1) / SumM) * dM / 2.0 + (up1 + up2) / 2.0

    F = (dd - (up2 - up1)) / SumM
    fxh = spread_hat(s, -F, x1, s.eps1) .+ spread_hat(s, F, x2, s.eps2) .+ pxh
    uxh, uyh = stokes(s, fxh, pyh)
    return uxh, uyh, U_stokes, U_poly
end

function dCdt(s::Swimmer, uxh, uyh)
    ux = real(s.Pi * uxh); uy = real(s.Pi * uyh)
    gx(h) = real(s.Pi * (1im .* s.KX .* h .* s.mask))
    gy(h) = real(s.Pi * (1im .* s.KY .* h .* s.mask))
    Lxx = gx(uxh); Lxy = gy(uxh); Lyx = gx(uyh); Lyy = gy(uyh)
    Cxxh = s.Pf * complex.(s.Cxx); Cxyh = s.Pf * complex.(s.Cxy); Cyyh = s.Pf * complex.(s.Cyy)
    adv(h) = -(ux .* gx(h) .+ uy .* gy(h))
    lap(h) = real(s.Pi * (-s.K2 .* h))
    rxx = adv(Cxxh) .+ 2 .* (Lxx .* s.Cxx .+ Lxy .* s.Cxy) .-
          (s.Cxx .- 1) ./ s.lam .+ s.eps_s .* lap(Cxxh)
    rxy = adv(Cxyh) .+ (Lxx .* s.Cxy .+ Lxy .* s.Cyy) .+ (s.Cxx .* Lyx .+ s.Cxy .* Lyy) .-
          s.Cxy ./ s.lam .+ s.eps_s .* lap(Cxyh)
    ryy = adv(Cyyh) .+ 2 .* (Lyx .* s.Cxy .+ Lyy .* s.Cyy) .-
          (s.Cyy .- 1) ./ s.lam .+ s.eps_s .* lap(Cyyh)
    return rxx, rxy, ryy
end

"""
    run_cycles!(s; ncycles, nsteps) -> Vector{(Δpoly, Δstokes)}

Advance the swimmer with an explicit RK2 (Heun) step, exactly as the NumPy `run`. Returns the
per-cycle net polymer displacement (the answer) and the Stokes residual (must be ~1e-16).
"""
function run_cycles!(s::Swimmer; ncycles=6, nsteps=400)
    dt = 2π / nsteps
    out = Tuple{Float64,Float64}[]
    for _ in 1:ncycles
        p0 = s.acc_poly; s0 = s.acc_stokes
        for n in 0:nsteps-1
            t = n * dt
            C0x = copy(s.Cxx); C0y = copy(s.Cxy); C0z = copy(s.Cyy); xc0 = s.xc
            ux1, uy1, Us1, Up1 = velocity_field(s, t)
            k1x, k1y, k1z = dCdt(s, ux1, uy1)
            s.Cxx = C0x .+ dt .* k1x; s.Cxy = C0y .+ dt .* k1y; s.Cyy = C0z .+ dt .* k1z
            s.xc = xc0 + dt * (Us1 + Up1)
            ux2, uy2, Us2, Up2 = velocity_field(s, t + dt)
            k2x, k2y, k2z = dCdt(s, ux2, uy2)
            s.Cxx = C0x .+ 0.5 * dt .* (k1x .+ k2x)
            s.Cxy = C0y .+ 0.5 * dt .* (k1y .+ k2y)
            s.Cyy = C0z .+ 0.5 * dt .* (k1z .+ k2z)
            s.xc = xc0 + 0.5 * dt * (Us1 + Us2 + Up1 + Up2)
            s.acc_poly += 0.5 * dt * (Up1 + Up2)
            s.acc_stokes += 0.5 * dt * (Us1 + Us2)
        end
        push!(out, (s.acc_poly - p0, s.acc_stokes - s0))
    end
    return out
end

end # module
