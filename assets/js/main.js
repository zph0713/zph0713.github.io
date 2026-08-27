/* Peihao's Garden — 轻量交互 */
(function () {
  "use strict";

  // 导航滚动阴影
  var header = document.getElementById("siteHeader");
  function onScroll() {
    if (!header) return;
    if (window.scrollY > 8) header.classList.add("scrolled");
    else header.classList.remove("scrolled");
  }
  window.addEventListener("scroll", onScroll, { passive: true });
  onScroll();

  // 滚动渐入
  var revealEls = document.querySelectorAll(".reveal");
  if (!("IntersectionObserver" in window)) {
    revealEls.forEach(function (el) { el.classList.add("in"); });
  } else {
    // 高内容元素（如长文章页）直接显示：threshold 要求元素 12% 进视口，
    // 超高元素永远达不到 → 正文永久透明（白屏 bug）
    var vh = window.innerHeight || 800;
    var pending = [];
    revealEls.forEach(function (el) {
      if (el.getBoundingClientRect().height > vh * 0.6) el.classList.add("in");
      else pending.push(el);
    });
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          entry.target.classList.add("in");
          io.unobserve(entry.target);
        }
      });
    }, { threshold: 0.12, rootMargin: "0px 0px -40px 0px" });
    pending.forEach(function (el) { io.observe(el); });
  }
})();
