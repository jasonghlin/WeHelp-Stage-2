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
  const data = await response.json();
  if (data) {
    loginEmailInput.value = "";
    loginEmailPassword.value = "";
    modalControl("hidden");
    login.removeEventListener("click", loginEvent);
    login.textContent = "登出系統";
    login.addEventListener("click", logoutEvent);
    return data;
  } else {
    modalControl("block");
    return false;
  }
}

async function checkStatus() {
  const jwtToken = localStorage.getItem("session");
  const userInfo = await checkLoginStatus(jwtToken);
  return;
}

checkStatus();

// handle booking plan
function handleBookingPlan() {
  const bookinPlanBtn = document.querySelector(".menu li:nth-child(1)");
  bookinPlanBtn.addEventListener("click", async (e) => {
    e.preventDefault();
    const jwtToken = localStorage.getItem("session");
    if (jwtToken) {
      const userInfo = await checkLoginStatus(jwtToken);
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

// Tappay
async function tappay() {
  // const data = await fetchAPPIdKey(jwtToken);
  const APP_ID = 150900;
  const APP_KEY =
    "app_yhuFjfOXpbURVThigcQLqf8GfLgF1RM5GLmpvNZYhO0RLZeSgqKglxQscdN4";

  await TPDirect.setupSDK(APP_ID, APP_KEY, "sandbox");
  let fields = {
    number: {
      // css selector
      element: "#credit-card-number",
      placeholder: "**** **** **** ****",
    },
    expirationDate: {
      // DOM object
      element: document.getElementById("expiration-date"),
      placeholder: "MM / YY",
    },
    ccv: {
      element: "#card-cvv",
      placeholder: "CVV",
    },
  };

  TPDirect.card.setup({
    fields: fields,
    styles: {
      // Style all elements
      input: {
        color: "gray",
      },
      // Styling ccv field
      "input.ccv": {
        // 'font-size': '16px'
      },
      // Styling expiration-date field
      "input.expiration-date": {
        // 'font-size': '16px'
      },
      // Styling card-number field
      "input.card-number": {
        // 'font-size': '16px'
      },
      // style focus state
      ":focus": {
        // 'color': 'black'
      },
      // style valid state
      ".valid": {
        color: "green",
      },
      // style invalid state
      ".invalid": {
        color: "red",
      },
      // Media queries
      // Note that these apply to the iframe, not the root window.
      "@media screen and (max-width: 400px)": {
        input: {
          color: "orange",
        },
      },
    },
    // 此設定會顯示卡號輸入正確後，會顯示前六後四碼信用卡卡號
    isMaskCreditCardNumber: true,
    maskCreditCardNumberRange: {
      beginIndex: 6,
      endIndex: 11,
    },
  });
}

tappay();

// check login status

let user_info;
async function checkLogin() {
  const loginStatus = await checkLoginStatus(jwtToken);
  if (!loginStatus) {
    window.location = "/";
  } else {
    login.removeEventListener("click", loginEvent);
    login.textContent = "登出";
    login.addEventListener("click", logoutEvent);
  }
}
checkLogin();

async function fetchUserBooking(token) {
  let response = await fetch("/api/booking", {
    method: "GET",
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });
  let data = await response.json();
  return data;
}

// get user info
async function fetchUserInfo(token) {
  let response = await fetch("/api/user/auth", {
    method: "GET",
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });
  user_info = await response.json();
  return;
}

// fetch delete api
async function fetchDelete(attractionId, token) {
  let response = await fetch(`/api/booking/${attractionId}`, {
    method: "DELETE",
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });
  let data = await response.json();
  return data;
}

function updateBookingInfo() {
  fetchUserBooking(jwtToken)
    .then((bookings) => {
      const container = document.querySelector(".booking-info-container");
      const price = document.querySelector(".price > span");
      const section2 = document.querySelector(".section2-container");
      const attractionBookingNumber = document.querySelector(
        ".attraction-booking-number"
      );
      let totalPrice = 0;

      container.innerHTML = ""; // 清空之前的內容

      if (bookings.length !== 0) {
        attractionBookingNumber.textContent = bookings.length;
        section2.classList.remove("hidden");
        bookings.forEach((booking) => {
          totalPrice += booking.data.price;
          let html = `
          <div class="booking-attraction-info-wrapper" data-attraction="${booking.data.attraction.id}">
          <div class="booking-image">
            <img src="https://${booking.data.attraction.image}" alt="attraction-image">
          </div>
          <div class="booking-attraction-info">
            <div class="attraction-name">台北一日遊：<span>${booking.data.attraction.name}</span></div>
            <div class="travel-day">日期：<span>${booking.data.date}</span></div>
            <div class="travel-time">時間：<span>${booking.data.time}</span></div>
            <div class="travel-fee">費用：<span>${booking.data.price}</span></div>
            <div class="travel-position">地點：<span>${booking.data.attraction.address}</span></div>
            <img src="/static/images/deletetrash.png" class="delete-icon" alt="delete-icon" data-attraction="${booking.data.attraction.id}">
          </div>
        </div>
        `;
          container.insertAdjacentHTML("beforeend", html);
        });
        price.textContent = `${totalPrice}`;
        deleteBooking(); // 重新綁定刪除按鈕的事件處理器
      } else {
        attractionBookingNumber.textContent = 0;
        const noBookingMessage = document.querySelector(".no-booking-message");
        noBookingMessage.classList.remove("hidden");
        container.classList.add("hidden");
        section2.classList.add("hidden");
        footer.style.alignItems = "start";
      }
    })
    .catch((error) => {
      console.error("Error updating booking info:", error);
    });
}

// add delete event on booking
function deleteBooking() {
  let deleteBtns = document.querySelectorAll(".delete-icon");
  deleteBtns.forEach((deleteBtn) => {
    deleteBtn.addEventListener("click", async () => {
      const attractionId = deleteBtn.dataset.attraction;
      const result = await fetchDelete(attractionId, jwtToken);
      if (result.ok) {
        // 刪除成功後，更新頁面
        const bookingInfoWrapper = deleteBtn.closest(
          ".booking-attraction-info-wrapper"
        );
        bookingInfoWrapper.remove();
        // 更新總價和其他資訊
        updateBookingInfo();
      } else {
        console.error("Delete failed:", result.message);
      }
    });
  });
}

// handle page
async function userBookings() {
  await fetchUserInfo(jwtToken);
  const bookings = await fetchUserBooking(jwtToken);
  const username = document.querySelector(".user-name");
  const container = document.querySelector(".booking-info-container");
  const price = document.querySelector(".price > span");
  const section2 = document.querySelector(".section2-container");
  const attractionBookingNumber = document.querySelector(
    ".attraction-booking-number"
  );
  let totalPrice = 0;
  username.textContent = user_info.data.name;
  document.querySelector("#name").value = user_info.data.name;
  document.querySelector("#email").value = user_info.data.email;
  container.innerHTML = ""; // 清空之前的內容
  if (bookings.length !== 0) {
    attractionBookingNumber.textContent = bookings.length;
    section2.classList.remove("hidden");
    bookings.forEach((booking) => {
      let urlSuffix = booking.data.attraction.image.split("/").pop();
      // https://d3u8ez3u55dl9n.cloudfront.net
      totalPrice += booking.data.price;
      let html = `
        <div class="booking-attraction-info-wrapper" data-attraction="${
          booking.data.attraction.id
        }">
        <div class="booking-image">
          <img src="https://d3u8ez3u55dl9n.cloudfront.net/${urlSuffix}" alt="attraction-image">
        </div>
        <div class="booking-attraction-info">
          <div class="attraction-name">台北一日遊：<span>${
            booking.data.attraction.name
          }</span></div>
          <div class="travel-day">日期：<span>${booking.data.date}</span></div>
          <div class="travel-time">時間：<span>${
            booking.data.time === "morning"
              ? "早上 9 點到下午 4 點"
              : "下午 2 點到晚上 9 點"
          }</span></div>
          <div class="travel-fee">費用：<span>新台幣 ${
            booking.data.price
          } 元</span></div>
          <div class="travel-position">地點：<span>${
            booking.data.attraction.address
          }</span></div>
          <img src="/static/images/deletetrash.png" class="delete-icon" alt="delete-icon" data-attraction="${
            booking.data.attraction.id
          }">
        </div>
      </div>
      `;
      container.insertAdjacentHTML("beforeend", html);
    });
    price.textContent = `${totalPrice}`;
    deleteBooking(); // 重新綁定刪除按鈕的事件處理器
  } else {
    const noBookingMessage = document.querySelector(".no-booking-message");
    noBookingMessage.classList.remove("hidden");
    container.classList.add("hidden");
    section2.classList.add("hidden");
    footer.style.alignItems = "start";
  }
}
userBookings();

// fetch post orders
async function bookingOrderSuccess(request, token) {
  const response = await fetch("/api/orders", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${token}`,
    },
    body: JSON.stringify(request),
  });
  if (!response.ok) {
    const message = `An error has occurred: ${response.statusText}`;
    throw new Error(message);
  }
  let data = await response.json();
  return data;
}

// check 2 forms
function checkFormsValidity() {
  const finalConfirmBtn = document.querySelector(".final-confirm-btn");

  finalConfirmBtn.addEventListener("click", async (e) => {
    e.preventDefault();
    const loginStatus = await checkLoginStatus(jwtToken);
    if (!loginStatus) {
      window.location = "/";
    }

    const form1 = document.querySelector(".user-info-container");
    const form2 = document.querySelector(".credit-card-container");
    const tappayStatus = TPDirect.card.getTappayFieldsStatus();

    if (form1.checkValidity() && form2.checkValidity()) {
      if (tappayStatus.canGetPrime === false) {
        alert("Can not get prime");
        return;
      }

      TPDirect.card.getPrime(async (result) => {
        if (result.status !== 0) {
          alert("get prime error " + result.msg);
          return;
        }
        const price = document.querySelector(".price > span").textContent;
        const attractionsInfo = document.querySelectorAll(
          ".booking-attraction-info-wrapper"
        );
        const trip = [];
        attractionsInfo.forEach((attractionInfo) => {
          let id = attractionInfo.dataset.attraction;
          let name = attractionInfo.querySelector(
            ".attraction-name > span"
          ).textContent;
          let address = attractionInfo.querySelector(
            ".travel-position > span"
          ).textContent;
          let image = attractionInfo.querySelector(".booking-image > img").src;
          let date =
            attractionInfo.querySelector(".travel-day > span").textContent;
          let time = attractionInfo.querySelector(
            ".travel-time > span"
          ).textContent;
          let attraction = {
            attraction: {
              id: id,
              name: name,
              address: address,
              image: image,
            },
            date: date,
            time: time,
          };
          trip.push(attraction);
        });
        let name = document.querySelector("#name").value;
        let email = document.querySelector("#email").value;
        let phone = document.querySelector("#phone").value;
        let contact = {
          name: name,
          email: email,
          phone: phone,
        };

        let request = {
          prime: result.card.prime,
          order: {
            price: price,
            trip: trip,
          },
          contact: contact,
        };
        console.log(request);
        const data = await bookingOrderSuccess(request, jwtToken);
        console.log(data);
        if (data.data) {
          alert("訂單建立成功！");
          window.location.href = "/thankyou?number=" + data.data.number;
        } else {
          alert("訂單建立失敗: " + data.message);
        }
      });
    } else {
      // 验证表单
      form1.reportValidity();
      form2.reportValidity();
    }
  });
}

checkFormsValidity();
