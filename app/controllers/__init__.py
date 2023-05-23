def blueprints():
    from .disciplina_controller import bp as disciplina_bp
    from .aula_controller import bp as aula_bp
    from .presenca_controller import bp as presenca_bp
    from .historico_controller import bp as historico_bp

    return [disciplina_bp, aula_bp, presenca_bp, historico_bp]
