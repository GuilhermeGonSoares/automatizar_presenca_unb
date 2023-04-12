from app import app, db 
from io import BytesIO
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from flask import render_template, redirect, url_for, flash, request, make_response
from .forms import RegisterForm, LoginForm, MatriculaForm
from .models import User, MatriculaAluno, MatriculaProfessor, Aula, Presenca, Disciplina, alunos_disciplinas
from.utils import professor_required
from flask_login import login_user, login_required, logout_user, current_user
from .models import fuso_horario
from datetime import datetime, timezone, timedelta


@app.errorhandler(404)
def page_not_found(e):
    return redirect(url_for('login'))

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
        matricula_aluno = MatriculaAluno.query.filter_by(matricula=matricula).first()

        if not matricula_professor and not matricula_aluno and matricula != '999999999':
            flash(f'Matrícula inválida, peça para ADMIN cadastra-la', category='danger')
            return redirect(url_for('register_page'))

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
    disciplinas = Disciplina.query.filter_by(professor=current_user).all()

    return render_template('pages/professor-disciplina.html', disciplinas=disciplinas)

@app.route('/disciplinasAluno')
@login_required
def aluno_page():
    disciplinas_matriculadas= current_user.disciplinas_matriculadas
    return render_template('pages/aluno-disciplina.html', disciplinas_matriculadas=disciplinas_matriculadas)

@app.route('/cadastrarDisciplina', methods=['POST'])
@login_required
def cadastrar_disciplina_page():
    codigo = request.form['disciplina_codigo']

    disciplina = Disciplina.query.filter_by(codigo=codigo).first()
    if not disciplina:
        flash(f'Código da disciplina inválido', category='danger')
        return redirect(url_for('aluno_page'))

    
    disciplina.alunos.append(current_user)
    
    aulas = disciplina.aulas

    for aula in aulas:
        aula.presencas.append(Presenca(presente=0, user=current_user))
    
    db.session.commit()
    flash(f'Disciplina cadastrada', category='success')
    return redirect(url_for('aluno_page'))


@app.route('/disciplina/<int:disciplina_id>')
@login_required
@professor_required
def disciplina_page(disciplina_id):
    disciplinas = Disciplina.query.filter_by(professor=current_user).all()
    disciplina = list(filter(lambda d: d.id == disciplina_id, disciplinas))[0]
    return render_template('pages/professor.html', disciplina=disciplina, disciplinas=disciplinas, aulas=disciplina.aulas)

@app.route('/disciplina_aluno/<int:disciplina_id>')
@login_required
def disciplina_aluno_page(disciplina_id):
    disciplinas_matriculadas = current_user.disciplinas_matriculadas
    disciplina = list(filter(lambda d: d.id == disciplina_id, disciplinas_matriculadas))[0]
    presencas = Presenca.query.join(Aula).filter(Aula.disciplina_id == disciplina_id).filter_by(user=current_user).all()
    
    return render_template('pages/aluno.html', disciplina=disciplina, disciplinas=disciplinas_matriculadas, presencas=presencas)


@app.route('/confirmPresenca/<int:disciplina_id>', methods=['POST'])
@login_required
def marcar_presenca(disciplina_id):
    aula_id = request.form['aula_id']
    codigo = request.form['codigo']
    data = datetime.now(fuso_horario) #Data atual na hora de marcar presenca

    aula = Aula.query.filter_by(id=aula_id).first()
    data_com_fuso = aula.data.replace(tzinfo=timezone(timedelta(hours=-3)))

    intervalo_inicio_chamada_marcar_presenca = (data - data_com_fuso).seconds//60

    if aula.codigo != codigo:
        flash('Código incorreto, tente novamente.', 'danger')
        return redirect(url_for('disciplina_aluno_page',disciplina_id=disciplina_id))
    
    if intervalo_inicio_chamada_marcar_presenca > 20:
        flash(f'Já passou o tempo de 20 minutos para marcar presença. Tempo atual: {intervalo_inicio_chamada_marcar_presenca} minutos', 'danger')
        return redirect(url_for('disciplina_aluno_page',disciplina_id=disciplina_id))


    presenca = Presenca.query.filter_by(user=current_user, aula = aula).first()
    presenca.presente= True

    db.session.commit()
    flash('Presença confirmada com sucesso!', 'success')
    return redirect(url_for('disciplina_aluno_page',disciplina_id=disciplina_id))

@app.route('/createAula/<int:disciplina_id>', methods=['POST'])
@login_required
@professor_required
def create_aula_page(disciplina_id):
    nome_aula = request.form['aula']
    nova_aula = Aula(nome=nome_aula, aberta=True, disciplina_id=disciplina_id)
    
    alunos = Disciplina.query.join(User).filter_by(id=disciplina_id).first().alunos
    for aluno in alunos:
        nova_aula.presencas.append(Presenca(presente=0, user=aluno))
  
    db.session.add(nova_aula)
    db.session.commit()
    return redirect(url_for('disciplina_page', disciplina_id=disciplina_id))

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


@app.route('/createDisciplina', methods=['POST'])
@login_required
@professor_required
def create_disciplina_page():
    user = current_user
    nome_disciplina = request.form['disciplina']
    nova_disciplina = Disciplina(nome=nome_disciplina, professor=user)
  
    db.session.add(nova_disciplina)
    db.session.commit()
    return redirect(url_for('disciplina_page', disciplina_id=nova_disciplina.id))


@app.route('/deletarDisciplina/<int:disciplina_id>', methods=['GET'])
@login_required
@professor_required
def deletar_disciplina(disciplina_id):
    disciplina = Disciplina.query.get(disciplina_id)
    if not disciplina:
        flash('Id da aula inválido!', 'danger')
        return redirect(url_for('professor_page'))
    
    db.session.delete(disciplina)
    db.session.commit()
    flash('Disciplina excluída com sucesso!', 'success')
    return redirect(url_for('professor_page'))

@app.route('/fecharPresenca/aula/<int:aula_id>/disciplina/<int:disciplina_id>', methods=['GET'])
@login_required
@professor_required
def fechar_presenca_aula(aula_id, disciplina_id):
    aula = Aula.query.get(aula_id)
    if not aula:
        flash('Id da aula inválido!', 'danger')
        return redirect(url_for('professor_page'))

    aula.aberta = False

    db.session.commit()
    flash('Presença fechada com sucesso', 'success')
    return redirect(url_for('disciplina_page', disciplina_id=disciplina_id))


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

@app.route('/admin', methods=['GET', 'POST'])
@login_required
def admin_page():
    form = MatriculaForm()

    if form.validate_on_submit():
        eh_professor = form.eh_professor.data

        if eh_professor:
            professor = MatriculaProfessor(matricula=form.matricula.data)
            db.session.add(professor)
            db.session.commit()
            return redirect(url_for('admin_page'))
        
        aluno = MatriculaAluno(matricula=form.matricula.data)
        db.session.add(aluno)
        db.session.commit()
        return redirect(url_for('admin_page'))
    
    professores = MatriculaProfessor.query.all()
    alunos = MatriculaAluno.query.all()

    return render_template('pages/admin.html', alunos=alunos, professores=professores)

