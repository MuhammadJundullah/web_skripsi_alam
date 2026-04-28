<script>
  import { onMount } from 'svelte';

  let jobs = [];
  let error = null;
  let isLoading = true;

  const API_BASE_URL = 'https://sayidj-backend-yolo-coffee-app.hf.space';

  async function fetchHistory() {
    try {
      const response = await fetch(`${API_BASE_URL}/history`);
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      jobs = await response.json();
    } catch (e) {
      error = e.message;
      console.error("Error fetching history:", e);
    } finally {
      isLoading = false;
    }
  }

  async function deleteJob(jobId) {
    if (!confirm('Are you sure you want to delete this job and its files?')) {
      return;
    }
    try {
      const response = await fetch(`${API_BASE_URL}/history/${jobId}`, { method: 'DELETE' });
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      fetchHistory();
    } catch (e) {
      alert(`Failed to delete job: ${e.message}`);
      console.error("Error deleting job:", e);
    }
  }

  async function retryJob(jobId) {
    try {
      const response = await fetch(`${API_BASE_URL}/retry/${jobId}`, { method: 'POST' });
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      fetchHistory();
    } catch (e) {
      alert(`Failed to retry job: ${e.message}`);
      console.error("Error retrying job:", e);
    }
  }

  function formatDateTime(isoString) {
    if (!isoString) return 'N/A';
    const options = { year: 'numeric', month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' };
    return new Date(isoString).toLocaleDateString('en-US', options);
  }

  onMount(() => {
    fetchHistory();
    const interval = setInterval(fetchHistory, 5000);
    return () => clearInterval(interval); 
  });
</script>

<div class="history-container">
  <h2 class="h4 mb-3">Vidio Detection History</h2>
  {#if isLoading}
    <p>Loading history...</p>
  {:else if error}
    <p class="error">Failed to load history: {error}</p>
  {:else if jobs.length === 0}
    <p>No detection jobs found.</p>
  {:else}
    <button on:click={fetchHistory} class="refresh-btn">Refresh</button>
    <div class="table-responsive">
      <table class="table table-striped table-hover align-middle">
        <thead>
          <tr>
            <th>ID</th>
            <th>Filename</th>
            <th>Status</th>
            <th>Upload Time</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          {#each jobs as job (job.id)}
            <tr>
              <td>{job.id}</td>
              <td>{job.filename}</td>
              <td>
                <span class={`badge status-badge status-${job.status.toLowerCase()}`}>{job.status}</span>
              </td>
              <td>{formatDateTime(job.upload_time)}</td>
              <td class="actions">
                {#if job.status === 'SUCCESS'}
                  <a href="{API_BASE_URL}/download/{job.id}" class="btn btn-sm btn-outline-success">Download</a>
                {/if}
                {#if job.status === 'FAILURE'}
                  <button on:click={() => retryJob(job.id)} class="btn btn-sm btn-outline-warning">Retry</button>
                {/if}
                <button on:click={() => deleteJob(job.id)} class="btn btn-sm btn-outline-danger">Delete</button>
              </td>
            </tr>
          {/each}
        </tbody>
      </table>
    </div>
  {/if}
</div>

<style>
  .history-container { margin-top: 2rem; padding: 1.5rem; background-color: #f9f9f9; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
  h2 { margin-top: 0; color: #333; }
  th, td { white-space: nowrap; vertical-align: middle; }
  .refresh-btn { padding: 0.5rem 1rem; background-color: #007bff; color: white; border: none; border-radius: 4px; cursor: pointer; margin-bottom: 1rem; }
  .refresh-btn:hover { background-color: #0056b3; }
  .status-badge { color: white !important; }
  .status-pending { background-color: #ffc107; }
  .status-processing { background-color: #17a2b8; }
  .status-success { background-color: #28a745; }
  .status-failure { background-color: #dc3545; }
  .actions { display: flex; gap: 0.5rem; }
  .error { color: #dc3545; }
</style>
