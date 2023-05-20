def blueprints():
    from .hello_controllers import bp as hello_bp
    from .disciplina_controller import bp as disciplina_bp

    return [hello_bp, disciplina_bp]
