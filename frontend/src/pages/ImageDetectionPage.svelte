<script>
  import ImageDetection from '../lib/ImageDetection.svelte';

  // Props that will be passed down from App.svelte
  export let selectedCameraId;
  export let imageDetectionComponent;

</script>

<div class="row">
  <div class="col-12">
    <ImageDetection
      bind:this={imageDetectionComponent}
      bind:selectedCameraId={selectedCameraId}
    />
  </div>
</div>
