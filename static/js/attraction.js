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
      } else {
        modalControl("block");
      }
    } else {
      modalControl("block");
    }
  });
}

handleBookingPlan();

// section 1
async function fetchAttraction(id) {
  const response = await fetch(`/api/attraction/${id}`);
  if (response.ok) {
    const data = await response.json();
    return data.data;
  } else {
    console.log("error on fetching attractions");
  }
}

const data = await fetchAttraction(window.location.pathname.split("/")[2]);

if (!data) {
  window.location = "/";
}

function createElementWithClass(element, className) {
  let container = document.createElement(element);
  container.className = className;
  return container;
}

async function createPage() {
  const profileContainer = document.querySelector(".profile");
  const section2Container = document.querySelector(".section2");
  let html = `
  <h3 class="attraction-name">${data.name}</h3>
  <p class="attraction-cat-mrt"><span class="attraction-category">${data.category}</span> at <span
      class="attraction-mrt">${data.mrt}</span></p>
  <div class="booking-form-wrapper">
    <form action="#" class="booking-form">
      <p class="form-title">訂購導覽行程</p>
      <p>以此景點為中心的一日行程，帶您探索城市角落故事</p>
      <div class="travel-day-wrapper">
        <label for="travel-day" class="travel-day-label">選擇日期：</label>
        <input type="date" id="travel-day" required>
      </div>
      <div class="travel-time-wrapper">
        <label class="travel-time-label">選擇時間：</label>
        <input type="radio" name="travel-time" id="morning" value="上半天" required>
        <label for="morning" class="morning-label">上半天</label>
        <input type="radio" name="travel-time" id="afternoon" value="下半天" required>
        <label for="afternoon" class="afternoon-label">下半天</label>
      </div>
      <p class="travel-fee">導覽費用：<span class="twd">新台幣 <span class="fee">2000</span> 元</span></p>
      <button class="booking-btn" type="submit">開始預約行程</button>
    </form>
  `;
  profileContainer.insertAdjacentHTML("beforeend", html);

  //   更改 fee
  const morningRadio = document.getElementById("morning");
  const afternoonRadio = document.getElementById("afternoon");
  const feeElement = document.querySelector(".fee");

  morningRadio.addEventListener("change", () => {
    if (morningRadio.checked) {
      feeElement.textContent = "2000";
    }
  });

  afternoonRadio.addEventListener("change", () => {
    if (afternoonRadio.checked) {
      feeElement.textContent = "2500";
    }
  });

  //   section2
  html = `
  <div class="infos">
      <div class="description">
        ${data.description}</div>
      <div class="address">
        <p>景點地址:</p>
        <p>${data.address}</p>
      </div>
      <div class="transport">
        <p>交通方式</p>
        <p>${data.transport}</p>
      </div>
    </div>
`;
  section2Container.insertAdjacentHTML("beforeend", html);
}

createPage();

