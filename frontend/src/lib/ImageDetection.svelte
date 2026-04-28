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

  // --- Variables for detection summary ---
  // This prop will hold the individual detection objects from the backend.
  // It's expected to be an array of objects, e.g., [{ class_name: 'normal', confidence: 0.9, bbox: {...} }, ...]
  export let detectionResults = []; 
  
  // This variable will hold the full JSON response from the backend, including the summary.
  let detectionResponse = null;

  // Helper function to format percentage
  function formatPercentage(value) {
    return value.toFixed(2); // Display with 2 decimal places
  }

  // Reactive statement to update counts and percentages whenever detectionResults change
  // REMOVED: Frontend recalculation of counts and percentages.
  // We will now rely on the backend's summary.
  // $: { ... }

  // --- End of removed section ---


  let canvasElement;

  export function handleImageSelect(e) {
    const file = e.target.files[0];
    if (!file) return;
    imageFile = file;
    imagePreviewUrl = URL.createObjectURL(file);
    imageResultUrl = null; // Clear previous results
    detectionResults = []; // Clear previous detection results
    detectionResponse = null; // Clear previous full response
    imageStatus = `Ready to process ${file.name}.`;
  }

  export async function uploadImage() {
    if (!imageFile) return;
    imageStatus = "Uploading and processing image...";
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
      
      // Parse the JSON response from the backend
      const responseJson = await response.json();
      
      // Update component state with data from backend response
      imageResultUrl = responseJson.imageUrl;
      console.log('Image URL set in frontend:', imageResultUrl); // Log the URL for debugging
      detectionResults = responseJson.detections; // Keep this if you want to display individual detections
      detectionResponse = responseJson; // Store the full response to access summary directly

      // Log the received detection response and summary for debugging
      console.log('Full detection response from backend:', detectionResponse);
      if (detectionResponse && detectionResponse.summary) {
        console.log('Summary from backend:', detectionResponse.summary);
      }

      imageStatus = "Processing complete. Results available.";
    } catch (error) {
      console.error("Image upload or detection error:", error);
      imageStatus = `Error: ${error.message}`;
      detectionResults = []; // Clear results on error
      detectionResponse = null; // Clear response on error
    }
  }

  export async function startCameraForPhoto() {
    imageStatus = "Starting camera for photo...";
    try {
      isCameraActiveForPhoto = true;
      await tick();
      const constraints = {
        video: {
          width: 640,
          height: 480,
          deviceId: selectedCameraId ? { exact: selectedCameraId } : undefined
        }
      };
      const stream = await navigator.mediaDevices.getUserMedia(constraints);
      videoElementForPhoto.srcObject = stream;
      photoCaptureStream = stream;
      await videoElementForPhoto.play();
      imageStatus = "Camera active. Capture photo.";
    } catch (error) {
      console.error("Failed to start camera for photo:", error);
      imageStatus = "Could not start camera for photo. Check permissions.";
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
      imageResultUrl = null; // Clear previous results
      detectionResults = []; // Clear previous detection results
      detectionResponse = null; // Clear previous full response
      imageStatus = "Photo captured. Ready for detection.";
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
    imageStatus = "Camera stopped.";
  }
</script>

<section class="bg-white p-4 rounded-3 shadow-sm mb-4">
  <h2 class="h4 mb-3">Image File Detection</h2>

  <div class="row g-2 align-items-end">
    <div class="col-12 col-md-5">
      <label class="form-label">Choose Image</label>
      <input type="file" accept="image/*" on:change={handleImageSelect} class="form-control form-control-sm" />
    </div>
    <div class="col-12 col-md-auto">
      <label class="form-label d-block invisible">.</label>
      <button on:click={startCameraForPhoto} disabled={isCameraActiveForPhoto} class="btn btn-secondary btn-sm">Take Photo from Camera</button>
    </div>
    <div class="col-12 col-md-auto">
      <label class="form-label d-block invisible">.</label>
      <button on:click={uploadImage} disabled={!imageFile} class="btn btn-primary btn-sm">Detect Objects in Image</button>
    </div>
  </div>

  {#if isCameraActiveForPhoto}
    <div class="card my-3">
      <div class="card-header">Camera Capture</div>
      <div class="card-body">
        <div class="ratio ratio-4x3 mb-2">
          <video class="w-100 h-100" bind:this={videoElementForPhoto} autoplay muted playsinline></video>
        </div>
        <div class="d-flex gap-2">
          <button on:click={capturePhoto} class="btn btn-primary btn-sm">Capture Photo</button>
          <button on:click={stopCameraForPhoto} class="btn btn-outline-secondary btn-sm">Stop Camera</button>
        </div>
      </div>
    </div>
  {/if}

  <p class="text-muted small mt-2 mb-3">Status: {imageStatus}</p>

  <div class="row g-3">
    <div class="col-12 col-lg-6">
      <div class="card h-100">
        <div class="card-header">Original Image</div>
        <div class="card-body">
          <img class="img-fluid" src={imagePreviewUrl} alt="Original to be processed" />
        </div>
      </div>
    </div>
    <div class="col-12 col-lg-6">
      <div class="card h-100">
        <div class="card-header">Processed Image</div>
        <div class="card-body">
          <img class="img-fluid" src={imageResultUrl} alt="Processed result" />
        </div>
      </div>
    </div>
  </div>

  <!-- --- New Section for Detection Summary --- -->
  <!-- Display summary directly from backend response -->
  {#if detectionResponse && detectionResponse.summary}
    <div class="mt-4 p-3 bg-light rounded border">
      <h3 class="h5 mb-3">Detection Summary:</h3>
      <div class="row">
        <div class="col-md-6">
          <p class="mb-1"><strong>Total Beans Detected:</strong> {detectionResponse.summary.normal_count + detectionResponse.summary.abnormal_count}</p>
          <p class="mb-1"><strong>Biji Normal:</strong> {detectionResponse.summary.normal_count} ({formatPercentage(detectionResponse.summary.normal_percentage)}%)</p>
        </div>
        <div class="col-md-6">
          <p class="mb-1"><strong>Biji Tidak Normal:</strong> {detectionResponse.summary.abnormal_count} ({formatPercentage(detectionResponse.summary.abnormal_percentage)}%)</p>
        </div>
      </div>
    </div>
  {/if}
  <!-- --- End of New Section --- -->

  <canvas bind:this={canvasElement} class="d-none"></canvas>
</section>