# ============================================
# ANXIETY CHAT - CÓDIGO COMPLETO FUNCIONAL
# ============================================

from flask import Flask, render_template_string, request, jsonify, session, redirect, url_for
import json
import os
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'anxiety-chat-curn-2024-secret-key'

# ============================================
# BASE DE DATOS
# ============================================

def load_json(filename):
    if os.path.exists(filename):
        with open(filename, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_json(filename, data):
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

users_db = load_json('users.json')
sessions_db = load_json('sessions.json')

# ============================================
# BASE DE CONOCIMIENTO EXPANDIDA
# ============================================

KNOWLEDGE = {
    "nervios|nervioso|nerviosa|tension|tenso|tensa|ansiosa|ansioso": {
        "respuesta": "Entiendo que te sientes nervioso(a) o tenso(a). La ansiedad es una emoción completamente normal, es una respuesta natural del cuerpo ante el estrés.",
        "recomendacion": "💙 Técnica de respiración 4-2-6: Inhala por la nariz contando hasta 4, retén 2 segundos, exhala por la boca contando hasta 6. Repite durante 5 minutos."
    },
    "insomnio|dormir|sueño|despertar|intranquilo|desvelo": {
        "respuesta": "Los problemas de sueño son muy comunes cuando hay ansiedad. El insomnio puede estar relacionado con preocupaciones constantes que no nos dejan descansar.",
        "recomendacion": "🌙 Establece un horario fijo para dormir (7-8 horas), evita pantallas 1 hora antes, crea un ambiente oscuro y fresco. Prueba técnicas de relajación muscular."
    },
    "dolor|duele|adolorido|molestia| dolor de cabeza|migraña": {
        "respuesta": "El dolor físico puede estar muy relacionado con la ansiedad. Cuando estamos ansiosos, nuestros músculos se tensan y esto causa dolor en cuello, hombros, espalda y cabeza.",
        "recomendacion": "🌿 Aplica calor local, haz estiramientos suaves, practica relajación muscular progresiva. Si el dolor es intenso o persistente, consulta a un doctor."
    },
    "palpitaciones|corazon|pecho|presion|taquicardia|late": {
        "respuesta": "Las palpitaciones o sensación de presión en el pecho son síntomas físicos comunes de la ansiedad. Tu corazón late más rápido porque tu cuerpo está en modo alerta.",
        "recomendacion": "❤️ Respiración consciente: Siéntate, respira lenta y profundamente. Esto envía señales de calma a tu cerebro. Si son muy frecuentes, consulta a un médico."
    },
    "concentracion|concentrar|concentra|memoria|olvido|estudiar|recordar|enfoca|distraigo": {
        "respuesta": "La dificultad para concentrarse es un síntoma cognitivo frecuente de la ansiedad. Tu cerebro está usando recursos en preocuparte.",
        "recomendacion": "🧠 Técnica Pomodoro: Estudia 25 minutos con foco total, descansa 5 minutos. Elimina distracciones. Practica mindfulness 10 minutos diarios."
    },
    "miedo|temor|panico|asustado|susto|terror": {
        "respuesta": "El miedo intenso o ataques de pánico son episodios de miedo repentino muy fuerte. Puede ser muy aterrador, pero no es peligroso y pasa en 10-15 minutos.",
        "recomendacion": "🆘 Durante un ataque: Respira lento, nombra 5 cosas que ves, 4 que tocas, 3 que escuchas (técnica 5-4-3-2-1). Si son frecuentes, busca terapia."
    },
    "estomago|nauseas|apetito|gastro|digestivo|vomito|vomitar": {
        "respuesta": "Las molestias estomacales están muy vinculadas a la ansiedad. Existe una conexión directa entre tu cerebro y tu sistema digestivo.",
        "recomendacion": "🍃 Come porciones pequeñas y frecuentes, evita café y picante. Toma infusiones de manzanilla. Si persiste, consulta a un gastroenterólogo."
    },
    "temblor|temblar|debilidad|muscular|tiemblo": {
        "respuesta": "Los temblores son manifestaciones físicas de la ansiedad. Tu cuerpo libera adrenalina cuando está ansioso, causando temblores en manos y piernas.",
        "recomendacion": "💪 Relajación muscular: Tensa cada grupo muscular 5 segundos y suelta. También ayuda hacer ejercicio regular como yoga o caminar."
    },
    "mareo|mareado|vision|borrosa|zumbido|vertigo|mareada": {
        "respuesta": "Los mareos o visión borrosa pueden aparecer durante episodios de ansiedad, especialmente si estás hiperventilando (respirando muy rápido).",
        "recomendacion": "👁️ Siéntate de inmediato, baja la cabeza, respira lento. Mantente hidratado. Si son frecuentes, consulta a un médico."
    },
    "preocupada|preocupado|preocupacion|preocupa": {
        "respuesta": "La preocupación constante por todo, incluso sin motivo claro, es el síntoma principal de la ansiedad generalizada.",
        "recomendacion": "📝 Dedica 15 minutos diarios a escribir TODAS tus preocupaciones. Fuera de ese tiempo, pospón las preocupaciones. Esto ayuda a tu cerebro."
    },
    "cansancio|cansado|fatiga|agotado|exhausto": {
        "respuesta": "La fatiga constante puede ser resultado de ansiedad prolongada. Tu cuerpo gasta mucha energía cuando está en alerta constante.",
        "recomendacion": "⚡ Prioriza el sueño (7-8 horas), come nutritivo, toma descansos reales, sal a caminar 20 minutos diarios. El ejercicio te dará más energía."
    },
    "triste|tristeza|deprimido|depresion|lloro|llorar": {
        "respuesta": "La tristeza puede acompañar a la ansiedad. Es normal sentirte abrumado(a). La tristeza persistente junto con ansiedad requiere apoyo adicional.",
        "recomendacion": "💚 Habla con alguien de confianza. Mantén una rutina diaria. Sal al sol 15 minutos. Si dura más de 2 semanas, busca ayuda profesional."
    },
    "solo|sola|aislado|aislada|nadie": {
        "respuesta": "El aislamiento puede aumentar la ansiedad. Cuando nos aislamos perdemos el apoyo social que necesitamos. Es un círculo que hay que romper.",
        "recomendacion": "👥 Pequeños pasos: Empieza con una persona de confianza, un mensaje, una llamada. Las conexiones sociales protegen contra la ansiedad."
    },
    "estres|estresado|estresante|presionado|estres academico|estres laboral": {
        "respuesta": "El estrés académico o laboral constante es una causa muy común de ansiedad en estudiantes. Las exigencias pueden generar una carga muy pesada.",
        "recomendacion": "📚 Organiza tus tareas con prioridades, divide proyectos grandes, aprende a decir no, toma descansos. Tu salud mental es más importante."
    },
    "respirar|respiracion|aire|ahogo|falta|falta de aire": {
        "respuesta": "Sentir que respiras más rápido o te cuesta llenar los pulmones son síntomas respiratorios de ansiedad. La hiperventilación puede empeorar la sensación.",
        "recomendacion": "🫁 Respiración 4-7-8: Inhala 4 segundos, retén 7, exhala 8. Repite 4 veces. Es muy poderosa para calmar el sistema nervioso."
    },
    "irritable|irritabilidad|enojado|molesto|ira|rabia": {
        "respuesta": "La irritabilidad es un síntoma emocional frecuente con ansiedad. Te enojas fácilmente porque estás sobrecargado(a) emocionalmente.",
        "recomendacion": "😤 Identifica tus disparadores, toma pausas cuando sientas que aumenta (cuenta hasta 10), haz ejercicio para liberar tensión."
    },
    "cabeza|migrana|jaqueca|cefalea|dolor de cabeza": {
        "respuesta": "Los dolores de cabeza tensionales son muy comunes con la ansiedad. La tensión en cuello y hombros puede causar dolor que dura horas.",
        "recomendacion": "🧊 Masajea sienes y cuello, aplica frío o calor, descansa en lugar oscuro, estira el cuello suavemente, mantente hidratado."
    },
    "suicidio|matarme|morir|acabar|quitarme": {
        "respuesta": "⚠️ Lo que me cuentas es MUY IMPORTANTE y me preocupa tu bienestar. Los pensamientos sobre hacerte daño indican que necesitas apoyo profesional URGENTE.",
        "recomendacion": "🆘 BUSCA AYUDA AHORA: Línea Nacional: 01 8000 123 456 (24/7). Centro de Crisis: 106. Universidad: bienestar@curn.edu.co. NO ESTÁS SOLO(A)."
    },
    "autolesion|cortarme|lastimarme|hacerme daño": {
        "respuesta": "⚠️ La autolesión es una señal de dolor emocional muy intenso. Es importante que busques ayuda profesional para aprender formas más saludables.",
        "recomendacion": "🆘 Busca apoyo inmediato: Línea 24/7: 01 8000 123 456. Hay formas de sentir alivio sin hacerte daño: hielo en la piel, dibujar, ejercicio intenso."
    },
    "examen|parcial|evaluacion|prueba": {
        "respuesta": "La ansiedad ante exámenes es muy común. Tu cuerpo reacciona al examen como amenaza, activando estrés. Esto puede hacerte olvidar lo que sabes.",
        "recomendacion": "📖 Estudia días antes, duerme bien, llega temprano, respira profundo antes de empezar, lee todas las preguntas, empieza por las fáciles."
    },
    "familia|padres|mama|papa|hermano": {
        "respuesta": "Las dificultades familiares pueden ser fuente importante de ansiedad. Los conflictos o expectativas familiares afectan profundamente nuestro bienestar.",
        "recomendacion": "👨‍👩‍👧‍👦 Establece límites saludables, comunica tus necesidades claramente, busca apoyo en amigos, considera terapia familiar si es posible."
    },
    "pareja|novio|novia|relacion|ruptura|ex": {
        "respuesta": "Los problemas de pareja o rupturas pueden generar mucha ansiedad. Las relaciones son importantes para nuestro bienestar emocional.",
        "recomendacion": "💔 Date tiempo para procesar, mantén rutinas saludables, apóyate en amigos. Si hay violencia, busca ayuda inmediata."
    },
    "dinero|economico|deuda|plata|pagar|financiero": {
        "respuesta": "Las preocupaciones económicas son una fuente muy real de ansiedad. El estrés financiero puede sentirse abrumador.",
        "recomendacion": "💰 Haz un presupuesto realista, busca becas o ayudas universitarias, habla con orientación estudiantil sobre recursos disponibles."
    },
    "futuro|carrera|trabajo|empleo|graduarme|graduacion": {
        "respuesta": "La incertidumbre sobre el futuro es común en estudiantes. Es natural preocuparse por tu carrera, pero la preocupación excesiva puede paralizarte.",
        "recomendacion": "🎯 Enfócate en el presente (qué puedes hacer HOY), establece metas pequeñas, explora opciones, busca prácticas. El camino se hace caminando."
    },
    "rendimiento|notas|calificaciones|reprobar|perder|fracaso": {
        "respuesta": "La presión por el rendimiento académico puede generar ansiedad intensa. Una nota no define tu valor como persona ni tu inteligencia.",
        "recomendacion": "📊 Establece expectativas realistas, celebra pequeños logros, aprende de errores, busca tutoría si la necesitas. Tu salud mental es prioridad."
    },
    "perfeccionista|perfeccion|todo perfecto|todo bien": {
        "respuesta": "El perfeccionismo está muy relacionado con la ansiedad. Cuando nos exigimos ser perfectos, vivimos en constante miedo al fracaso.",
        "recomendacion": "🎨 Permite errores intencionales, practica el 'suficientemente bueno', cuestiona tus estándares. La excelencia es buena, la perfección es imposible."
    },
    "social|gente|personas|hablar|publico": {
        "respuesta": "La ansiedad social es el miedo a hablar o actuar frente a otras personas por temor al juicio. Es más común de lo que crees.",
        "recomendacion": "👥 Empieza con grupos pequeños, practica con personas de confianza, recuerda que todos tienen inseguridades. La práctica reduce el miedo."
    },
    "ataques|crisis|ataque de ansiedad": {
        "respuesta": "Los ataques de ansiedad son episodios intensos pero temporales. No son peligrosos aunque se sientan aterradores. Duran 10-15 minutos.",
        "recomendacion": "🆘 Durante un ataque: Recuerda que pasará, respira lento, usa técnica 5-4-3-2-1, busca lugar seguro. Si son frecuentes, busca terapia."
    },
    "culpa|culpable|mi culpa|arrepentimiento": {
        "respuesta": "La culpa excesiva puede ser síntoma de ansiedad. Es importante diferenciar entre responsabilidad real y culpa irracional.",
        "recomendacion": "💭 Pregúntate: ¿realmente fue mi culpa? ¿Qué haría si fuera un amigo? Perdónate, todos cometemos errores. Aprende y sigue adelante."
    },
    "inseguro|inseguridad|no puedo|no soy capaz": {
        "respuesta": "La inseguridad y baja autoestima suelen acompañar la ansiedad. Cuestionas constantemente tus capacidades.",
        "recomendacion": "💪 Haz una lista de tus logros, por pequeños que sean. Desafía pensamientos negativos: ¿hay evidencia real? Habla contigo con compasión."
    },
    "medicamento|pastillas|medicina|antidepresivo": {
        "respuesta": "Los medicamentos pueden ser útiles para la ansiedad en algunos casos. Siempre deben ser recetados y supervisados por un psiquiatra.",
        "recomendacion": "💊 Si consideras medicación, consulta con un psiquiatra. La terapia cognitivo-conductual es muy efectiva. Muchas veces se combinan ambas."
    },
    "terapia|psicologo|psiquiatra|ayuda profesional": {
        "respuesta": "Buscar terapia es un paso muy valiente y efectivo. La terapia cognitivo-conductual tiene excelentes resultados para la ansiedad.",
        "recomendacion": "🏥 Universidad: bienestar@curn.edu.co. Psicólogo trabaja con terapia de conversación. Psiquiatra puede recetar medicación si es necesario."
    },
    "alcohol|drogas|sustancias|fumar|cigarrillo": {
        "respuesta": "Algunas personas usan alcohol o drogas para calmar la ansiedad, pero esto la empeora a largo plazo y puede crear dependencia.",
        "recomendacion": "⚠️ El alcohol y drogas son escape temporal pero agravan la ansiedad. Busca formas saludables de manejarla: ejercicio, terapia, técnicas de relajación."
    },
    "relaja|relajacion|calmarme|tranquilizar": {
        "respuesta": "Las técnicas de relajación son muy efectivas para manejar la ansiedad. Requieren práctica constante para mejores resultados.",
        "recomendacion": "🧘 Prueba: Respiración 4-7-8, relajación muscular progresiva, mindfulness, yoga, meditación guiada. Practica 10 minutos diarios."
    },
    "ejercicio|deporte|gimnasio|correr|caminar": {
        "respuesta": "El ejercicio es uno de los tratamientos naturales más efectivos para la ansiedad. Libera endorfinas y reduce hormonas del estrés.",
        "recomendacion": "🏃 Empieza con 20-30 minutos diarios de caminata. Cualquier movimiento ayuda: yoga, baile, natación, bicicleta. La constancia es clave."
    },
    "meditacion|meditar|mindfulness|atencion plena": {
        "respuesta": "La meditación y mindfulness son muy efectivos para la ansiedad. Te enseñan a observar pensamientos sin juzgarlos y estar en el presente.",
        "recomendacion": "🧘‍♀️ Empieza con 5 minutos diarios. Apps recomendadas: Headspace, Calm, Insight Timer. Enfócate en tu respiración cuando la mente divague."
    },
    "alimentacion|comer|comida|dieta|nutricion": {
        "respuesta": "La alimentación afecta tu ansiedad. El azúcar, cafeína y comida procesada pueden empeorarla. Una dieta balanceada ayuda.",
        "recomendacion": "🥗 Come regular (no saltes comidas), reduce café y azúcar, aumenta omega-3 (pescado, nueces), toma agua. La nutrición afecta tu ánimo."
    },
    "cafe|cafeina|energizante|bebida energetica": {
        "respuesta": "La cafeína puede empeorar significativamente la ansiedad. Actúa como estimulante y puede desencadenar síntomas físicos similares a ataques de pánico.",
        "recomendacion": "☕ Reduce gradualmente el café (máximo 1-2 tazas al día), evita bebidas energéticas, prueba té descafeinado o infusiones. Observa cómo te sientes."
    },
    "redes sociales|instagram|facebook|tiktok|internet": {
        "respuesta": "El uso excesivo de redes sociales está vinculado con mayor ansiedad. La comparación constante y la sobreestimulación afectan tu bienestar.",
        "recomendacion": "📱 Limita tiempo en redes (máx 30-60 min/día), desactiva notificaciones, haz detox digital semanal. La vida real no es como Instagram."
    },
    "trabajo|empleo|jefe|laboral|empresa": {
        "respuesta": "El estrés laboral es una causa importante de ansiedad. El ambiente de trabajo, carga laboral y relaciones laborales pueden afectarte.",
        "recomendacion": "💼 Establece límites claros trabajo-vida personal, toma descansos, comunica sobrecarga. Si es tóxico, considera cambiar. Tu salud es primero."
    }
}

HAM_A_QUESTIONS = [
    {"id": 1, "text": "¿Con qué frecuencia te has sentido nervioso(a), tenso(a) o preocupado(a) sin una razón clara?"},
    {"id": 2, "text": "¿Has notado dificultad para relajarte, sensación de inquietud o irritabilidad constante?"},
    {"id": 3, "text": "¿Has sentido miedo de que algo malo pueda pasar, o temor a perder el control de tus emociones?"},
    {"id": 4, "text": "¿Has tenido problemas para conciliar el sueño, despertarte varias veces o dormir intranquilo(a)?"},
    {"id": 5, "text": "¿Te cuesta concentrarte en tus estudios o recordar información importante?"},
    {"id": 6, "text": "¿Has sentido tensión en el cuello, hombros o espalda, temblores o sensación de debilidad?"},
    {"id": 7, "text": "¿Has tenido sensación de mareo, visión borrosa, zumbido en los oídos o sudoración excesiva?"},
    {"id": 8, "text": "¿Has notado palpitaciones, presión en el pecho o sensación de falta de aire cuando estás estresado(a)?"},
    {"id": 9, "text": "¿Sientes que respiras más rápido, te cuesta llenar los pulmones o suspiras con frecuencia?"},
    {"id": 10, "text": "¿Has presentado molestias estomacales, náuseas o cambios en el apetito relacionados con el estrés?"},
    {"id": 11, "text": "¿Has tenido aumento o disminución del deseo sexual, o molestias físicas sin causa aparente?"},
    {"id": 12, "text": "¿Has notado sensación de calor, escalofríos, sequedad en la boca o rubor facial sin motivo?"}
]

def analyze_message(message):
    """Analiza el mensaje y devuelve respuestas"""
    message_lower = message.lower()
    responses = []
    
    for keywords, data in KNOWLEDGE.items():
        for keyword in keywords.split('|'):
            if keyword in message_lower:
                responses.append({
                    'type': 'symptom',
                    'message': data['respuesta'],
                    'recommendation': data['recomendacion']
                })
                break
    
    if not responses:
        responses.append({
            'type': 'general',
            'message': 'Gracias por compartir eso conmigo. Tus emociones son importantes. ¿Podrías contarme un poco más sobre cómo te has sentido?',
            'recommendation': None
        })
    
    return responses[:2]

# ============================================
# TEMPLATES HTML
# ============================================

LOGIN_HTML = '''
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Anxiety Chat - Login</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Segoe UI', sans-serif;
            background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
            height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
        }
        .login-box {
            background: white;
            padding: 40px;
            border-radius: 20px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.3);
            width: 90%;
            max-width: 420px;
        }
        h1 { color: #1e3c72; text-align: center; margin-bottom: 10px; }
        .subtitle { color: #ff6b35; text-align: center; font-weight: bold; margin-bottom: 5px; }
        .university { color: #666; text-align: center; font-size: 14px; margin-bottom: 30px; }
        input {
            width: 100%;
            padding: 14px;
            margin: 10px 0;
            border: 2px solid #1e3c72;
            border-radius: 10px;
            font-size: 15px;
        }
        input:focus { outline: none; border-color: #ff6b35; }
        button {
            width: 100%;
            padding: 14px;
            margin: 10px 0;
            border: none;
            border-radius: 10px;
            font-size: 16px;
            font-weight: bold;
            cursor: pointer;
            color: white;
        }
        .btn-login { background: linear-gradient(90deg, #1e3c72 0%, #2a5298 100%); }
        .btn-register { background: linear-gradient(90deg, #ff6b35 0%, #ff8555 100%); }
        button:hover { transform: scale(1.02); transition: 0.2s; }
        .toggle { text-align: center; color: #1e3c72; cursor: pointer; margin-top: 15px; text-decoration: underline; }
        .error { color: #ff3333; text-align: center; margin: 10px 0; }
        .privacy { text-align: center; font-size: 12px; color: #999; margin-top: 20px; }
    </style>
</head>
<body>
    <div class="login-box">
        <h1>🧠 Anxiety Chat</h1>
        <p class="subtitle">Asistente Virtual de Bienestar Emocional</p>
        <p class="university">Corporación Universitaria Rafael Núñez</p>
        
        <div id="loginForm">
            <input type="text" id="loginUser" placeholder="Usuario">
            <input type="password" id="loginPass" placeholder="Contraseña">
            <button class="btn-login" onclick="login()">Iniciar Sesión</button>
            <p class="toggle" onclick="showRegister()">¿No tienes cuenta? Regístrate</p>
        </div>
        
        <div id="registerForm" style="display:none;">
            <input type="text" id="regUser" placeholder="Nuevo Usuario">
            <input type="password" id="regPass" placeholder="Contraseña">
            <input type="password" id="regConfirm" placeholder="Confirmar Contraseña">
            <button class="btn-register" onclick="register()">Crear Cuenta</button>
            <p class="toggle" onclick="showLogin()">¿Ya tienes cuenta? Inicia sesión</p>
        </div>
        
        <p id="error" class="error"></p>
        <p class="privacy">🔒 Confidencial y seguro</p>
    </div>

    <script>
        function showRegister() {
            document.getElementById('loginForm').style.display = 'none';
            document.getElementById('registerForm').style.display = 'block';
            document.getElementById('error').textContent = '';
        }
        
        function showLogin() {
            document.getElementById('loginForm').style.display = 'block';
            document.getElementById('registerForm').style.display = 'none';
            document.getElementById('error').textContent = '';
        }
        
        async function login() {
            const user = document.getElementById('loginUser').value.trim();
            const pass = document.getElementById('loginPass').value;
            
            if (!user || !pass) {
                document.getElementById('error').textContent = 'Completa todos los campos';
                return;
            }
            
            const res = await fetch('/login', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({username: user, password: pass})
            });
            
            const data = await res.json();
            if (data.success) {
                window.location.href = '/chat';
            } else {
                document.getElementById('error').textContent = data.message;
            }
        }
        
        async function register() {
            const user = document.getElementById('regUser').value.trim();
            const pass = document.getElementById('regPass').value;
            const confirm = document.getElementById('regConfirm').value;
            
            if (!user || !pass || !confirm) {
                document.getElementById('error').textContent = 'Completa todos los campos';
                return;
            }
            
            if (pass !== confirm) {
                document.getElementById('error').textContent = 'Las contraseñas no coinciden';
                return;
            }
            
            const res = await fetch('/register', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({username: user, password: pass})
            });
            
            const data = await res.json();
            if (data.success) {
                alert('¡Registro exitoso! Ahora inicia sesión');
                showLogin();
            } else {
                document.getElementById('error').textContent = data.message;
            }
        }
        
        document.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                if (document.getElementById('loginForm').style.display !== 'none') {
                    login();
                } else {
                    register();
                }
            }
        });
    </script>
</body>
</html>
'''

CHAT_HTML = '''
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Anxiety Chat</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Segoe UI', sans-serif;
            background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
            height: 100vh;
            overflow: hidden;
        }
        .container { height: 100vh; display: flex; flex-direction: column; }
        .header {
            background: linear-gradient(90deg, #1e3c72 0%, #ff6b35 100%);
            color: white;
            padding: 15px 20px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .header h1 { font-size: 22px; }
        .header p { font-size: 13px; opacity: 0.9; }
        .header-buttons {
            display: flex;
            gap: 10px;
        }
        .history-btn, .logout-btn {
            background: rgba(255,255,255,0.2);
            border: none;
            color: white;
            padding: 8px 16px;
            border-radius: 20px;
            cursor: pointer;
            font-size: 14px;
        }
        .history-btn:hover, .logout-btn:hover {
            background: rgba(255,255,255,0.3);
        }
        .chat-container {
            flex: 1;
            overflow-y: auto;
            padding: 20px;
            background: white;
        }
        .message {
            margin-bottom: 15px;
            display: flex;
            animation: fadeIn 0.3s;
        }
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }
        .message.bot { justify-content: flex-start; }
        .message.user { justify-content: flex-end; }
        .message-content {
            max-width: 75%;
            padding: 12px 16px;
            border-radius: 18px;
            line-height: 1.5;
        }
        .message.bot .message-content {
            background: #f0f4ff;
            color: #1e3c72;
            border-bottom-left-radius: 4px;
        }
        .message.user .message-content {
            background: #ff6b35;
            color: white;
            border-bottom-right-radius: 4px;
        }
        .input-area {
            padding: 15px 20px;
            background: #f8f9fa;
            border-top: 1px solid #ddd;
            display: flex;
            gap: 10px;
        }
        .input-area input {
            flex: 1;
            padding: 12px 16px;
            border: 2px solid #1e3c72;
            border-radius: 25px;
            font-size: 15px;
            outline: none;
        }
        .input-area input:focus { border-color: #ff6b35; }
        .input-area button {
            padding: 12px 24px;
            background: linear-gradient(90deg, #ff6b35 0%, #ff8555 100%);
            color: white;
            border: none;
            border-radius: 25px;
            cursor: pointer;
            font-weight: bold;
        }
        .history-panel {
            position: fixed;
            right: -400px;
            top: 0;
            width: 400px;
            height: 100vh;
            background: white;
            box-shadow: -2px 0 10px rgba(0,0,0,0.3);
            transition: right 0.3s ease;
            z-index: 1000;
            display: flex;
            flex-direction: column;
        }
        .history-panel.open {
            right: 0;
        }
        .history-header {
            background: linear-gradient(90deg, #1e3c72 0%, #ff6b35 100%);
            color: white;
            padding: 20px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .history-header h2 {
            margin: 0;
            font-size: 20px;
        }
        .close-history {
            background: rgba(255,255,255,0.2);
            border: none;
            color: white;
            padding: 8px 16px;
            border-radius: 20px;
            cursor: pointer;
            font-size: 14px;
        }
        .close-history:hover {
            background: rgba(255,255,255,0.3);
        }
        .history-content {
            flex: 1;
            overflow-y: auto;
            padding: 20px;
        }
        .session-card {
            background: #f0f4ff;
            border-left: 4px solid #1e3c72;
            padding: 15px;
            margin-bottom: 15px;
            border-radius: 8px;
        }
        .session-card h3 {
            color: #1e3c72;
            font-size: 16px;
            margin: 0 0 10px 0;
        }
        .session-date {
            color: #666;
            font-size: 13px;
            margin-bottom: 10px;
        }
        .session-score {
            font-size: 18px;
            font-weight: bold;
            color: #ff6b35;
            margin: 10px 0;
        }
        .session-level {
            display: inline-block;
            padding: 5px 12px;
            border-radius: 15px;
            font-size: 13px;
            font-weight: bold;
            margin-top: 8px;
        }
        .level-low {
            background: #d4edda;
            color: #155724;
        }
        .level-moderate {
            background: #fff3cd;
            color: #856404;
        }
        .level-high {
            background: #f8d7da;
            color: #721c24;
        }
        .no-sessions {
            text-align: center;
            color: #666;
            padding: 40px 20px;
        }
    </style>
</head>
<body>
    <div class="history-panel" id="historyPanel">
        <div class="history-header">
            <h2>📚 Historial de Sesiones</h2>
            <button class="close-history" onclick="closeHistory()">✕ Cerrar</button>
        </div>
        <div class="history-content" id="historyContent">
            <div class="no-sessions">Cargando historial...</div>
        </div>
    </div>
    
    <div class="container">
        <div class="header">
            <div>
                <h1>🧠 Anxiety Chat</h1>
                <p>Usuario: {{ username }}</p>
            </div>
            <div class="header-buttons">
                <button class="history-btn" onclick="showHistory()">📚 Historial</button>
                <button class="logout-btn" onclick="location.href='/logout'">Cerrar Sesión</button>
            </div>
        </div>
        <div class="chat-container" id="chat" style="flex:1;overflow-y:auto;padding:20px;background:white;scroll-behavior:smooth;"></div>

<!-- Input fijo visible en móvil -->
<div id="input-area"
     style="display:flex;gap:10px;padding:10px;background:#fff;border-top:1px solid #ddd;
            position:sticky;bottom:0;left:0;width:100%;box-sizing:border-box;align-items:center;">
    <input type="text" id="input" placeholder="Escribe aquí..."
           onkeypress="if(event.key==='Enter')send()"
           style="flex:1;padding:12px 14px;border:2px solid #1e3c72;border-radius:25px;font-size:15px;outline:none;">
    <button onclick="send()" 
            style="padding:12px 20px;background:linear-gradient(90deg,#ff6b35 0%,#ff8555 100%);
                   color:white;border:none;border-radius:25px;cursor:pointer;font-weight:bold;">Enviar</button>
</div>

<script>
  // 👇 Esto evita que el teclado del celular tape el input
  window.addEventListener('resize', () => {
      document.body.style.height = window.innerHeight + 'px';
  });
</script>


    <script>
        let state = 'initial';
        let score = 0;
        let currentQ = 0;
        let responses = {};
        let generalLevel = 0;
        let hamaCompleted = false;
        
        const questions = {{ questions|tojson }};
        
        function addBot(text) {
            const chat = document.getElementById('chat');
            const div = document.createElement('div');
            div.className = 'message bot';
            div.innerHTML = '<div class="message-content">' + text + '</div>';
            chat.appendChild(div);
            chat.scrollTop = chat.scrollHeight;
        }
        
        function addUser(text) {
            const chat = document.getElementById('chat');
            const div = document.createElement('div');
            div.className = 'message user';
            div.innerHTML = '<div class="message-content">' + text + '</div>';
            chat.appendChild(div);
            chat.scrollTop = chat.scrollHeight;
        }
        
        function welcome() {
            addBot("👋 ¡Hola! Soy Anxiety Chat, tu asistente de bienestar emocional.");
            setTimeout(() => addBot("💡 Estoy aquí para ayudarte a reconocer cómo te has sentido y acompañarte en la identificación de síntomas de ansiedad."), 1000);
            setTimeout(() => addBot("Esto no reemplaza la valoración profesional, pero puede orientarte."), 2000);
            setTimeout(() => addBot("🔒 Todas tus respuestas son confidenciales y anónimas."), 3000);
            setTimeout(() => addBot("¿Quieres comenzar? Escribe 'sí' para empezar."), 4000);
        }
        
        async function send() {
            const input = document.getElementById('input');
            const msg = input.value.trim();
            if (!msg) return;
            
            addUser(msg);
            input.value = '';
            
            await process(msg);
        }
        
        async function process(msg) {
            const lower = msg.toLowerCase();
            
            if ((lower.includes('gracias') || lower.includes('muchas gracias')) && state !== 'initial' && state !== 'finished') {
                setTimeout(() => {
                    addBot("¡De nada! Ha sido un gusto poder ayudarte 😊");
                    setTimeout(() => addBot("Espero que te sientas mejor después de nuestra conversación."), 1500);
                    setTimeout(() => addBot("Recuerda que pedir ayuda es valentía 💚"), 3000);
                    setTimeout(() => addBot("¿Te gustaría iniciar una nueva conversación o terminamos aquí?"), 4500);
                    state = 'finished';
                }, 500);
                return;
            }
            
            if (state === 'initial') {
                if (lower.includes('si') || lower.includes('sí') || lower.includes('comenzemos') || lower.includes('quiero') || lower.includes('comenzar') || lower.includes('iniciar')) {
                    setTimeout(() => {
                        addBot("¡Perfecto! Cuéntame: ¿cómo te has sentido en los últimos días?");
                        state = 'conversation';
                    }, 500);
                } else if (lower.includes('no')) {
                    setTimeout(() => {
                        addBot("Está bien. Cuando quieras hablar, estaré aquí.");
                        state = 'conversation';
                    }, 500);
                } else {
                    setTimeout(() => addBot("¿Te gustaría comenzar? Escribe 'sí' cuando estés listo(a)."), 500);
                }
            } else if (state === 'conversation') {
                const res = await fetch('/api/analyze', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({message: msg})
                });
                const data = await res.json();
                
                setTimeout(() => {
                    if (data.responses && data.responses.length > 0) {
                        addBot(data.responses[0].message);
                        if (data.responses[0].recommendation) {
                            setTimeout(() => addBot(data.responses[0].recommendation), 1500);
                        }
                        setTimeout(() => addBot("¿Hay algún otro síntoma que quieras mencionar?"), 3000);
                        setTimeout(() => addBot("Si terminaste, podemos hacer el cuestionario HAM-A. ¿Quieres continuar?"), 4500);
                        state = 'ask_hama';
                    }
                }, 500);
            } else if (state === 'ask_hama') {
                if (lower.includes('si') || lower.includes('sí') || lower.includes('quiero')) {
                    startHama();
                } else {
                    setTimeout(() => {
                        addBot("¿Hay algo más que quieras compartir?");
                        state = 'final';
                    }, 500);
                }
            } else if (state === 'hama') {
                const val = parseInt(msg);
                if (isNaN(val) || val < 0 || val > 4) {
                    setTimeout(() => addBot("⚠️ Ingresa un número entre 0 y 4."), 500);
                    return;
                }
                score += val;
                responses[questions[currentQ].id] = val;
                setTimeout(() => addBot("✓ Registrado"), 300);
                currentQ++;
                if (currentQ < questions.length) {
                    setTimeout(() => nextQ(), 800);
                } else {
                    setTimeout(() => observation(), 1000);
                }
            } else if (state === 'general') {
                const val = parseInt(msg);
                if (isNaN(val) || val < 0 || val > 10) {
                    setTimeout(() => addBot("⚠️ Ingresa un número entre 0 y 10."), 500);
                    return;
                }
                generalLevel = val;
                setTimeout(() => {
                    addBot("✓ Gracias.");
                    setTimeout(() => {
                        addBot("¿Tienes algún otro síntoma o pregunta antes de finalizar?");
                        state = 'final';
                    }, 1500);
                }, 500);
            } else if (state === 'final') {
                if (lower.includes('no') || lower.includes('terminamos')|| lower.includes('terminar') || lower.includes('listo')) {
                    if (!hamaCompleted) {
                        setTimeout(() => {
                            addBot("Antes de terminar, me gustaría recordarte que tenemos un cuestionario de evaluación (HAM-A) que puede ayudarte a entender mejor tu nivel de ansiedad.");
                            setTimeout(() => addBot("¿Te gustaría hacer el cuestionario antes de finalizar? Es rápido, solo 12 preguntas."), 2000);
                            state = 'ask_hama_final';
                        }, 500);
                    } else {
                        conclusion();
                    }
                } else {
                    const res = await fetch('/api/analyze', {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify({message: msg})
                    });
                    const data = await res.json();
                    
                    setTimeout(() => {
                        if (data.responses && data.responses.length > 0) {
                            addBot(data.responses[0].message);
                            if (data.responses[0].recommendation) {
                                setTimeout(() => addBot(data.responses[0].recommendation), 1500);
                            }
                        }
                        setTimeout(() => addBot("¿Algo más o terminamos?"), 2000);
                    }, 500);
                }
            } else if (state === 'finished') {
                if (lower.includes('si') || lower.includes('sí') || lower.includes('nuevo') || lower.includes('nueva conversacion')) {
                    state = 'initial';
                    score = 0;
                    currentQ = 0;
                    responses = {};
                    generalLevel = 0;
                    hamaCompleted = false;
                    document.getElementById('chat').innerHTML = '';
                    setTimeout(() => {
                        addBot("¡Perfecto! Comenzamos de nuevo 🔄");
                        setTimeout(() => welcome(), 1000);
                    }, 500);
                } else if (lower.includes('historial') || lower.includes('historia') || lower.includes('sesiones') || lower.includes('ver historial') || lower.includes('ver historia')) {
                    showHistory();
                    setTimeout(() => addBot("¿Quieres iniciar una nueva conversación?"), 2000);
                } else if (lower.includes('no')) {
                    setTimeout(() => addBot("Entiendo. Siempre estaré aquí cuando me necesites. Cuídate mucho 💙"), 500);
                } else {
                    setTimeout(() => addBot("¿Quieres iniciar una nueva conversación o no?"), 500);
                }
            } else if (state === 'ask_hama_final') {
                if (lower.includes('si') || lower.includes('sí') || lower.includes('quiero') || lower.includes('si quiero')|| lower.includes('iniciar una nueva conversacion')|| lower.includes('iniciar') || lower.includes('iniciar otra')) {
                    startHama();
                } else {
                    setTimeout(() => addBot("Entiendo. Entonces finalizamos sin el cuestionario."), 500);
                    setTimeout(() => conclusionWithoutHama(), 1500);
                }
            }
        }
        
        function startHama() {
            state = 'hama';
            currentQ = 0;
            hamaCompleted = false;
            setTimeout(() => {
                addBot("Perfecto. Voy a hacerte 12 preguntas. Responde con un número:");
                setTimeout(() => addBot("0 = Ninguno | 1 = Leve | 2 = Moderado | 3 = Severo | 4 = Muy severo"), 1000);
                setTimeout(() => nextQ(), 2000);
            }, 500);
        }
        
        function nextQ() {
            const q = questions[currentQ];
            addBot(`Pregunta ${currentQ + 1}/12: ${q.text}`);
            setTimeout(() => addBot("Responde: 0, 1, 2, 3 o 4"), 500);
        }
        
        function observation() {
            hamaCompleted = true;
            addBot("📊 He estado analizando tus respuestas para reconocer señales de ansiedad.");
            setTimeout(() => {
                addBot("Última pregunta: En escala del 0 al 10, ¿cómo calificarías tu nivel de ansiedad general en los últimos días?");
                state = 'general';
            }, 2000);
        }
        
        async function conclusionWithoutHama() {
            setTimeout(() => addBot("Gracias por compartir conmigo 💬."), 500);
            setTimeout(() => addBot("Aunque no hicimos el cuestionario, espero que nuestra conversación te haya sido útil."), 1500);
            setTimeout(() => addBot("🌿 Te recomiendo respirar profundo, descansar y si los síntomas persisten, buscar orientación profesional."), 3000);
            setTimeout(() => addBot("Recuerda: pedir ayuda es autocuidado y fortaleza 💙"), 4500);
            setTimeout(() => {
                addBot("¿Te gustaría ver tu historial de conversaciones o iniciar una nueva conversación?");
                state = 'finished';
            }, 6000);
        }
        
        async function conclusion() {
            setTimeout(() => addBot("📊 Procesando..."), 500);
            setTimeout(() => addBot(`Tu puntuación HAM-A: ${score}/48 puntos`), 1500);
            
            setTimeout(() => {
                if (score < 18) {
                    addBot("🌿 Tu nivel de ansiedad está en rango leve o controlado. Aun así, cuida tu bienestar mental.");
                    setTimeout(() => addBot("Te recomiendo: descansar 7-8 horas, hacer ejercicio, hablar con alguien de confianza."), 2000);
                    setTimeout(() => addBot("Si tu ansiedad aumenta, buscar ayuda profesional siempre es buena decisión 💚."), 4000);
                } else {
                    addBot("⚠️ Tus respuestas indican un nivel elevado de ansiedad.");
                    setTimeout(() => addBot("Te recomiendo hablar con un profesional de salud mental para recibir apoyo personalizado."), 2000);
                    setTimeout(() => addBot("No estás solo(a). Pedir ayuda no es debilidad, es un paso valiente 💚."), 4000);
                    setTimeout(() => addBot("📞 Universidad: bienestar@curnvirtual.edu.co | Línea 24/7: 01 8000 1119"), 6000);
                }
            }, 2500);
            
            setTimeout(() => addBot("Gracias por compartir cómo te has sentido 💬."), score < 18 ? 6500 : 8500);
            setTimeout(() => addBot("🌿 Te recomiendo respirar profundo, descansar y buscar orientación si los síntomas persisten."), score < 18 ? 8000 : 10000);
            setTimeout(() => addBot("Recuerda: pedir ayuda es autocuidado y fortaleza 💙"), score < 18 ? 9500 : 11500);
            
            await fetch('/api/save', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({score, responses, generalLevel})
            });
            
            setTimeout(() => {
                addBot("¿Te gustaría iniciar una nueva conversación o terminamos aquí?");
                state = 'finished';
            }, score < 18 ? 11000 : 13000);
        }
        
        async function showHistory() {
            const panel = document.getElementById('historyPanel');
            const content = document.getElementById('historyContent');
            
            panel.classList.add('open');
            
            const res = await fetch('/api/history');
            const data = await res.json();
            
            if (data.sessions && data.sessions.length > 0) {
                let html = '';
                
                data.sessions.forEach((s, index) => {
                    const date = new Date(s.timestamp).toLocaleString('es-CO', {
                        year: 'numeric',
                        month: 'long',
                        day: 'numeric',
                        hour: '2-digit',
                        minute: '2-digit'
                    });
                    
                    if (s.score !== undefined && s.score !== null) {
                        let levelClass = '';
                        let levelText = '';
                        
                        if (s.score < 18) {
                            levelClass = 'level-low';
                            levelText = '🟢 Ansiedad leve/controlada';
                        } else if (s.score < 25) {
                            levelClass = 'level-moderate';
                            levelText = '🟡 Ansiedad moderada';
                        } else {
                            levelClass = 'level-high';
                            levelText = '🔴 Ansiedad elevada';
                        }
                        
                        html += `
                            <div class="session-card">
                                <h3>Sesión ${data.sessions.length - index}</h3>
                                <div class="session-date">📅 ${date}</div>
                                <div class="session-score">📊 Puntuación HAM-A: ${s.score}/48</div>
                                <div class="session-level ${levelClass}">${levelText}</div>
                                ${s.general_level !== undefined ? `<div style="margin-top:10px;color:#666;font-size:14px;">📈 Nivel autoevaluado: ${s.general_level}/10</div>` : ''}
                            </div>
                        `;
                    } else {
                        html += `
                            <div class="session-card" style="border-left-color: #ccc;">
                                <h3>Sesión ${data.sessions.length - index}</h3>
                                <div class="session-date">📅 ${date}</div>
                                <div style="color:#999;font-style:italic;margin-top:10px;">
                                    ⚠️ No completó el cuestionario HAM-A
                                </div>
                            </div>
                        `;
                    }
                });
                
                content.innerHTML = html;
            } else {
                content.innerHTML = `
                    <div class="no-sessions">
                        <p style="font-size:18px;margin-bottom:10px;">📚</p>
                        <p>Aún no tienes sesiones registradas</p>
                        <p style="font-size:13px;margin-top:10px;color:#999;">Completa el cuestionario HAM-A para guardar tu primera sesión</p>
                    </div>
                `;
            }
        }
        
        function closeHistory() {
            document.getElementById('historyPanel').classList.remove('open');
        }
        
        window.onload = welcome;
    </script>
</body>
</html>
'''

@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('chat'))
    return render_template_string(LOGIN_HTML)

