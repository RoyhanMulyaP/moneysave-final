const lanjutBtn = document.getElementById("lanjutBtn");
  const userId = document.getElementById("userId").value;
  const jenisKelaminSelect = document.getElementById("jenis_kelamin");

  lanjutBtn.addEventListener("click", async () => {
    const jenisKelamin = jenisKelaminSelect.value;

    if (!jenisKelamin) {
      alert("Silahkan pilih jenis kelamin!");
      return;
    }

    const formData = new FormData();
    formData.append("userId", userId);
    formData.append("jenis_kelamin", jenisKelamin);

    const response = await fetch("/update_jenis_kelamin", {
      method: "POST",
      body: formData
    });

    const result = await response.json();

    if (result.success) {
      window.location.href = "/isi_no_rek";
    } else {
      alert("Terjadi kesalahan: " + result.error);
    }
  });