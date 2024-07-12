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
      // console.error("Error:", errorData);
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

// token verify, check login status, logout event
async function checkLoginStatus(token) {
  const response = await fetch("/api/user/auth", {
    method: "GET",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${token}`,
    },
  });
  console.log("Response status:", response.status); // 新增這一行

  if (!response.ok) {
    console.error("Error:", response.statusText);
    window.location = "/";
    // modalControl("block");
    return false;
  }
  const data = await response.json();
  console.log(data);
  if (data) {
    loginEmailInput.value = "";
    loginEmailPassword.value = "";
    modalControl("hidden");
    login.removeEventListener("click", loginEvent);
    login.textContent = "登出系統";
    login.addEventListener("click", logoutEvent);
    return data;
  } else {
    return false;
  }
}

let userInfo;
async function checkStatus() {
  const jwtToken = localStorage.getItem("session");
  userInfo = await checkLoginStatus(jwtToken);

  return;
}

// handle booking plan
function handleBookingPlan() {
  const bookinPlanBtn = document.querySelector(".menu li:nth-child(1)");
  bookinPlanBtn.addEventListener("click", async (e) => {
    e.preventDefault();
    const jwtToken = localStorage.getItem("session");
    if (jwtToken) {
      userInfo = await checkLoginStatus(jwtToken);
      if (userInfo) {
        window.location.href = "/booking";
        console.log("ok");
      } else {
        modalControl("block");
      }
    } else {
      modalControl("block");
    }
  });
}

handleBookingPlan();

// main

async function init() {
  await checkStatus();
  await createOrderTable();
  updateName();
  updateEmail();
  updatePassword();
  userImg();
}

init();

// update name
async function saveName(newName) {
  if (!newName.trim()) {
    alert("新姓名不能為空值!");
    return;
  }

  let token = localStorage.getItem("session");
  let response = await fetch("/api/user/edit", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${token}`,
    },
    body: JSON.stringify({ name: newName }),
  });
  token = await response.json();
  return token;
}

function cancelNameEdit(el) {
  document.querySelector(".user-name-edit").removeChild(el);
  document.querySelector(".user-name-edit > img").classList.remove("hidden");
  document.querySelector(".user-name-edit > div").classList.remove("hidden");
}

async function updateName() {
  document.querySelector(".name").textContent = userInfo.data.name;
  document
    .querySelector(".user-name-edit > img")
    .addEventListener("click", async () => {
      userInfo = await checkLoginStatus(localStorage.getItem("session"));
      document.querySelector(".user-name-edit > img").classList.add("hidden");
      document.querySelector(".user-name-edit > div").classList.add("hidden");

      let editNameDiv = document.createElement("div");
      editNameDiv.className = "edit-name-input-container";

      let input = document.createElement("input");
      input.className = "input-value";
      input.type = "text";
      input.value = userInfo.data.name;

      let btnContainer = document.createElement("div");
      btnContainer.className = "button-container";

      let saveButton = document.createElement("button");
      saveButton.textContent = "更新姓名";
      saveButton.onclick = async () => {
        let jwtToken = await saveName(input.value);
        if (jwtToken) {
          localStorage.setItem("session", jwtToken.token);
          document.querySelector(".name").textContent = document.querySelector(
            ".edit-name-input-container > .input-value"
          ).value;
          document.querySelector(".user-name-edit").removeChild(editNameDiv);
          document
            .querySelector(".user-name-edit > img")
            .classList.remove("hidden");
          document
            .querySelector(".user-name-edit > div")
            .classList.remove("hidden");
        }
      };

      let cancelButton = document.createElement("button");
      cancelButton.textContent = "取消";
      cancelButton.onclick = () => cancelNameEdit(editNameDiv);

      btnContainer.appendChild(saveButton);
      btnContainer.appendChild(cancelButton);

      editNameDiv.appendChild(input);
      editNameDiv.appendChild(btnContainer);

      document.querySelector(".user-name-edit").appendChild(editNameDiv);
    });
}

// update email
function validateEmail(email) {
  const re = /\S+@\S+\.\S+/;
  return re.test(email);
}

async function saveEmail(newEmail) {
  if (!newEmail.trim()) {
    alert("新 Email 不能為空值!");
    return;
  }
  if (validateEmail(newEmail)) {
    let token = localStorage.getItem("session");
    let response = await fetch("/api/user/edit", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify({ email: newEmail }),
    });
    token = await response.json();
    if (token.error) {
      alert(token.message);
      return;
    }
    return token;
  } else {
    alert("請輸入有效的電子郵件");
  }
}

