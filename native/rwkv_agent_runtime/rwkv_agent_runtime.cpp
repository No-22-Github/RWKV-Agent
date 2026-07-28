#include "rwkv_agent_runtime.h"

#include "MLXModelFFI.h"
#include "rwkv_pth_model.h"
#include "sampler.h"
#include "tensor.h"
#include "tokenizer.h"

#include <algorithm>
#include <atomic>
#include <chrono>
#include <cctype>
#include <condition_variable>
#include <cstdint>
#include <cstring>
#include <deque>
#include <filesystem>
#include <limits>
#include <map>
#include <memory>
#include <mutex>
#include <new>
#include <string>
#include <thread>
#include <unordered_set>
#include <utility>
#include <vector>

using rwkvmobile::NucleusSampler;
using rwkvmobile::Tensor1D;
using rwkvmobile::TensorDType;
using rwkvmobile::trie_tokenizer;

namespace {

constexpr uint32_t kMaxMLXSlots = 16;
constexpr uint32_t kDefaultActiveBatch = 4;
constexpr uint32_t kDefaultQueueCapacity = 64;
constexpr size_t kMaxStateBytes = size_t(1) << 30;
constexpr char kStateMagic[8] = {'R', 'W', 'A', 'S', 'T', 'A', 'T', 'E'};
constexpr uint32_t kStateVersion = 1;
constexpr const char *kCodecID = "mlx-fp16-cache-logits";

bool is_pth_path(const char *path) {
    if (path == nullptr) return false;
    std::string extension = std::filesystem::path(path).extension().string();
    std::transform(
        extension.begin(),
        extension.end(),
        extension.begin(),
        [](unsigned char ch) { return static_cast<char>(std::tolower(ch)); });
    return extension == ".pth";
}

uint64_t prefix_hash(const std::vector<int32_t> &tokens) {
    uint64_t hash = 1469598103934665603ull;
    for (int32_t token : tokens) {
        uint32_t value = static_cast<uint32_t>(token);
        for (int i = 0; i < 4; ++i) {
            hash ^= static_cast<uint8_t>(value >> (i * 8));
            hash *= 1099511628211ull;
        }
    }
    return hash;
}

bool is_prefix(const std::vector<int32_t> &prefix, const std::vector<int32_t> &value) {
    return prefix.size() <= value.size() &&
        std::equal(prefix.begin(), prefix.end(), value.begin());
}

template <typename T>
bool struct_valid(const T *value) {
    return value != nullptr && value->struct_size >= sizeof(T);
}

void append_u32(std::vector<uint8_t> &out, uint32_t value) {
    for (int i = 0; i < 4; ++i) out.push_back(static_cast<uint8_t>(value >> (8 * i)));
}

void append_u64(std::vector<uint8_t> &out, uint64_t value) {
    for (int i = 0; i < 8; ++i) out.push_back(static_cast<uint8_t>(value >> (8 * i)));
}

bool read_u32(const std::vector<uint8_t> &in, size_t &offset, uint32_t &value) {
    if (offset > in.size() || in.size() - offset < 4) return false;
    value = 0;
    for (int i = 0; i < 4; ++i) value |= uint32_t(in[offset++]) << (8 * i);
    return true;
}

bool read_u64(const std::vector<uint8_t> &in, size_t &offset, uint64_t &value) {
    if (offset > in.size() || in.size() - offset < 8) return false;
    value = 0;
    for (int i = 0; i < 8; ++i) value |= uint64_t(in[offset++]) << (8 * i);
    return true;
}

struct ErrorState {
    mutable std::mutex mutex;
    std::string message;

    void set(std::string value) {
        std::lock_guard<std::mutex> lock(mutex);
        message = std::move(value);
    }

    const char *get() const {
        thread_local std::string copy;
        std::lock_guard<std::mutex> lock(mutex);
        copy = message;
        return copy.c_str();
    }
};

struct GenerateJob;

} // namespace

struct rwa_runtime {
    ErrorState error;
    uint32_t max_active_batch = kDefaultActiveBatch;
    uint32_t queue_capacity = kDefaultQueueCapacity;
    std::mutex mutex;
    bool closed = false;
    std::unordered_set<rwa_model *> models;
};

struct rwa_model {
    ErrorState error;
    rwa_runtime *runtime = nullptr;
    void *mlx = nullptr;
    std::unique_ptr<trie_tokenizer> tokenizer;
    int32_t vocab_size = 0;
    int32_t hidden_size = 0;
    int32_t head_dim = 0;
    int32_t layers = 0;
    int32_t cache_size = 0;
    uint32_t max_active_batch = kDefaultActiveBatch;
    uint32_t queue_capacity = kDefaultQueueCapacity;

    std::mutex mutex;
    bool closed = false;
    std::unordered_set<rwa_session *> sessions;

    std::mutex compute_mutex;
    std::atomic<uint32_t> active_count{0};
    std::atomic<uint32_t> max_observed_batch{0};

    std::mutex queue_mutex;
    std::condition_variable queue_cv;
    std::deque<std::shared_ptr<GenerateJob>> pending;
    bool scheduler_stopping = false;
    std::thread scheduler;
};

struct rwa_session {
    ErrorState error;
    rwa_model *model = nullptr;
    mutable std::mutex operation_mutex;
    mutable std::mutex state_mutex;
    bool closed = false;
    std::atomic<uint32_t> status{RWA_SESSION_CLEAN};
    std::atomic<bool> cancel_requested{false};
    std::atomic<uint64_t> active_request_id{0};
    std::vector<uint8_t> cache;
    std::vector<float> logits;
    std::vector<int32_t> prefix_tokens;
    std::string dirty_reason;
};

namespace {

struct GenerateJob {
    rwa_session *session = nullptr;
    rwa_generate_options options{};
    std::vector<int32_t> input_tokens;
    rwa_stream_callback callback = nullptr;
    void *user_data = nullptr;
    rwa_generate_result result{};
    rwa_status result_status = RWA_OK;
    std::string callback_error;

