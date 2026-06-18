<script>
  import { apiBaseUrl } from './stores.js';
  import { onDestroy } from 'svelte';

  let videoFile = null;
  let videoPreviewUrl = null;
  let videoStatus = "Pilih file video daun cabai atau rekam video baru.";

  // Recording state
  let isCameraOpen = false;
  let isRecording = false;
  let mediaRecorder;
  let recordedChunks = [];
  let cameraStream;
  let cameraPreviewEl;
  let selectedFacingMode = 'environment'; // 'user' or 'environment'

  function handleVideoSelect(e) {
    const file = e.target.files[0];
    if (!file) return;
    videoFile = file;
    videoPreviewUrl = URL.createObjectURL(file);
    videoStatus = `Siap memproses ${file.name}.`;
  }

  async function uploadVideo() {
    if (!videoFile) {
      alert("Pilih atau rekam file video terlebih dahulu.");
      return;
    }
    videoStatus = "Mengunggah video...";
    const formData = new FormData();
    formData.append("file", videoFile);
    const apiUrl = `${$apiBaseUrl}/detect/video`;
    
    try {
      const response = await fetch(apiUrl, {
        method: "POST",
        body: formData,
      });
      if (!response.ok) throw new Error(`Server error: ${response.statusText}`);
      const data = await response.json();
      videoStatus = `Upload selesai untuk ${data.original_filename}. Cek riwayat untuk melihat status proses.`;
      videoFile = null;
      videoPreviewUrl = null;
    } catch (error) {
      console.error("Video upload error:", error);
      videoStatus = `Error: ${error.message}`;
    }
  }

  async function openCamera() {
    try {
      const constraints = {
        video: {
          facingMode: { ideal: selectedFacingMode },
          width: { ideal: 1280 },
          height: { ideal: 720 }
        },
        audio: true
      };
      cameraStream = await navigator.mediaDevices.getUserMedia(constraints);
      cameraPreviewEl.srcObject = cameraStream;
      isCameraOpen = true;
    } catch (err) {
      alert("Kamera tidak dapat diakses. Periksa izin perangkat.");
      console.error("Camera access error:", err);
    }
  }

  function closeCamera() {
    if (cameraStream) {
      cameraStream.getTracks().forEach(track => track.stop());
    }
    isCameraOpen = false;
    isRecording = false;
    mediaRecorder = null;
    recordedChunks = [];
  }

  function startRecording() {
    if (!cameraStream) return;
    recordedChunks = [];
    mediaRecorder = new MediaRecorder(cameraStream);
    mediaRecorder.ondataavailable = (e) => {
      if (e.data.size > 0) recordedChunks.push(e.data);
    };
    mediaRecorder.onstop = () => {
      const blob = new Blob(recordedChunks, { type: 'video/webm' });
      const fileName = `recording-${new Date().toISOString()}.webm`;
      videoFile = new File([blob], fileName, { type: blob.type });
      videoPreviewUrl = URL.createObjectURL(blob);
      videoStatus = `Rekaman selesai. Siap memproses ${fileName}.`;
      closeCamera();
    };
    mediaRecorder.start();
    isRecording = true;
  }

  function stopRecording() {
    if (mediaRecorder) mediaRecorder.stop();
  }

  onDestroy(() => {
    closeCamera();
  });
</script>

<div class="card bg-white shadow-sm rounded-3">
  <div class="card-body p-4">
    <h5 class="card-title h4 mb-4 text-primary">Deteksi Penyakit dari Video</h5>
    <div class="row g-3 align-items-end mb-4">
      <div class="col-12 col-md-4">
        <label class="form-label fw-bold" for="video-upload">Pilih File Video</label>
        <input id="video-upload" type="file" accept="video/*" on:change={handleVideoSelect} class="form-control form-control-sm" />
      </div>
      
      <div class="col-12 col-md-3">
        <label for="video-camera-mode" class="form-label fw-bold">Mode Kamera</label>
        <select id="video-camera-mode" class="form-select form-select-sm" bind:value={selectedFacingMode} disabled={isCameraOpen}>
          <option value="environment">Kamera Belakang</option>
          <option value="user">Kamera Depan</option>
        </select>
      </div>

      <div class="col-12 col-md-auto">
        <button type="button" class="btn btn-outline-secondary btn-sm w-100" on:click={openCamera}>Buka Kamera & Rekam</button>
      </div>
    </div>

    {#if videoPreviewUrl}
      <div class="mb-4 p-3 bg-light rounded border">
        <h6 class="fw-bold mb-3">Pratinjau Video</h6>
        <div class="ratio ratio-16x9 bg-dark rounded overflow-hidden shadow-sm">
          <video class="w-100 h-100 object-fit-contain" src={videoPreviewUrl} controls muted></video>
        </div>
        <div class="d-grid mt-3">
          <button type="button" on:click={uploadVideo} class="btn btn-primary">Mulai Deteksi Penyakit pada Video</button>
        </div>
      </div>
    {/if}

    <div class="alert alert-info py-2 px-3 mb-0">
      <i class="bi bi-info-circle me-2"></i>
      <span class="small">Status: {videoStatus}</span>
    </div>
  </div>
</div>

{#if isCameraOpen}
  <div class="modal-backdrop fade show"></div>
  <div class="modal fade show" style="display: block; background: rgba(0,0,0,0.5);" tabindex="-1">
    <div class="modal-dialog modal-lg modal-dialog-centered">
      <div class="modal-content border-0 shadow-lg">
        <div class="modal-header bg-primary text-white">
          <h5 class="modal-title">Rekam Video Daun Cabai</h5>
          <button type="button" class="btn-close btn-close-white" on:click={closeCamera}></button>
        </div>
        <div class="modal-body p-1 bg-dark">
          <div class="ratio ratio-4x3 rounded overflow-hidden">
            <video bind:this={cameraPreviewEl} class="w-100 h-100 object-fit-contain" autoplay muted playsinline></video>
          </div>
        </div>
        <div class="modal-footer justify-content-center bg-light">
          <button type="button" class="btn btn-outline-secondary px-4" on:click={closeCamera}>Batal</button>
          {#if isRecording}
            <button type="button" class="btn btn-danger px-4" on:click={stopRecording}>
              <span class="spinner-grow spinner-grow-sm me-2" role="status" aria-hidden="true"></span>
              Hentikan Rekaman
            </button>
          {:else}
            <button type="button" class="btn btn-success px-4" on:click={startRecording}>Mulai Rekam Video</button>
          {/if}
        </div>
      </div>
    </div>
  </div>
{/if}
