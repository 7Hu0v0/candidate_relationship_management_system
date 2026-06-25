# Large-Model Talent Company Taxonomy

Use this as a replaceable default taxonomy until a project-specific `sourcing_from_paper` definition is available.

## Tier 1: Foundation Model Labs and Frontier Teams

- OpenAI: GPT, ChatGPT, Codex, Sora, reasoning, multimodal, agents.
- Anthropic: Claude, Constitutional AI, safety, post-training.
- Google DeepMind / Google Research: Gemini, DeepMind, TPU, JAX, inference, robotics.
- Meta AI: Llama, PyTorch, FAIR, GenAI.
- xAI: Grok, frontier model training and inference.
- Mistral AI: open-weight and commercial LLMs.
- Cohere: enterprise LLMs, RAG, command models.

## China Foundation Model and AI Product Companies

- DeepSeek: DeepSeek-V series, R series, efficient training/inference.
- Moonshot AI / Kimi: long-context LLMs and AI assistant products.
- Zhipu AI / GLM: GLM models, agents, enterprise deployment.
- MiniMax: multimodal, voice, agent/product models.
- Baichuan: foundation models and AI applications.
- StepFun: Step models, multimodal/foundation models.
- 01.AI: Yi models, open models, applications.
- Alibaba / Qwen / Tongyi: Qwen models, ModelScope, cloud AI.
- Tencent / Hunyuan: Hunyuan models, WeChat/QQ/cloud AI applications.
- ByteDance / Seed / Doubao: Seed models, Doubao, recommendation and AI product infra.
- Baidu / ERNIE: Wenxin/ERNIE, PaddlePaddle, search plus LLM products.
- Huawei / Pangu / MindSpore: Pangu models, Ascend, enterprise AI.

## Infrastructure and Systems Counterparts

- NVIDIA: GPU systems, CUDA, TensorRT, Megatron, inference optimization.
- AMD: GPU systems and ROCm.
- Intel / Habana: accelerators, inference, compilers.
- AWS, Azure, Google Cloud, Alibaba Cloud, Tencent Cloud, Huawei Cloud: cloud AI infrastructure, serving platforms, ML platforms.
- Databricks, Snowflake, MongoDB, Elastic: data/AI platforms with enterprise AI workloads.

## High-Signal Role Keywords

- Model: pretraining, post-training, SFT, RLHF, DPO, reward model, alignment, reasoning, multimodal, diffusion, speech, video.
- Infra: distributed training, GPU, CUDA, NCCL, JAX, XLA, PyTorch, Megatron, DeepSpeed, vLLM, TensorRT-LLM, Triton, serving, inference, quantization, KV cache.
- Data/eval: data engine, synthetic data, eval, benchmark, annotation, safety, red teaming, retrieval, RAG.
- Product/agent: agent, tool use, browser, coding assistant, workflow automation, copilots, AI search.

## Matching Guidance

- Prefer exact company/product/lab mentions in remarks and messages.
- Accept common aliases: `Qwen` for Alibaba, `Hunyuan` for Tencent, `Seed` or `Doubao` for ByteDance, `GLM` for Zhipu, `Kimi` for Moonshot, `ERNIE` for Baidu.
- If only a broad company appears, tag `company_match` but keep `llm_relevance` at `medium` unless role keywords also appear.
- If only role keywords appear with no company, leave `company` as `unknown` and preserve role signals.
