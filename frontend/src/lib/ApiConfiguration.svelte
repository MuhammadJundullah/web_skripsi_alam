<script>
  import { apiBaseUrl } from './stores.js';
  import { onMount } from 'svelte';

  let currentApiUrl = $apiBaseUrl;
  let status = '';

  onMount(() => {
    // Sync local state when store changes from initial load
    apiBaseUrl.subscribe(value => {
      currentApiUrl = value;
    });
  });

  async function saveSettings() {
    status = 'Saving...';
    try {
      const response = await fetch(`${$apiBaseUrl}/settings`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ key: 'api_base_url', value: currentApiUrl })
      });

      if (!response.ok) {
        throw new Error('Failed to save settings');
      }

      // Update the global store, which will trigger reactivity
      apiBaseUrl.set(currentApiUrl);
      status = 'Saved successfully!';
    } catch (error) {
      status = `Error: ${error.message}`;
      console.error(error);
    } finally {
      setTimeout(() => status = '', 3000);
    }
  }
</script>

<div class="card">
  <div class="card-body">
    <h5 class="card-title">API Configuration</h5>
    <div class="row g-2 align-items-end">
      <div class="col">
        <label for="api-url" class="form-label">API Base URL</label>
        <input id="api-url" type="text" class="form-control" bind:value={currentApiUrl} />
      </div>
      <div class="col-auto">
        <button class="btn btn-primary" on:click={saveSettings}>Save</button>
      </div>
    </div>
    {#if status}
      <div class="form-text">{status}</div>
    {/if}
  </div>
</div>