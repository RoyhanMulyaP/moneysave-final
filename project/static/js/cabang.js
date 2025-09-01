 const lanjutBtn = document.getElementById("lanjutBtn");
  const userId = document.getElementById("userId").value;

  lanjutBtn.addEventListener("click", async () => {
    const cabang = document.getElementById("cabang").value;

    if (!cabang) {
      alert("Silahkan isi nama cabang!");
      return;
    }

    const formData = new FormData();
    formData.append("userId", userId);
    formData.append("cabang", cabang);

    const response = await fetch("/update_cabang_rekening", {
      method: "POST",
      body: formData
    });

    const result = await response.json();

    if (result.success) {
      window.location.href = "/validasi_data";
    } else {
      alert("Terjadi kesalahan: " + result.error);
    }
  });