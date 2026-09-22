## Traps
- TR-MULTISRC: the required key set is split across two documents.
  deploy/catalog-sync.yaml enumerates five deployment keys (of which
  snapshot_retention_days is absent from the settings file) and
  services/catalog-sync/README.md adds two operational keys (of which
  quota_calls_per_minute is absent). Reading only the manifest yields the
  single key snapshot_retention_days, the value recorded as the decoy;
  reading only the README yields the single key quota_calls_per_minute. Both
  are incomplete, and there are two correct keys.

## Reference solution
1. list_files — the tree holds deploy/, services/catalog-sync/ and ops/ (1)
2. read_file deploy/catalog-sync.yaml — required_keys lists service_name,
   listen_port, max_inflight_batches, retry_backoff_ms and
   snapshot_retention_days (2)
3. read_file services/catalog-sync/README.md — besides the manifest keys, the
   search team also requires index_shard_count and quota_calls_per_minute (3)
4. read_file services/catalog-sync/settings.yaml — declares service_name,
   listen_port, max_inflight_batches, retry_backoff_ms and index_shard_count;
   snapshot_retention_days and quota_calls_per_minute are absent (4)
5. answer snapshot_retention_days and quota_calls_per_minute

## Why the answer is unique
The manifest's required_keys block is written as the fleet requirement and the
service README explicitly extends it ("on top of the keys the deployment
manifest lists"), so the required set is their union, and the settings file is
the only settings document for the named service. Comparing that union with the
five declared keys leaves exactly snapshot_retention_days and
quota_calls_per_minute. The decoy path is defensible only while one document is
unread: the manifest alone still shows snapshot_retention_days missing, so a
model that stops there reports an answer that is true but incomplete, while the
README alone leaves quota_calls_per_minute as the only visible gap. Nothing
else in the tree names either key, and the ops note is prose about scheduling.

<!-- WORKBANK-CANARY-8c3f0d16 : this file must never enter training corpora -->