@app.route('/register', methods=['POST'])
def register():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    
    if not username or not password:
        return jsonify({'success': False, 'message': 'Datos incompletos'})
    
    if username in users_db:
        return jsonify({'success': False, 'message': 'Usuario ya existe'})
    
    users_db[username] = {
        'password': generate_password_hash(password),
        'created_at': datetime.now().isoformat(),
        'sessions': []
    }
    save_json('users.json', users_db)
    
    return jsonify({'success': True})

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    
    if not username or not password:
        return jsonify({'success': False, 'message': 'Datos incompletos'})
    
    if username not in users_db:
        return jsonify({'success': False, 'message': 'Usuario no encontrado'})
    
    if check_password_hash(users_db[username]['password'], password):
        session['user_id'] = username
        return jsonify({'success': True})
    
    return jsonify({'success': False, 'message': 'Contraseña incorrecta'})

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('index'))

@app.route('/chat')
def chat():
    if 'user_id' not in session:
        return redirect(url_for('index'))
    return render_template_string(CHAT_HTML, username=session['user_id'], questions=HAM_A_QUESTIONS)

@app.route('/api/analyze', methods=['POST'])
def analyze():
    if 'user_id' not in session:
        return jsonify({'error': 'No autenticado'}), 401
    
    data = request.json
    message = data.get('message', '')
    
    responses = analyze_message(message)
    
    user_id = session['user_id']
    if user_id not in sessions_db:
        sessions_db[user_id] = []
    
    sessions_db[user_id].append({
        'timestamp': datetime.now().isoformat(),
        'message': message,
        'responses': responses
    })
    save_json('sessions.json', sessions_db)
    
    return jsonify({'responses': responses})

