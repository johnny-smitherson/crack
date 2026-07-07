use std::collections::HashMap;

/// LRU cache entry
#[derive(Clone)]
struct CacheEntry<T> {
    val: T,
    last_access_ms: i64,
}

pub struct LruCache<T> {
    entries: HashMap<String, CacheEntry<T>>,
    max_entries: usize,
}

impl<T: Clone> LruCache<T> {
    pub fn new(max_entries: usize) -> Self {
        Self {
            entries: HashMap::new(),
            max_entries,
        }
    }

    pub fn get(&mut self, key: &str) -> Option<T> {
        let now = _crack_utils::get_timestamp_now_ms();
        if let Some(entry) = self.entries.get_mut(key) {
            entry.last_access_ms = now;
            Some(entry.val.clone())
        } else {
            None
        }
    }

    pub fn insert(&mut self, key: String, val: T) {
        let now = _crack_utils::get_timestamp_now_ms();
        if self.entries.len() >= self.max_entries {
            // Find the oldest entry to evict
            let oldest_key = self.entries.iter()
                .min_by_key(|(_, v)| v.last_access_ms)
                .map(|(k, _)| k.clone());
            if let Some(old_key) = oldest_key {
                self.entries.remove(&old_key);
            }
        }
        self.entries.insert(key, CacheEntry {
            val,
            last_access_ms: now,
        });
    }
}
