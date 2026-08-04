# Anonymous Transactions in Cellframe: A Post‑Quantum, Lattice‑Based Privacy Stack

> A technical deep dive into the two independent cryptographic proof systems that underpin
> anonymous transactions in the Cellframe node — a transparent (no trusted setup),
> post‑quantum architecture built entirely on lattice cryptography.

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Architectural Overview](#2-architectural-overview)
3. [Preliminaries: The Lattice Substrate](#3-preliminaries-the-lattice-substrate)
4. [Stack A — The FRI‑Based zk‑SNARK for Ring Membership](#4-stack-a--the-fri-based-zk-snark-for-ring-membership)
5. [Confidential Amounts: Pedersen Commitments & Range Proofs](#5-confidential-amounts-pedersen-commitments--range-proofs)
6. [The Anonymous Transaction Data Model & Lifecycle](#6-the-anonymous-transaction-data-model--lifecycle)
7. [Stack B — MRNG/v1: A Log‑N Threshold Ring Signature](#7-stack-b--mrngv1-a-log-n-threshold-ring-signature)
8. [Privacy Properties → Cryptographic Component Map](#8-privacy-properties--cryptographic-component-map)
9. [Honest Caveats and Open Items](#9-honest-caveats-and-open-items)
10. [Further Reading](#10-further-reading)

---

## 1. Executive Summary

Cellframe implements anonymous (shielded) transactions using **two completely separate
proof systems** that share a common lattice substrate but never call each other:

| | Stack A — SNARK anon‑TX path | Stack B — MRNG/v1 ring signature |
|---|---|---|
| **Purpose** | Anonymous transfers (hidden sender + hidden amount) | Threshold ring signatures for governance/attestation |
| **Proof mechanism** | FRI‑DEEP polynomial commitment + hash commitments | Bulletproofs‑style halving inner‑product fold |
| **Threshold** | 1‑of‑N (single signer hides in a ring) | k‑of‑N (true threshold, subset‑hiding) |
| **Signature size** | ~tens of KB (FRI rounds) | O(log N): ~66 KB @ N=2 → ~186 KB @ N=256 |
| **Trusted setup** | **None** (transparent) | **None** (transparent) |
| **Post‑quantum** | **Yes** (lattice + hashes) | **Yes** (lattice + hashes) |
| **Wire identity** | embedded in anon‑TX items (`0xb0`–`0xb4`) | magic `'MRNG'`, profile `'MRV1'` |

A critical point for anyone familiar with Zcash‑style SNARKs: **there is no elliptic‑curve
cryptography, no bilinear pairing, no KZG, and no trusted setup anywhere in this codebase.**
Greps for `groth16`, `plonk`, `BLS12-381`, `BN254`, `miller_loop` return zero hits.
Everything runs over the polynomial ring `R_q = Z_q[X]/(X^N+1)` with `N=512, q=3 168 257`.

So although the code uses the name "SNARK" (in the strict sense: a *Succinct Non‑interactive
Argument of Knowledge*), by construction it is far closer to what the broader community
calls a **STARK**: a transparent, hash‑commitment‑based, post‑quantum argument that uses
FRI and Reed‑Solomon codes. It is, in fact, stronger than a classical STARK in one
respect — its underlying hardness rests on **lattice problems (Module‑SIS / Module‑LWE)**,
not only on hash‑function security.

---

## 2. Architectural Overview

```
                     ┌─────────────────────────────────────────────┐
                     │            cellframe-sdk (application)       │
                     │                                             │
   anonymous TX  ──▶ │  dap_chain_tx_anon_*     dap_sign_*_ring    │
   (Stack A)         │        │                      │             │
                     │        ▼                      ▼             │
                     │  chipmunk_snark_prove   chipmunk_ring_sign  │ ◀── Stack B
                     │  chipmunk_snark_verify  chipmunk_ring_verify│     (MRNG/v1)
                     │  chipmunk_pedersen_*                         │
                     │  chipmunk_range_proof_*                      │
                     └───────────────────────┬─────────────────────┘
                                             │  (submodule boundary)
                     ┌───────────────────────▼─────────────────────┐
                     │              dap-sdk (crypto core)           │
                     │           module/crypto/src/sig/chipmunk/    │
                     │                                             │
                     │   ┌─────────────┐    ┌──────────────────┐   │
                     │   │  SNARK/FRI  │    │   MRNG fold      │   │
                     │   │  (Stack A)  │    │   (Stack B)      │   │
                     │   └──────┬──────┘    └────────┬─────────┘   │
                     │          │       shared      │             │
                     │          └──── algebraic ────┘             │
                     │                 substrate                  │
                     │   chipmunk_lrs · chipmunk_poly · chipmunk_ntt │
                     │   chipmunk_fq6_ext (R_q^(e) degree-6 ext)    │
                     └─────────────────────────────────────────────┘
```

**Key relationships:**

- The SNARK (Stack A) and MRNG fold (Stack B) are **independent proof systems**. `grep`
  confirms `chipmunk_mring*.c` contains zero references to `snark`/`fri`, and the SNARK
  never invokes the fold.
- They share **low‑level primitives**: the LRS substrate (`chipmunk_lrs`), polynomial
  arithmetic (`chipmunk_poly`), the NTT (`chipmunk_ntt`), and the degree‑6 ring extension
  (`chipmunk_fq6_ext`).
- Stack A is wired into **anonymous transactions** via cellframe-sdk.
- Stack B is exposed through the generic signing API `dap_sign_create_ring` /
  `dap_sign_verify_ring` (`DAP_ENC_KEY_TYPE_SIG_CHIPMUNK_RING`).

---

## 3. Preliminaries: The Lattice Substrate

All constructions operate over

```
R_q = Z_q[X] / (X^N + 1),   N = 512,   q = 3 168 257   (22 bits)
```

with module dimension `K = 6`. Public keys are matrices `A ∈ R_q^{K×L}` sampled from a
seed; secret keys are short vectors `s ∈ R_q^K` with coefficients bounded by `β_w = 13`.
The hardness assumptions are **Module‑SIS** and **Module‑LWE** over this ring.

A subtle but decisive property: `q − 1 = 2^11 · 7 · 13 · 17` is divisible by `1024`, so
`R_q` **fully splits** into 512 linear factors over `F_q`:

```
R_q  ≅  F_q × F_q × … × F_q   (512 copies)
```

This full splitting is the source of a serious soundness problem for any fold‑based
argument performed directly in `R_q` (Section 7.3). The fix is a **degree‑6 extension**:

```
R_q^(e) = R_q[Y] / Φ_9(Y),   Φ_9(Y) = Y^6 + Y^3 + 1,   e = 6
```

`Φ_9` is irreducible over `F_q` (verified by both the cyclotomic criterion
`ord_9(q) = ord_9(5) = 6 = φ(9)` and Rabin's test). Because the modulus is irreducible in
*every* CRT slot, each `F_q` factor lifts to `F_{q^6}`, so

```
R_q^(e)  ≅  (F_{q^6})^512,   |F_{q^6}| = q^6 ≈ 2^129.6
```

This yields a **subtractive challenge set** `S = F_{q^6} \ {0}` of size `q^6 − 1 ≈ 2^129.6`,
all of whose nonzero differences are invertible in `R_q^(e)`. The sampler
(`chipmunk_fq6_ext_sample_challenge_q`) rejection‑samples six `F_q` coordinates and rejects
the all‑zero scalar, so **challenges are always invertible by construction — no retry loop
on non‑invertibility is needed**. `Φ_9` is the smallest cyclotomic giving `q^e ≥ 2^128`;
the trinomial shape makes reduction cheap (`Y^6 ≡ −Y^3 − 1`).

Both proof systems evaluate in `R_q^(e)` and use **SHA3‑256 / SHAKE256** with domain
separation throughout (Fiat–Shamir in the QROM).

---

## 4. Stack A — The FRI‑Based zk‑SNARK for Ring Membership

**Location:** `dap-sdk/module/crypto/src/sig/chipmunk/chipmunk_snark.{c,h}`

### 4.1 The statement

The SNARK proves a **linkable ring‑membership** statement:

> *"I know the secret key `sk_j` corresponding to one public key `pk_j` in the ring
> `{pk_0, …, pk_{N−1}}`, without revealing `j`."*

Concretely, the witness is a **one‑hot indicator vector** `b ∈ {0,1}^N`
(`witness.indicator.coeffs[signer_index] = 1`). The constraint system enforces two
polynomial conditions on `b` (`s_build_constraint_polynomial`, `chipmunk_snark.c:354-403`):

- **C1 (binary):** `b_i · (b_i − 1) = 0` for all `i` — every coordinate is 0 or 1.
- **C2 (exactly‑one):** `Σ b_i − 1 = 0` — exactly one signer is selected.

These are combined with a transcript‑derived **randomizer** `r ∈ F_{q^6} \ {0}` into a
single polynomial

```
z(X) = C1(X) + r · C2(X)
```

which is identically zero for an honest prover. (An earlier design had additional
constraints C3/C4 for explicit ring binding; these were removed in "Phase 5" because ring
binding is now carried by the Fiat–Shamir transcript — see `chipmunk_snark.c:14-16, 307-316`.)

**Ring binding** is achieved by hashing all ring public keys
`ring_hash = SHAKE256(pk_0 ‖ … ‖ pk_{N−1})` and mixing `ring_hash` into the randomizer
derivation transcript. A proof is therefore not replayable against a different ring.

> **Privacy note on `w_commit`:** the commitment to the witness is
> `w_commit = H(domain_sep ‖ random_nonce)` — deliberately *random*, not `H(b)`. Because `b`
> is 1‑of‑`N` sparse, `H(b)` would be brute‑forceable with only `N` precomputable hashes,
> destroying anonymity (`chipmunk_snark.c:697-713`).

### 4.2 The proof structure

A proof (`chipmunk_snark_proof_t`) contains:

| Field | Size | Role |
|---|---|---|
| `w_commit`, `z_commit`, `q_commit`, `r_commit` | 4 × 32 B | SHA3‑256 commitments to witness, combined polynomial, quotient, randomizer |
| `opening_proof` | 4 096 B | Serialized `z` and `q` polynomials (bridge phase, to be replaced by DEEP composition) |
| `fri_proof` | variable | FRI‑DEEP proof for `q(X)` |
| `fri_grinding_nonce` | — | 16‑bit PoW grinding nonce |
| `transcript_hash` | 32 B | Fiat–Shamir transcript digest |

### 4.3 The prover pipeline (`chipmunk_snark_prove`)

1. Build the one‑hot indicator `b`.
2. Compute `w_commit = H(domain ‖ nonce)`.
3. Compute `ring_hash`, derive the randomizer `r`, commit `r_commit`.
4. Build `z(X) = C1 + r·C2`; commit `z_commit`.
5. Sample the evaluation point `α ∈ F_{q^6} \ {0}` from the transcript
   `(domain ‖ w_commit ‖ r_commit ‖ z_commit ‖ msg_hash)`.
6. **Quotient polynomial** `q(X) = z(X)/(X − α)` via synthetic division over `F_{q^6}`
   (requires `z(α) = 0`); commit `q_commit`.
7. Serialize `z, q` into `opening_proof`.
8. Run **FRI** on `q(X)`: seed `"CHIPMUNK-SNARK-F"`, absorb the four commitments +
   `msg_hash` + `transcript_hash`, derive 7 folding `α`s, RS‑encode `q`, fold 7 rounds
   (codeword sizes `2048 → … → 32`), build Merkle caps, absorb caps + final evals,
   finalize with ~2^16 grinding, derive 8 query indices, open `q` at those positions.

**FRI parameters** (`chipmunk_fri.h`): 7 rounds, rate `ρ = 1/4` (blowup 4), final
polynomial of 16 coefficients, Merkle cap of 16 nodes/round (Poseidon compression), 8 query
openings each carrying a leaf + antipodal sibling + authentication path.

### 4.4 The verifier (`chipmunk_snark_verify`)

Everything is re‑derived from the transcript and compared in constant time:

1. Re‑derive the randomizer and verify `r_commit`.
2. Re‑derive `α`; verify `transcript_hash`.
3. **FRI verification**: replay the transcript, verify the grinding nonce by single‑hash,
   re‑derive the 8 query indices, verify each opening (index match + Merkle auth + folding
   relation) via `chipmunk_fri_verify_query_q`.
4. Reconstruct `z, q` from `opening_proof`, range‑check coefficients in `[0, q)`, recompute
   and compare `z_commit`, `q_commit`.
5. **Extension check**: `z(α) == 0` over `F_{q^6}` — the primary soundness gate.
6. **Quotient relation**: 11 random test points `β` drawn from a SHAKE256 stream seeded by
   `(transcript_hash, msg_hash)`; for each, check `z(β) == q(β)·(β − α_scalar)` via Horner
   evaluation.

### 4.5 Soundness budget

The header (`chipmunk_snark.h:20`) claims **~391 bits** as a sum of component margins:

| Component | Bits | Note |
|---|---|---|
| Extension `α` check | ~129 | `α ∈ F_{q^6}\{0}`, `|S| = q^6−1 ≈ 2^129.6` |
| Quotient checks (×11) | ~238 | per‑check margin attributed in the header |
| FRI queries | 8 | 8 query openings |
| Grinding PoW | 16 | ~2^16 single‑hash grind |

The companion `CHIPMUNK_SECURITY_ANALYSIS.md` separately gives a post‑QROM Fiat–Shamir
advantage estimate (~77 bits after a ~48‑bit QROM loss from a ~125‑bit base). These two
numbers are **not directly comparable**: the 391‑bit figure sums independent component
budgets that an adversary must satisfy simultaneously, while the QROM figure bounds the
overall adversarial advantage. An article should present both and note the distinction.

---

## 5. Confidential Amounts: Pedersen Commitments & Range Proofs

Anonymous transactions hide not only the sender but also the **amounts**. Two lattice
primitives cooperate: Pedersen commitments for hiding, and a Stern‑like range proof for
bounding.

### 5.1 Lattice Pedersen commitments (`chipmunk_pedersen.{c,h}`)

```
C = A · r + encode(m)   mod q
```

- `A ∈ R_q^{K×L}` (`K=6, L=3`) is a public matrix derived from a **network‑wide fixed seed**
  `"chipchain-pedersen-params-v1"` (`dap_chain_ledger_type.c:112`). A fixed `A` is what makes
  commitments **additively comparable across transactions** — the foundation of conservation.
- `r ∈ R_q^L` is a short blinding vector.
- `m` is the amount.

The scalar encoding is the crucial **Phase 6 fix** (`chipmunk_pedersen.c:32-62`): every
coefficient of `encode(v)` equals `v mod q`. This is **Z‑linear** —

```
encode(v1) + encode(v2) = encode(v1 + v2)   in R_q
```

— with no carry‑propagation. (Earlier base‑256 and base‑14 encodings broke additivity at
chunk boundaries; the file documents this history.)

The proven range is therefore `[0, q−1]` (≈ 3.17 M atomic units), **not** `[0, 2^64)` as
the `OUT_ANON` header comment suggests — that 64‑bit figure is the field width, not the
proven range. Commitment arithmetic uses pre‑NTT'd matrices, needing only 6 inverse NTTs
per commit instead of 36 round trips.

### 5.2 Range proofs (`chipmunk_range_proof.{c,h}`)

A **Stern‑style** Sigma protocol with bit‑decomposition, made non‑interactive via Fiat–Shamir.

- **Parameters:** 256‑bit decomposition, **128 binary challenges** → soundness error
  `(1/2)^128 = 2^{-128}`.
- **Prove flow:** bit‑decompose the value; derive per‑bit blinding polynomials via SHAKE256
  rejection sampling (with the residual blinding chosen to close
  `Σ bit_r[i] = orig_r`); commit each bit as `b_i · 2^i mod q`; aggregate `A = B = Σ bit_commits[i]`;
  draw 128 binary challenges from the transcript; for each, respond with either a permuted
  bit vector (challenge 0) or permuted complements `1 − b` (challenge 1).
- **Verify flow:** recompute and constant‑time‑compare the transcript hash; verify each of
  the 128 responses is binary; verify the aggregate `A == C` (the original commitment)
  coefficient‑by‑coefficient. This last check ties the range proof to the published
  Pedersen commitment.

Honest‑verifier ZK; full ZK under Fiat–Shamir in the QROM.

---

## 6. The Anonymous Transaction Data Model & Lifecycle

**Location:** `cellframe-sdk/modules/common/include/dap_chain_datum_tx_anon.h`,
`cellframe-sdk/modules/net/tx/dap_chain_tx_anon_create.c`,
`cellframe-sdk/modules/ledger/dap_chain_ledger_type.c`.

### 6.1 Transaction items

An anonymous transaction is assembled from typed items:

| Type byte | Item | Holds |
|---|---|---|
| `0xb0` | `IN_ANON` | `prev_hash`, `prev_out_idx`, **`key_image[9216]`**, **`snark_proof`**, `ring_size`, + variable‑length ring pubkeys |
| `0xb1` | `OUT_ANON` | `addr`, **`pedersen_commitment`**, **`range_proof`**, `token_ticker` |
| `0xb2` | `KEY_IMAGE` | on‑chain double‑spend tag |
| `0xb3` | `ANON_PROOF` | (auxiliary proof container) |
| `0xb4` | `PEDERSEN_COMMIT` | (auxiliary commitment container) |

The **9216‑byte `key_image`** is `K = 6` q‑packed polynomials representing the lattice
key image `I = A_I · s` (a one‑time public‑key image), computed by `s_ring_key_image`.

### 6.2 Create flow (`dap_chain_tx_anon_create.c`)

The core routine is `s_anon_transfer_generic`, behind an **algorithm adapter** abstraction
supporting either native chipmunk‑ring key material or LRS seed‑based keys.

1. **Ring assembly.** The real signer's key is placed in a ring; decoy validators' keys are
   gathered automatically, and the ring is topped up with freshly synthesized keypairs if
   needed (`s_ring_fill_decoys`). Ring size is clamped to `[N_min, 64]` on this path.
2. **Witness population.** `witness.signer_index` and the secret‑key polynomials are filled
   by the adapter's `populate_witness`.
3. **Key‑image UTXO binding.** The wallet‑level key image `I` is bound to the specific UTXO
   by hashing:
   ```
   key_image = SHA3-256( I_wallet ‖ prev_hash ‖ prev_out_idx )
   ```
   (`s_bind_key_image_to_utxo`). This makes each spend commit a *unique* tag even though the
   wallet‑level image is constant, so one wallet can spend multiple UTXOs. Note this binding
   **hashes the lattice image down to 32 bytes**; the remaining bytes of the 9216‑byte field
   are zeroed.
4. **Cross‑component message binding.** The SNARK message is not the TX itself but a
   purpose‑built binding buffer (`dap_chain_anon_snark_build_message`):
   ```
   msg = addr ‖ commit_hash ‖ ticker ‖ ki_hash ‖ rp_hash
   ```
   where `commit_hash = SHA3-256(out.commitment)`, `ki_hash = SHA3-256(key_image)`,
   `rp_hash = SHA3-256(out.range_proof)`. This **ties the proof to a specific Pedersen
   commitment, range proof, and key image**, so it cannot be replayed against a different
   output set.
5. **Prove.** `chipmunk_snark_prove(&snark, &ctx, &statement, &witness)`. The witness is
   wiped immediately after.
6. **Outputs.** For each output (recipient, change, fee), a Pedersen commitment + range proof
   are built from a random seed.
7. **Anchor output (Pedersen conservation closure).** Because the verifier checks
   `Σ C_out == C_in`, and the input's blinding is *deterministically* derived from
   `(prev_hash, prev_out_idx)`, the prover must make the output blindings sum exactly to
   `r_in`. The recipient/change/fee outputs each consume their own random blinding; the
   **anchor** is a zero‑value output that absorbs the residual blinding
   (`chipmunk_pedersen_blinding_sub`). This is what closes the homomorphic balance equation
   without revealing any amount.

### 6.3 Verify flow (`dap_chain_ledger_type.c`)

`s_anon_tx_crypto_verify` validates, in order:

1. **SNARK ring‑membership proofs.** For each `IN_ANON`: extract ring pubkeys, locate the
   first `OUT_ANON` to bind against, reconstruct the SNARK message identically to the prover,
   call `chipmunk_snark_verify`. Failure → reject.
2. **Key‑image double‑spend check.** For each `KEY_IMAGE` item: compute
   `image_hash = hash_fast(image, 9216)`, then an **atomic check‑and‑insert** under a write
   lock (`s_key_image_add`). Collision → `-EEXIST`, logged as "Double‑spend attempt
   detected", with partial‑failure rollback.
3. **Range proofs** on each `OUT_ANON` via `chipmunk_range_proof_verify`.
4. **Pedersen conservation.** Reconstruct the input commitment (recompute for standard
   outputs, or use the stored field for anon outputs), sum all `OUT_ANON` commitments
   homomorphically via `chipmunk_pedersen_add`, and check equality
   (`dap_ledger_pedersen_commit_equal`). This enforces "no amount created out of thin air"
   without revealing any amount.

---

## 7. Stack B — MRNG/v1: A Log‑N Threshold Ring Signature

**Location:** `dap-sdk/module/crypto/src/sig/chipmunk/chipmunk_mring*.{c,h}` and
companion design docs `README_MRNG.md`, `MRNG_M4_FOLD.md`, `MRNG_G3_1_*.md`,
`MRNG_M4_INVERTIBILITY.md`.

This is the production **k‑of‑N threshold ring signature** (wire magic `'MRNG'`, version 1,
profile `'MRV1'`). It is exposed via `chipmunk_ring_sign_to_bytes` /
`chipmunk_ring_verify_from_bytes`. Crucially, **it does not use FRI and does not call the
SNARK** — it is a self‑contained Bulletproofs‑style halving fold.

### 7.1 The statement

The fold proves a single **unified inner‑product identity** over `R_q` (lifted into
`R_q^(e)`):

```
⟨b̃, P̃(c)⟩ = ρ(c)
```

using an **augmented vector** `b̃ = (b, b∘(b−1)) ∈ R_q^{2N}` and a public vector

```
P̃[i](c)    = c + c³ · pk_i     for i ∈ [0, N)
P̃[N+i](c)  = c²                for i ∈ [0, N)

ρ(c) = c · t + c³ · Y_pk
```

This single identity bundles three relations:

- **REL‑1 (binary):** the `b∘(b−1)` half is zero only if every `b_i ∈ {0,1}`.
- **REL‑2 (threshold):** `Σ b_i = t` appears as the `c·t` term.
- **REL‑3 (pk correctness):** `Σ b_i·pk_i = Y_pk` appears as the `c³·Y_pk` term.

Here `b ∈ {0,1}^N` is the **secret signer‑subset indicator**: `b_i = 1` iff ring member `i`
is one of the `t` actual signers. The subset is never revealed; only its commitment `C_b`
and the folded proof are.

### 7.2 The halving fold

Augmented dimension `2N` is zero‑padded to `padded_dim = 2·2^⌈log₂ N⌉`, and both `b̃` and
`P̃` are embedded into `R_q^(e)`. Each **fold round** (reduction factor 2):

1. Split `b̃ = (b_L ‖ b_R)`, `P̃ = (p_L ‖ p_R)`.
2. Compute the only two new committed cross‑terms:
   ```
   L_r = ⟨b_L, p_R⟩ ∈ R_q^(e)
   R_r = ⟨b_R, p_L⟩ ∈ R_q^(e)
   ```
3. Commit `L_r, R_r` (Pedersen‑style vector commitments `C_L, C_R`) — the raw values stay
   off the wire.
4. Derive the Fiat–Shamir challenge `x_r ∈ S = F_{q^6}\{0}` from
   `SHAKE256("MRNG-M4-fold-round-fs-v1" ‖ fs_seed ‖ LE32(r) ‖ C_L ‖ C_R)`, and its inverse
   `x_r⁻¹`.
5. Apply the fold maps (the standard Bulletproofs identity, adapted to `R_q^(e)`):
   ```
   b̃'[j] = b_L[j] + x_r · b_R[j]
   P̃'[j] = p_L[j] + x_r⁻¹ · p_R[j]
   ρ'    = ρ + x_r · L_r + x_r⁻¹ · R_r
   ```
   The invariance `⟨b̃', P̃'⟩ = ρ'` holds identically for an honest prover.
6. Halve: write `b̃', P̃'` into the first half and shrink `length` to `length/2`.

After `D = 1 + ⌈log₂ N⌉` rounds, both vectors collapse to length‑1 elements `b*`, `a*`.
The prover applies a **MatRiCT+ leaf mask** `ω` (a single `R_q` polynomial blinding `b*`,
sampled uniformly in `[−WC^D, +WC^D]` via SHAKE256) and sends `β = b* + ω`. The verifier
unmasks `b* = β − ω` and checks `⟨b*, a*⟩ = ρ^(D)`.

**Verifier:** recomputes `P̃` and `ρ` from public inputs only, re‑derives every `x_r` /
`x_r⁻¹` from `(C_L, C_R)` via FS, opens `L_r` / `R_r` via the seed‑derived vector‑commitment
openings, folds `P̃` down to `a*`, checks the public‑side match, the leaf‑mask bound
`‖ω‖∞ ≤ WC^D`, and the final inner product.

**Rounds:** `fold_depth = 1 + ⌈log₂ N⌉`, capped at `FOLD_DEPTH_MAX = 9` for `N_MAX = 256`.
The "+1" is the cost of carrying the binary‑check half of the augmented vector.

### 7.3 Why the degree‑6 extension is mandatory

This is the single most important security finding in the MRNG design
(`MRNG_M4_INVERTIBILITY.md`). Because `R_q` fully splits into 512 `F_q` factors (Section 3),
a fold performed **directly in `R_q`** decomposes by CRT into 512 independent scalar
inner‑product arguments, one per slot. A cheating prover survives a round iff the per‑slot
challenge projection is a root of a low‑degree identity, giving per‑round/per‑slot soundness
of only `≈ 2/q ≈ 2^{-20.6}`. Over `D = 9` rounds the union bound collapses to
`2D/q ≈ 2^{-17.6}` — **a single‑shot fold in `R_q` would deliver only ~17–18 bits of
soundness, not 128.** This was confirmed empirically: 8 of 50 000 sampled challenges were
non‑invertible, matching the prediction `n/q = 1.616e-4`.

Lifting to `R_q^(e)` makes each slot `F_{q^6}`, so the subtractive set has size
`q^6 − 1 ≈ 2^129.6`. Per‑round soundness becomes `≤ 2·D/|S| ≤ 9·2/2^128 ≈ 2^{-123.8}`, and
the tighter Vandermonde‑extractor reading gives total
`κ ≤ D·2/|S| ≈ 2^{-125.4}` — **single‑shot, no parallel repetition, ≥ 125‑bit knowledge
soundness.**

### 7.4 The bind block and the link tag

The fold proves the *aggregated* statement, but the prover must also show it knows a short
witness `X` consistent with both the public‑key claim and the link tag. This is a
**same‑witness Schnorr‑style binding** using a single response vector:

```
z_x = ρ_x + c*·X ∈ R_q^{K_pk}
```

- `ρ_x` is a bounded‑uniform mask (`MASK_BOUND = 524 769`).
- `c*` is the bind‑block FS challenge (sparse‑ternary, weight 37).
- `X = Σ_{i∈S} x_i` is the aggregated witness across the `t` signers.

The verifier never sees the masks `M_pk, M_T`; it **reconstructs** them and re‑absorbs them
into the FS transcript to re‑derive `c*`:

```
M_pk = A_pk · z_x − c* · Y_pk
M_T  = A_T  · z_x − c* · T
```

Because the *same* `z_x` must satisfy both equations, a malicious prover trying to split the
witness between the two sides must break Module‑SIS over the stacked vector `[A_pk ‖ A_T]`.

**Link tag `T`:** `T = A_T · X ∈ R_q`, where `A_T` is per‑(ring, ctx). Two signatures from
the **same signer subset** under the **same (ring, ctx)** produce the same `T`; different
subsets produce (with overwhelming probability) different `T`. This gives **linkability /
double‑spend detection** without revealing the subset.

### 7.5 Threshold mechanics

"Exactly `t` distinct members signed" is enforced by REL‑2 (the `c·t` term) plus the prover's
own indicator construction, which rejects duplicate matches (`-EEXIST`) and requires
`count == threshold`. The "combining" is **purely algebraic** — there is no interactive
combiner round, no DKG, no network protocol. A coordinator collects the `t` signers' secret
wectors out of band, sums them into `X`, sets the indicator bits, and produces **one**
signature. Verification is `O(log N)`, independent of `t`. **Fully non‑interactive.**

### 7.6 Fiat–Shamir transcript & rejection sampling

- 384‑bit FS output; transcript root `fs_seed = SHA3-256(ring_hash ‖ ctx_hash ‖ msg_hash ‖ T ‖ C_b)`.
- Fold‑round challenges use SHAKE256 as an XOF.
- **Lyubashevsky bounded‑uniform abort:** `ρ_x` is uniform in `[−MASK_BOUND, +MASK_BOUND]`;
  `z_x` is accepted only if every coefficient lands in `[−RESPONSE_BOUND, RESPONSE_BOUND)`
  (`RESPONSE_BOUND = 2^19`); the gap `MASK_BOUND − RESPONSE_BOUND = BETA = WC·β_w = 37·13 = 481`
  is exactly the LRS bounded‑uniform construction, so the statistical‑distance abort proof
  transfers verbatim.
- The outer sign loop retries up to `MAX_ATTEMPTS = 2048` on `-EAGAIN`, mixing an attempt
  counter into the master seed. This is rejection‑sampling resampling, **not** hashcash‑style
  PoW — there is no difficulty target.

### 7.7 Signature sizes

```
total(D) = 33 532 + D · 16 896   bytes,   D = 1 + ⌈log₂ N⌉
```

| N | D | Total | ~KB |
|---:|---:|---:|---:|
| 2 | 2 | 67 324 | 65.7 |
| 16 | 5 | 118 012 | 115.2 |
| 64 | 7 | 151 804 | 148.2 |
| 256 | 9 | 185 596 | 181.2 |

(An older, now‑superseded size table in the header reflects a retired estimate that assumed
fold elements live in bare `R_q`; the authoritative corrected table is in `README_MRNG.md §11`.)

**Packing:** `qpack` = 1 408 B/poly (`512·22/8`) for `T, C_b, Y_pk, c*` and each `R_q` limb
of an `R_q^(e)` element; `zpack` = 1 280 B/poly (`512·20/8`) for the bind response `z_x`;
the leaf mask uses a 49‑bit biased pack (3 136 B).

### 7.8 Wire layout

A 28‑byte little‑endian header (`magic='MRNG'`, `version=1`, `params_id='MRV1'`, `n_ring`,
`threshold`, `fold_depth`, `flags[0]=linkable`), followed by: 128 B of fixed hashes (`ring_hash`,
`ctx_hash`, `msg_hash`, `fs_seed`), `T`, `C_b`, `Y_pk` (qpacked), a 32‑byte `fold_opening_seed`,
the fold tree (`D` rounds × `C_L‖C_R`), the final scalars `a*‖b*`, the leaf mask `ω`, and the
bind block `z_x[0..5] ‖ c*`.

---

## 8. Privacy Properties → Cryptographic Component Map

| Privacy property | Provided by | Code |
|---|---|---|
| **Anonymity set (signer hidden in ring)** | SNARK over one‑hot `b` with blinded `w_commit = H(nonce)` + transcript‑bound `ring_hash` | `chipmunk_snark.c` |
| **Ring binding (no cross‑ring replay)** | `ring_hash` mixed into randomizer transcript | `chipmunk_snark.c` |
| **Hidden amounts** | Lattice Pedersen `C = A·r + encode(m)` (MLWE‑hiding) | `chipmunk_pedersen.{c,h}` |
| **Amount‑in‑range (no negative/overflow)** | Stern‑like range proof, 128 challenges, `2^{-128}` soundness | `chipmunk_range_proof.{c,h}` |
| **Conservation (no inflation)** | Homomorphic Pedersen additivity `Σ C_out == C_in` + anchor‑output blinding closure | `dap_chain_ledger_type.c`, `dap_chain_tx_anon_create.c` |
| **Double‑spend protection** | Key image `I = A_I·s`, bound per‑UTXO via `SHA3-256(I‖prev_hash‖prev_out_idx)`, atomic check‑and‑insert | `dap_chain_tx_anon_create.c`, `dap_chain_ledger_type.c` |
| **Cross‑component binding (proof tied to outputs & KI)** | SNARK message `addr‖commit_hash‖ticker‖ki_hash‖rp_hash` | `dap_chain_datum_tx_anon.c` |
| **Threshold subset‑hiding (Stack B)** | MRNG fold over secret indicator `b`, `O(log N)` proof | `chipmunk_mring*` |
| **Threshold linkability (Stack B)** | Link tag `T = A_T·X` | `chipmunk_mring*` |
| **Post‑quantum** | Module‑SIS / Module‑LWE substrate, hash‑based commitments | entire stack |
| **QROM non‑interactivity** | Fiat–Shamir with SHA3/SHAKE domain separation | entire stack |

---

## 9. Honest Caveats and Open Items

For an honest engineering account, the following are worth stating explicitly:

1. **Soundness figures have internal inconsistencies.** The SNARK header claims ~391 bits
   (sum of component budgets) while `CHIPMUNK_SECURITY_ANALYSIS.md` gives a post‑QROM
   advantage of ~77 bits; the ledger call‑site comment cites yet another figure (~138 bits
   for quotient checks). Some call‑site comments still describe the retired C3/C4
   constraints. For precision, cite `chipmunk_snark.{c,h}` for what the code actually does.

2. **MRNG Galois‑consistency lane is implemented but not wired.** The design specifies
   base‑case checks `σ(b*) = b*` / `is_in_base(b*)` (Frobenius / trace consistency); the
   primitives exist and are tested, but `chipmunk_mring_fold_verify` does not currently call
   them. This is a tracked M4 obligation, not a silent gap.

3. **Range proven is `[0, q−1]`, not `[0, 2^64)`.** The `OUT_ANON` header comment overstates
   the range; the scalar encoding constrains amounts to `[0, 3 168 256]` atomic units per
   output.

4. **Key‑image binding hashes the lattice image to 32 bytes.** The on‑chain double‑spend tag
   is effectively `SHA3-256(I_wallet ‖ prev_hash ‖ prev_out_idx)` stored in a 9 216‑byte
   field (trailing bytes zeroed). This is a deliberate compression but worth noting.

5. **Two ring stacks, two ring‑size policies.** The SNARK anon‑TX path clamps rings to
   `[N_min, 64]`; MRNG supports `N ∈ [2, 256]`. They share primitives but are different code
   paths serving different purposes.

6. **No trusted setup — by design.** This is a strength (no toxic waste, no ceremony to
   compromise), but it is paid for in proof size and prove/verify time relative to a
   pairing‑based Groth16 SNARK. The trade‑off buys post‑quantum security and transparency.

---

## 10. Further Reading

Within the repository (`dap-sdk/module/crypto/src/sig/chipmunk/`):

- `README.md`, `README_MRNG.md` — overall + MRNG design.
- `CHIPMUNK_SECURITY_ANALYSIS.md`, `CHIPMUNK_QROM_PROOF.md` — security arguments.
- `MRNG_M4_FOLD.md`, `MRNG_M4_INVERTIBILITY.md`, `MRNG_G3_1_EXTENSION_SOUNDNESS.md`,
  `MRNG_G3_1_NOGAP_LEMMA.md`, `MRNG_G4_TRANSCRIPT.md` — MRNG design locks.
- `doc/2023-1820.pdf` — the referenced Chipmunk paper (IACR ePrint 2023/1820).

External background:

- FRI / STARK foundations — Ben‑Sasson et al.
- Bulletproofs inner‑product arguments — Bünz et al.
- MatRiCT+ lattice ring signatures — Esgin, Steinfeld, Zhao (2022).
- ACK21 and RoK 2024 — lattice‑fold soundness in small rings / CRT extensions.

---

*This document describes the implementation as of the `feature/zk-snark` branch. Cryptographic
constructions are reproduced from source for explanatory purposes; the authoritative
reference is always the code and the in‑tree design documents.*