    std::vector<int32_t> output_tokens;
    std::string output;
    std::vector<float> logits;
    std::map<int, float> occurrences;
    std::unique_ptr<NucleusSampler> sampler;
    int32_t sampled_token = 0;
    size_t physical_slot = 0;
    uint64_t prefill_tokens = 0;
    std::chrono::steady_clock::time_point prefill_start;
    std::chrono::steady_clock::time_point decode_start;

    std::mutex mutex;
    std::condition_variable cv;
    bool done = false;
};

std::string mlx_error(const std::string &prefix) {
    const char *detail = mlx_last_error_message();
    if (detail == nullptr || *detail == '\0') return prefix;
    return prefix + ": " + detail;
}

rwa_status cache_read_slot(rwa_model *model, int32_t slot, std::vector<uint8_t> &out) {
    out.resize(static_cast<size_t>(model->cache_size));
    int32_t got = mlx_cache_read_slot(
        model->mlx, slot, out.data(), model->cache_size);
    if (got != model->cache_size) {
        model->error.set(mlx_error("read MLX State slot"));
        return RWA_BACKEND_FAILURE;
    }
    return RWA_OK;
}

rwa_status cache_write_slot(
    rwa_model *model,
    int32_t slot,
    const std::vector<uint8_t> &cache) {
    if (cache.size() != static_cast<size_t>(model->cache_size)) {
        model->error.set("MLX State cache size mismatch");
        return RWA_INCOMPATIBLE_STATE;
    }
    if (mlx_cache_write_slot(
            model->mlx, slot, cache.data(), model->cache_size) != 0) {
        model->error.set(mlx_error("write MLX State slot"));
        return RWA_BACKEND_FAILURE;
    }
    return RWA_OK;
}

rwa_status cache_zero_slot(rwa_model *model, int32_t slot) {
    if (mlx_cache_zero_slot(model->mlx, slot) != 0) {
        model->error.set(mlx_error("zero MLX State slot"));
        return RWA_BACKEND_FAILURE;
    }
    return RWA_OK;
}

struct ActiveSlotsGuard {
    rwa_model *model;
    std::vector<std::vector<uint8_t>> saved;
    bool restore = false;
    rwa_status status = RWA_OK;

    explicit ActiveSlotsGuard(rwa_model *m) : model(m) {
        const uint32_t active =
            model->active_count.load(std::memory_order_acquire);
        saved.resize(active);
        for (uint32_t slot = 0; slot < active; ++slot) {
            status = cache_read_slot(
                model, static_cast<int32_t>(slot), saved[slot]);
            if (status != RWA_OK) {
                saved.clear();
                return;
            }
        }
        restore = !saved.empty();
    }

    ~ActiveSlotsGuard() {
        if (restore) (void)restore_now();
    }

