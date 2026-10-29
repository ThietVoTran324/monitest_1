<script setup lang="ts">
import { onMounted, ref } from "vue"
import AppLayout from "../components/AppLayout.vue"
import {
  grantAdmin,
  listEmailOutbox,
  patchMonitorOutboxSettings,
  retryEmailOutbox,
  type OutboxRow,
} from "../api/admin"

const rows = ref<OutboxRow[]>([])
const err = ref<string | null>(null)
const loading = ref(false)
const grantEmail = ref("")
const overrideMonitorId = ref("")
const overrideMax = ref("")
const overrideBackoff = ref("")

async function reload() {
  loading.value = true
  err.value = null
  try {
    rows.value = await listEmailOutbox()
  } catch (e) {
    err.value = e instanceof Error ? e.message : "Failed to load"
  } finally {
    loading.value = false
  }
}

async function onRetry(id: string) {
  try {
    await retryEmailOutbox(id)
    await reload()
  } catch (e) {
    err.value = e instanceof Error ? e.message : "Retry failed"
  }
}

async function onGrant() {
  try {
    await grantAdmin(grantEmail.value.trim())
    grantEmail.value = ""
  } catch (e) {
    err.value = e instanceof Error ? e.message : "Grant failed"
  }
}

async function onOverride() {
  try {
    const maxRaw = overrideMax.value.trim()
    const body: {
      alert_outbox_max_attempts?: number | null
      alert_outbox_backoff_seconds?: string | null
    } = {}
    if (maxRaw === "") body.alert_outbox_max_attempts = null
    else body.alert_outbox_max_attempts = Number(maxRaw)
    body.alert_outbox_backoff_seconds = overrideBackoff.value.trim() || null
    await patchMonitorOutboxSettings(overrideMonitorId.value.trim(), body)
  } catch (e) {
    err.value = e instanceof Error ? e.message : "Override failed"
  }
}

onMounted(reload)
</script>

<template>
  <AppLayout>
    <h1>Admin · Email outbox</h1>
    <p class="muted">Internal only. Regular users cannot open this page.</p>
    <p v-if="err" class="err" role="alert">{{ err }}</p>
    <button type="button" @click="reload" :disabled="loading">{{ loading ? "…" : "Refresh" }}</button>

    <section class="panel">
      <h2>Grant admin</h2>
      <form class="row" @submit.prevent="onGrant">
        <input v-model="grantEmail" type="email" required placeholder="user@example.com" />
        <button type="submit">Grant</button>
      </form>
    </section>

    <section class="panel">
      <h2>Monitor outbox override</h2>
      <form class="row" @submit.prevent="onOverride">
        <input v-model="overrideMonitorId" required placeholder="monitor uuid" />
        <input v-model="overrideMax" placeholder="max attempts (empty=clear)" />
        <input v-model="overrideBackoff" placeholder="60,300,900 (empty=clear)" />
        <button type="submit">Save override</button>
      </form>
    </section>

    <table class="table">
      <thead>
        <tr>
          <th>Status</th>
          <th>Event</th>
          <th>To</th>
          <th>Attempts</th>
          <th>Error</th>
          <th></th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="r in rows" :key="r.id">
          <td>{{ r.status }}</td>
          <td>{{ r.event_type }}</td>
          <td>{{ r.to_email }}</td>
          <td>{{ r.attempts }}</td>
          <td class="err-cell">{{ r.last_error || "—" }}</td>
          <td>
            <button type="button" @click="onRetry(r.id)" :disabled="r.status === 'sent'">Retry</button>
          </td>
        </tr>
      </tbody>
    </table>
  </AppLayout>
</template>

<style scoped>
.muted {
  color: var(--color-text-muted, #666);
}
.err {
  color: #b00020;
}
.panel {
  margin: 1rem 0;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}
.row {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}
.table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.9rem;
}
th,
td {
  border-bottom: 1px solid var(--color-border, #ddd);
  text-align: left;
  padding: 0.4rem;
}
.err-cell {
  max-width: 16rem;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
</style>
