# PROMPT
Inspect the GitHub repository https://github.com/next-state/open-dreamer in depth and report what it actually is and how reusable it is for a NON-video, NON-Minecraft scientific application.

Clone it into /private/tmp/claude-501/-Users-raj-Downloads-Vizuara/0ddf2ea6-71c5-4ee7-94da-c1eb7d68fb0d/scratchpad/open-dreamer (shallow clone is fine: `git clone --depth 1`). If cloning fails, fall back to WebFetch on the repo's file pages / raw.githubusercontent.com. Then actually READ the code.

Report on:

1. **What it implements.** It claims to be a JAX/Flax NNX implementation of the Dreamer 4 world 

# RESULT
I've read the full codebase. Report below.

---

# Open Dreamer (`next-state/open-dreamer`) — technical assessment

## Bottom line (blunt)

**Do not adopt this repo for a physics-field world model. Read it, steal three specific algorithms from it, and write your own.**

Three independent reasons, in order of severity:

1. **The licence forbids it.** `LICENSE` is *"All rights reserved… No license or permission is granted, whether express or implied, to use, copy, modify…"*. GitHub reports `NOASSERTION`. You cannot legally fork, vendor, or derive from this today.
2. **There is no agent in it.** Only the world model (tokenizer + action-conditioned dynamics). No reward model, no value function, no actor-critic, no imagination rollout training, no behaviour cloning. It is a *controllable video predictor*, not a model-based controller. The README roadmap admits this: `- [ ] Full Dreamer 4 Behaviour-Cloning / RL agent training loop`.
3. **It is one week old, has zero tests, and only one working data path (Minecraft VPT).** 8 commits on `main`, all cosmetic except the initial squash; the CoinRun "small" path is provably broken at HEAD (two separate bugs, below). Your modality would be the third path — and the first two don't both work.

What *is* worth taking: the shortcut-forcing loss (`dreamer/training.py:294-479`), the τ-ladder sampler (`dreamer/generation.py:45-219`), and the x-prediction + v-space loss weighting trick (`dreamer/training.py:120-132`). That's ~400 lines of genuinely useful reference implementation, plus an unusually candid engineering blog post in `site/article/article.html`. For a 64×64 field with a low-dim continuous action, a bespoke latent-dynamics model is smaller than the diff you'd need to apply here.

---

## 1. What it implements (and what it does not)

**Confirmed:** JAX + Flax **NNX** (`from flax import nnx` throughout; `nnx.Module`, `nnx.jit`, `nnx.Optimizer`, Orbax checkpoints). It is a re-implementation of the *world-model half* of Dreamer 4 (Hafner, Yan, Lillicrap, arXiv 2509.24527), trained on Minecraft/VPT-format data. Acknowledged lineage to p-doom/`jasmine` (README:250).

**Present:**

| Component | Where |
|---|---|
| Causal latent video tokenizer (encoder+decoder) | `dreamer/models.py:740-996` |
| Action-conditioned flow-matching dynamics w/ shortcut forcing | `dreamer/models.py:1162-1407`, `dreamer/training.py:294-479` |
| Offline tokenization of episodes → latent shards | `scripts/tokenize_minecraft_dataset.py` |
| AR rollout with ring-buffer KV cache | `dreamer/generation.py`, `dreamer/models.py:33-125` |
| FVD eval (self-contained pure-JAX I3D) | `dreamer/fvd/fvd.py`, `dreamer/fvd/i3d_pretrained_400.npz` (50 MB, checked in) |
| Muon/LaProp/AdamW, MuP, WSD schedules, EMA, scaling-law helpers | `dreamer/utils.py`, `dreamer/scaling.py` |

**Absent — verified by exhaustive grep, not inference:**

- No `policy`, `actor`, `critic`, `value`, `advantage`, `GAE`, `PPO`, `REINFORCE`, `imagination`, or `behaviour cloning` anywhere in `dreamer/` or `scripts/`. The single hit for "policy" is a comment in `dreamer/configs.py:30`.
- **No reward model or reward head.** `rewards` appears *only* as a data-loading convenience: CoinRun episodes store rewards and the loader can bias its random window toward non-zero-reward timesteps (`dreamer/data/transforms.py:192-226`, `configs/dataset/coinrun.yaml:73`). For VPT, `"rewards": None` (`transforms.py:340`). Nothing consumes rewards for learning.
- No planner (no CEM/MPPI/MCTS).

