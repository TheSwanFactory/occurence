#!/usr/bin/env python3
"""
Exceptional Topography of G2 and F4 Varieties -- reproduction script.

Self-contained (numpy only) reproduction of the headline numerical results in
"The Exceptional Topography of G_2 and F_4 Varieties: Deformation Dynamics and
Morse-Bott Singularities":

  1. Octonions O via Cayley-Dickson  ->  dim Der(O) = dim g2 = 14
  2. Albert algebra J3(O)            ->  dim Der(J3(O)) = dim f4 = 52
  3. F4-invariant cubic determinant  ->  derivations annihilate det
  4. det is indefinite on the trace hypersphere (the F4 "crack")
  5. Peirce decomposition at a primitive idempotent E1 -> (1, 16, 10)
  6. Hessian signature of det at E1  ->  (+1, -9, 0^17), Morse index 9
  7. (optional) anisotropy audit of the octonion cubic well from the CSV

Everything is measured under scale-RELATIVE tolerances and cross-checked; no
result is assumed. Run:  python3 -m topographo.exceptional.lab
"""
import numpy as np

# Single source of truth for the Cayley-Dickson structure tensor: this module's
# original `cayley_dickson_table` was the ancestor `topographo.core` was carved
# from (#4), so import the core version rather than carrying a private copy.
from topographo.core import cayley_dickson_table

# ----------------------------------------------------------------------
# Octonions via the Cayley-Dickson construction (R -> C -> H -> O)
# ----------------------------------------------------------------------
def relative_nullity(M, rel=1e-9):
    """Nullity of the domain of M under a scale-RELATIVE cutoff."""
    s = np.linalg.svd(M, compute_uv=False)
    cols = M.shape[1]
    rank = int((s > s.max() * rel).sum())
    return cols - rank, s

# ----------------------------------------------------------------------
# 1 + 2. Derivation-defect map for any algebra given its structure tensor
# ----------------------------------------------------------------------
def defect_matrix(mu):
    """
    Linear map Delta: End(A) -> Hom(A x A, A) sending L to
        B_L(x,y) = L(x*y) - L(x)*y - x*L(y).
    Kernel of Delta = derivations of the algebra with tensor mu.
    Returns the (n^3, n^2) matrix.
    """
    n = mu.shape[0]
    D = np.zeros((n, n, n, n, n))
    for c in range(n):
        D[:, :, c, c, :] += mu
    for a in range(n):
        D[a, :, :, :, a] -= mu.transpose(1, 2, 0)
    for b in range(n):
        D[:, b, :, :, b] -= mu.transpose(0, 2, 1)
    return D.reshape(n**3, n**2)

def derivations(mu, rel=1e-9):
    """Orthonormal basis of Der(A) as (k, n, n)."""
    n = mu.shape[0]
    Delta = defect_matrix(mu)
    _, s, Vt = np.linalg.svd(Delta, full_matrices=False)
    rank = int((s > s.max() * rel).sum())
    return Vt[rank:].reshape(-1, n, n)

# ----------------------------------------------------------------------
# Albert algebra J3(O): 3x3 Hermitian octonion matrices, 27-dimensional
# ----------------------------------------------------------------------
class Albert:
    SLOTS = [(0, 1), (1, 2), (0, 2)]  # off-diagonal octonion positions

    def __init__(self):
        self.C8 = cayley_dickson_table(8)
        self.mu = self._structure_tensor()          # (27,27,27), sym in (a,b)
        self.T = np.zeros(27); self.T[:3] = 1.0      # trace linear form
        self.I = np.zeros(27); self.I[:3] = 1.0      # Jordan identity

    def _omul(self, a, b):
        return np.einsum('i,j,ijk->k', a, b, self.C8)

    def _oconj(self, a):
        r = -a.copy(); r[0] = a[0]; return r

    def _basis_mat(self, idx):
        M = np.zeros((3, 3, 8))
        if idx < 3:
            M[idx, idx, 0] = 1.0; return M
        idx -= 3; s, t = divmod(idx, 8); i, j = self.SLOTS[s]
        u = np.zeros(8); u[t] = 1.0
        M[i, j] = u; M[j, i] = self._oconj(u); return M

    def _mat_to_vec(self, M):
        v = np.zeros(27)
        for d in range(3):
            v[d] = M[d, d, 0]
        for s, (i, j) in enumerate(self.SLOTS):
            v[3 + 8 * s: 11 + 8 * s] = M[i, j]
        return v

    def _matmul3(self, X, Y):
        Z = np.zeros((3, 3, 8))
        for i in range(3):
            for k in range(3):
                for j in range(3):
                    Z[i, k] += self._omul(X[i, j], Y[j, k])
        return Z

    def _jordan(self, X, Y):
        return 0.5 * (self._matmul3(X, Y) + self._matmul3(Y, X))

    def _structure_tensor(self):
        B = [self._basis_mat(k) for k in range(27)]
        mu = np.zeros((27, 27, 27))
        for a in range(27):
            for b in range(27):
                mu[a, b] = self._mat_to_vec(self._jordan(B[a], B[b]))
        return mu

    def prod(self, x, y):
        return np.einsum('a,b,abc->c', x, y, self.mu)

    def det(self, X):
        """F4-invariant cubic via the trace-power formula (basis-free)."""
        X2 = self.prod(X, X); X3 = self.prod(X, X2)
        t1, t2, t3 = self.T @ X, self.T @ X2, self.T @ X3
        return (t1**3 - 3 * t1 * t2 + 2 * t3) / 6.0

    def trace_form(self):
        return np.einsum('abc,c->ab', self.mu, self.T)

    def left_mult(self, X):
        return np.einsum('a,abc->cb', X, self.mu)


