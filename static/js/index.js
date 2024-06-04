const login = document.querySelector(".menu li:nth-child(2)");
const modalContainer = document.querySelector(".modal-container");
const loginForm = document.querySelector(".login-container");
const loginEmailInput = document.querySelector("#login-email");
const loginEmailPassword = document.querySelector("#login-password");
const loginErrorDiv = document.querySelector(".login-error-message");
const registerForm = document.querySelector(".register-container");
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
      console.error("Error:", errorData);
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
  });
}

handleRegister();

function logoutEvent() {
  login.removeEventListener("click", logoutEvent);
  login.textContent = "登入/註冊";
  login.addEventListener("click", loginEvent);
  sessionStorage.removeItem("session");
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
      loginErrorDiv.textContent = errorData.message;
    } else {
      const data = await response.json();
      loginEmailInput.value = "";
      loginEmailPassword.value = "";
      modalControl("hidden");
      login.removeEventListener("click", loginEvent);
      login.textContent = "登出";
      login.addEventListener("click", logoutEvent);
      return data;
    }
  };

  loginForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    const jwtToken = await loginUser(loginEmail.value, loginPassword.value);
    sessionStorage.setItem("session", jwtToken.token);
  });
}

handleLogin();

// token verify
async function checkLoginStatus(token) {
  const response = await fetch("/api/user/auth", {
    method: "GET",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${token}`,
    },
  });
  console.log(response);
  const data = await response.json();
  if (data) {
    console.log(data);
    return data;
  } else {
    modalControl("block");
    return false;
  }
}

// handle booking plan
function handleBookingPlan() {
  const bookinPlanBtn = document.querySelector(".menu li:nth-child(1)");
  bookinPlanBtn.addEventListener("click", async (e) => {
    e.preventDefault();
    const jwtToken = sessionStorage.getItem("session");
    if (jwtToken) {
      const userInfo = await checkLoginStatus(jwtToken);
      console.log(userInfo);
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
// main

function createElementWithClass(element, className) {
  let container = document.createElement(element);
  container.className = className;
  return container;
}

async function fetchMRT() {
  const response = await fetch("/api/mrts");
  if (response.ok) {
    const data = await response.json();
    return data.data;
  } else {
    console.log("error on fetching mtrs");
  }
}

// scroll mrt list bar
async function listBar() {
  const mrts = await fetchMRT();

  let root_scrollAttraction = document.querySelector(".scroll-attraction");

  let prevBtn = createElementWithClass("div", "scroll-btn prev-btn");
  let prevBtnImage = createElementWithClass("img", "prev-btn-img");
  prevBtnImage.src = "../static/images/buttons/arrow-left-default.png";
  prevBtn.appendChild(prevBtnImage);

  let nextBtn = createElementWithClass("div", "scroll-btn next-btn");
  let nextBtnImage = createElementWithClass("img", "next-btn-img");
  nextBtnImage.src = "../static/images/buttons/arrow-right-default.png";
  nextBtn.appendChild(nextBtnImage);

  let mrtList = createElementWithClass("div", "mrt-list");
  mrts.forEach((mrt) => {
    let listItem = createElementWithClass("button", "list-item");
    listItem.textContent = mrt;
    mrtList.appendChild(listItem);
  });
  root_scrollAttraction.appendChild(prevBtn);
  root_scrollAttraction.appendChild(mrtList);
  root_scrollAttraction.appendChild(nextBtn);

  document.querySelector(".prev-btn").addEventListener("click", function () {
    const mrtList = document.querySelector(".mrt-list");
    // 每次點擊滾動左移 300px
    mrtList.scrollLeft -= 800;
  });

  document.querySelector(".next-btn").addEventListener("click", function () {
    const mrtList = document.querySelector(".mrt-list");
    // 每次點擊滾動右移 300px
    mrtList.scrollLeft += 800;
  });

  // add event listner on scroll list
  const scrollMrtList = document.querySelectorAll(".list-item");
  const searchInput = document.querySelector(".search-wrapper > input");
  const searchBtn = document.querySelector(".search-wrapper > button");
  scrollMrtList.forEach((mrt) => {
    mrt.addEventListener("click", () => {
      searchInput.value = mrt.textContent;
      searchBtn.click();
    });
  });
}

listBar();

function goToAttraction(attractionId) {
  window.location = `/attraction/${attractionId}`;
}

// create attraction element
function createAttractionElement(data, imgIndex) {
  let attractionWrapper = createElementWithClass("li", "attraction-wrapper");
  let attraction = createElementWithClass(
    "div",
    `attraction attraction-${imgIndex}`
  );

  let attractionFigure = createElementWithClass("div", "attraction-figure");
  let attractionImgWrapper = createElementWithClass("div", "image-wrapper");
  let attractionImg = createElementWithClass("img", "attraction-img");
  attractionImg.src = "./static/images/loading.gif";
  attractionImg.dataset.src = `https://${data.images[0]}`;

  attractionImg.onerror = function () {
    this.onerror = null; // 避免無窮迴圈
    this.alt = "目前無圖片可顯示";
    this.style.textAlign = "center";
    this.style.lineHeight = this.height + "px"; // 設置行高使文字垂直置中
    this.style.fontWeight = "bold";
    this.style.color = "#666";
  };

  const lazyloading = function (entries) {
    // console.log(entries);
    entries.forEach((entry) => {
      if (entry.isIntersecting) {
        attractionImg.src = attractionImg.dataset.src;
        imgObserver.unobserve(attractionImg);
      }
    });
  };
  const obsOptions = {
    rootMargin: "50px 0px",
    root: null,
    threshold: 0,
  };
  const imgObserver = new IntersectionObserver(lazyloading, obsOptions);
  imgObserver.observe(attractionImg);

  attractionImgWrapper.appendChild(attractionImg);

  let attractionTitle = createElementWithClass("div", "attraction-title");
  let attractionTitleP = document.createElement("p");
  attractionTitleP.textContent = data.name;
  attractionTitle.appendChild(attractionTitleP);

  attractionFigure.appendChild(attractionImgWrapper);
  attractionFigure.appendChild(attractionTitle);

  let attractionInfo = createElementWithClass("div", "attraction-info");
  let attractionCategory = createElementWithClass("div", "attraction-category");
  attractionCategory.textContent = data.category;
  let attractionMrt = createElementWithClass("div", "attraction-mrt");
  attractionMrt.textContent = data.mrt;
  attractionInfo.appendChild(attractionCategory);
  attractionInfo.appendChild(attractionMrt);

  attraction.appendChild(attractionFigure);
  attraction.appendChild(attractionInfo);

  attractionWrapper.appendChild(attraction);

  attractionWrapper.addEventListener("click", () => {
    // 在這裡處理點擊事件，例如導航到特定景點頁面
    window.location = `/attraction/${data.id}`;
  });

  return attractionWrapper;
}

// fetch attraction
async function fetchAttraction(page = 0, keyword = "") {
  let response = await fetch(
    `/api/attractions?page=${page}&keyword=${keyword}`,
    {
      method: "GET",
    }
  );
  let data = await response.json();
  return data;
}

// create attraction list
async function createAttractionList() {
  let data;
  let imgIndex = 0;
  let attractionContainer = document.querySelector(".attractions-container");
  let searchInput = document.querySelector(".search-wrapper > input");
  let searchBtn = document.querySelector(".search-wrapper > button");
  let footer = document.querySelector("footer");
  let isLoading = false;

  const loadingAttractions = async function (entries) {
    entries.forEach(async (entry) => {
      if (entry.isIntersecting && data.nextPage !== null && !isLoading) {
        // 加載並顯示下一頁的資料
        isLoading = true;
        data = await fetchAttraction(data.nextPage, searchInput.value);
        for (let i = 0; i < data.data.length; i++) {
          let attraction = createAttractionElement(data.data[i], imgIndex);
          attractionContainer.appendChild(attraction);
          imgIndex++;
        }
        isLoading = false;
        // 如果沒有下一頁，停止觀察 footer
        if (data.nextPage === null) {
          attractionObserver.unobserve(footer);
        }
      }
    });
  };

  const obsOptions = {
    rootMargin: "50px 0px",
    root: null,
    threshold: 0,
  };

  const attractionObserver = new IntersectionObserver(
    loadingAttractions,
    obsOptions
  );

  searchBtn.addEventListener("click", async () => {
    data = await fetchAttraction(0, searchInput.value);
    attractionContainer.innerHTML = "";

    // 加載第一批資料並添加到畫面上
    let imgIndex = 0;
    for (let i = 0; i < data.data.length; i++) {
      let attraction = createAttractionElement(data.data[i], imgIndex);
      attractionContainer.appendChild(attraction);
      imgIndex++;
    }

    // 觀察 footer 以加載更多景點
    if (data.nextPage) {
      attractionObserver.observe(footer);
    }
  });

  data = await fetchAttraction(0);
  for (let i = 0; i < data.data.length; i++) {
    let attraction = createAttractionElement(data.data[i], imgIndex);
    attractionContainer.appendChild(attraction);
    imgIndex++;
  }

  // 觀察 footer 以加載更多景點
  if (data.nextPage) {
    attractionObserver.observe(footer);
  }
}

createAttractionList();
