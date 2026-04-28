<script>
  import ApiConfiguration from '../lib/ApiConfiguration.svelte';
  import ServerMonitoring from '../lib/ServerMonitoring.svelte';
  import ModelConfiguration from '../lib/ModelConfiguration.svelte';

  export let serverStats;
</script>

<div class="row">
  <div class="col-lg-5 mb-4">
    <ApiConfiguration />
  </div>
  <div class="col-lg-5 mb-4">
    <ModelConfiguration />
  </div>
  <ServerMonitoring {serverStats} />
</div>