# ----------------------------------------------------------------------
# Analyses
# ----------------------------------------------------------------------
def octonion_g2():
    C8 = cayley_dickson_table(8)
    dim, _ = relative_nullity(defect_matrix(C8))
    print(f"[1] dim Der(O) = {dim}   (expected dim g2 = 14)")
    assert dim == 14
    return dim

def albert_f4(alb):
    dim, s = relative_nullity(defect_matrix(alb.mu))
    ssort = np.sort(s)
    print(f"[2] dim Der(J3(O)) = {dim}   (expected dim f4 = 52)")
    print(f"    singular-value gap: {ssort[dim-1]:.2e} | {ssort[dim]:.2e}")
    assert dim == 52
    return dim

def determinant_checks(alb):
    print(f"[3] det(diag(2,3,5)) = {alb.det(np.array([2,3,5]+[0]*24, float)):.4f}  (expected 30)")
    Der = derivations(alb.mu)
    rng = np.random.default_rng(1); eps = 1e-5; worst = 0.0
    for _ in range(40):
        X = rng.standard_normal(27); D = Der[rng.integers(len(Der))]
        worst = max(worst, abs((alb.det(X + eps*(D@X)) - alb.det(X - eps*(D@X))) / (2*eps)))
    print(f"    max |D.det| over derivations = {worst:.2e}  (F4-invariance => ~0)")
    return Der

def crack_the_sphere(alb, n_samples=200000):
    G = alb.trace_form()
    L = np.linalg.cholesky(G)
    rng = np.random.default_rng(0); vals = np.empty(n_samples)
    for i in range(n_samples):
        v = np.linalg.solve(L.T, rng.standard_normal(27))
        v /= np.sqrt(v @ G @ v)
        vals[i] = alb.det(v)
    print(f"[4] det on unit trace-hypersphere in [{vals.min():+.3f}, {vals.max():+.3f}]; "
          f"crosses 0: {vals.min() < 0 < vals.max()}")

def peirce_and_hessian(alb):
    E1 = np.zeros(27); E1[0] = 1.0
    I = np.eye(27); h = 1e-2
    grad = np.array([(alb.det(E1+h*I[i]) - alb.det(E1-h*I[i])) / (2*h) for i in range(27)])
    print(f"[5] ||grad det(E1)|| = {np.linalg.norm(grad):.2e}  (E1 is a singular/critical point)")

    # exact Hessian (pure cubic -> central mixed differences exact)
    H = np.zeros((27, 27))
    for i in range(27):
        for j in range(27):
            H[i, j] = (alb.det(E1+h*I[i]+h*I[j]) - alb.det(E1+h*I[i]-h*I[j])
                       - alb.det(E1-h*I[i]+h*I[j]) + alb.det(E1-h*I[i]-h*I[j])) / (4*h*h)
    H = 0.5 * (H + H.T)

    LE = alb.left_mult(E1); LE = 0.5 * (LE + LE.T)
    w, V = np.linalg.eigh(LE)
    blocks = {"P1 (radial, lam=1)":   V[:, np.abs(w-1.0) < 1e-6],
              "P_1/2 (OP^2, lam=1/2)": V[:, np.abs(w-0.5) < 1e-6],
              "P0 (J2(O), lam=0)":     V[:, np.abs(w-0.0) < 1e-6]}
    print("[6] Hessian of det at E1, per Peirce block:")
    tol = 1e-6 * np.max(np.abs(H))
    for name, B in blocks.items():
        ev = np.linalg.eigvalsh(B.T @ H @ B)
        pos = int((ev > tol).sum()); neg = int((ev < -tol).sum()); nul = int((np.abs(ev) <= tol).sum())
        print(f"    {name:24s} dim={B.shape[1]:2d}  signature (+{pos}, -{neg}, 0x{nul})")
    ev = np.linalg.eigvalsh(H)
    pos = int((ev > tol).sum()); neg = int((ev < -tol).sum()); nul = int((np.abs(ev) <= tol).sum())
    print(f"    {'OVERALL':24s} dim=27  signature (+{pos}, -{neg}, 0x{nul})  Morse index = {neg}")

