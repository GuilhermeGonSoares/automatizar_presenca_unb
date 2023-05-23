from app.webapp import mail
from flask_mail import Message


def send_email(email, total_aula, faltas, faltas_permitidas):
    msg_title = "Attendance - Reprovação por falta"
    sender = "noreply@app.com"
    msg = Message(msg_title, sender=sender, recipients=[email])
    msg.body = f"Este e-mail tem o objetivo de informar que é importante comparecer a todas as aulas da disciplina. Gostaríamos de lembrar que a próxima falta implicará em reprovação por falta. Até o momento, tivemos um total de {total_aula} aulas, das quais você faltou {faltas} vezes. Lembrando que, para este total de aulas ({total_aula}), você tem um limite de {faltas_permitidas} faltas permitidas. Portanto, é essencial que você esteja presente nas próximas aulas para garantir seu aproveitamento na disciplina."
    mail.send(msg)
    print("Email enviado com sucesso para ", email)