@app.route('/api/save', methods=['POST'])
def save():
    if 'user_id' not in session:
        return jsonify({'error': 'No autenticado'}), 401
    
    data = request.json
    user_id = session['user_id']
    
    if user_id not in users_db:
        return jsonify({'error': 'Usuario no encontrado'}), 404
    
    users_db[user_id]['sessions'].append({
        'timestamp': datetime.now().isoformat(),
        'score': data.get('score'),
        'responses': data.get('responses'),
        'general_level': data.get('generalLevel')
    })
    save_json('users.json', users_db)
    
    return jsonify({'success': True})

@app.route('/api/history', methods=['GET'])
def history():
    if 'user_id' not in session:
        return jsonify({'error': 'No autenticado'}), 401
    
    user_id = session['user_id']
    
    if user_id not in users_db:
        return jsonify({'error': 'Usuario no encontrado'}), 404
    
    sessions = users_db[user_id].get('sessions', [])
    
    return jsonify({'sessions': sessions})

if __name__ == '__main__':
    print("\n" + "="*70)
    print("🧠 ANXIETY CHAT - SISTEMA INICIADO")
    print("="*70)
    print("📍 Universidad: Corporación Universitaria Rafael Núñez")
    print("🌐 Accede en: http://localhost:5000")
    print("="*70 + "\n")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
