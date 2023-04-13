# Automatizar presença

## DEPLOY:

- Realizado utilizando site RENDER
  <a src="https://unbpresenca.onrender.com/login">https://unbpresenca.onrender.com/login</a>

## Objetivos:

- Permitir que o aluno marque presença online, para evitar que o professor perca muito tempo com a chamada oral tradicional.
- Impedir que os alunos possam burlar o sistema marcando presença sem estar na sala de aula.

## Implementação

- Os alunos precisarão de fornecer o código da disciplina para poder se cadastrar nela.
- Os alunos precisarão fornecer um código, que será gerado para a aula, para validar a sua presença em sala de aula.
- Para que não tenha só esse codigo que poderia ser passado para outros alunos, fora da sala, pensei em duas possibilidades:

  1. Permitir que apenas usuários utilizando o wifi da faculdade possam realizar login e utilizar o sistema. (FALTA IMPLEMENTAR)
  2. Além disso, estou analisando a viabilidade de utilizar Geolocalização, para que apenas alunos dentro de um raio da sala de aula poderiam marcar presença

### Login/ Registro

- Para o registro foi utilizado uma tabela no banco de dados("matricula_professor") para registrar as matrículas dos professores(essa matrícula é adicionada pelo ADMIN).
- Ao realizar o registro é verificado se a matrícula fornecida está na tabela "matricula_professor" se estiver o usuário é definido como professor, caso contrário é definido como aluno.
<p align="left">
    <img
      src="https://user-images.githubusercontent.com/99030229/231774087-986a348a-61e1-4d22-ae68-c6cd401275ce.png"
      alt="Página de login"
      min-width="500"
      min-height="400"
    />
    <img
      src="https://user-images.githubusercontent.com/99030229/231775606-3d1ff9b2-a079-41ee-8d43-2d601bfb4f6b.png"
      alt="Página de registro"
      min-width="500"
      min-height="400"
    />
</p>

## Login -> PROFESSOR:

- O professor tem acesso a página que cria disciplina e gerencia suas disciplinas e os alunos cadastrados.
- Cada disciplina tem um código que deve ser fornecido ao estudante para que ele possa se matricular na disciplina.
<p align="center">
    <img
      src="https://user-images.githubusercontent.com/99030229/231776088-99feddb7-9c65-4cac-9401-b215333b373a.png"
      alt="Disciplinas do professor + alunos cadastrados"
    />
</p>

- Para cada disciplina o professor irá registrar a sua aula do dia e isso deve ser feito durante a aula, visto que o usuário tem um tempo de 20 minutos para marcar presença, contando desde o horário que o professor abriu a aula.
- Registro de uma aula:
<p align="center">
    <img
      src="https://user-images.githubusercontent.com/99030229/231778209-d86a0cf5-a8bf-4911-9041-b2680024595e.png"
      alt="Criando uma aula"
    />
</p>

- É gerado automaticamente um código e o professor depois que abrir a aula pode fechar a qualquer momento, mas se ele nao fechar não tem problema, porque os alunos não poderão marcar depois de 20 minutos que foi aberto.

<p align="center">
    <img
      src="https://user-images.githubusercontent.com/99030229/231778975-115eb98f-fa59-48e2-8f70-70479fbe0e43.png"
      alt="Aulas criadas"
    />
</p>

- O botão RELATÓRIO gera um pdf com todos os alunos cadastrado, mostrando a Matrícula, Nome, Data que marcou a presença e se estava PRESENTE ou se FALTOU

## Login -> ALUNO:

- O aluno tem acesso a página para realizar o cadastro em uma disciplina e verificar em quais disciplinas ele esta cadastrado e qual é o professor:

<p align="center">
    <img
      src="https://user-images.githubusercontent.com/99030229/231783439-34baeb52-5015-4867-8e81-82c8c8b523e2.png"
      alt="Disciplinas do aluno"
    />
</p>

## Página para marcar a presença:

<p align="center">
    <img
      src="https://user-images.githubusercontent.com/99030229/231785518-bbbf07e4-8897-42e0-956b-7dd7ac7c9a56.png"
      alt="Marcar presença"
    />
</p>

## Registro das presenças do aluno:

<p align="center">
    <img
      src="https://user-images.githubusercontent.com/99030229/231786094-2bbdbccc-a9d1-46ca-8e74-ef487ae758db.png"
      alt="Marcar presença"
    />
</p>
