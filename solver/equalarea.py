"""Sharper test of the degenerate-MDP claim.

The area law says displacement ~ enclosed area.  The STRONGER claim -- the one that actually
kills the sequential-decision structure -- is that displacement depends ONLY on the area and
not at all on the loop's SHAPE.  Test it with wildly different loops of IDENTICAL area.
"""
import numpy as np
from gait import net_displacement, signed_area

def circle(b):     return lambda s: (b*np.cos(2*np.pi*s), -b*np.sin(2*np.pi*s))
def ellipse(b,r):  # semi-axes (r*b, b/r) -> same area pi b^2 for any r
    return lambda s: (r*b*np.cos(2*np.pi*s), -(b/r)*np.sin(2*np.pi*s))
def square(b):     # axis-aligned square, area pi b^2  -> side L = b*sqrt(pi)
    L = b*np.sqrt(np.pi)
    def f(s):
        t = (4*s) % 4; h = L/2
        if   t < 1: return ( h, -h + L*t)
        elif t < 2: return ( h - L*(t-1),  h)
        elif t < 3: return (-h,  h - L*(t-2))
        else:       return (-h + L*(t-3), -h)
    return lambda s: f(s)
def triangle(b):   # equilateral-ish triangle with area pi b^2
    A = np.pi*b*b; base = 2.0*b; hgt = 2*A/base
    P = [(-base/2,-hgt/3), (base/2,-hgt/3), (0.0, 2*hgt/3)]
    def f(s):
        t = (3*s) % 3; i = int(t); u = t-i
        p,q = P[i], P[(i+1)%3]
        return (p[0]+u*(q[0]-p[0]), p[1]+u*(q[1]-p[1]))
    return lambda s: f(s)

print("Loops of IDENTICAL enclosed area but very different shape.")
print("If displacement depends only on area, every row at a given b must agree.\n")
for b in (0.10, 0.04, 0.02):
    print(f"  b = {b}   (target area = pi*b^2 = {np.pi*b*b:.6e})")
    print(f"    {'loop':<26} {'area':>13} {'net displ':>15} {'displ/area':>12}")
    for name, g in [("circle", circle(b)),
                    ("ellipse 2:1 (r=1.41)", ellipse(b,np.sqrt(2))),
                    ("ellipse 4:1 (r=2)", ellipse(b,2.0)),
                    ("square (corners!)", square(b)),
                    ("triangle (corners!)", triangle(b))]:
        d = net_displacement(g, nt=480); a = signed_area(g)
        print(f"    {name:<26} {a:13.6e} {d:15.6e} {d/a:12.6f}")
    print()