**Vestigial agent hooks** (someone started, then stopped): `Modality.AGENT` (`dreamer/utils.py:94`), a `wm_agent` attention hierarchy where agent tokens see everything (`utils.py:161-178`), a `task_embeddings` argument threaded through `Dynamics.__call__` that returns per-timestep agent hidden states `h_t` (`models.py:1280, 1331-1332, 1362`), and `h_states` returned in the loss aux dict (`training.py:475`). The trainer passes `task_embeddings=None, # Not used in dynamics pretraining` (`scripts/train_dynamics.py:144`). `dreamer/training.py:1-9`'s docstring advertises "dynamics and imagination training" — the imagination half does not exist.

**Consequence for you:** usable as a differentiable/samplable simulator surrogate. For control you would write the entire policy-learning layer yourself. The dynamics does expose a clean hook for it (`task_embeddings` → `h_t`), so the design isn't hostile — it's just not there.

---

## 2. Architecture specifics

### 2.1 Tokenizer — MAE-style latent autoencoder, **not** a VAE and **not** a VQ

`grep -E "vq|codebook|quantiz|kl_loss|logvar|reparam|gumbel"` over `dreamer/` and `scripts/`: **zero hits.** The bottleneck is deterministic and continuous:

```python
# dreamer/models.py:820-822
# Project latent tokens to bottleneck and tanh
latent_tokens = encoded_tokens[:, :, :self.n_latents]
proj_tokens = nnx.tanh(self.bottleneck_proj(latent_tokens))
```

