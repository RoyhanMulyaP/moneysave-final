const video = document.getElementById("camera");
const canvas = document.getElementById("snapshot");
const captureBtn = document.getElementById("captureBtn");

// Akses kamera
navigator.mediaDevices.getUserMedia({ video: { facingMode: "environment" } })
  .then((stream) => {
    video.srcObject = stream;
  })
  .catch((err) => {
    console.error("Kamera tidak dapat diakses: ", err);
  });

// Tombol ambil foto & upload
captureBtn.addEventListener("click", async () => {
  let context = canvas.getContext("2d");
  context.drawImage(video, 0, 0, canvas.width, canvas.height);

  let imageData = canvas.toDataURL("image/jpeg"); // hasil base64

  let formData = new FormData();
  formData.append("userId", document.getElementById("userId").value);
  formData.append("fotoKartu", imageData);

  try {
    let response = await fetch("/upload_foto", {
      method: "POST",
      body: formData,
    });

    let result = await response.json();

    if (result.message) {
      alert(result.message); // popup berhasil
      window.location.href = "/verifikasi_wajah"; // redirect setelah klik OK
    } else if (result.error) {
      alert(result.error);
    }
  } catch (err) {
    console.error(err);
    alert("Terjadi kesalahan!");
  }
});
