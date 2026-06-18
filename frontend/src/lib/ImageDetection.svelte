<script>
  import { tick } from 'svelte';
  import { apiBaseUrl } from './stores.js';

  export let imageFile;
  export let imagePreviewUrl;
  export let imageResultUrl;
  export let imageStatus;
  export let isCameraActiveForPhoto;
  export let photoCaptureStream;
  export let videoElementForPhoto;
  export let selectedCameraId;

  // Detection summary from backend.
  export let detectionResults = []; 
  
  // This variable will hold the full JSON response from the backend, including the summary.
  let detectionResponse = null;
  let selectedFacingMode = 'environment'; // 'user', 'environment', or 'manual'

  // Helper function to format percentage
  function formatPercentage(value) {
    return value.toFixed(2); // Display with 2 decimal places
  }

  let canvasElement;

  export function handleImageSelect(e) {
    const file = e.target.files[0];
    if (!file) return;
    imageFile = file;
    imagePreviewUrl = URL.createObjectURL(file);
    imageResultUrl = null; // Clear previous results
    detectionResults = []; // Clear previous detection results
    detectionResponse = null; // Clear previous full response
    imageStatus = `Siap memproses ${file.name}.`;
  }

  export async function uploadImage() {
    if (!imageFile) return;
    imageStatus = "Mengunggah dan memproses gambar...";
    imageResultUrl = null; // Clear previous results
    detectionResults = []; // Clear previous detection results
    detectionResponse = null; // Clear previous full response

    const formData = new FormData();
    formData.append("file", imageFile);
    try {
      const response = await fetch(`${$apiBaseUrl}/detect/image`, {
        method: "POST",
        body: formData,
      });
      if (!response.ok) {
        let errorMsg = `Server error: ${response.status} ${response.statusText}`;
        try {
            const errorData = await response.json();
            errorMsg = errorData.message || JSON.stringify(errorData);
        } catch {}
        throw new Error(errorMsg);
      }
      
      const responseJson = await response.json();
      imageResultUrl = responseJson.imageUrl;
      detectionResults = responseJson.detections;
      detectionResponse = responseJson;
      imageStatus = "Pemrosesan selesai. Hasil deteksi tersedia.";
    } catch (error) {
      console.error("Image upload or detection error:", error);
      imageStatus = `Error: ${error.message}`;
      detectionResults = [];
      detectionResponse = null;
    }
  }

  export async function startCameraForPhoto() {
    imageStatus = "Menyalakan kamera untuk mengambil foto...";
    try {
      isCameraActiveForPhoto = true;
      await tick();
      const constraints = {
        video: {
          width: { ideal: 1280 },
          height: { ideal: 720 },
        }
      };

      if (selectedFacingMode === 'manual' && selectedCameraId) {
        constraints.video.deviceId = { exact: selectedCameraId };
      } else {
        constraints.video.facingMode = { ideal: selectedFacingMode };
      }

      const stream = await navigator.mediaDevices.getUserMedia(constraints);
      videoElementForPhoto.srcObject = stream;
      photoCaptureStream = stream;
      await videoElementForPhoto.play();
      imageStatus = "Kamera aktif. Silakan ambil foto.";
    } catch (error) {
      console.error("Failed to start camera for photo:", error);
      imageStatus = "Kamera untuk foto tidak dapat dijalankan. Periksa izin perangkat.";
    }
  }

  export function capturePhoto() {
    if (!videoElementForPhoto || !canvasElement) return;
    const context = canvasElement.getContext('2d');
    canvasElement.width = videoElementForPhoto.videoWidth;
    canvasElement.height = videoElementForPhoto.videoHeight;
    context.drawImage(videoElementForPhoto, 0, 0, canvasElement.width, canvasElement.height);
    canvasElement.toBlob((blob) => {
      const capturedFile = new File([blob], "captured_photo.png", { type: "image/png" });
      imageFile = capturedFile;
      imagePreviewUrl = URL.createObjectURL(capturedFile);
      imageResultUrl = null;
      detectionResults = [];
      detectionResponse = null;
      imageStatus = "Foto berhasil diambil. Siap untuk deteksi.";
      stopCameraForPhoto();
    }, 'image/png');
  }

  export function stopCameraForPhoto() {
    if (photoCaptureStream) {
      photoCaptureStream.getTracks().forEach(track => track.stop());
      photoCaptureStream = null;
    }
    if (videoElementForPhoto) {
      videoElementForPhoto.srcObject = null;
    }
    isCameraActiveForPhoto = false;
    imageStatus = "Kamera dihentikan.";
  }
