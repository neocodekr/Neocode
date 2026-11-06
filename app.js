const switchButton = document.querySelector('#language-switch');
const menuButton = document.querySelector('#menu-toggle');
const nav = document.querySelector('#site-nav');
const form = document.querySelector('#contact-form');
const status = document.querySelector('#form-status');
const otherInquiry = document.querySelector('#other-inquiry');
const otherDetails = document.querySelector('#other-details');
let language = 'ko';

function updateOtherInquiry() {
  const isOther = form.querySelector('input[name="inquiry_type"]:checked')?.value === 'Other';
  otherInquiry.hidden = !isOther;
  otherDetails.disabled = !isOther;
  otherDetails.required = isOther;
  if (!isOther) otherDetails.value = '';
}

function syncChartVideo() {
  const chartVideo = document.querySelector('#chart-video');
  const variant = (window.matchMedia('(max-width: 700px)').matches ? 'Mobile' : '') + (language === 'ko' ? 'Ko' : 'En');
  const videoSource = chartVideo.dataset[`src${variant}`];
  chartVideo.poster = chartVideo.dataset[`poster${variant}`];
  if (chartVideo.getAttribute('src') !== videoSource) {
    chartVideo.setAttribute('src', videoSource);
    chartVideo.load();
    chartVideo.play().catch(() => {});
  }
}

function applyLanguage(next) {
  language = next;
  document.documentElement.lang = next;
  for (const element of document.querySelectorAll('[data-ko][data-en]')) {
    element.innerHTML = element.dataset[next];
  }
  for (const element of document.querySelectorAll('[data-placeholder-ko][data-placeholder-en]')) {
    element.placeholder = next === 'ko' ? element.dataset.placeholderKo : element.dataset.placeholderEn;
  }
  document.title = next === 'ko' ? 'NEOCODE — 감동을 전하는 소프트웨어' : 'NEOCODE — Software for meaningful moments';
  switchButton.innerHTML = next === 'ko' ? 'KOR <span aria-hidden="true">↗</span>' : 'ENG <span aria-hidden="true">↗</span>';
  switchButton.setAttribute('aria-label', next === 'ko' ? 'Switch to English' : '한국어로 전환');
  menuButton.setAttribute('aria-label', next === 'ko' ? '메뉴 열기' : 'Open menu');
  syncChartVideo();
}

switchButton.addEventListener('click', () => applyLanguage(language === 'ko' ? 'en' : 'ko'));
window.addEventListener('resize', syncChartVideo);
menuButton.addEventListener('click', () => {
  const isOpen = nav.classList.toggle('open');
  menuButton.setAttribute('aria-expanded', String(isOpen));
  menuButton.setAttribute('aria-label', language === 'ko' ? (isOpen ? '메뉴 닫기' : '메뉴 열기') : (isOpen ? 'Close menu' : 'Open menu'));
});
nav.addEventListener('click', event => {
  if (event.target.closest('a')) {
    nav.classList.remove('open');
    menuButton.setAttribute('aria-expanded', 'false');
  }
});
form.addEventListener('change', event => {
  if (event.target.name === 'inquiry_type') updateOtherInquiry();
});

form.addEventListener('submit', async event => {
  event.preventDefault();
  const button = document.querySelector('#submit-button');
  const data = new FormData(form);
  if (data.get('_honey')) return;
  button.disabled = true;
  status.textContent = language === 'ko' ? '문의 내용을 전송하고 있습니다…' : 'Sending your inquiry…';
  try {
    const response = await fetch('https://formsubmit.co/ajax/neocode.kr@gmail.com', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', Accept: 'application/json' },
      body: JSON.stringify(Object.fromEntries(data)),
    });
    const result = await response.json();
    if (!response.ok || !(result.success === true || result.success === 'true')) {
      if (/activation|activate form/i.test(result.message || '')) throw new Error('activation_required');
      throw new Error('submission_failed');
    }
    form.reset();
    updateOtherInquiry();
    status.textContent = language === 'ko' ? '문의가 접수되었습니다. 감사합니다.' : 'Your inquiry was submitted. Thank you.';
  } catch (error) {
    status.textContent = error.message === 'activation_required'
      ? (language === 'ko' ? '현재 문의 메일 수신 설정을 확인 중입니다. 입력 내용은 유지됩니다. 잠시 후 다시 시도해 주세요.' : 'Email delivery is being activated. Your details remain in the form. Please try again shortly.')
      : (language === 'ko' ? '전송하지 못했습니다. 입력 내용은 유지됩니다. 잠시 후 다시 시도해 주세요.' : 'Could not send. Your details remain in the form. Please try again shortly.');
  } finally {
    button.disabled = false;
  }
});

applyLanguage(language);
updateOtherInquiry();
