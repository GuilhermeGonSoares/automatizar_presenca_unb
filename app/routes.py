from app import app, db 
from io import BytesIO
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from flask import render_template, redirect, url_for, flash, request, make_response
from .forms import RegisterForm, LoginForm
from .models import User, MatriculaProfessor, Aula, Presenca
from.utils import professor_required
from flask_login import login_user, login_required, logout_user, current_user
from .models import fuso_horario
from datetime import datetime, timezone, timedelta


@app.route('/login', methods=['GET', 'POST'])
def login_page():
    form = LoginForm()
    if form.validate_on_submit():
        attempted_user = User.query.filter_by(matricula=form.matricula.data).first()
        if attempted_user and attempted_user.check_password_correction(
                attempted_password=form.senha.data
        ):
            login_user(attempted_user)
            flash(f'Sucesso! Seja bem-vindo {attempted_user.nome} - {attempted_user.matricula}', category='success')
            if attempted_user.eh_professor:
                return redirect(url_for('professor_page'))
            else:
                return redirect(url_for('aluno_page'))   
        else:
            flash('Matrícula e senha não batem! Por favor, tente novamente', category='danger')

    return render_template('pages/login.html', form=form)


@app.route('/register', methods=['GET', 'POST'])
def register_page():
    form = RegisterForm()
    if form.validate_on_submit():
        matricula = form.matricula.data
        matricula_professor = MatriculaProfessor.query.filter_by(matricula=matricula).first()

        user = User(matricula=matricula,
                    email = form.email.data,
                    nome = form.nome.data,
                    senha=form.senha.data)

        user.eh_professor = True if matricula_professor else False

        db.session.add(user)
        db.session.commit()
        
        return redirect(url_for('login_page'))
    
    if form.errors != {}:
        for err_msg in form.errors.values():
            flash(f'There was an error with creating a user: {err_msg}', category='danger')
    return render_template('pages/register.html', form=form)


@app.route('/logout')
@login_required
def logout_page():
    logout_user()
    return redirect(url_for('login_page'))

@app.route('/gerenciarPresenca')
@login_required
@professor_required
def professor_page():
    print(request.remote_addr)
    aulas = Aula.query.all()
    return render_template('pages/professor.html', aulas=aulas)

@app.route('/marcarPresenca')
@login_required
def aluno_page():
    aula_presenca = []
    aulas = Aula.query.all()
    presencas = Presenca.query.join(Aula).filter_by(user=current_user).all()
    return render_template('pages/aluno.html', presencas=presencas)

@app.route('/confirmPresenca', methods=['POST'])
@login_required
def marcar_presenca():
    aula_id = request.form['aula_id']
    codigo = request.form['codigo']
    data = datetime.now(fuso_horario) #Data atual na hora de marcar presenca

    aula = Aula.query.filter_by(id=aula_id).first()
    data_com_fuso = aula.data.replace(tzinfo=timezone(timedelta(hours=-3)))

    intervalo_inicio_chamada_marcar_presenca = (data - data_com_fuso).seconds//60

    if aula.codigo != codigo:
        flash('Código incorreto, tente novamente.', 'danger')
        return redirect(url_for('aluno_page'))
    
    if intervalo_inicio_chamada_marcar_presenca > 20:
        flash(f'Já passou o tempo de 20 minutos para marcar presença. Tempo atual: {intervalo_inicio_chamada_marcar_presenca} minutos', 'danger')
        return redirect(url_for('aluno_page'))


    presenca = Presenca.query.filter_by(user=current_user, aula = aula).first()
    presenca.presente= True

    db.session.commit()
    print(presenca)
    print(presenca.presente)
    flash('Presença confirmada com sucesso!', 'success')
    return redirect(url_for('aluno_page'))

@app.route('/createAula', methods=['POST'])
@login_required
@professor_required
def create_aula_page():
    nome_aula = request.form['aula']
    nova_aula = Aula(nome=nome_aula, aberta=True)

    alunos = User.query.filter_by(eh_professor=False).all()
    for aluno in alunos:
        nova_aula.presencas.append(Presenca(presente=0, user=aluno))
  
    db.session.add(nova_aula)
    db.session.commit()
    return redirect(url_for('professor_page'))

@app.route('/deletarAula/<int:aula_id>', methods=['GET'])
@login_required
@professor_required
def deletar_aula(aula_id):
    print('aula', aula_id)
    aula = Aula.query.get(aula_id)
    if not aula:
        flash('Id da aula inválido!', 'danger')
        return redirect(url_for('professor_page'))
    
    db.session.delete(aula)
    db.session.commit()
    flash('Aula excluída com sucesso!', 'success')
    return redirect(url_for('professor_page'))

@app.route('/fecharPresenca/<int:aula_id>', methods=['GET'])
@login_required
@professor_required
def fechar_presenca_aula(aula_id):
    aula = Aula.query.get(aula_id)
    if not aula:
        flash('Id da aula inválido!', 'danger')
        return redirect(url_for('professor_page'))

    aula.aberta = False

    db.session.commit()
    flash('Presença fechada com sucesso', 'success')
    return redirect(url_for('professor_page'))


@app.route('/relatorioPresenca/<int:aula_id>', methods=['GET'])
@login_required
@professor_required
def relatorio_presenca(aula_id):
    presencas = Presenca.query.filter_by(aula_id=aula_id).all()
    aula = presencas[0].aula
    # Cria o documento PDF
    buff = BytesIO()
    doc = SimpleDocTemplate(buff, pagesize=landscape(letter))
    style = getSampleStyleSheet()
    data = [['Matrícula', 'Aula', 'Data da presença', 'Presente?']]
    for presenca in presencas:
        aluno = presenca.user  
        data_hora = presenca.data
        
        presente = 'Presente' if presenca.presente else 'Faltou'
        data_formatada = data_hora.strftime('%H:%M %d/%m/%Y') if presenca.presente else '----'
        
        data.append([presenca.user_matricula, aluno.nome, data_formatada, presente])
    table = Table(data)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 14),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
        ('ALIGN', (0, 1), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 12),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
    ]))
    elements = []
    elements.append(table)
    doc.build(elements)

    # Envia a resposta com o arquivo PDF
    response = make_response(buff.getvalue())
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = f'attachment; filename=relatorio_presencas_{aula.nome}.pdf'
    return response