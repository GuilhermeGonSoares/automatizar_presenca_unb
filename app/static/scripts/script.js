const logSubject = document.querySelector('.log-subject-btn');
const modal = document.querySelector('.modal-background');
const closeBtn = document.querySelector('.close-btn');

function hideModal() {
  modal.classList.add('hidden');
}

function showModal() {
  modal.classList.remove('hidden');
}

logSubject.addEventListener('click', () => {
  showModal();
});

window.addEventListener('click', (event) => {
  if (event.target === modal) {
    hideModal();
  }
});

window.addEventListener('keydown', (event) => {
  if (event.key === 'Escape') {
    hideModal();
  }
});

closeBtn.addEventListener('click', () => {
  hideModal();
});