function cancelEmailEdit(el) {
  document.querySelector(".user-email-edit").removeChild(el);
  document.querySelector(".user-email-edit > img").classList.remove("hidden");
  document.querySelector(".user-email-edit > div").classList.remove("hidden");
}

async function updateEmail() {
  document.querySelector(".email").textContent = userInfo.data.email;
  document
    .querySelector(".user-email-edit > img")
    .addEventListener("click", async () => {
      userInfo = await checkLoginStatus(localStorage.getItem("session"));
      document.querySelector(".user-email-edit > img").classList.add("hidden");
      document.querySelector(".user-email-edit > div").classList.add("hidden");

      let editEmailDiv = document.createElement("div");
      editEmailDiv.className = "edit-email-input-container";

      let input = document.createElement("input");
      input.className = "input-value";
      input.type = "text";
      input.value = userInfo.data.email;

      let btnContainer = document.createElement("div");
      btnContainer.className = "button-container";

      let saveButton = document.createElement("button");
      saveButton.textContent = "更新 Email";
      saveButton.onclick = async () => {
        let jwtToken = await saveEmail(input.value);
        if (jwtToken) {
          localStorage.setItem("session", jwtToken.token);
          document.querySelector(".email").textContent = document.querySelector(
            ".edit-email-input-container > .input-value"
          ).value;
          document.querySelector(".user-email-edit").removeChild(editEmailDiv);
          document
            .querySelector(".user-email-edit > img")
            .classList.remove("hidden");
          document
            .querySelector(".user-email-edit > div")
            .classList.remove("hidden");
        }
      };

      let cancelButton = document.createElement("button");
      cancelButton.textContent = "取消";
      cancelButton.onclick = () => cancelEmailEdit(editEmailDiv);

      btnContainer.appendChild(saveButton);
      btnContainer.appendChild(cancelButton);

      editEmailDiv.appendChild(input);
      editEmailDiv.appendChild(btnContainer);

      document.querySelector(".user-email-edit").appendChild(editEmailDiv);
    });
}

// update password
function validatePassword(password, passwordValidate) {
  if (!password.trim() || !passwordValidate.trim()) {
    alert("新密碼不能為空值!");
    return;
  }
  return password === passwordValidate;
}

function cancelPasswordEdit(el) {
  document.querySelector(".password-container").removeChild(el);
  document
    .querySelector(".user-password-edit > img")
    .classList.remove("hidden");
}

async function savePassword() {
  const newPasswordInput = document.querySelector(".new-password").value;
  const newPasswordInputValidate = document.querySelector(
    ".new-password-validate"
  ).value;

  if (validatePassword(newPasswordInput, newPasswordInputValidate)) {
    let token = localStorage.getItem("session");
    let response = await fetch("/api/user/edit", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify({ password: newPasswordInput }),
    });
    let fetchStatus = await response.json();
    console.log(fetchStatus);
    if (fetchStatus.ok) {
      alert("密碼更新成功");
      return;
    }
  } else {
    alert("兩次密碼輸入不相同");
  }
}

function updatePassword() {
  document
    .querySelector(".user-password-edit > img")
    .addEventListener("click", () => {
      document
        .querySelector(".user-password-edit > img")
        .classList.add("hidden");

      let html = `<div class="password-update-form">
                <div class="new-password-container">
                    <label>請輸入新的密碼：</label>
                    <input type="password" class="new-password">
                </div>
                <div>
                    <label>請再輸入一次新的密碼：</label>
                    <input type="password" class="new-password-validate">
                </div>
                <div class="button-container"><button class="password-update-btn">更新密碼</button><button class="password-cancel-btn">取消</button></div>
            </div>`;

      document
        .querySelector(".password-container")
        .insertAdjacentHTML("beforeend", html);

      document
        .querySelector(".password-cancel-btn")
        .addEventListener("click", (e) => {
          const editPasswordDiv = document.querySelector(
            ".password-update-form"
          );
          cancelPasswordEdit(editPasswordDiv);
        });

      document
        .querySelector(".password-update-btn")
        .addEventListener("click", (e) => {
          const editPasswordDiv = document.querySelector(
            ".password-update-form"
          );
          savePassword();
          let child = document.querySelector(".password-update-form");
          document.querySelector(".password-container").removeChild(child);
          document
            .querySelector(".user-password-edit > img")
            .classList.remove("hidden");
        });
    });
}