    rwa_status restore_now() {
        if (!restore) return status;
        restore = false;
        for (size_t slot = 0; slot < saved.size(); ++slot) {
            status = cache_write_slot(
                model, static_cast<int32_t>(slot), saved[slot]);
            if (status != RWA_OK) return status;
        }
        return RWA_OK;
    }
};

rwa_status eval_tokens_slot_zero(
    rwa_model *model,
    rwa_session *session,
    const std::vector<int32_t> &target,
    size_t start,
    rwa_prefill_progress_callback progress,
    void *user_data,
    uint64_t *evaluated) {
    if (target.empty()) {
        std::lock_guard<std::mutex> state_lock(session->state_mutex);
        session->cache.clear();
        session->logits.clear();
        session->prefix_tokens.clear();
        if (evaluated) *evaluated = 0;
        return RWA_OK;
    }

    ActiveSlotsGuard slots_guard(model);
    if (slots_guard.status != RWA_OK) return slots_guard.status;
    std::vector<uint8_t> cache;
    {
        std::lock_guard<std::mutex> state_lock(session->state_mutex);
        cache = session->cache;
    }
    rwa_status status = cache.empty()
        ? cache_zero_slot(model, 0)
        : cache_write_slot(model, 0, cache);
    if (status != RWA_OK) return status;

    std::vector<float> logits(static_cast<size_t>(model->vocab_size));
    constexpr size_t kChunk = 2048;
    uint64_t completed = 0;
    const uint64_t total = static_cast<uint64_t>(target.size() - start);
    for (size_t offset = start; offset < target.size();) {
        if (session->cancel_requested.load(std::memory_order_acquire)) {
            return RWA_CANCELLED;
        }
        size_t count = std::min(kChunk, target.size() - offset);
        if (mlx_model_eval(
                model->mlx,
                target.data() + offset,
                static_cast<int32_t>(count),
                logits.data()) != 0) {
            model->error.set(mlx_error("MLX prefill"));
            return RWA_BACKEND_FAILURE;
        }
        offset += count;
        completed += count;
        if (progress && progress(completed, total, user_data) != 0) {
            session->cancel_requested.store(true, std::memory_order_release);
            return RWA_CANCELLED;
        }
    }
    status = cache_read_slot(model, 0, cache);
    if (status != RWA_OK) return status;
    {
        std::lock_guard<std::mutex> state_lock(session->state_mutex);
        session->cache = std::move(cache);
        session->logits = std::move(logits);
        session->prefix_tokens = target;
    }
    status = slots_guard.restore_now();
    if (status != RWA_OK) return status;
    if (evaluated) *evaluated = completed;
    return RWA_OK;
}

rwa_status sync_prefix_locked(
    rwa_session *session,
    const std::vector<int32_t> &target,
    rwa_prefill_progress_callback progress,
    void *user_data,
    uint64_t *evaluated) {
    rwa_model *model = session->model;
    std::vector<int32_t> current;
    bool dirty = session->status.load(std::memory_order_acquire) == RWA_SESSION_DIRTY;
    {
        std::lock_guard<std::mutex> state_lock(session->state_mutex);
        current = session->prefix_tokens;
    }
    size_t start = (!dirty && is_prefix(current, target)) ? current.size() : 0;
    if (start == target.size()) {
        if (evaluated) *evaluated = 0;
        session->status.store(RWA_SESSION_CLEAN, std::memory_order_release);
        return RWA_OK;
    }
    if (start == 0) {
        std::lock_guard<std::mutex> state_lock(session->state_mutex);
        session->cache.clear();
        session->logits.clear();
        session->prefix_tokens.clear();
    }
    session->status.store(RWA_SESSION_REBUILDING, std::memory_order_release);
    rwa_status status;
    {
        std::lock_guard<std::mutex> compute_lock(model->compute_mutex);
        status = eval_tokens_slot_zero(
            model, session, target, start, progress, user_data, evaluated);
    }
    if (status == RWA_OK) {
        std::lock_guard<std::mutex> state_lock(session->state_mutex);
        session->dirty_reason.clear();
        session->status.store(RWA_SESSION_CLEAN, std::memory_order_release);
    } else {
        std::lock_guard<std::mutex> state_lock(session->state_mutex);
        session->dirty_reason =
            status == RWA_CANCELLED ? "prefix rebuild cancelled" : "prefix rebuild failed";
        session->status.store(RWA_SESSION_DIRTY, std::memory_order_release);
    }
    return status;
}

bool is_stop_sequence(const std::vector<int32_t> &tokens, int32_t next) {
    static const std::vector<std::vector<int32_t>> stops = {
        {261}, {28329, 11}, {28324, 11}, {28331, 11}, {5585}, {11, 24281, 59}
    };
    for (const auto &stop : stops) {
        if (tokens.size() + 1 < stop.size()) continue;
        size_t existing = stop.size() - 1;
        if (next != stop.back()) continue;
        if (existing == 0 ||
            std::equal(stop.begin(), stop.end() - 1, tokens.end() - existing)) {
            return true;
        }
    }
    return next == 0;
}

void set_session_dirty(rwa_session *session, const std::string &reason) {
    std::lock_guard<std::mutex> state_lock(session->state_mutex);
    session->dirty_reason = reason;
    session->status.store(RWA_SESSION_DIRTY, std::memory_order_release);
}

void complete_job(
    const std::shared_ptr<GenerateJob> &job,
    rwa_status status,
    rwa_finish_reason reason,
    bool clean) {
    job->result_status = status;
    job->result.finish_reason = reason;
    job->result.state_clean = clean ? 1u : 0u;
    job->result.decode_tokens = job->output_tokens.size();
    {
        std::lock_guard<std::mutex> state_lock(job->session->state_mutex);
        job->result.prefix_hash = prefix_hash(job->session->prefix_tokens);
    }
    auto decode_elapsed = std::chrono::duration<double>(
        std::chrono::steady_clock::now() - job->decode_start).count();
    if (!job->output_tokens.empty() && decode_elapsed > 0) {
        job->result.decode_tokens_per_second =
            static_cast<double>(job->output_tokens.size()) / decode_elapsed;
    }
    job->session->active_request_id.store(0, std::memory_order_release);
    if (clean) {
        job->session->status.store(RWA_SESSION_CLEAN, std::memory_order_release);
    }
    if (job->callback) {
        rwa_stream_event event{};
        event.struct_size = sizeof(event);
        event.kind = RWA_STREAM_FINISH;
        event.request_id = job->options.request_id;
        (void)job->callback(&event, job->user_data);
    }
    {
        std::lock_guard<std::mutex> lock(job->mutex);
        job->done = true;
    }
    job->cv.notify_all();
}

rwa_status prepare_job(
    rwa_model *model,
    const std::shared_ptr<GenerateJob> &job) {
    job->prefill_start = std::chrono::steady_clock::now();
    uint64_t evaluated = 0;
    rwa_status status = sync_prefix_locked(
        job->session, job->input_tokens, nullptr, nullptr, &evaluated);
    job->prefill_tokens = evaluated;
    job->result.prefill_tokens = evaluated;
    auto elapsed = std::chrono::duration<double>(
        std::chrono::steady_clock::now() - job->prefill_start).count();
    if (evaluated > 0 && elapsed > 0) {
        job->result.prefill_tokens_per_second = double(evaluated) / elapsed;
    }
    if (status != RWA_OK) return status;

    {
        std::lock_guard<std::mutex> state_lock(job->session->state_mutex);
        job->logits = job->session->logits;
    }
    if (job->logits.size() != static_cast<size_t>(model->vocab_size)) {
        job->session->error.set("generation prefix has no valid next-token logits");
        return RWA_BACKEND_FAILURE;
    }
    job->sampler = std::make_unique<NucleusSampler>();
    if (job->options.has_seed) {
        job->sampler->set_seed(static_cast<int32_t>(job->options.seed));
    }
    job->decode_start = std::chrono::steady_clock::now();
    return RWA_OK;
}

rwa_status place_job(rwa_model *model, GenerateJob &job, size_t slot) {
    std::vector<uint8_t> cache;
    {
        std::lock_guard<std::mutex> state_lock(job.session->state_mutex);
        cache = job.session->cache;
    }
    if (cache.empty()) return RWA_BACKEND_FAILURE;
    rwa_status status = cache_write_slot(model, static_cast<int32_t>(slot), cache);
    if (status == RWA_OK) job.physical_slot = slot;
    return status;
}

void finalize_active_job(
    rwa_model *model,
    const std::shared_ptr<GenerateJob> &job,
    rwa_status status,
    rwa_finish_reason reason) {
    bool clean = status == RWA_OK;
    if (clean) {
        std::vector<uint8_t> cache;
        if (cache_read_slot(
                model, static_cast<int32_t>(job->physical_slot), cache) != RWA_OK) {
            status = RWA_BACKEND_FAILURE;
            reason = RWA_FINISH_ERROR;
            clean = false;
        } else {
            std::lock_guard<std::mutex> state_lock(job->session->state_mutex);
            job->session->cache = std::move(cache);
            job->session->logits = job->logits;
            job->session->prefix_tokens = job->input_tokens;
            job->session->prefix_tokens.insert(
                job->session->prefix_tokens.end(),
                job->output_tokens.begin(),
                job->output_tokens.end());
            job->session->dirty_reason.clear();
        }
    }
    if (!clean) {
        set_session_dirty(
            job->session,
            status == RWA_CANCELLED ? "generation cancelled" : "generation failed");
    }
    complete_job(job, status, reason, clean);
}

void scheduler_main(rwa_model *model) {
    std::vector<std::shared_ptr<GenerateJob>> active;
    for (;;) {
        {
            std::unique_lock<std::mutex> queue_lock(model->queue_mutex);
            if (active.empty() && model->pending.empty() && !model->scheduler_stopping) {
                model->queue_cv.wait(queue_lock, [&] {
                    return model->scheduler_stopping || !model->pending.empty();
                });
            }
            while (!model->pending.empty() &&
                   active.size() < model->max_active_batch) {
                auto job = model->pending.front();
                model->pending.pop_front();
                queue_lock.unlock();

                rwa_status status = prepare_job(model, job);
                if (status == RWA_OK) {
                    std::lock_guard<std::mutex> compute_lock(model->compute_mutex);
                    status = place_job(model, *job, active.size());
                }
                if (status == RWA_OK) {
                    active.push_back(job);
                    model->active_count.store(
                        static_cast<uint32_t>(active.size()),
                        std::memory_order_release);
                } else {
                    set_session_dirty(job->session, "generation prefill failed");
                    complete_job(
                        job,
                        status,
                        status == RWA_CANCELLED ? RWA_FINISH_CANCELLED : RWA_FINISH_ERROR,
                        false);
                }
                queue_lock.lock();
            }
            if (model->scheduler_stopping) {
                while (!model->pending.empty()) {
                    auto job = model->pending.front();
                    model->pending.pop_front();
                    set_session_dirty(job->session, "model closed");
                    complete_job(job, RWA_CLOSED, RWA_FINISH_ERROR, false);
                }
            }
        }

        if (active.empty()) {
            if (model->scheduler_stopping) break;
            continue;
        }

        std::vector<bool> remove(active.size(), false);
        std::vector<rwa_status> statuses(active.size(), RWA_OK);
        std::vector<rwa_finish_reason> reasons(active.size(), RWA_FINISH_STOP);

        for (size_t i = 0; i < active.size(); ++i) {
            auto &job = active[i];
            if (model->scheduler_stopping ||
                job->session->cancel_requested.load(std::memory_order_acquire)) {
                remove[i] = true;
                statuses[i] = model->scheduler_stopping ? RWA_CLOSED : RWA_CANCELLED;
                reasons[i] = model->scheduler_stopping
                    ? RWA_FINISH_ERROR : RWA_FINISH_CANCELLED;
                continue;
            }
            Tensor1D logits = Tensor1D::make(
                job->logits.data(), TensorDType::F32, job->logits.size());
            job->sampler->apply_penalties(
                logits,
                static_cast<size_t>(model->vocab_size),
                job->occurrences,
                {},
                job->options.presence_penalty,
                job->options.frequency_penalty,
                job->options.penalty_decay);
            job->sampled_token = job->sampler->sample(
                logits,
                static_cast<size_t>(model->vocab_size),
                job->options.temperature,
                job->options.top_k,
                job->options.top_p);
            if (is_stop_sequence(job->output_tokens, job->sampled_token)) {
                remove[i] = true;
                reasons[i] = RWA_FINISH_STOP;
                continue;
            }
            if (job->output_tokens.size() >= job->options.max_output_tokens) {
                remove[i] = true;
                reasons[i] = RWA_FINISH_LENGTH;
            }
        }

        {
            std::lock_guard<std::mutex> compute_lock(model->compute_mutex);

            for (size_t i = 0; i < active.size(); ++i) {
                if (remove[i]) {
                    finalize_active_job(model, active[i], statuses[i], reasons[i]);
                }
            }

            std::vector<std::shared_ptr<GenerateJob>> remaining;
            remaining.reserve(active.size());
            std::vector<std::vector<uint8_t>> moved_cache;
            std::vector<size_t> moved_destination;
            for (size_t old = 0; old < active.size(); ++old) {
                if (remove[old]) continue;
                size_t next = remaining.size();
                if (next != old) {
                    moved_cache.emplace_back();
                    if (cache_read_slot(
                            model,
                            static_cast<int32_t>(old),
                            moved_cache.back()) != RWA_OK) {
                        set_session_dirty(active[old]->session, "State slot move failed");
                        complete_job(
                            active[old],
                            RWA_BACKEND_FAILURE,
                            RWA_FINISH_ERROR,
                            false);
                        continue;
                    }
                    moved_destination.push_back(next);
                }
                active[old]->physical_slot = next;
                remaining.push_back(active[old]);
            }
            for (size_t i = 0; i < moved_cache.size(); ++i) {
                (void)cache_write_slot(
                    model,
                    static_cast<int32_t>(moved_destination[i]),
                    moved_cache[i]);
            }
            active.swap(remaining);
            model->active_count.store(
                static_cast<uint32_t>(active.size()),
                std::memory_order_release);

            if (!active.empty()) {
                std::vector<int32_t> ids(active.size());
                std::vector<float> batched_logits(
                    active.size() * static_cast<size_t>(model->vocab_size));
                for (size_t i = 0; i < active.size(); ++i) {
                    ids[i] = active[i]->sampled_token;
                }
                if (mlx_model_eval_batch_tokens(
                        model->mlx,
                        ids.data(),
                        static_cast<int32_t>(ids.size()),
                        batched_logits.data()) != 0) {
                    model->error.set(mlx_error("MLX continuous batch decode"));
                    for (auto &job : active) {
                        set_session_dirty(job->session, "batch decode failed");
                        complete_job(
                            job, RWA_BACKEND_FAILURE, RWA_FINISH_ERROR, false);
                    }
                    active.clear();
                    model->active_count.store(0, std::memory_order_release);
                } else {
                    uint32_t observed = static_cast<uint32_t>(active.size());
                    uint32_t previous =
                        model->max_observed_batch.load(std::memory_order_relaxed);
                    while (observed > previous &&
                           !model->max_observed_batch.compare_exchange_weak(
                               previous,
                               observed,
                               std::memory_order_relaxed)) {
                    }
                    for (size_t i = 0; i < active.size(); ++i) {
                        auto &job = active[i];
                        job->logits.assign(
                            batched_logits.begin() + i * model->vocab_size,
                            batched_logits.begin() + (i + 1) * model->vocab_size);
                        job->output_tokens.push_back(job->sampled_token);
                        job->occurrences[job->sampled_token] += 1.0f;
                        std::string text = model->tokenizer->decode(job->sampled_token);
                        job->output += text;
                        if (job->callback) {
                            rwa_stream_event event{};
                            event.struct_size = sizeof(event);
                            event.kind = RWA_STREAM_TOKEN;
                            event.request_id = job->options.request_id;
                            event.token_id = job->sampled_token;
                            event.text = text.data();
                            event.text_size = text.size();
                            if (job->callback(&event, job->user_data) != 0) {
                                job->session->cancel_requested.store(
                                    true, std::memory_order_release);
                            }
                        }
                    }
                }
            }
        }

        for (size_t i = 0; i < active.size();) {
            auto &job = active[i];
            if (job->output_tokens.size() >= job->options.max_output_tokens) {
                std::lock_guard<std::mutex> compute_lock(model->compute_mutex);
                finalize_active_job(model, job, RWA_OK, RWA_FINISH_LENGTH);
                std::vector<uint8_t> last_cache;
                if (i + 1 < active.size()) {
                    (void)cache_read_slot(
                        model,
                        static_cast<int32_t>(active.size() - 1),
                        last_cache);
                }
                active.erase(active.begin() + i);
                for (size_t slot = i; slot < active.size(); ++slot) {
                    std::vector<uint8_t> cache;
                    (void)cache_read_slot(
                        model, static_cast<int32_t>(slot + 1), cache);
                    (void)cache_write_slot(
                        model, static_cast<int32_t>(slot), cache);
                    active[slot]->physical_slot = slot;
                }
                model->active_count.store(
                    static_cast<uint32_t>(active.size()),
                    std::memory_order_release);
            } else {
                ++i;
            }
        }
    }
}

void close_sessions(rwa_model *model) {
    std::vector<rwa_session *> sessions;
    {
        std::lock_guard<std::mutex> lock(model->mutex);
        sessions.assign(model->sessions.begin(), model->sessions.end());
    }
    for (auto *session : sessions) {
        session->cancel_requested.store(true, std::memory_order_release);
    }
    for (auto *session : sessions) {
        std::lock_guard<std::mutex> operation_lock(session->operation_mutex);
        std::lock_guard<std::mutex> state_lock(session->state_mutex);
        session->closed = true;
        session->model = nullptr;
        session->status.store(RWA_SESSION_CLOSED, std::memory_order_release);
    }
    {
        std::lock_guard<std::mutex> lock(model->mutex);
        model->sessions.clear();
    }
}

} // namespace

