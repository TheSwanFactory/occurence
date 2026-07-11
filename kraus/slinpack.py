"""
SlinPack: Sedenion Linear Algebra Package

Provides the algebraic infrastructure for Occurrence Theory:
- Cayley-Dickson multiplication tables
- Zero-divisor crack (Σ) and its invariant measure
- Observables and transition functionals
- Verification gates

All operations use numpy for performance. No external dependencies beyond numpy.
"""

import numpy as np
from typing import Tuple, List, Optional


class SlinPack:
    """
    Sedenion linear algebra for OT dynamics.
    
    Encapsulates the static algebraic structure:
    - Multiplication table C (dim × dim × dim)
    - Crack Σ: the 84 unit zero divisors (for dim=16)
    - Invariant measure μ on Σ
    - Observables: transition functionals, alternators, complex structure
    
    Usage:
        alg = SlinPack(dim=16)
        z = alg.sample_from_crack()
        x = alg.normalize(np.random.standard_normal(16))
        product = alg.mul(z, x)
        norm = alg.norm(product)
    """
    
    def __init__(self, dim: int = 16):
        """
        Initialize SlinPack for a Cayley-Dickson algebra of given dimension.
        
        Args:
            dim: dimension (2, 4, 8, 16, 32, ...)
        
        Raises:
            ValueError if dim is not a power of 2 or > 32.
        """
        if dim not in [2, 4, 8, 16, 32]:
            raise ValueError(f"dim must be in [2, 4, 8, 16, 32], got {dim}")
        
        self.dim = dim
        self.C = self._build_cayley_dickson_table(dim)
        
        # Basis vectors (canonical basis)
        self.e = np.eye(dim, dtype=np.float64)
        
        # Spine and pencil structure (for dim >= 8)
        if dim >= 8:
            self.spine_indices = [0, dim // 2]  # e_0 and e_{dim/2}
            self.pencil_indices = list(range(1, dim // 2)) + list(range(dim // 2 + 1, dim))
        else:
            self.spine_indices = [0]
            self.pencil_indices = list(range(1, dim))
        
        # Crack Σ and measure μ (computed once, cached)
        self._sigma = None
        self._mu = None
        self._sigma_computed = False
    
    # =========================================================================
    # MULTIPLICATION AND BASIC OPERATIONS
    # =========================================================================
    
    def mul(self, a: np.ndarray, b: np.ndarray) -> np.ndarray:
        """
        Multiply two elements of the algebra: a * b.
        
        Uses Einstein summation for efficiency.
        
        Args:
            a, b: vectors of shape (dim,)
        
        Returns:
            product: vector of shape (dim,), result of a * b
        """
        return np.einsum('i,j,ijk->k', a, b, self.C, dtype=np.float64)
    
    def norm(self, x: np.ndarray) -> float:
        """Euclidean norm of x."""
        return np.linalg.norm(x)
    
    def normalize(self, x: np.ndarray) -> np.ndarray:
        """Return x normalized to unit norm."""
        n = self.norm(x)
        if n < 1e-15:
            raise ValueError("Cannot normalize zero vector")
        return x / n
    
    def inner_product(self, x: np.ndarray, y: np.ndarray) -> float:
        """Euclidean inner product <x, y>."""
        return np.dot(x, y)
    
    def composition_law(self, x: np.ndarray, y: np.ndarray) -> float:
        """
        Verify composition law: ||x * y|| = ||x|| * ||y||.
        
        Returns the defect ||x * y|| - ||x|| * ||y||.
        """
        return abs(self.norm(self.mul(x, y)) - self.norm(x) * self.norm(y))
    
    # =========================================================================
    # CRACK AND MEASURE
    # =========================================================================
    
    def crack(self) -> List[np.ndarray]:
        """
        Compute Σ, the zero-divisor variety: unit vectors z where ker L_z ≠ 0.
        
        For dim=16 (sedenions): Σ has exactly 84 elements, one G₂ orbit.
        Cached after first computation.
        
        Returns:
            List of 84 numpy arrays, each shape (16,), unit norm
        """
        if self._sigma_computed:
            return self._sigma
        
        if self.dim == 16:
            self._sigma = self._compute_crack_sedenion()
        elif self.dim == 8:
            self._sigma = self._compute_crack_octonion()
        else:
            raise NotImplementedError(f"Crack computation not implemented for dim={self.dim}")
        
        self._sigma_computed = True
        return self._sigma
    
    def invariant_measure(self) -> np.ndarray:
        """
        Compute μ, the unique Aut-invariant probability measure on Σ.
        
        For dim=16: uniform measure on the 84-element crack, weights = 1/84 each.
        
        Returns:
            Array of shape (84,) with probabilities summing to 1
        """
        if self._mu is not None:
            return self._mu
        
        n_crack = len(self.crack())
        self._mu = np.ones(n_crack) / n_crack
        return self._mu
    
    def sample_from_crack(self) -> np.ndarray:
        """
        Sample a zero divisor z uniformly from Σ according to μ.
        
        Returns:
            A unit vector z from the crack
        """
        sigma = self.crack()
        mu = self.invariant_measure()
        idx = np.random.choice(len(sigma), p=mu)
        return sigma[idx].copy()
    
    # =========================================================================
    # TRANSITION FUNCTIONALS (Theorem 3.10)
    # =========================================================================
    
    def event_strain(self, z: np.ndarray, x: np.ndarray) -> float:
        """
        Compute τ(z, x) = <x, T_z x>, the event-strain functional.
        
        Measures how much the product z*x "strains" relative to its norm.
        
        Args:
            z: a zero divisor (unit vector)
            x: a state (unit vector)
        
        Returns:
            τ(z, x) scalar, typically in [-1, 1]
        """
        T_z = self.alternator(z)
        return np.dot(x, T_z @ x)
    
    def hermitian_overlap(self, z: np.ndarray, x: np.ndarray) -> float:
        """
        Compute A(z, x) = |<z, x>_ℂ|², the Hermitian overlap.
        
        Uses the canonical complex structure J = R_{e_{dim/2}}.
        
        Args:
            z, x: unit vectors
        
        Returns:
            A(z, x) scalar, in [0, 2]
        """
        if self.dim < 8:
            raise NotImplementedError("Hermitian structure only for dim >= 8")
        
        # Real part: <z, x>
        real_part = np.dot(z, x)
        
        # Imaginary part: <J*z, x> where J = R_{e_8} (right mult by spine axis)
        J = self._right_mult_matrix(self.e[self.dim // 2])
        imag_part = np.dot(J @ z, x)
        
        return real_part**2 + imag_part**2
    
    def spine_share(self, x: np.ndarray) -> float:
        """
        Fraction of state living in the spine (ℂ¹ component).
        
        For dim=16: s = x[0]² + x[8]²
        
        Args:
            x: a state vector (unit or not)
        
        Returns:
            Scalar in [0, 1]
        """
        spine_part = sum(x[i]**2 for i in self.spine_indices)
        return spine_part
    
    def pencil_norm(self, x: np.ndarray) -> float:
        """
        Norm of the pencil component (ℂ⁷ part).
        
        For dim=16: ||x_{pencil}|| = sqrt(sum of x[i]² for i in 1..7, 9..15)
        
        Args:
            x: a state vector
        
        Returns:
            Scalar in [0, 1]
        """
        pencil_part = sum(x[i]**2 for i in self.pencil_indices)
        return np.sqrt(pencil_part)
    
    # =========================================================================
    # OPERATORS AND MATRICES
    # =========================================================================
    
    def alternator(self, z: np.ndarray) -> np.ndarray:
        """
        Compute the alternator (commutator matrix) T_z.
        
        T_z encodes how much left and right multiplication by z differ.
        For z in the crack (zero divisor), T_z has specific structure.
        
        Args:
            z: a unit vector
        
        Returns:
            Matrix of shape (dim, dim)
        """
        # T_z[i, j] = (z*e_i · e_j - e_i*z · e_j) / 2
        # Equivalently: L_z - R_z where L, R are left/right mult matrices
        L_z = self._left_mult_matrix(z)
        R_z = self._right_mult_matrix(z)
        return (L_z - R_z) / 2.0
    
    def left_mult_matrix(self, z: np.ndarray) -> np.ndarray:
        """
        Compute the left-multiplication matrix L_z.
        
        L_z[i, j] = (z * e_j) · e_i
        
        Args:
            z: a unit vector
        
        Returns:
            Matrix of shape (dim, dim)
        """
        return self._left_mult_matrix(z)
    
    def right_mult_matrix(self, z: np.ndarray) -> np.ndarray:
        """
        Compute the right-multiplication matrix R_z.
        
        R_z[i, j] = (e_j * z) · e_i
        
        Args:
            z: a unit vector
        
        Returns:
            Matrix of shape (dim, dim)
        """
        return self._right_mult_matrix(z)
    
    def complex_structure(self) -> np.ndarray:
        """
        Return the canonical complex structure J = R_{e_{dim/2}}.
        
        For dim=16: J corresponds to multiplication by e_8 on the right.
        
        Returns:
            Matrix of shape (dim, dim) with J² = -I
        """
        if self.dim < 8:
            raise NotImplementedError("Complex structure only for dim >= 8")
        return self._right_mult_matrix(self.e[self.dim // 2])
    
    def conjugation_involution(self) -> np.ndarray:
        """
        Return the unique Aut-invariant anti-automorphic involution.
        
        For dim=16 (sedenions): conjugation swaps the two slots of multiplication.
        
        Returns:
            Matrix of shape (dim, dim) with V² = I, anti-automorphic
        """
        if self.dim == 16:
            # conjugation: +1 on spine (e_0, e_8), -1 on pencil
            V = np.diag([1.0] + [-1.0] * 7 + [1.0] + [-1.0] * 7)
            return V
        else:
            raise NotImplementedError(f"Conjugation not implemented for dim={self.dim}")
    
    # =========================================================================
    # CHANNEL (KRAUS REPRESENTATION)
    # =========================================================================
    
    def settlement_channel(self, x: np.ndarray) -> np.ndarray:
        """
        Apply the settlement channel Φ to a linear map (represented as a vector).
        
        Φ(X) = ∫_Σ L_z^T X L_z dμ(z)
        
        This is the "dissipation" from multiplying by random crack elements.
        
        Args:
            x: a vector or matrix (flattened to shape (dim*dim,))
        
        Returns:
            Result of channel application, same shape as input
        """
        sigma = self.crack()
        mu = self.invariant_measure()
        
        X = x.reshape(self.dim, self.dim) if x.ndim == 1 else x
        result = np.zeros_like(X)
        
        for z, weight in zip(sigma, mu):
            L_z = self._left_mult_matrix(z)
            result += weight * (L_z.T @ X @ L_z)
        
        return result.flatten() if x.ndim == 1 else result
    
    def channel_spectrum(self) -> Tuple[np.ndarray, np.ndarray]:
        """
        Compute the spectrum of the settlement channel Φ.
        
        For dim=16: eigenvalues lie in (1/7)*{0, ±1, ±3, ±2√3, ±7}.
        
        Returns:
            (eigenvalues, multiplicities) where eigenvalues are unique and sorted
        """
        sigma = self.crack()
        mu = self.invariant_measure()
        
        # Build the full channel matrix (dim² × dim²)
        channel_matrix = np.zeros((self.dim**2, self.dim**2))
        for z, weight in zip(sigma, mu):
            L_z = self._left_mult_matrix(z)
            kraus = np.kron(L_z, L_z.T)
            channel_matrix += weight * kraus
        
        evals = np.linalg.eigvalsh(channel_matrix)
        evals = np.sort(evals)[::-1]  # descending order
        
        # Count multiplicities
        unique_evals = []
        multiplicities = []
        tol = 1e-10
        for ev in evals:
            if len(unique_evals) == 0 or abs(ev - unique_evals[-1]) > tol:
                unique_evals.append(ev)
                multiplicities.append(1)
            else:
                multiplicities[-1] += 1
        
        return np.array(unique_evals), np.array(multiplicities)
    
    # =========================================================================
    # VERIFICATION GATES
    # =========================================================================
    
    def verify_composition_law(self, n_samples: int = 100) -> Tuple[bool, float]:
        """
        Gate G1: Composition law ||x*y|| = ||x||*||y||.
        
        Args:
            n_samples: number of random pairs to test
        
        Returns:
            (passes, max_defect) where passes is True if max_defect < 1e-12
        """
        rng = np.random.default_rng(42)
        max_defect = 0.0
        
        for _ in range(n_samples):
            x = rng.standard_normal(self.dim)
            y = rng.standard_normal(self.dim)
            defect = self.composition_law(x, y)
            max_defect = max(max_defect, defect)
        
        passes = max_defect < 1e-12
        return passes, max_defect
    
    def verify_antisymmetry(self, n_samples: int = 100) -> Tuple[bool, float]:
        """
        Gate G2: Left multiplication antisymmetry L_x + L_x^T = 0.
        
        Args:
            n_samples: number of random pure vectors to test
        
        Returns:
            (passes, max_defect)
        """
        rng = np.random.default_rng(43)
        max_defect = 0.0
        
        for _ in range(n_samples):
            x = rng.standard_normal(self.dim)
            x[0] = 0  # pure (no real part)
            x /= self.norm(x)
            
            L_x = self._left_mult_matrix(x)
            defect = np.linalg.norm(L_x + L_x.T)
            max_defect = max(max_defect, defect)
        
        passes = max_defect < 1e-12
        return passes, max_defect
    
    def verify_quadratic_identity(self, n_samples: int = 100) -> Tuple[bool, float]:
        """
        Gate G3: Quadratic identity x² = -e_0 for pure unit x.
        
        Args:
            n_samples: number of random pure unit vectors to test
        
        Returns:
            (passes, max_defect)
        """
        rng = np.random.default_rng(44)
        max_defect = 0.0
        
        for _ in range(n_samples):
            x = rng.standard_normal(self.dim)
            x[0] = 0
            x = self.normalize(x)
            
            x2 = self.mul(x, x)
            expected = -self.e[0]
            defect = self.norm(x2 - expected)
            max_defect = max(max_defect, defect)
        
        passes = max_defect < 1e-12
        return passes, max_defect
    
    def verify_moufang_identity(self, n_samples: int = 100) -> Tuple[bool, float]:
        """
        Gate G4: Moufang identity (ab)(ca) = a(bc)a.
        
        Args:
            n_samples: number of random triples to test
        
        Returns:
            (passes, max_defect)
        """
        rng = np.random.default_rng(45)
        max_defect = 0.0
        
        for _ in range(n_samples):
            a = rng.standard_normal(self.dim)
            b = rng.standard_normal(self.dim)
            c = rng.standard_normal(self.dim)
            
            lhs = self.mul(self.mul(a, b), self.mul(c, a))
            rhs = self.mul(self.mul(a, self.mul(b, c)), a)
            defect = self.norm(lhs - rhs)
            max_defect = max(max_defect, defect)
        
        passes = max_defect < 1e-12
        return passes, max_defect
    
    def verify_all_gates(self) -> bool:
        """
        Run all four mandatory verification gates.
        
        Returns:
            True if all gates pass, False otherwise
        """
        gates = [
            ("Composition law", self.verify_composition_law),
            ("Antisymmetry", self.verify_antisymmetry),
            ("Quadratic identity", self.verify_quadratic_identity),
            ("Moufang identity", self.verify_moufang_identity),
        ]
        
        all_pass = True
        for name, gate_func in gates:
            passes, defect = gate_func()
            status = "✓" if passes else "✗"
            print(f"{status} {name}: defect = {defect:.2e}")
            all_pass = all_pass and passes
        
        return all_pass
    
    # =========================================================================
    # PRIVATE HELPER METHODS
    # =========================================================================
    
    def _build_cayley_dickson_table(self, dim: int) -> np.ndarray:
        """
        Build the multiplication table C for a Cayley-Dickson algebra.
        
        Uses the doubling construction: if e_i (i < dim/2) is a basis for
        the smaller algebra, then e_i and e_{i+dim/2} form a basis for the
        current one, with multiplication rules:
        
            e_i * e_j = e_k  (from smaller algebra)
            e_{i+d} * e_{j+d} = -e_k  (conjugate of smaller)
            e_i * e_{j+d} = e_{k+d}  (cross terms)
            e_{i+d} * e_j = -e_{k+d}  (anti-cross)
        
        where d = dim/2.
        
        Args:
            dim: dimension (power of 2)
        
        Returns:
            Table C of shape (dim, dim, dim) where C[i,j,k] = 1 if e_i*e_j = e_k
        """
        if dim == 2:
            # Complex numbers: i*i = -1
            C = np.zeros((2, 2, 2))
            C[0, 0, 0] = 1  # 1*1 = 1
            C[0, 1, 1] = 1  # 1*i = i
            C[1, 0, 1] = 1  # i*1 = i
            C[1, 1, 0] = -1  # i*i = -1
            return C
        
        # Recursive: use the smaller algebra
        d = dim // 2
        C_small = self._build_cayley_dickson_table(d)
        C = np.zeros((dim, dim, dim))
        
        # Copy small algebra into both diagonal blocks
        C[:d, :d, :d] = C_small
        
        # Conjugate block: C[i+d, j+d, k] = -C[i, j, k]
        C[d:, d:, :d] = -C_small
        
        # Cross terms: C[i, j+d, k+d] = C[i, j, k]
        C[:d, d:, d:] = C_small
        
        # Anti-cross: C[i+d, j, k+d] = -C[i, j, k]
        C[d:, :d, d:] = -C_small
        
        return C
    
    def _left_mult_matrix(self, z: np.ndarray) -> np.ndarray:
        """
        Compute L_z: the matrix representation of left multiplication by z.
        
        L_z[i, j] = (z * e_j) · e_i
        
        Args:
            z: a vector of shape (dim,)
        
        Returns:
            Matrix of shape (dim, dim)
        """
        L = np.zeros((self.dim, self.dim))
        for j in range(self.dim):
            result = self.mul(z, self.e[j])
            L[:, j] = result
        return L
    
    def _right_mult_matrix(self, z: np.ndarray) -> np.ndarray:
        """
        Compute R_z: the matrix representation of right multiplication by z.
        
        R_z[i, j] = (e_j * z) · e_i
        
        Args:
            z: a vector of shape (dim,)
        
        Returns:
            Matrix of shape (dim, dim)
        """
        R = np.zeros((self.dim, self.dim))
        for j in range(self.dim):
            result = self.mul(self.e[j], z)
            R[:, j] = result
        return R
    
    def _compute_crack_octonion(self) -> List[np.ndarray]:
        """
        Compute Σ for octonions (dim=8).
        
        The crack of the octonions is empty (octonions form a division algebra).
        Return empty list or raise error.
        
        Returns:
            List of zero divisors (empty for octonions)
        """
        return []  # Octonions have no zero divisors
    
    def _compute_crack_sedenion(self) -> List[np.ndarray]:
        """
        Compute Σ for sedenions (dim=16): the 84 unit zero divisors.
        
        A unit vector z is in Σ if ker L_z ≠ 0, i.e., if there exists
        nonzero x with z*x = 0.
        
        For sedenions: Σ = {(a + b*e_8)/√2 : a, b ∈ Im(O), ||a||=||b||=1, a⊥b}
        where Im(O) is the 7-dimensional imaginary octonions.
        
        The 84 basic elements are: (e_i ± e_{j+8})/√2 for i,j ∈ 1..7, i ≠ j.
        
        Returns:
            List of 84 numpy arrays, each shape (16,), unit norm
        """
        sigma = []
        
        # Generate all (e_i ± e_{j+8})/√2
        for i in range(1, 8):
            for j in range(1, 8):
                if i != j:
                    for sign in [1, -1]:
                        z = np.zeros(16)
                        z[i] = 1.0
                        z[8 + j] = sign * 1.0
                        z = self.normalize(z)
                        sigma.append(z)
        
        return sigma


# =========================================================================
# UTILITIES
# =========================================================================

def describe_algebra(dim: int) -> None:
    """Print a human-readable description of the algebra structure."""
    alg = SlinPack(dim=dim)
    print(f"Algebra: dim={dim}")
    print(f"  Spine: indices {alg.spine_indices}")
    print(f"  Pencil: indices {alg.pencil_indices}")
    
    if dim == 16:
        sigma = alg.crack()
        print(f"  Crack Σ: {len(sigma)} zero divisors")
        print(f"  All gates pass: {alg.verify_all_gates()}")
        evals, mults = alg.channel_spectrum()
        print(f"  Channel spectrum: {len(evals)} unique eigenvalues")
        print(f"    Top 5: {evals[:5]}")


if __name__ == "__main__":
    # Quick sanity check
    alg = SlinPack(dim=16)
    print("SlinPack initialized.")
    print(f"Dimension: {alg.dim}")
    print(f"Crack size: {len(alg.crack())}")
    print()
    
    print("Running verification gates...")
    all_pass = alg.verify_all_gates()
    print()
    print(f"All gates pass: {all_pass}")