// image slider https://ithelp.ithome.com.tw/articles/10301221
function imageSlider() {
  const imagesContainer = document.querySelector(".images");

  data.images.forEach((image, index) => {
    let urlSuffix = image.split("/").pop();
    // https://d3u8ez3u55dl9n.cloudfront.net

    let html =
      index === 0
        ? `
    <img src="https://d3u8ez3u55dl9n.cloudfront.net/${urlSuffix}" alt="image-${index}" class="img--active"
      data-slide="${index}">
`
        : `
    <img src="https://d3u8ez3u55dl9n.cloudfront.net/${urlSuffix}" alt="image-${index}" data-slide="${index}">
`;

    imagesContainer.insertAdjacentHTML("beforeend", html);
  });

  const slides = document.querySelectorAll(".images > img");
  const leftBtn = document.querySelector(".left-arrow");
  const rightBtn = document.querySelector(".right-arrow");

  function createClonedSlides() {
    const firstSlideClone = slides[0].cloneNode(true);
    const lastSlideClone = slides[slides.length - 1].cloneNode(true);

    imagesContainer.appendChild(firstSlideClone);
    imagesContainer.insertBefore(lastSlideClone, slides[0]);

    return [firstSlideClone, lastSlideClone];
  }
  // 複製最前面與最後面的圖片
  const [firstSlideClone, lastSlideClone] = createClonedSlides();
  const slidesWithClones = document.querySelectorAll(".images > img");
  let currentSlide = 1;
  const maxSlide = slidesWithClones.length - 2;

  function goToSlide(slideIndex, transition = true) {
    slidesWithClones.forEach((slide, index) => {
      if (!transition) {
        slide.style.transition = "none";
      } else {
        slide.style.transition = "";
      }
      slide.style.transform = `translateX(${100 * (index - slideIndex)}%)`;
      slide.style.opacity = index === slideIndex ? "1" : "0";
    });
  }

  function nextSlide() {
    currentSlide++;
    if (currentSlide === maxSlide + 1) {
      goToSlide(currentSlide);
      setTimeout(() => {
        currentSlide = 1;
        goToSlide(currentSlide, false);
      }, 1500); //  match css transition setting
    } else {
      goToSlide(currentSlide);
    }
    activateDot(currentSlide);
  }

  function prevSlide() {
    currentSlide--;
    if (currentSlide < 0) {
      currentSlide = maxSlide;
      goToSlide(currentSlide, false);
      setTimeout(() => {
        currentSlide--;
        goToSlide(currentSlide, true);
      }, 1500); // match css transition setting
    } else if (currentSlide === 0) {
      // 處理 current slide 是 0 的狀況
      goToSlide(currentSlide);
      setTimeout(() => {
        currentSlide = maxSlide;
        goToSlide(currentSlide, false);
      }, 1500); // match css transition setting
    } else {
      goToSlide(currentSlide);
    }
    activateDot(currentSlide);
  }

  function activeSlide(slideIndex) {
    slidesWithClones.forEach((slide) => {
      slide.classList.remove("img--active");
    });
    const activeSlide = document.querySelector(
      `.images > img[data-slide="${slideIndex}"]`
    );
    if (activeSlide) {
      activeSlide.classList.add("img--active");
    }
  }

  // go to next slide
  leftBtn.addEventListener("click", prevSlide);
  rightBtn.addEventListener("click", nextSlide);

  document.addEventListener("keydown", (e) => {
    e.key === "ArrowLeft" && prevSlide();
    e.key === "ArrowRight" && nextSlide();
  });

  // Create Dots
  const dotContainer = document.querySelector(".dots");

  function createDots() {
    slides.forEach((_, index) => {
      dotContainer.insertAdjacentHTML(
        "beforeend",
        `<button class="dots__dot" data-slide="${index}"></button>`
      );
    });
  }

  function activateDot(slideIndex) {
    const dots = document.querySelectorAll(".dots__dot");
    dots.forEach((dot) => {
      dot.classList.remove("dots__dot--active");
    });
    // Adjust dot index for clones
    let dotIndex = slideIndex - 1;
    if (slideIndex === 0) {
      dotIndex = dots.length - 1;
    } else if (slideIndex === maxSlide + 1) {
      dotIndex = 0;
    }
    if (dots[dotIndex]) {
      dots[dotIndex].classList.add("dots__dot--active");
    }
  }

  dotContainer.addEventListener("click", (e) => {
    if (e.target.classList.contains("dots__dot")) {
      const { slide } = e.target.dataset;
      currentSlide = parseInt(slide) + 1;
      goToSlide(currentSlide);
      activateDot(currentSlide);
      activeSlide(currentSlide);
    }
  });

  goToSlide(currentSlide);
  goToSlide(currentSlide);
  createDots();
  activateDot(currentSlide);
  activeSlide(currentSlide);
}

imageSlider();

async function bookingTravel(attractionId, date, time, price, token) {
  // console.log(token);
  const response = await fetch("/api/booking", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${token}`,
    },
    body: JSON.stringify({ attractionId, date, time, price }),
  });

  if (!response.ok) {
    const message = `An error has occurred: ${response.statusText}`;
    throw new Error(message);
  }

  return await response.json();
}

function booking() {
  const bookingBtn = document.querySelector(".booking-btn");
  bookingBtn.addEventListener("click", async (e) => {
    // check login status
    e.preventDefault();
    const jwtToken = localStorage.getItem("session");
    if (jwtToken) {
      const userInfo = await checkLoginStatus(jwtToken);
      if (userInfo) {
        const id = window.location.pathname.split("/")[2];
        const date = document.querySelector("#travel-day");
        const selectedRadio = document.querySelector(
          'input[name="travel-time"]:checked'
        );
        const fee = document.querySelector(".fee");

        // 檢查日期是否已選擇
        if (!date.value) {
          alert("請選擇日期");
          return;
        }

        // 檢查是否選中任何 radio input
        if (!selectedRadio) {
          alert("請選擇一個時間段");
          return;
        }
        const result = await bookingTravel(
          id,
          date.value,
          selectedRadio.id,
          fee.textContent,
          jwtToken
        );
        window.location.href = "/booking";
      } else {
        modalControl("block");
        return;
      }
    } else {
      modalControl("block");
    }
  });
}

booking();