Mechanism (`models.py:788-825`): patchify → `patch_proj` linear → **MAE mask-and-replace** on patch tokens with per-`(b,t)` drop prob `p ~ U(mae_p_min, mae_p_max)` (`models.py:245-275`) → prepend `n_latents` **learned latent query tokens** (`models.py:769, 810-811`) → block-causal transformer → take the latent slice → tanh bottleneck. The decoder (`models.py:886-918`) up-projects latents, concatenates learned per-patch query tokens, and reads out patches with a zero-init head. This is the MAETok/Perceiver-resampler pattern (the repo's own figure is `maetok-autoencoder-platformer.svg`); MAE masking is the only regulariser on the latent space.

Attention masks are declarative (`dreamer/utils.py:128-185`): `"encoder"` = latents attend to everything, patches only to patches; `"decoder"` = latents to latents, patches to patches+latents.

Losses (`scripts/train_tokenizer.py:61-121`): normalized-pixel MSE (`mse` full-frame, or `mae` masked-region-only) + `0.2 ×` LPIPS(alexnet, via `jaxlpips`), PSNR logged. EMA 0.999.

**Causality:** every 4th layer is a causal time-attention layer with sliding window `context_length-1` (`models.py:566, 817`, `configs/tokenizer.yaml:77,103`); other layers are full attention within a frame. So yes — causal in time, streamable, KV-cacheable.

**Config defaults** (`configs/tokenizer.yaml`, with the OmegaConf resolvers evaluated):

```yaml
encoder: n_latents 512 · d_bottleneck 16 · depth 12 · d_model 128*12=1536 · n_heads 24 · n_kv_heads 3
         patch_size 16 · time_every 4 · time_layer_offset 3 · mae_p_max 0.9 · context_length 16 · qk_norm
decoder: depth 8 · d_model 128*8=1024 · n_heads 16 · n_kv_heads 2 · d_patch 16*16*3=768 · H 368 W 640
train:   B 8 (global) · short_T=long_T=16 · max_steps 10_000 · Muon lr 3e-3 wsd · lpips_weight 0.2
```

My arithmetic on those numbers: **~405M encoder + ~121M decoder ≈ 527M params** — cross-checks against `tokenizer_ckpt: logs/tokenizer-500M/checkpoints` (`configs/dynamics.yaml:20`).

**Compression ratio (Minecraft default):** input frame 368×640×3 = 706,560 values → 512 latents × 16 dims = **8,192 values, ≈ 86×**. Per-frame only — there is **no temporal compression** (latents are one set per input frame). Latent count (512) is less than patch count (920), so it is a learned resampling, not a grid downsample.

### 2.2 Dynamics — flow matching with shortcut/self-consistency distillation (not autoregressive-discrete)

Rectified-flow interpolation, **x-prediction** (predicts clean latent, not velocity):

```python
# dreamer/training.py:380-389
z0 = jax.random.normal(key_noise, latents.shape, ...)
z0 = apply_ot_coupling(z0, latents, key_ot, ot_cfg=ot_cfg)
z_tilde = (1.0 - sigma_full[...,None,None]) * z0 + sigma_full[...,None,None] * latents
z_pred_full, (h_states, _) = dynamics_model(actions, step_idx_full, sigma_idx_full, z_tilde, ...)
```

- Output head `flow_x_head`, zero-init (`models.py:1223-1229`).
- Loss weighting `v_space` = `1/max(1-σ,1e-3)²` (`training.py:129-131`) — the algebraic equivalent of a velocity-space loss on an x-space prediction; `configs/dynamics.yaml:171`.
- **Shortcut/bootstrap:** the model is conditioned on a *step size* as well as a noise level and self-distilled so one big step ≈ two half-steps. Two stop-grad half-steps are taken **by the EMA model** (`bootstrap_model=dynamics_ema`, `train_dynamics.py:145`; `training.py:421-459`), target velocity averaged and clipped to ±4, compared in x-space (`training.py:244-287`). Gated by `bootstrap_start: 100_000`, `bootstrap_fraction: 0.25`.
- **Minibatch optimal-transport coupling** of noise↔data pairs via `ott-jax` Sinkhorn, barycentric pairing, at whole-sequence granularity (`training.py:135-191`, `configs/dynamics.yaml:146-167`).
- Block-causal masking so short clips can be packed into long sequences with independent causal chunks (`train_dynamics.py:116-128`), plus an `image_fraction` that makes some rows attend to themselves only (identity time mask).

**Conditioning injection.** Both σ and step-size are sinusoidally embedded and concatenated into **one "shortcut token" per timestep**:

```python
# dreamer/models.py:1325-1327
step_emb   = self.step_embed(step_indices.astype(jnp.float32))            # (B,T,d/2)
signal_emb = self.signal_embed(tau_indices.astype(jnp.float32)/self.k_max) # (B,T,d/2)
shortcut_token = jnp.concatenate([step_emb, signal_emb], -1)[:, :, None, :]
```

**Action conditioning** (`models.py:1003-1110`) — a *sum* of contributions collapsed into **one action token per timestep**:

- learned base embedding (always), plus
- one `nnx.Embed(2, d_model)` **per binary channel** (27 separate tables for VPT), plus
- one `nnx.Embed(categorical_action_dim, d_model)`, plus
- `nnx.Linear(continuous_action_dim, d_model)` ← **the continuous path already exists**.

The space mask puts the action token at hierarchy level 0 so it attends only to itself while spatial/register tokens attend to spatial+action (`utils.py:161-178`) — one-way action→state information flow. Actions are **shifted right by one with a no-op prepended** (`actions.py:54-67`, called at `train_dynamics.py:274`), so the token at time *t* carries *a_{t-1}*, i.e. the action that produced frame *t*. Get this wrong in a physics port and your control is off by one step.

**Backbone.** The same `BlockCausalTransformer`: alternating space-attention layers and causal time-attention layers (`time_every: 4`), GQA, QK-RMSNorm, SwiGLU MLP (ratio 4), RMSNorm pre-norm, `nnx.remat` on both attention and MLP (activation checkpointing — `models.py:499, 542, 618`).

Token layout per timestep (`models.py:1231-1247`): `[action ×1][shortcut ×1][spatial ×(n_latents/packing_factor)][register ×n_register]` (+ optional agent tokens). Defaults → **1+1+256+32 = 290 tokens/timestep**; at `long_T=256` that's **74,240 tokens per sequence**.

**Positional encoding caveat, relevant to you:** RoPE is applied unconditionally inside `GroupedQueryAttention` over whatever the second axis is (`models.py:412-414`). In `SpaceSelfAttention` the tensor is reshaped `B T S D -> (B T) S D` (`models.py:497`), so the *spatial* layers get a **1-D RoPE over the raster-flattened token index** — vertical neighbours in a 2-D grid are `W/patch` positions apart in RoPE phase. There is a `2d-rope` dev branch on the remote, which suggests the authors know. For a 2-D fluid field this is a real, if survivable, inductive-bias defect.

**Config defaults** (`configs/dynamics.yaml`):

```yaml
d_bottleneck 16 · depth 30 · d_model 64*30=1920 · n_heads 30 · n_kv_heads 3
packing_factor 2 · n_register 32 · mlp_ratio 4 · k_max 256 · context_length min(192,long_T)=192
B 8 (global) · short_T 64 · long_T 256 · long_ratio 0.1 · num_workers 16
max_steps 200_000 · bootstrap_start 100_000 · bootstrap_fraction 0.25 · image_fraction 0.0
Muon lr 3e-4 wsd (warmup 5%, decay 10%) · ema 0.999 · ot.enabled true · loss_weighting v_space
```

My arithmetic: **≈1.57B params**, matching the blog's *"At 1.6B parameters, the model state — parameters, gradients, optimizer state, and EMA — took around 24 GiB."*

**Sampling** (`dreamer/generation.py`): τ-ladder with precomputed `beta_values = (1-τ_{s+1})/(1-τ_s)` (`:64`), applied as `latent ← β·latent + (1-β)·x̂` (`:179`). Few-step = `DenoiseSchedule.init(4, k_max=256)`; the quality reference is `k_max` steps (`training.py:522-527`; `eval_fvd.py:97` `num_steps = 4 if use_shortcut else k_max`). During AR rollout, already-generated context is **re-noised to τ_ctx≈0.9** before caching (`generation.py:66-78, 203`) — diffusion-forcing style. There is a candid `# FIXME` at `generation.py:325` noting the prefill uses `step_idx=emax`, a ladder that bootstrap training excludes.

---

## 3. Data pipeline, and the cost of a new modality

### 3.1 Required input format

Three formats, all ArrayRecord shards named contiguously `shard-00000.array_record`. Schema is defined in **`dreamer/data/README.md:23-58`** (prose) and enforced by the readers in **`dreamer/data/transforms.py`**:

| Path | Record | Reader |
|---|---|---|
| Minecraft VPT (raw) | pickled `{"video": mp4_bytes, "video_shape": (T,H,W,C), "actions": [VPT action dicts], "source": str}` | `transforms.py:290-344`, decoded with `decord` |
| CoinRun (raw) | pickled `{"raw_video": uint8 bytes, "sequence_length": int, "actions": …, "rewards": …}` | `transforms.py:162-227` |
| Latent (what dynamics actually trains on) | msgpack `{"latents": (T, n_latents, d_bottleneck), "actions": {"binary","categorical","continuous"}, "source": …}` | `transforms.py:351-384` + `data/serialization.py` |

Dispatch: `dreamer/data/data.py:107-146`; path construction `dreamer/data/path_utils.py:51-78`; length filtering `transforms.py:43-109`. Batch packing / short-vs-long alternating iterator: `data.py:187-288`. Config surface: `dreamer/configs.py:26-67` + `configs/dataset/*.yaml`.

Note the dataclasses in `dreamer/configs.py` are **not registered with Hydra's ConfigStore** (grep: no `ConfigStore`, no `_target_`) — they are type hints/documentation only. The live config is an unvalidated `DictConfig` from YAML.

### 3.2 Is the action space Minecraft-specific?

**The model is already continuous-capable; the trainer is not.** `Actions.continuous` (`actions.py:21-23`) and `ActionEncoder.continuous_proj` (`models.py:1057-1066`) are fully wired, `configs.py:48` has `continuous_action_dim`, and even the VPT parser has a continuous mouse mode (`actions.py:152-160`). But:

```python
# scripts/train_dynamics.py:194-195
assert cfg.dataset.num_binary_actions == NUM_BINARY_ACTIONS      # == 27
assert cfg.dataset.categorical_action_dim == NUM_CAMERA_CLASSES  # == 121
```

Two hard asserts pinning the VPT action space. Note `configs/dataset/coinrun.yaml` (0 binary, 16 categorical) **cannot satisfy these** — i.e. the repo's own non-Minecraft config cannot train a dynamics model at HEAD. Deleting the asserts is a 2-line fix, but their presence is the tell: only one path has been run.

### 3.3 Concrete port: sequences of 64×64 or 128×128 float fields + low-dim continuous action

Every file you must touch:

1. **Writer** — new script modelled on `dreamer/data/generate_coinrun_dataset.py`, using `dreamer/data/shard_writer.py`. (Do not copy the CoinRun script literally: it calls `ShardWriter(..., serialization_format="pickle")` at `:110-114`, a kwarg `ShardWriter.__init__` does not accept (`shard_writer.py:23-27`) → `TypeError`. And `ShardWriter` always writes msgpack while `ProcessEpisodeAndSlice` reads `pickle.loads` (`transforms.py:172`) → format mismatch. **The CoinRun generator is broken at HEAD.**)
2. **Reader/transform** — clone `ProcessEpisodeAndSlice` (`transforms.py:116-227`); replace the uint8 reinterpret at `:181-182` (`np.frombuffer(..., dtype=np.uint8)`) with float32, and drop MP4/decord entirely.
3. **Dispatch** — add a branch in `data.py:107-146`, extend the `Literal` in `path_utils.py:51-78`, add a `format_hint` in `transforms.py:80-99`.
4. **Channel count** — `dreamer/models.py:754` hardcodes RGB in the encoder: `nnx.Linear(cfg.patch_size * cfg.patch_size * 3, cfg.d_model, ...)`. The *decoder* already reads `d_patch` from config (`configs/tokenizer.yaml:159` = `patch²·C`), so encoder and decoder disagree for `C≠3`. One-line fix, but it means `C≠3` has never been run.
5. **Value scaling** — `dreamer/utils.py:209` (`videos.astype(float32)/255`) and `:238` (`*255`). Physical units get silently rescaled. Also uint8 clipping at `sampler.py:77,92,93`, `generation.py:266`, `training.py:735`.
6. **Perceptual/pixel eval** — set `lpips_weight: 0.0` (config comment at `tokenizer.yaml:254` confirms this avoids loading it); LPIPS assumes 3-channel [-1,1] (`train_tokenizer.py:73-86`), PSNR assumes [0,1] (`training.py:197-214`).
7. **Actions** — delete `train_dynamics.py:194-195`; set `continuous_action_dim: <k>`, `num_binary_actions: 0`, `categorical_action_dim: 0`. Write `{"binary": None, "categorical": None, "continuous": arr}` — all three keys are mandatory (`Actions.from_dict`, `actions.py:34-37`, raises `KeyError`). `shift_actions` works unchanged for the continuous-only case.
8. **Eval** — the whole FVD stack (`dreamer/fvd/*`, `scripts/eval_fvd.py`) is I3D/3-channel/MP4-specific and meaningless for scalar fields; you'd write your own metric (spectral energy, vorticity error, conserved quantities). `run_evaluation` (`training.py:486-640`) writes libx264 MP4 grids and hardcodes 5 columns; disable via `write_video_every: 0` (already the default) or rewrite.
9. **Tokenizer requirement** — `train_dynamics.py:198` loads `TokenizerCheckpointBundle.from_pretrained(cfg.tokenizer_ckpt, ...)` **unconditionally**, even for pre-tokenized latent data ("so dynamics checkpoints are self-contained"). For a 64×64×1 field (4,096 values/frame) an 86× tokenizer is probably pointless — you'd want to feed patch embeddings straight to the dynamics, which means editing `train_dynamics.py`, `training.run_evaluation`, and `sampler.sample_video`.

**Estimate:** ~300-600 lines of edits across ~10 files, in a codebase with **zero tests** to tell you when a subtle change (normalization, action shift, mask) silently degrades quality rather than crashing. Diffusion/flow bugs are famously silent — the repo's own blog post says exactly this: *"most stability problems happen despite the loss going down!"*

Good news: nothing about the *modelling* forbids your use case. Sequence-of-2D-tensors + one action token per step is precisely the interface. It's the plumbing that's welded to RGB Minecraft.

---

## 4. Compute requirements and practicality

**Stated requirements** (README:78-94): Python 3.11, `uv`, **CUDA-12 JAX**. `pyproject.toml:16` pins `jax[cuda12]` with a cuSPARSE pin for CUDA 12.8; `optax` is installed **from git master** (`pyproject.toml:42`) — a reproducibility hazard.

**No stated GPU count, training time, or dataset size in the README.** From the code and the in-repo blog post (`site/article/article.html` — author claims, not code-verified):

- Development on **B200s**; ~**400 B200-hours per run** for the Muon-vs-LaProp comparison; **57-58% MFU**; 256 frames/GPU to stay compute-bound.
- **1.6B params → ~24 GiB of model state** (params + grads + optimizer + EMA).
- *"Even with a batch size of one video sequence per GPU, we still needed activation checkpointing to fit training in memory."*
- They tried DP/FSDP/TP/SP and **shipped plain data parallelism** — FSDP added communication without benefit.
- Dataset scale is implicit: they pre-tokenized *"the entire dataset"* of VPT; `index_max: 1500` raw shards → `89` latent shards in the example (`minecraft_vpt_latent.yaml:20`).

**Sharding/mesh** (`dreamer/parallel.py:79-112`): `jax.make_mesh` with four strategies — `data`, `fsdp`, `tp`, `sp` — driven by a `MeshRules` dataclass mapping `embed/mlp/attn/data/seq` axes onto `nnx.with_partitioning` in every layer. Multi-host init auto-detects Slurm/OpenMPI/`JAX_COORDINATOR_ADDRESS` (`parallel.py:28-76`). Caveats: `use_seq_parallel` raises `NotImplementedError` in GQA (`models.py:358-359`); `train_tokenizer.py:196` hardcodes `build_parallel("data")` and ignores the config (documented at `common.yaml:80-82`).

**Small/debug configs:** `configs/dataset/coinrun.yaml` is the "single GPU" path per the blog (64×64, patch 8, B 512, T 64) — but see §3.3: its generator crashes and its action dims fail the dynamics asserts. There is **no small *model* config**; you'd override `depth`/`d_model` on the Hydra CLI. `configs/tokenizer_finetune.yaml` and `configs/dynamics_finetune.yaml` are stage-2 configs, not debug ones (and `dynamics_finetune.yaml:15`'s `long_batch_ratio` is a dead key — grep finds no reader).

