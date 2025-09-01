const video = document.getElementById("camera");
const canvas = document.getElementById("snapshot");
const captureBtn = document.getElementById("captureBtn");

navigator.mediaDevices.getUserMedia({ video: { facingMode: "environment" } })
  .then((stream) => {
    video.srcObject = stream;
  })
  .catch((err) => {
    console.error("Kamera tidak dapat diakses: ", err);
  });

captureBtn.addEventListener("click", async () => {
  let context = canvas.getContext("2d");
  context.drawImage(video, 0, 0, canvas.width, canvas.height);

  let imageData = canvas.toDataURL("image/jpeg");

  let formData = new FormData();
  formData.append("userId", document.getElementById("userId").value);
  formData.append("fotoWajah", imageData);

  try {
    let response = await fetch("/upload_wajah", {
      method: "POST",
      body: formData,
    });

    let result = await response.json();

    if (result.message) {
      alert(result.message);
      window.location.href = "/verifikasi_data";
    } else if (result.error) {
      alert(result.error);
    }
  } catch (err) {
    console.error(err);
    alert("Terjadi kesalahan!");
  }
});
