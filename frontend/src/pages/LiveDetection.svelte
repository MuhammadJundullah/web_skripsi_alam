<script>
  import RealtimeStreaming from '../lib/RealtimeStreaming.svelte';

  // Props that will be passed down from App.svelte
  export let availableCameras;
  export let selectedCameraId;
  export let streamingInterval;
  export let realtimeStreamingComponent;

  const intervalOptions = [
    { label: 'Tinggi (10 FPS)', value: 100 },
    { label: 'Sedang (5 FPS)', value: 200 },
    { label: 'Rendah (2 FPS)', value: 500 },
  ];
</script>

<div class="row">
  <div class="col-12">
    <RealtimeStreaming
      bind:this={realtimeStreamingComponent}
      bind:availableCameras={availableCameras}
      bind:selectedCameraId={selectedCameraId}
      bind:streamingInterval={streamingInterval}
      {intervalOptions}
    />
  </div>
</div>