extern "C" {

uint32_t rwa_abi_version(void) {
    return RWA_ABI_VERSION;
}

const char *rwa_status_string(rwa_status status) {
    switch (status) {
        case RWA_OK: return "ok";
        case RWA_INVALID_ARGUMENT: return "invalid argument";
        case RWA_UNAVAILABLE: return "unavailable";
        case RWA_UNSUPPORTED: return "unsupported";
        case RWA_BUSY: return "busy";
        case RWA_CANCELLED: return "cancelled";
        case RWA_INCOMPATIBLE_STATE: return "incompatible state";
        case RWA_CORRUPT_STATE: return "corrupt state";
        case RWA_BACKEND_FAILURE: return "backend failure";
        case RWA_CLOSED: return "closed";
        case RWA_CAPACITY: return "capacity";
    }
    return "unknown";
}

rwa_status rwa_runtime_create(
    const rwa_runtime_options *options,
    rwa_runtime **out_runtime) {
    if (out_runtime == nullptr) return RWA_INVALID_ARGUMENT;
    *out_runtime = nullptr;
    auto runtime = std::unique_ptr<rwa_runtime>(new (std::nothrow) rwa_runtime());
    if (!runtime) return RWA_BACKEND_FAILURE;
    if (options != nullptr) {
        if (!struct_valid(options)) return RWA_INVALID_ARGUMENT;
        if (options->max_active_batch > 0) {
            runtime->max_active_batch =
                std::min(options->max_active_batch, kMaxMLXSlots);
        }
        if (options->queue_capacity > 0) {
            runtime->queue_capacity = options->queue_capacity;
        }
    }
    *out_runtime = runtime.release();
    return RWA_OK;
}

rwa_status rwa_runtime_destroy(rwa_runtime *runtime) {
    if (runtime == nullptr) return RWA_OK;
    std::vector<rwa_model *> models;
    {
        std::lock_guard<std::mutex> lock(runtime->mutex);
        if (runtime->closed) return RWA_OK;
        runtime->closed = true;
        models.assign(runtime->models.begin(), runtime->models.end());
    }
    for (auto *model : models) (void)rwa_model_destroy(model);
    delete runtime;
    return RWA_OK;
}

const char *rwa_runtime_last_error(const rwa_runtime *runtime) {
    return runtime == nullptr ? "runtime is null" : runtime->error.get();
}

rwa_status rwa_model_load(
    rwa_runtime *runtime,
    const rwa_model_options *options,
    rwa_model **out_model) {
    if (runtime == nullptr || !struct_valid(options) || out_model == nullptr ||
        options->model_path == nullptr || options->tokenizer_path == nullptr) {
        return RWA_INVALID_ARGUMENT;
    }
    *out_model = nullptr;
    {
        std::lock_guard<std::mutex> lock(runtime->mutex);
        if (runtime->closed) return RWA_CLOSED;
    }
    if (options->provider != nullptr &&
        std::string(options->provider) != "mlx" &&
        std::string(options->provider) != "auto") {
        runtime->error.set("only the MLX provider is available");
        return RWA_UNAVAILABLE;
    }
    if (mlx_initialize() != 0) {
        runtime->error.set(mlx_error("initialize MLX"));
        return RWA_UNAVAILABLE;
    }

    auto model = std::unique_ptr<rwa_model>(new (std::nothrow) rwa_model());
    if (!model) return RWA_BACKEND_FAILURE;
    model->runtime = runtime;
    model->max_active_batch = runtime->max_active_batch;
    model->queue_capacity = runtime->queue_capacity;
    model->tokenizer = std::make_unique<trie_tokenizer>();
    if (model->tokenizer->load(options->tokenizer_path) != 0) {
        runtime->error.set("load RWKV tokenizer failed");
        return RWA_BACKEND_FAILURE;
    }
    std::string direct_pth_error;
    if (is_pth_path(options->model_path)) {
        model->mlx = rwkv_agent_load_pth_model(
            options->model_path,
            options->index_path == nullptr ? "" : options->index_path,
            direct_pth_error);
    } else {
        model->mlx = mlx_model_load(options->model_path);
    }
    if (model->mlx == nullptr) {
        std::string message = mlx_error(
            is_pth_path(options->model_path)
                ? "load RWKV .pth directly"
                : "load MLX model");
        if (!direct_pth_error.empty()) {
            message += ": " + direct_pth_error;
        }
        runtime->error.set(std::move(message));
        return RWA_BACKEND_FAILURE;
    }
    if (mlx_model_get_config(
            model->mlx,
            &model->vocab_size,
            &model->hidden_size,
            &model->head_dim,
            &model->layers) != 0) {
        runtime->error.set(mlx_error("read MLX model configuration"));
        mlx_model_release(model->mlx);
        model->mlx = nullptr;
        return RWA_BACKEND_FAILURE;
    }
    model->cache_size = mlx_cache_get_size(model->mlx);
    if (model->cache_size <= 0) {
        runtime->error.set(mlx_error("read MLX State cache size"));
        mlx_model_release(model->mlx);
        model->mlx = nullptr;
        return RWA_BACKEND_FAILURE;
    }
    for (uint32_t slot = 0; slot < model->max_active_batch; ++slot) {
        if (mlx_cache_zero_slot(model->mlx, static_cast<int32_t>(slot)) != 0) {
            runtime->error.set(mlx_error("initialize MLX State slots"));
            mlx_model_release(model->mlx);
            model->mlx = nullptr;
            return RWA_BACKEND_FAILURE;
        }
    }
    model->scheduler = std::thread(scheduler_main, model.get());
    {
        std::lock_guard<std::mutex> lock(runtime->mutex);
        runtime->models.insert(model.get());
    }
    *out_model = model.release();
    return RWA_OK;
}

rwa_status rwa_model_destroy(rwa_model *model) {
    if (model == nullptr) return RWA_OK;
    {
        std::lock_guard<std::mutex> lock(model->mutex);
        if (model->closed) return RWA_OK;
        model->closed = true;
    }
    {
        std::lock_guard<std::mutex> lock(model->queue_mutex);
        model->scheduler_stopping = true;
    }
    model->queue_cv.notify_all();
    {
        std::lock_guard<std::mutex> lock(model->mutex);
        for (auto *session : model->sessions) {
            session->cancel_requested.store(true, std::memory_order_release);
        }
    }
    if (model->scheduler.joinable()) model->scheduler.join();
    close_sessions(model);
    if (model->runtime != nullptr) {
        std::lock_guard<std::mutex> lock(model->runtime->mutex);
        model->runtime->models.erase(model);
    }
    if (model->mlx != nullptr) {
        mlx_model_release(model->mlx);
        model->mlx = nullptr;
    }
    delete model;
    return RWA_OK;
}

const char *rwa_model_last_error(const rwa_model *model) {
    return model == nullptr ? "model is null" : model->error.get();
}

rwa_status rwa_model_capabilities(
    const rwa_model *model,
    rwa_capabilities *out_capabilities) {
    if (model == nullptr || !struct_valid(out_capabilities)) {
        return RWA_INVALID_ARGUMENT;
    }
    out_capabilities->flags =
        RWA_CAP_NATIVE_STATE |
        RWA_CAP_CONTINUOUS_BATCH |
        RWA_CAP_EXACT_TOKENS |
        RWA_CAP_CANCELLATION;
    out_capabilities->max_state_slots = kMaxMLXSlots;
    uint32_t active = model->active_count.load(std::memory_order_acquire);
    out_capabilities->available_state_slots =
        active >= model->max_active_batch ? 0 : model->max_active_batch - active;
    out_capabilities->max_active_batch = model->max_active_batch;
    out_capabilities->queue_capacity = model->queue_capacity;
    out_capabilities->max_observed_batch =
        model->max_observed_batch.load(std::memory_order_acquire);
    return RWA_OK;
}

rwa_status rwa_model_encode(
    rwa_model *model,
    const char *utf8,
    size_t utf8_size,
    int32_t **out_tokens,
    size_t *out_token_count) {
    if (model == nullptr || utf8 == nullptr || out_tokens == nullptr ||
        out_token_count == nullptr) {
        return RWA_INVALID_ARGUMENT;
    }
    *out_tokens = nullptr;
    *out_token_count = 0;
    std::lock_guard<std::mutex> lock(model->mutex);
    if (model->closed) return RWA_CLOSED;
    auto encoded = model->tokenizer->encode(std::string_view(utf8, utf8_size));
    if (encoded.empty()) return RWA_OK;
    auto *buffer = static_cast<int32_t *>(
        std::malloc(encoded.size() * sizeof(int32_t)));
    if (buffer == nullptr) return RWA_BACKEND_FAILURE;
    std::copy(encoded.begin(), encoded.end(), buffer);
    *out_tokens = buffer;
    *out_token_count = encoded.size();
    return RWA_OK;
}

void rwa_token_buffer_free(int32_t *tokens) {
    std::free(tokens);
}

rwa_status rwa_session_create(
    rwa_model *model,
    const rwa_session_options *options,
    rwa_session **out_session) {
    if (model == nullptr || !struct_valid(options) || out_session == nullptr) {
        return RWA_INVALID_ARGUMENT;
    }
    *out_session = nullptr;
    auto session = std::unique_ptr<rwa_session>(new (std::nothrow) rwa_session());
    if (!session) return RWA_BACKEND_FAILURE;
    session->model = model;
    {
        std::lock_guard<std::mutex> lock(model->mutex);
        if (model->closed) return RWA_CLOSED;
        model->sessions.insert(session.get());
    }
    *out_session = session.release();
    return RWA_OK;
}

rwa_status rwa_session_destroy(rwa_session *session) {
    if (session == nullptr) return RWA_OK;
    session->cancel_requested.store(true, std::memory_order_release);
    {
        std::lock_guard<std::mutex> operation_lock(session->operation_mutex);
        {
            std::lock_guard<std::mutex> state_lock(session->state_mutex);
            session->closed = true;
            session->status.store(RWA_SESSION_CLOSED, std::memory_order_release);
        }
    }
    if (session->model != nullptr) {
        std::lock_guard<std::mutex> lock(session->model->mutex);
        session->model->sessions.erase(session);
    }
    delete session;
    return RWA_OK;
}

const char *rwa_session_last_error(const rwa_session *session) {
    return session == nullptr ? "session is null" : session->error.get();
}

rwa_status rwa_session_info_get(
    const rwa_session *session,
    rwa_session_info *out_info) {
    if (session == nullptr || !struct_valid(out_info)) return RWA_INVALID_ARGUMENT;
    std::lock_guard<std::mutex> state_lock(session->state_mutex);
    out_info->status = session->status.load(std::memory_order_acquire);
    out_info->prefix_token_count = session->prefix_tokens.size();
    out_info->prefix_hash = prefix_hash(session->prefix_tokens);
    out_info->active_request_id =
        session->active_request_id.load(std::memory_order_acquire);
    out_info->dirty_reason = session->dirty_reason.c_str();
    return RWA_OK;
}

rwa_status rwa_session_reset(rwa_session *session) {
    if (session == nullptr) return RWA_INVALID_ARGUMENT;
    std::lock_guard<std::mutex> operation_lock(session->operation_mutex);
    std::lock_guard<std::mutex> state_lock(session->state_mutex);
    if (session->closed) return RWA_CLOSED;
    session->cache.clear();
    session->logits.clear();
    session->prefix_tokens.clear();
    session->dirty_reason.clear();
    session->cancel_requested.store(false, std::memory_order_release);
    session->status.store(RWA_SESSION_CLEAN, std::memory_order_release);
    return RWA_OK;
}

rwa_status rwa_session_sync_prefix(
    rwa_session *session,
    const int32_t *token_ids,
    size_t token_count,
    rwa_prefill_progress_callback callback,
    void *user_data) {
    if (session == nullptr || (token_count > 0 && token_ids == nullptr)) {
        return RWA_INVALID_ARGUMENT;
    }
    std::lock_guard<std::mutex> operation_lock(session->operation_mutex);
    {
        std::lock_guard<std::mutex> state_lock(session->state_mutex);
        if (session->closed) return RWA_CLOSED;
    }
    session->cancel_requested.store(false, std::memory_order_release);
    std::vector<int32_t> target;
    if (token_count > 0) {
        target.assign(token_ids, token_ids + token_count);
    }
    return sync_prefix_locked(session, target, callback, user_data, nullptr);
}

rwa_status rwa_session_generate(
    rwa_session *session,
    const rwa_generate_options *options,
    rwa_stream_callback callback,
    void *user_data,
    rwa_generate_result *out_result) {
    if (session == nullptr || !struct_valid(options) || callback == nullptr ||
        !struct_valid(out_result) || options->input_token_ids == nullptr ||
        options->input_token_count == 0 || options->max_output_tokens == 0 ||
        options->temperature <= 0 || options->top_k <= 0 ||
        options->top_p <= 0 || options->top_p > 1) {
        return RWA_INVALID_ARGUMENT;
    }
    std::lock_guard<std::mutex> operation_lock(session->operation_mutex);
    {
        std::lock_guard<std::mutex> state_lock(session->state_mutex);
        if (session->closed) return RWA_CLOSED;
    }
    auto job = std::make_shared<GenerateJob>();
    job->session = session;
    job->options = *options;
    job->input_tokens.assign(
        options->input_token_ids,
        options->input_token_ids + options->input_token_count);
    job->options.input_token_ids = job->input_tokens.data();
    job->callback = callback;
    job->user_data = user_data;
    job->result.struct_size = sizeof(job->result);

    session->cancel_requested.store(false, std::memory_order_release);
    session->active_request_id.store(options->request_id, std::memory_order_release);
    session->status.store(RWA_SESSION_GENERATING, std::memory_order_release);

    rwa_model *model = session->model;
    {
        std::lock_guard<std::mutex> lock(model->queue_mutex);
        if (model->scheduler_stopping) return RWA_CLOSED;
        if (model->pending.size() >= model->queue_capacity) {
            session->active_request_id.store(0, std::memory_order_release);
            session->status.store(RWA_SESSION_CLEAN, std::memory_order_release);
            return RWA_CAPACITY;
        }
        model->pending.push_back(job);
    }
    model->queue_cv.notify_one();

    std::unique_lock<std::mutex> job_lock(job->mutex);
    job->cv.wait(job_lock, [&] { return job->done; });
    *out_result = job->result;
    return job->result_status;
}

rwa_status rwa_session_cancel(rwa_session *session, uint64_t request_id) {
    if (session == nullptr || request_id == 0) return RWA_INVALID_ARGUMENT;
    uint64_t active = session->active_request_id.load(std::memory_order_acquire);
    if (active == 0 || active != request_id) return RWA_INVALID_ARGUMENT;
    session->cancel_requested.store(true, std::memory_order_release);
    return RWA_OK;
}

rwa_status rwa_session_export_state(
    rwa_session *session,
    rwa_writer writer,
    void *user_data,
    rwa_state_descriptor *out_descriptor) {
    if (session == nullptr || writer == nullptr || !struct_valid(out_descriptor)) {
        return RWA_INVALID_ARGUMENT;
    }
    std::lock_guard<std::mutex> operation_lock(session->operation_mutex);
    std::vector<uint8_t> cache;
    std::vector<float> logits;
    std::vector<int32_t> tokens;
    {
        std::lock_guard<std::mutex> state_lock(session->state_mutex);
        if (session->closed) return RWA_CLOSED;
        if (session->status.load(std::memory_order_acquire) != RWA_SESSION_CLEAN) {
            return RWA_BUSY;
        }
        cache = session->cache;
        logits = session->logits;
        tokens = session->prefix_tokens;
    }
    std::vector<uint8_t> data;
    data.insert(data.end(), kStateMagic, kStateMagic + sizeof(kStateMagic));
    append_u32(data, kStateVersion);
    append_u32(data, static_cast<uint32_t>(cache.size()));
    append_u32(data, static_cast<uint32_t>(logits.size()));
    append_u64(data, static_cast<uint64_t>(tokens.size()));
    data.insert(data.end(), cache.begin(), cache.end());
    const uint8_t *logit_bytes = reinterpret_cast<const uint8_t *>(logits.data());
    data.insert(
        data.end(),
        logit_bytes,
        logit_bytes + logits.size() * sizeof(float));
    const uint8_t *token_bytes = reinterpret_cast<const uint8_t *>(tokens.data());
    data.insert(
        data.end(),
        token_bytes,
        token_bytes + tokens.size() * sizeof(int32_t));
    if (writer(data.data(), data.size(), user_data) != 0) return RWA_BACKEND_FAILURE;
    out_descriptor->format_version = kStateVersion;
    out_descriptor->prefix_token_count = tokens.size();
    out_descriptor->prefix_hash = prefix_hash(tokens);
    out_descriptor->codec_id = kCodecID;
    out_descriptor->codec_version = kStateVersion;
    return RWA_OK;
}

rwa_status rwa_session_import_state(
    rwa_session *session,
    rwa_reader reader,
    void *user_data,
    const rwa_state_descriptor *descriptor) {
    if (session == nullptr || reader == nullptr || !struct_valid(descriptor)) {
        return RWA_INVALID_ARGUMENT;
    }
    if (descriptor->format_version != kStateVersion ||
        descriptor->codec_version != kStateVersion ||
        descriptor->codec_id == nullptr ||
        std::string(descriptor->codec_id) != kCodecID) {
        return RWA_INCOMPATIBLE_STATE;
    }
    std::lock_guard<std::mutex> operation_lock(session->operation_mutex);
    {
        std::lock_guard<std::mutex> state_lock(session->state_mutex);
        if (session->closed || session->model == nullptr) return RWA_CLOSED;
    }
    std::vector<uint8_t> data;
    std::vector<uint8_t> chunk(64 * 1024);
    for (;;) {
        size_t count = 0;
        if (reader(chunk.data(), chunk.size(), &count, user_data) != 0) {
            return RWA_CORRUPT_STATE;
        }
        if (count > chunk.size()) return RWA_CORRUPT_STATE;
        if (count == 0) break;
        if (data.size() > kMaxStateBytes - count) return RWA_CORRUPT_STATE;
        data.insert(data.end(), chunk.begin(), chunk.begin() + count);
    }
    if (data.size() < sizeof(kStateMagic) ||
        std::memcmp(data.data(), kStateMagic, sizeof(kStateMagic)) != 0) {
        return RWA_CORRUPT_STATE;
    }
    size_t offset = sizeof(kStateMagic);
    uint32_t version = 0, cache_size = 0, logits_count = 0;
    uint64_t token_count = 0;
    if (!read_u32(data, offset, version) ||
        !read_u32(data, offset, cache_size) ||
        !read_u32(data, offset, logits_count) ||
        !read_u64(data, offset, token_count)) {
        return RWA_CORRUPT_STATE;
    }
    if (version != kStateVersion ||
        token_count > (size_t(1) << 30)) {
        return RWA_INCOMPATIBLE_STATE;
    }
    const bool empty_state =
        token_count == 0 && cache_size == 0 && logits_count == 0;
    if (!empty_state &&
        (cache_size != static_cast<uint32_t>(session->model->cache_size) ||
         logits_count != static_cast<uint32_t>(session->model->vocab_size))) {
        return RWA_INCOMPATIBLE_STATE;
    }
    uint64_t expected = offset;
    expected += cache_size;
    expected += uint64_t(logits_count) * sizeof(float);
    expected += token_count * sizeof(int32_t);
    if (expected != data.size()) return RWA_CORRUPT_STATE;

    std::vector<uint8_t> cache(
        data.begin() + offset, data.begin() + offset + cache_size);
    offset += cache_size;
    std::vector<float> logits(logits_count);
    std::memcpy(logits.data(), data.data() + offset, logits.size() * sizeof(float));
    offset += logits.size() * sizeof(float);
    std::vector<int32_t> tokens(static_cast<size_t>(token_count));
    std::memcpy(tokens.data(), data.data() + offset, tokens.size() * sizeof(int32_t));
    if (descriptor->prefix_token_count != tokens.size() ||
        descriptor->prefix_hash != prefix_hash(tokens)) {
        return RWA_INCOMPATIBLE_STATE;
    }
    {
        std::lock_guard<std::mutex> state_lock(session->state_mutex);
        if (session->closed) return RWA_CLOSED;
        session->cache = std::move(cache);
        session->logits = std::move(logits);
        session->prefix_tokens = std::move(tokens);
        session->dirty_reason.clear();
        session->status.store(RWA_SESSION_CLEAN, std::memory_order_release);
    }
    return RWA_OK;
}

} // extern "C"
