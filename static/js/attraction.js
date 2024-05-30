const login = document.querySelector(".menu:nth-child(2)");
const modalContainer = document.querySelector(".modal-container");
const loginForm = document.querySelector(".login-container");
const registerForm = document.querySelector(".register-container");
const loginExit = document.querySelector(".login-form-exit");
const registerExit = document.querySelector(".register-form-exit");
const overlay = document.querySelector(".overlay");
const formExit = document.querySelectorAll(".form-exit");
const toRegisterLink = document.querySelector(".to-register-link");
const toLoginLink = document.querySelector(".to-login-link");
const footer = document.querySelector("footer");

login.addEventListener("click", () => {
  overlay.classList.remove("hidden");
  // gradientBar.classList.remove("hidden");
  loginForm.classList.remove("hidden");
  modalContainer.classList.remove("hidden");
});

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

// section 1
const data = await fetchAttraction(window.location.pathname.split("/")[2]);

function createElementWithClass(element, className) {
  let container = document.createElement(element);
  container.className = className;
  return container;
}

async function fetchAttraction(id) {
  const response = await fetch(`/api/attraction/${id}`);
  if (response.ok) {
    const data = await response.json();
    return data.data;
  } else {
    console.log("error on fetching mtrs");
  }
}

async function createPage() {
  const profileContainer = document.querySelector(".profile");
  const section2Container = document.querySelector(".section2");
  let html = `
  <h3 class="attraction-name">${data.name}</h3>
  <p class="attraction-cat-mrt"><span class="attraction-category">${data.category}</span> at <span
      class="attraction-mrt">${data.mrt}</span></p>
  <div class="booking-form-wrapper">
    <form action="">
      <p class="form-title">訂購導覽行程</p>
      <p>以此景點為中心的一日行程，帶您探索城市角落故事</p>
      <div class="travel-day-wrapper">
        <label for="travel-day" class="travel-day-label">選擇日期: </label>
        <input type="date" id="travel-day">
      </div>
      <div class="travel-time-wrapper">
        <label class="travel-time-label">選擇時間: </label>
        <input type="radio" name="travel-time" id="morning" value="上半天">
        <label for="morning" class="morning-label">上半天</label>
        <input type="radio" name="travel-time" id="afternoon" value="下半天">
        <label for="afternoon" class="afternoon-label">下半天</label>
      </div>
      <p class="travel-fee">導覽費用: <span class="fee">新台幣2000元</span></p>
      <button type="submit">開始預約行程</button>
    </form>
  `;
  profileContainer.insertAdjacentHTML("beforeend", html);

  //   更改 fee
  const morningRadio = document.getElementById("morning");
  const afternoonRadio = document.getElementById("afternoon");
  const feeElement = document.querySelector(".fee");

  morningRadio.addEventListener("change", () => {
    if (morningRadio.checked) {
      feeElement.textContent = "新台幣2000元";
    }
  });

  afternoonRadio.addEventListener("change", () => {
    if (afternoonRadio.checked) {
      feeElement.textContent = "新台幣2500元";
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

// image slider
function imageSlider() {
  const imagesContainer = document.querySelector(".images");

  data.images.forEach((image, index) => {
    let html =
      index === 0
        ? `
    <img src="https://${image}" alt="image-${index}" class="img--active"
      data-slide="${index}">
`
        : `
    <img src="https://${image}" alt="image-${index}" data-slide="${index}">
`;

    imagesContainer.insertAdjacentHTML("beforeend", html);
  });

  const slides = document.querySelectorAll(".images > img");
  const leftBtn = document.querySelector(".left-arrow");
  const rightBtn = document.querySelector(".right-arrow");
  let currentSlide = 0;
  const maxSlide = slides.length;

  function goToSlide(currentSlide) {
    slides.forEach((slide, index) => {
      slide.style.transform = `translateX(${100 * (index - currentSlide)}%)`;
    }); // currentSide = 1; -100%, 0%, 100%, 200%
  }

  function nextSlide() {
    if (currentSlide === maxSlide - 1) {
      currentSlide = 0;
    } else {
      currentSlide++;
    }

    goToSlide(currentSlide);
    activateDot(currentSlide);
    activeSlide(currentSlide);
  }

  function prevSlide() {
    if (currentSlide === 0) {
      currentSlide = maxSlide - 1;
    } else {
      currentSlide--;
    }
    goToSlide(currentSlide);
    activateDot(currentSlide);
    activeSlide(currentSlide);
  }

  function activeSlide(slide) {
    slides.forEach((slide) => {
      slide.classList.remove("img--active");
    });
    document
      .querySelector(`.images > img[data-slide="${slide}"]`)
      .classList.add("img--active");
  }

  goToSlide(0);
  activeSlide(0);

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
  createDots();
  activateDot(0);

  function activateDot(slide) {
    document.querySelectorAll(".dots__dot").forEach((dot) => {
      dot.classList.remove("dots__dot--active");
    });

    document
      .querySelector(`.dots__dot[data-slide="${slide}"]`)
      .classList.add("dots__dot--active");
  }

  dotContainer.addEventListener("click", (e) => {
    if (e.target.classList.contains("dots__dot")) {
      const { slide } = e.target.dataset;
      goToSlide(slide);
      activateDot(slide);
      activeSlide(slide);
    }
  });
}

imageSlider();