**Single A100/H100 on Modal?**

- **At default configs: no.** 1.6B dynamics (24 GiB state) plus 74k-token sequences with 30 layers won't train usefully on one 80 GB card even with the built-in `remat`. Multi-node isn't *required* by the code (DP works at any device count), but the defaults presume a large B200 box.
- **At your scale: comfortably yes.** 64×64×1 with `patch_size 8` → 64 patches/frame; a `d_model 512 / depth 12` dynamics ≈ 45M params, with `n_latents 64 / packing 2 / n_register 8` → 42 tokens/timestep → 2,688 tokens at T=64. That's a small-transformer workload. The architecture scales down cleanly; `configs.py` dataclass defaults (`d_model 512/768`, `k_max 8`) show it was developed at that scale. **Compute is not the blocker here — the licence and the plumbing are.**

---

## 5. Maturity and risk

| Signal | Value |
|---|---|
| `main` commits | **8** (squashed publish `f7d3125` on 2026-07-24 → `797e41f` 2026-07-26; all 7 follow-ups are README/licence/blog) |
| Repo age | Created **2026-07-20**, last push **2026-07-26** — one week old |
| Remote branches | **116** (dev branches pushed: `2d-rope`, `agent-fading-dynamics`, `bugfix/kvcache`, `barebones`, `delete-code`, …) — real history exists but was not published as history |
| Contributors | **4** (diego-marti 4, Francesco215 2, Dere-Wah 1, edwhu 1) |
| Stars / forks | 288 / 23 |
| Issues | **1 open** (#7 *"Tokenization silently drops the final partial batch"* — real: `drop_remainder=True`, `tokenize_minecraft_dataset.py:100`). 5 merged PRs, **all** website/licence; zero code PRs. |
| **Tests** | **None.** No pytest, no `tests/`, no `*_test.py`. The only CI (`.github/workflows/deploy-pages.yml`) builds the Next.js site. |
| **Licence** | **All rights reserved, no permission granted.** `LICENSE`; GitHub `NOASSERTION`. Says *"provisional… expected to be replaced by a formal license in a future release."* |
| **Pretrained checkpoints** | **None.** No HF/GCS/S3 URL anywhere. The live demo hits Reactor's hosted API (`site/lib/open-dreamer/config.ts:12` → `https://api.reactor.inc`). The linked `reactor-team/open-dreamer` "inference repo" is 3.6 MB (metadata only — I did not clone it), so weights are not there either. |
| FVD self-contained? | **Yes.** `dreamer/fvd/i3d_pretrained_400.npz` (50 MB) is committed and `fvd.py` is a pure-JAX I3D with no network fetch. It is also 3-channel-video-only, so worthless for your modality. |

**Additional rot found by reading:**

- `generate_coinrun_dataset.py:110-114` — `ShardWriter(serialization_format="pickle")`, unsupported kwarg → `TypeError`; plus msgpack-write/pickle-read mismatch. **CoinRun data generation is broken.**
- `train_dynamics.py:194-195` — VPT action asserts block the CoinRun dynamics path.
- `run_x0_visualization` (`training.py:694`) and `run_attention_visualization` (`training.py:773`) are **dead code** — never called — yet `run_evaluation`'s docstring (`training.py:508`) claims *"Also runs x0 and attention visualizations."*
- `configs/tokenizer.yaml:191-193` documents `freeze_encoder` as a "reserved switch" that the training step doesn't read.
- `dynamics_finetune.yaml:15` `long_batch_ratio` — dead key.
- No config schema validation (no ConfigStore), so a typo in YAML surfaces as a runtime `AttributeError` deep in a training loop.

### Honest verdict: adopt vs. write your own

**Write your own, and read this one as a paper appendix.**

Against a bespoke model for a low-dimensional physics problem — say a patch-embedding encoder plus a 6-12 layer causal transformer (or a GRU/SSM latent-dynamics model) with flow-matching or plain next-step MSE, action injected as one token or a FiLM conditioning:

- **Bespoke cost:** ~400-800 lines you fully understand, unit-testable against analytic solutions (a diffusing Gaussian, a linear advection, a decaying Taylor-Green vortex), one training script, one eval metric that means something physically.
- **Adopt cost:** ~300-600 lines of edits inside 8,000 LOC you didn't write, no tests, one working modality, an all-rights-reserved licence, a 1-D-RoPE-over-raster spatial prior, plus a two-stage tokenizer pipeline that a 64×64 field almost certainly doesn't need — and you still write the eval and the entire control layer yourself.

The asymmetry is stark: you'd inherit almost all of the complexity (built for 360×640 RGB at 1.6B params on B200s) and almost none of the benefit (no weights, no agent, no metric that transfers).

**What to actually lift, once licensing is resolved** (ask the authors — they are responsive and this is clearly meant to be open eventually):

1. **Shortcut forcing** — `dreamer/training.py:294-479`. ~190 self-contained lines; gets you 4-step sampling instead of 256-step. This is the single highest-value idea in the repo for a real-time or many-rollout physics surrogate.
2. **x-prediction + v-space loss weighting** — `training.py:120-132`, and the algebraic cancellation of the unstable `1/(1-σ)` in the bootstrap target (`training.py:274-287`). Small, sharp, non-obvious.
3. **τ-ladder sampler + context re-noising** — `generation.py:45-219`.
4. **The engineering blog** (`site/article/article.html`) — read it end to end before you write your own trainer. The stability section (EMA is mandatory for diffusion inference; Muon ≫ LaProp for stability; exact bf16/fp32 boundaries — fp32 for norms, sinusoidal embeddings, and the flow output head; attention-entropy collapse as a diagnostic invisible in the loss) is worth more than the code.

**Things I could not verify** (stated rather than inferred): I could not execute anything — no JAX/CUDA available, so all findings are static reads; parameter counts are my arithmetic over the resolved YAML (cross-checked against `tokenizer-500M` in `dynamics.yaml:20` and "1.6B" in the article), not a runtime `count_parameters_by_component` call. All hardware/MFU/training-hour figures are author claims in the blog post, unverifiable from source. I did not clone `reactor-team/open-dreamer` (metadata only). And with no released weights, there is no way to confirm the published code reproduces the demo's quality.

**Local clone for further inspection:** `/private/tmp/claude-501/-Users-raj-Downloads-Vizuara/0ddf2ea6-71c5-4ee7-94da-c1eb7d68fb0d/scratchpad/open-dreamer` (full history fetched, 116 branches available via `git branch -r`).