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

function openModal(materia, materia_id, aula, aula_id) {
  // Obtém a referência do modal
  const modal = document.querySelector('.modal-background');
  const form = modal.querySelector('form');

  // Criar um novo elemento input
  const inputAula = document.createElement('input');
  inputAula.type = 'hidden';
  inputAula.name = 'aula_id';
  inputAula.value = aula_id;

  // Criar um novo elemento input
  const inputMateria = document.createElement('input');
  inputMateria.type = 'hidden';
  inputMateria.name = 'disciplina_id';
  inputMateria.value = materia_id;

  // Adicionar o novo elemento input ao formulário
  form.appendChild(inputAula);
  form.appendChild(inputMateria);

  // Atualiza o conteúdo do modal com a matéria
  const modalDesc = modal.querySelector('.modal-desc');
  modalDesc.innerHTML =
    'Cadastre-se na aula: ' + aula + ' da disciplina ' + materia;

  // Exibe o modal
  modal.classList.remove('hidden');
}
