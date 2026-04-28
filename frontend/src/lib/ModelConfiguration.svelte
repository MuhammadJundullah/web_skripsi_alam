<script>
  import { onMount } from 'svelte';
  import { apiBaseUrl } from './stores.js';

  let confidence = 0.25;
  let status = '';
  let initialValue = 0.25;

  async function fetchConfidence() {
    try {
      const response = await fetch(`${$apiBaseUrl}/settings/model_confidence`);
      if (response.ok) {
        const data = await response.json();
        confidence = parseFloat(data.value);
        initialValue = confidence;
      }
    } catch (error) {
      console.error("Failed to fetch model confidence:", error);
    }
  }

  async function saveConfidence() {
    status = 'Saving...';
    try {
      const response = await fetch(`${$apiBaseUrl}/settings`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ key: 'model_confidence', value: String(confidence) })
      });
      if (!response.ok) throw new Error('Failed to save setting');
      initialValue = confidence;
      status = 'Saved!';
    } catch (error) {
      status = `Error: ${error.message}`;
    } finally {
      setTimeout(() => status = '', 3000);
    }
  }

  onMount(() => {
    const unsubscribe = apiBaseUrl.subscribe(url => {
      if (url) fetchConfidence();
    });
    return unsubscribe;
  });

  // Reactive statement to save when slider is released
  $: if (confidence !== initialValue) {
    const handler = setTimeout(() => saveConfidence(), 500);
    // cleanup function
    () => clearTimeout(handler);
  }
</script>

<div class="card h-100">
  <div class="card-body">
    <h5 class="card-title">Model Configuration</h5>
    <label for="confidence-slider" class="form-label">Confidence Threshold: {confidence.toFixed(2)}</label>
    <input type="range" class="form-range" min="0.1" max="0.9" step="0.05" id="confidence-slider" bind:value={confidence}>
    <div class="form-text">Detection boxes with a confidence score below this value will be ignored.</div>
    {#if status}
      <div class="form-text mt-2">{status}</div>
    {/if}
  </div>
</div>