// upload Image
async function uploadImage(event) {
  let file = event.target.files[0];
  let token = localStorage.getItem("session");
  if (!file) {
    alert("No file selected.");
    return;
  }

  let fileType = file.type;
  console.log(fileType);
  if (
    fileType !== "image/jpeg" &&
    fileType !== "image/jpg" &&
    fileType !== "image/png"
  ) {
    alert("只能上傳 JPG 或 PNG 檔案圖片!");
    return;
  }

  let formData = new FormData();
  formData.append("file", file);
  try {
    let response = await fetch("/api/upload", {
      method: "POST",
      headers: {
        Authorization: `Bearer ${token}`,
      },
      body: formData,
    });

    let getUploadInfo = await response.json();
    if (!response.ok) {
      console.error("HTTP error", response.status);
      alert(getUploadInfo.message);
      return;
    } else {
      alert(getUploadInfo.message);
      localStorage.setItem("proImg", getUploadInfo.url);
      window.location.href = `/memberpage`;
    }
  } catch (err) {
    console.error("Error:", err);
    alert("Failed to upload file.");
  }
}

document.getElementById("fileInput").addEventListener("change", uploadImage);

async function userImg() {
  let sessionImgURL = localStorage.getItem("proImg");

  if (sessionImgURL) {
    document.querySelector(".photo > img").src = sessionImgURL;
  } else {
    let response = await fetch("/api/upload", {
      method: "GET",
      headers: {
        Authorization: `Bearer ${localStorage.getItem("session")}`,
      },
    });
    let url = await response.json();
    if (url.detail !== "Token decode error") {
      document.querySelector(".photo > img").src = url.url;
    }
  }
}

// 訂單資料

async function fetchOrder(token) {
  const response = await fetch(`/api/order/all/${userInfo.data.id}`, {
    method: "GET",
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });
  if (!response.ok) {
    const message = `An error has occurred: ${response.statusText}`;
    throw new Error(message);
  }
  let data = await response.json();
  console.log(data);
  return data;
}

async function createOrderTable() {
  const response = await fetchOrder(localStorage.getItem("session"));
  const data = response.data;
  const orderTableBody = document.getElementById("order-table-body");

  // Function to create a new table cell
  function createCell(text) {
    const cell = document.createElement("td");
    cell.innerText = text;
    return cell;
  }

  // Function to create a new table row
  function createRow(order, trip, isFirstRow) {
    const row = document.createElement("tr");

    if (isFirstRow) {
      const orderNumberCell = createCell(order.number);
      orderNumberCell.rowSpan = order.trip.length;
      row.appendChild(orderNumberCell);
    }

    let morningTime = trip.time === "morning" ? "上午" : "下午";
    row.appendChild(createCell(trip.attraction.name));
    row.appendChild(createCell(trip.date));
    row.appendChild(createCell(morningTime));
    row.appendChild(createCell(trip.attraction.address));

    if (isFirstRow) {
      //   const contactCell = createCell(order.contact.name);
      //   contactCell.rowSpan = order.trip.length;
      //   row.appendChild(contactCell);

      //   const emailCell = createCell(order.contact.email);
      //   emailCell.rowSpan = order.trip.length;
      //   row.appendChild(emailCell);

      //   const phoneCell = createCell(order.contact.phone);
      //   phoneCell.rowSpan = order.trip.length;
      //   row.appendChild(phoneCell);

      const priceCell = createCell(order.price);
      priceCell.rowSpan = order.trip.length;
      row.appendChild(priceCell);

      const statusCell = createCell(order.status === 0 ? "已付款" : "未付款");
      statusCell.rowSpan = order.trip.length;
      row.appendChild(statusCell);
    }

    return row;
  }

  // Generate table rows
  data.forEach((order) => {
    const orderRows = [];
    order.trip.forEach((trip, index) => {
      const isFirstRow = index === 0;
      const row = createRow(order, trip, isFirstRow);
      orderRows.push(row);
      orderTableBody.appendChild(row);
    });

    // Add hover event listeners to all rows of the same order
    orderRows.forEach((row) => {
      row.addEventListener("mouseenter", () => {
        orderRows.forEach((r) => r.classList.add("hover-highlight"));
      });
      row.addEventListener("mouseleave", () => {
        orderRows.forEach((r) => r.classList.remove("hover-highlight"));
      });
    });
  });
}
