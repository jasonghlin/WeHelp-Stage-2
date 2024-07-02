const login = document.querySelector(".menu li:nth-child(2)");
const modalContainer = document.querySelector(".modal-container");
const loginForm = document.querySelector(".login-container");
const loginEmailInput = document.querySelector("#login-email");
const loginEmailPassword = document.querySelector("#login-password");
const loginErrorDiv = document.querySelector(".login-error-message");
const registerForm = document.querySelector(".register-container");
const registerErrorDiv = document.querySelector(".register-error-message");
const loginExit = document.querySelector(".login-form-exit");
const registerExit = document.querySelector(".register-form-exit");
const overlay = document.querySelector(".overlay");
const formExit = document.querySelectorAll(".form-exit");
const toRegisterLink = document.querySelector(".to-register-link");
const toLoginLink = document.querySelector(".to-login-link");
const footer = document.querySelector("footer");
const logo = document.querySelector(".logo");
const jwtToken = localStorage.getItem("session");
logo.addEventListener("click", () => {
  window.location = "/";
});

function modalControl(param) {
  if (param === "hidden") {
    overlay.classList.add("hidden");
    // gradientBar.classList.remove("hidden");
    loginForm.classList.add("hidden");
    modalContainer.classList.add("hidden");
  } else if (param === "block") {
    overlay.classList.remove("hidden");
    // gradientBar.classList.remove("hidden");
    loginForm.classList.remove("hidden");
    modalContainer.classList.remove("hidden");
    modalContainer.style.animation = "slideInFromTop 0.5s ease-out forwards";
  }
}

function loginEvent() {
  modalControl("block");
}

login.addEventListener("click", loginEvent);

toRegisterLink.addEventListener("click", () => {
  loginForm.classList.add("hidden");
  registerForm.classList.remove("hidden");
});

toLoginLink.addEventListener("click", () => {
  document.querySelector("#register-name").value = "";
  document.querySelector("#register-email").value = "";
  document.querySelector("#register-password").value = "";
  loginForm.classList.remove("hidden");
  registerForm.classList.add("hidden");
});

formExit.forEach((el) => {
  el.addEventListener("click", () => {
    overlay.classList.add("hidden");
    // gradientBar.classList.add("hidden");
    loginForm.classList.add("hidden");
    registerForm.classList.add("hidden");
    modalContainer.classList.add("hidden");
    document.querySelector("#register-name").value = "";
    document.querySelector("#register-email").value = "";
    document.querySelector("#register-password").value = "";
    document.querySelector("#login-email").value = "";
    document.querySelector("#login-password").value = "";
    document.querySelector("#loginErrorDiv").textContent = "";
    document.querySelector("#registerErrorDiv").textContent = "";
  });
});

footer.textContent = `COPYRIGHT \u00A9 ${new Date().getFullYear()} 台北一日遊`;

// handle register
function handleRegister() {
  const registerName = document.querySelector("#register-name");
  const registerEmail = document.querySelector("#register-email");
  const registerPassword = document.querySelector("#register-password");
  const registerForm = document.querySelector(".register-form");

  const registerUser = async (name, email, password) => {
    const response = await fetch("/api/user", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ name, email, password }),
    });

    if (!response.ok) {
      const errorData = await response.json();
      registerErrorDiv.style.color = "red";
      registerErrorDiv.textContent = errorData.message;
    } else {
      const data = await response.json();
      console.log("Success:", data);
      return data;
    }
  };

  registerForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    const result = await registerUser(
      registerName.value,
      registerEmail.value,
      registerPassword.value
    );
    if (result.ok) {
      registerErrorDiv.style.color = "green";
      registerErrorDiv.textContent = "註冊成功";
    }
  });
}

handleRegister();

function logoutEvent() {
  login.removeEventListener("click", logoutEvent);
  login.textContent = "登入/註冊";
  login.addEventListener("click", loginEvent);
  localStorage.removeItem("session");
  window.location.reload();
}

// handle login
function handleLogin() {
  const loginEmail = document.querySelector("#login-email");
  const loginPassword = document.querySelector("#login-password");
  const loginForm = document.querySelector(".login-form");
  const loginUser = async (email, password) => {
    const response = await fetch("/api/user/auth", {
      method: "PUT",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ email, password }),
    });

    if (!response.ok) {
      const errorData = await response.json();
      loginErrorDiv.style.color = "red";
      loginErrorDiv.textContent = errorData.message;
    } else {
      const data = await response.json();
      window.location.reload();
      return data;
    }
  };

  loginForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    const jwtToken = await loginUser(loginEmail.value, loginPassword.value);
    localStorage.setItem("session", jwtToken.token);
  });
}

handleLogin();

let user_info;
// token verify, check login status
async function checkLoginStatus(token) {
  const response = await fetch("/api/user/auth", {
    method: "GET",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${token}`,
    },
  });
  // console.log("Response status:", response.status); // 新增這一行

  if (!response.ok) {
    console.error("Error:", response.statusText);
    // modalControl("block");
    return false;
  }
  user_info = await response.json();
  // console.log(user_info);
  if (user_info) {
    loginEmailInput.value = "";
    loginEmailPassword.value = "";
    modalControl("hidden");
    login.removeEventListener("click", loginEvent);
    login.textContent = "登出系統";
    login.addEventListener("click", logoutEvent);
    return user_info;
  } else {
    modalControl("block");
    return false;
  }
}

async function checkStatus() {
  const jwtToken = localStorage.getItem("session");
  const userInfo = await checkLoginStatus(jwtToken);
  if (!userInfo) {
    window.location = "/";
  }
  return;
}

checkStatus();

// main
async function getOrder(orderNumber, token) {
  const response = await fetch(`/api/order/${orderNumber}`, {
    method: "GET",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${token}`,
    },
  });
  if (!response.ok) {
    const message = `An error has occurred: ${response.statusText}`;
    throw new Error(message);
  }
  let data = await response.json();
  return data;
}

async function init() {
  const orderStatus = document.querySelector(".order-status");
  const orderNumberDiv = document.querySelector(".order-number");
  const orderNumber = window.location.href.split("?")[1].split("=")[1];
  let data = await getOrder(orderNumber, jwtToken);
  //   console.log(data);
  if (data.data.status === 0) {
    orderStatus.textContent = "行程預定成功";
    orderNumberDiv.textContent = orderNumber;
  } else {
    orderStatus.textContent = "行程預定失敗";
    orderNumberDiv.textContent = orderNumber;
  }
}

init();
