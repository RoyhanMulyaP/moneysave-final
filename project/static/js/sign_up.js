document.getElementById("signUpBtn").addEventListener("click", async () => {
    const userId = document.getElementById("userId").value;
    const email = document.getElementById("email").value;
    const password = document.getElementById("password").value;

    if (password.length < 8) {
        alert("Password minimal 8 karakter!");
        return;
    }

    const response = await fetch("/sign_up_process", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({ user_id: userId, email: email, password: password })
    });

    const result = await response.json();
    if (result.status === "success") {
        window.location.href = "/beranda";
    } else {
        alert(result.message);
    }
});