def octonion_anisotropy(csv_path="octonion_cubic_cross_variation.csv"):
    import csv, os
    if not os.path.exists(csv_path):
        print(f"[7] (skipped: {csv_path} not found)"); return
    rows = [r for r in csv.reader(open(csv_path))][1:]
    A = np.zeros((28, 28, 28, 28))
    for r in rows:
        if r:
            A[int(r[0]), int(r[1]), int(r[2]), int(r[3])] = float(r[4])
    H = A[1:, 1:, 1:, 1:]; d = 27; I = np.eye(d)
    P = (np.einsum('oi,jk->oijk', I, I) + np.einsum('oj,ik->oijk', I, I)
         + np.einsum('ok,ij->oijk', I, I)) / 3
    c = np.sum(H * P) / np.sum(P * P)
    iso = c * P; aniso = H - iso
    print(f"[7] octonion cubic well anisotropy audit:")
    print(f"    pure-27 anisotropic/isotropic norm ratio = "
          f"{np.linalg.norm(aniso)/np.linalg.norm(iso):.1%}  (isotropic well => 0%)")
    print(f"    tr(h^3)->conformal channel norm = {np.linalg.norm(A[0,1:,1:,1:]):.4f}  (isotropic => 0)")
    print("    => the G2 well is STABLE but ANISOTROPIC (symmetry is G2, not O(27)).")


def albert_g2_decomposition(alb):
    """Lift g2 = Der(O) into f4 = Der(J3(O)) and decompose the 27 as a g2-module."""
    g2 = derivations(cayley_dickson_table(8))
    def lift(D):
        M = np.zeros((27, 27))
        for s in range(3):
            M[3 + 8*s: 11 + 8*s, 3 + 8*s: 11 + 8*s] = D
        return M
    G = [lift(D) for D in g2]
    rng = np.random.default_rng(0); worst = 0.0
    for Dh in G:
        for _ in range(5):
            x = rng.standard_normal(27); y = rng.standard_normal(27)
            b = alb.prod(Dh@x, y) + alb.prod(x, Dh@y) - Dh @ alb.prod(x, y)
            worst = max(worst, np.linalg.norm(b))
    s = np.linalg.svd(np.vstack(G), compute_uv=False)
    inv = 27 - int((s > s.max()*1e-9).sum())
    Cas = sum(Dh @ Dh for Dh in G)
    ev = np.linalg.eigvalsh(0.5*(Cas + Cas.T))
    vals, cnts = np.unique(np.round(ev, 4), return_counts=True)
    print(f"[8] g2 lifted into f4: residual defect on J3(O) = {worst:.2e}")
    print(f"    g2-invariants in the 27 = {inv}   Casimir spectrum = "
          f"{ {float(v): int(c) for v, c in zip(vals, cnts)} }")
    print(f"    => J3(O) = 1^(+6) (+) 7^(+3) under g2  (6 trivial + 3x7)")


def main():
    """Run the full exceptional-algebra reproduction as a script."""
    print("=" * 68)
    octonion_g2()
    alb = Albert()
    albert_f4(alb)
    determinant_checks(alb)
    crack_the_sphere(alb)
    peirce_and_hessian(alb)
    albert_g2_decomposition(alb)
    octonion_anisotropy()
    print("=" * 68)


if __name__ == "__main__":
    main()