</script>

<section class="bg-white p-4 rounded-3 shadow-sm mb-4">
  <h2 class="h4 mb-3">Deteksi Penyakit pada Gambar Daun Cabai</h2>

  <div class="row g-2 align-items-end">
    <div class="col-12 col-md-4">
      <label class="form-label" for="image-upload">Pilih Gambar Daun Cabai</label>
      <input id="image-upload" type="file" accept="image/*" on:change={handleImageSelect} class="form-control form-control-sm" />
    </div>
    <div class="col-12 col-md-3">
      <label for="photo-camera-mode" class="form-label">Mode Kamera</label>
      <select id="photo-camera-mode" class="form-select form-select-sm" bind:value={selectedFacingMode} disabled={isCameraActiveForPhoto}>
        <option value="environment">Kamera Belakang</option>
        <option value="user">Kamera Depan</option>
        <option value="manual">Manual (Pilih Perangkat)</option>
      </select>
    </div>
    <div class="col-12 col-md-auto">
      <button type="button" on:click={startCameraForPhoto} disabled={isCameraActiveForPhoto} class="btn btn-secondary btn-sm">Buka Kamera</button>
    </div>
    <div class="col-12 col-md-auto">
      <button type="button" on:click={uploadImage} disabled={!imageFile} class="btn btn-primary btn-sm">Deteksi Penyakit</button>
    </div>
  </div>

  {#if isCameraActiveForPhoto}
    <div class="card my-3 border-primary">
      <div class="card-header bg-primary text-white">Ambil Gambar dari Kamera</div>
      <div class="card-body p-1">
        <div class="ratio ratio-4x3 bg-dark rounded overflow-hidden mb-2">
          <video class="w-100 h-100 object-fit-contain" bind:this={videoElementForPhoto} autoplay muted playsinline></video>
        </div>
        <div class="p-2 d-flex gap-2 justify-content-center">
          <button type="button" on:click={capturePhoto} class="btn btn-primary">Ambil Foto</button>
          <button type="button" on:click={stopCameraForPhoto} class="btn btn-outline-secondary">Batal</button>
        </div>
      </div>
    </div>
  {/if}

  <p class="text-muted small mt-2 mb-3">Status: {imageStatus}</p>

  <div class="row g-3">
    <div class="col-12 col-lg-6">
      <div class="card h-100">
        <div class="card-header bg-light">Gambar Asli</div>
        <div class="card-body p-1">
          <div class="ratio ratio-4x3 bg-light rounded overflow-hidden">
            {#if imagePreviewUrl}
              <img class="w-100 h-100 object-fit-contain" src={imagePreviewUrl} alt="Gambar daun cabai asli" />
            {:else}
              <div class="d-flex align-items-center justify-content-center h-100 text-muted">Belum ada gambar</div>
            {/if}
          </div>
        </div>
      </div>
    </div>
    <div class="col-12 col-lg-6">
      <div class="card h-100">
        <div class="card-header bg-light">Hasil Deteksi</div>
        <div class="card-body p-1">
          <div class="ratio ratio-4x3 bg-light rounded overflow-hidden">
            {#if imageResultUrl}
              <img class="w-100 h-100 object-fit-contain" src={imageResultUrl} alt="Hasil deteksi penyakit daun cabai" />
            {:else}
              <div class="d-flex align-items-center justify-content-center h-100 text-muted">Hasil akan muncul di sini</div>
            {/if}
          </div>
        </div>
      </div>
    </div>
  </div>

  {#if detectionResponse && detectionResponse.summary}
    <div class="mt-4 p-3 bg-light rounded border shadow-sm">
      <h3 class="h5 mb-3 border-bottom pb-2">Ringkasan Deteksi</h3>
      <div class="row">
        <div class="col-md-6">
          <p class="mb-1 text-primary"><strong>Total Daun:</strong> {detectionResponse.summary.normal_count + detectionResponse.summary.abnormal_count}</p>
          <p class="mb-1 text-success"><strong>Daun Sehat:</strong> {detectionResponse.summary.normal_count} ({formatPercentage(detectionResponse.summary.normal_percentage)}%)</p>
        </div>
        <div class="col-md-6">
          <p class="mb-1 text-danger"><strong>Terindikasi Penyakit:</strong> {detectionResponse.summary.abnormal_count} ({formatPercentage(detectionResponse.summary.abnormal_percentage)}%)</p>
        </div>
      </div>
    </div>
  {/if}

  <canvas bind:this={canvasElement} class="d-none"></canvas>
</section>
